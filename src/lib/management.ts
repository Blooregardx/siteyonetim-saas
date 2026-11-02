import { dashboardReads } from "./dashboard-reads";
import { incomeExpenses } from "./income-expenses";
import { financialReporting } from "./financial-reporting";
import { bulkInput, BulkInput, fingerprint, bulkTotal } from "./bulk-charges";
import { siteInput, blockInput, unitInput, personInput, dateInput } from "./property-validation";
import { chargeBalance } from "./finance";
import { z } from "zod";
import { actor, audit, organizationAccess, lockOrganization } from "./security";
import { Prisma, PrismaClient, ReversalReason } from "@prisma/client";

// Only a server-side session verifier may supply this callback. Never use request user IDs.
export type SessionVerifier = () => Promise<{ userId: string } | null>;
export function management(db: PrismaClient, verifySession: SessionVerifier) {
  async function authorize(tx: Prisma.TransactionClient, siteId: string) {
    const user = await actor(tx, verifySession);
    const session = { userId: user.id };
    const site = await tx.site.findUnique({ where: { id: siteId } });
    if (site?.organizationId) await lockOrganization(tx, site.organizationId);
    const direct = await tx.membership.findUnique({ where: { siteId_userId: { siteId, userId: session.userId } } });
    const org = site?.organizationId ? await tx.organizationMembership.findUnique({ where: { organizationId_userId: { organizationId: site.organizationId, userId: session.userId } } }) : null;
    if (![direct?.role, org?.role].some(role => role === "ADMIN" || role === "MANAGER")) throw new Error("FORBIDDEN");
    return { userId: user.id, organizationId: site?.organizationId };
  }
  async function bulkSnapshot(tx: Prisma.TransactionClient, input: ReturnType<typeof bulkInput.parse>) {
    const units = await tx.unit.findMany({where:{siteId:input.siteId,id:{in:input.unitIds}},include:{block:true},orderBy:{id:"asc"}});
    if(units.length!==input.unitIds.length)throw new Error("INVALID_UNITS");
    const charges=await tx.charge.findMany({where:{siteId:input.siteId,unitId:{in:input.unitIds},period:input.period},orderBy:{id:"asc"}});
    const rows=units.map(u=>({unitId:u.id,block:u.block.name,number:u.number,exists:charges.some(c=>c.unitId===u.id)}));
    const conflicts=rows.filter(r=>r.exists).map(r=>`${r.block} / ${r.number}`);
    return {rows,conflicts,selectedCount:units.length,newCount:units.length-conflicts.length,totalKurus:bulkTotal(input.amountKurus,units.length-conflicts.length),snapshot:fingerprint({input,units,charges})};
  }
  return {
    ...dashboardReads(db,verifySession),
    ...incomeExpenses(db,verifySession),
    ...financialReporting(db,verifySession),
    async previewBulkCharges(raw: BulkInput) {
      const input=bulkInput.parse(raw);
      return db.$transaction(async tx=>{await authorize(tx,input.siteId);return bulkSnapshot(tx,input);});
    },
    async commitBulkCharges(raw: BulkInput, snapshot:string, idempotencyKey:string) {
      const input=bulkInput.parse(raw);z.string().uuid().parse(idempotencyKey);z.string().regex(/^[a-f0-9]{64}$/).parse(snapshot);
      const requestHash=fingerprint({input,snapshot});
      return db.$transaction(async tx=>{
        const scope=await authorize(tx,input.siteId);
        // Also serializes legacy sites without an organization.
        await tx.$queryRaw`SELECT id FROM "Site" WHERE id=${input.siteId} FOR UPDATE`;
        const previous=await tx.bulkChargeOperation.findUnique({where:{siteId_idempotencyKey:{siteId:input.siteId,idempotencyKey}}});
        if(previous){if(previous.requestHash!==requestHash)throw new Error("IDEMPOTENCY_CONFLICT");return {createdCount:previous.createdCount,totalKurus:Number(previous.totalKurus),period:previous.period};}
        // Freeze selected unit and block metadata until commit, including external writers.
        await tx.$queryRaw`SELECT u.id FROM "Unit" u JOIN "Block" b ON b.id=u."blockId" WHERE u."siteId"=${input.siteId} FOR UPDATE OF u,b`;
        const current=await bulkSnapshot(tx,input);
        if(current.conflicts.length)throw new Error("BULK_CONFLICT:"+current.conflicts.join(", "));
        if(current.snapshot!==snapshot)throw new Error("STALE_PREVIEW");
        for(const unitId of input.unitIds){
          const charge=await tx.charge.create({data:{siteId:input.siteId,unitId,period:input.period,amountKurus:input.amountKurus,dueDate:new Date(input.dueDate)}});
          await audit(tx,scope.userId,"CHARGE_CREATE",charge.id,scope.organizationId,input.siteId);
        }
        const result={createdCount:input.unitIds.length,totalKurus:bulkTotal(input.amountKurus,input.unitIds.length),period:input.period};
        await tx.bulkChargeOperation.create({data:{...result,siteId:input.siteId,idempotencyKey,requestHash}});
        return result;
      },{timeout:60000});
    },
    async setPartialPaymentsAllowed(siteId:string,allowed:boolean) {
      z.boolean().parse(allowed);
      return db.$transaction(async tx=>{
        const user=await actor(tx,verifySession);
        const site=await tx.site.findUnique({where:{id:siteId}});
        if(!site?.organizationId)throw new Error("ORGANIZATION_REQUIRED");
        await organizationAccess(tx,user.id,site.organizationId,true);
        await tx.$queryRaw`SELECT id FROM "Site" WHERE id=${siteId} FOR UPDATE`;
        const current=await tx.site.findUniqueOrThrow({where:{id:siteId}});
        if(current.partialPaymentsAllowed===allowed)return current;
        const change=await tx.paymentPolicyChange.create({data:{siteId,organizationId:site.organizationId,actorId:user.id,oldValue:current.partialPaymentsAllowed,newValue:allowed}});
        const result=await tx.site.update({where:{id:siteId},data:{partialPaymentsAllowed:allowed}});
        await audit(tx,user.id,"PAYMENT_POLICY_CHANGE",change.id,site.organizationId,siteId);
        return result;
      });
    },
    async updateSite(siteId: string, input: unknown) {
      const data=siteInput.parse(input);
      return db.$transaction(async tx=>{const scope=await authorize(tx,siteId);const result=await tx.site.update({where:{id:siteId},data});await audit(tx,scope.userId,"SITE_UPDATE",result.id,scope.organizationId,siteId);return result;});
    },
    async updateBlock(siteId: string, blockId: string, input: unknown) {
      const data=blockInput.parse(input);
      return db.$transaction(async tx=>{const scope=await authorize(tx,siteId);const block=await tx.block.findFirstOrThrow({where:{id:blockId,siteId}});const result=await tx.block.update({where:{id:block.id},data});await audit(tx,scope.userId,"BLOCK_UPDATE",result.id,scope.organizationId,siteId);return result;});
    },
    async updateUnit(siteId: string, unitId: string, input: unknown) {
      const data=unitInput.parse(input);
      return db.$transaction(async tx=>{const scope=await authorize(tx,siteId);const unit=await tx.unit.findFirstOrThrow({where:{id:unitId,siteId}});const result=await tx.unit.update({where:{id:unit.id},data});await audit(tx,scope.userId,"UNIT_UPDATE",result.id,scope.organizationId,siteId);return result;});
    },
    async createPerson(siteId: string, name: string) {
      const validName=personInput.parse(name);
      return db.$transaction(async tx=>{const scope=await authorize(tx,siteId);if(!scope.organizationId)throw new Error("ORGANIZATION_REQUIRED");await organizationAccess(tx,scope.userId,scope.organizationId);const result=await tx.person.create({data:{organizationId:scope.organizationId,name:validName}});await audit(tx,scope.userId,"PERSON_CREATE",result.id,scope.organizationId,siteId);return result;});
    },
    async linkPerson(siteId: string, unitId: string, personId: string, kind: "OWNER"|"TENANT", start: string) {
      const startedAt=dateInput.parse(start);z.enum(["OWNER","TENANT"]).parse(kind);
      return db.$transaction(async tx=>{
        const scope=await authorize(tx,siteId);if(!scope.organizationId)throw new Error("ORGANIZATION_REQUIRED");
        await organizationAccess(tx,scope.userId,scope.organizationId);
        await tx.unit.findFirstOrThrow({where:{id:unitId,siteId}});
        const person=await tx.person.findFirstOrThrow({where:{id:personId,organizationId:scope.organizationId}});
        const where={siteId,unitId,personId,OR:[{endedAt:null},{endedAt:{gte:startedAt}}]};
        const duplicate=kind==="OWNER" ? await tx.ownership.findFirst({where}) : await tx.occupancy.findFirst({where:{...where,kind:"TENANT"}});
        if(duplicate)throw new Error("OVERLAPPING_RELATION");
        const data={organizationId:scope.organizationId,siteId,unitId,personId,startedAt};
        const result=kind==="OWNER" ? await tx.ownership.create({data}) : await tx.occupancy.create({data:{...data,name:person.name,kind:"TENANT"}});
        await audit(tx,scope.userId,kind==="OWNER"?"OWNERSHIP_CREATE":"TENANCY_CREATE",result.id,scope.organizationId,siteId);return result;
      });
    },
    async endRelation(siteId: string, id: string, kind: "OWNER"|"TENANT", end: string) {
      const endedAt=dateInput.parse(end);z.enum(["OWNER","TENANT"]).parse(kind);
      return db.$transaction(async tx=>{
        const scope=await authorize(tx,siteId);
        const current=kind==="OWNER"?await tx.ownership.findFirstOrThrow({where:{id,siteId}}):await tx.occupancy.findFirstOrThrow({where:{id,siteId,kind:"TENANT"}});
        if(current.endedAt||endedAt<current.startedAt)throw new Error("INVALID_RELATION_END");
        const result=kind==="OWNER"?await tx.ownership.update({where:{id},data:{endedAt}}):await tx.occupancy.update({where:{id},data:{endedAt}});
        await audit(tx,scope.userId,kind==="OWNER"?"OWNERSHIP_END":"TENANCY_END",id,scope.organizationId,siteId);return result;
      });
    },
    async propertyDetails(siteId: string) {
      return db.$transaction(async tx=>{const scope=await authorize(tx,siteId);const member=scope.organizationId?await tx.organizationMembership.findUnique({where:{organizationId_userId:{organizationId:scope.organizationId,userId:scope.userId}}}):null;const canReadPeople=member&&["ADMIN","MANAGER"].includes(member.role);return {site:await tx.site.findUniqueOrThrow({where:{id:siteId},include:{blocks:true,units:{include:{occupants:true,ownerships:{include:{person:true}}}}}}),persons:scope.organizationId&&canReadPeople?await tx.person.findMany({where:{organizationId:scope.organizationId},orderBy:{name:"asc"}}):[]};});
    },
    async createOrganization(name: string, kind: "INDIVIDUAL" | "COMPANY") {
      if (!name.trim() || name.length > 200 || !["INDIVIDUAL", "COMPANY"].includes(kind)) throw new Error("INVALID_ORGANIZATION");
      return db.$transaction(async tx => {
        const user = await actor(tx, verifySession);
        const result = await tx.organization.create({ data: { name: name.trim(), kind, memberships: { create: { userId: user.id, role: "ADMIN" } } } });
        await audit(tx, user.id, "ORGANIZATION_CREATE", result.id, result.id);
        return result;
      });
    },
    async portfolio(organizationId: string) {
      return db.$transaction(async tx => {
        const user = await actor(tx, verifySession);
        await organizationAccess(tx, user.id, organizationId);
        return tx.organization.findUniqueOrThrow({ where: { id: organizationId }, include: { sites: { include: { _count: { select: { blocks: true, units: true } } } } } });
      });
    },
    async createSite(organizationId: string, name: string) {
      if (!name.trim() || name.length > 200) throw new Error("INVALID_NAME");
      return db.$transaction(async tx => {
        const user = await actor(tx, verifySession);
        await organizationAccess(tx, user.id, organizationId);
        const result = await tx.site.create({ data: { organizationId, name: name.trim() } });
        await audit(tx, user.id, "SITE_CREATE", result.id, organizationId, result.id);
        return result;
      });
    },
    async dashboard(siteId: string) {
      return db.$transaction(async tx => {
        await authorize(tx, siteId);
        return tx.site.findUniqueOrThrow({ where: { id: siteId }, include: { blocks: true, units: { include: { occupants: true, ownerships: { include: { person: true } } } }, charges: { include: { payments: { include: { reversal: { include: { actor: { select: { name: true } } } } } } } } } });
      });
    },
    async createBlock(siteId: string, name: string) {
      if (!name.trim() || name.length > 100) throw new Error("INVALID_NAME");
      return db.$transaction(async tx => { const scope = await authorize(tx, siteId); const result = await tx.block.create({ data: { siteId, name: name.trim() } }); await audit(tx, scope.userId, "BLOCK_CREATE", result.id, scope.organizationId, siteId); return result; });
    },
    async createUnit(siteId: string, blockId: string, number: string) {
      if (!number.trim() || number.length > 30) throw new Error("INVALID_NUMBER");
      return db.$transaction(async tx => { const scope = await authorize(tx, siteId); const result = await tx.unit.create({ data: { siteId, blockId, number: number.trim() } }); await audit(tx, scope.userId, "UNIT_CREATE", result.id, scope.organizationId, siteId); return result; });
    },
    async recordOccupant(siteId: string, unitId: string, name: string, kind: "OWNER" | "TENANT", startedAt: Date) {
      if (!name.trim() || name.length > 200 || !["OWNER", "TENANT"].includes(kind) || !Number.isFinite(startedAt.getTime())) throw new Error("INVALID_OCCUPANT");
      return db.$transaction(async tx => {
        const scope=await authorize(tx,siteId);if(!scope.organizationId)throw new Error("ORGANIZATION_REQUIRED");
        await organizationAccess(tx,scope.userId,scope.organizationId);
        await tx.unit.findFirstOrThrow({where:{id:unitId,siteId}});
        const person=await tx.person.create({data:{organizationId:scope.organizationId,name:name.trim()}});
        await audit(tx,scope.userId,"PERSON_CREATE",person.id,scope.organizationId,siteId);
        const data={siteId,unitId,organizationId:scope.organizationId,personId:person.id,startedAt};
        const result=kind==="OWNER"?await tx.ownership.create({data}):await tx.occupancy.create({data:{...data,name:person.name,kind}});
        await audit(tx,scope.userId,"OCCUPANT_CREATE",result.id,scope.organizationId,siteId);return result;
      });
    },
    async createCharge(siteId: string, unitId: string, period: string, amountKurus: number, dueDate: Date) {
      if (!/^\d{4}-(0[1-9]|1[0-2])$/.test(period) || !Number.isInteger(amountKurus) || amountKurus <= 0 || amountKurus > 2147483647 || !Number.isFinite(dueDate.getTime())) throw new Error("INVALID_CHARGE");
      return db.$transaction(async tx => { const scope = await authorize(tx, siteId); const result = await tx.charge.create({ data: { siteId, unitId, period, amountKurus, dueDate } }); await audit(tx, scope.userId, "CHARGE_CREATE", result.id, scope.organizationId, siteId); return result; });
    },
    async reversePayment(siteId: string, paymentId: string, reasonCode: ReversalReason, idempotencyKey: string) {
      z.string().uuid().parse(idempotencyKey);
      z.enum(["DUPLICATE_ENTRY", "WRONG_AMOUNT", "WRONG_CHARGE", "ENTRY_ERROR"]).parse(reasonCode);
      return db.$transaction(async tx => {
        const user = await actor(tx, verifySession);
        const site = await tx.site.findUnique({ where: { id: siteId } });
        if (!site?.organizationId) throw new Error("FORBIDDEN");
        await organizationAccess(tx, user.id, site.organizationId, true);
        const payment = await tx.payment.findFirst({ where: { id: paymentId, siteId } });
        if (!payment) throw new Error("PAYMENT_NOT_FOUND");
        await tx.$queryRaw`SELECT id FROM "Charge" WHERE id = ${payment.chargeId} AND "siteId" = ${siteId} FOR UPDATE`;
        await tx.$queryRaw`SELECT id FROM "Payment" WHERE id = ${paymentId} AND "siteId" = ${siteId} FOR UPDATE`;
        const previous = await tx.paymentReversal.findUnique({ where: { siteId_idempotencyKey: { siteId, idempotencyKey } } });
        if (previous) {
          if (previous.paymentId !== paymentId || previous.reasonCode !== reasonCode) throw new Error("IDEMPOTENCY_CONFLICT");
          return previous;
        }
        if (await tx.paymentReversal.findUnique({ where: { paymentId } })) throw new Error("ALREADY_REVERSED");
        const result = await tx.paymentReversal.create({ data: { siteId, paymentId, amountKurus: payment.amountKurus, reasonCode, actorId: user.id, idempotencyKey } });
        await audit(tx, user.id, "PAYMENT_REVERSE", result.id, site.organizationId, siteId);
        return result;
      });
    },
    async collect(siteId: string, chargeId: string, amountKurus: number, idempotencyKey: string, method: "CASH" | "TRANSFER" = "CASH", fullBalance = false) {
      z.boolean().parse(fullBalance);
      if (!["CASH", "TRANSFER"].includes(method) || !Number.isInteger(amountKurus) || amountKurus <= 0 || amountKurus > 2147483647 || !idempotencyKey.trim() || idempotencyKey.length > 128) throw new Error("INVALID_PAYMENT");
      return db.$transaction(async tx => {
        const scope = await authorize(tx, siteId);
        // Lock order: actor -> organization -> Site -> Charge. Policy changes use the same prefix.
        await tx.$queryRaw`SELECT id FROM "Site" WHERE id=${siteId} FOR UPDATE`;
        // Serialize all receipts for this charge, including concurrent partial payments.
        const rows = await tx.$queryRaw<{ amountKurus: number }[]>`SELECT "amountKurus" FROM "Charge" WHERE "siteId" = ${siteId} AND id = ${chargeId} FOR UPDATE`;
        if (!rows.length) throw new Error("CHARGE_NOT_FOUND");
        const previous = await tx.payment.findUnique({ where: { siteId_idempotencyKey: { siteId, idempotencyKey } } });
        if (previous) {
          if (previous.chargeId !== chargeId || previous.amountKurus !== amountKurus || previous.method !== method || previous.fullBalance !== fullBalance) throw new Error("IDEMPOTENCY_CONFLICT");
          return previous;
        }
        const payments = await tx.payment.findMany({ where: { siteId, chargeId }, include: { reversal: true } });
        const remaining=chargeBalance({ amountKurus: rows[0].amountKurus, payments }).remainingKurus;
        if(amountKurus>remaining)throw new Error("OVERPAYMENT");
        const policy=await tx.site.findUniqueOrThrow({where:{id:siteId},select:{partialPaymentsAllowed:true}});
        if(fullBalance&&amountKurus!==remaining)throw new Error("BALANCE_CHANGED");
        if(!policy.partialPaymentsAllowed&&amountKurus!==remaining)throw new Error("PARTIAL_PAYMENTS_DISABLED");
        const result = await tx.payment.create({ data: { siteId, chargeId, amountKurus, idempotencyKey, method, fullBalance } });
        await audit(tx, scope.userId, "PAYMENT_COLLECT", result.id, scope.organizationId, siteId);
        return result;
      });
    },
  };
}
