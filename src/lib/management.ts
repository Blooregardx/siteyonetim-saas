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
  return {
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
        return tx.site.findUniqueOrThrow({ where: { id: siteId }, include: { blocks: true, units: { include: { occupants: true } }, charges: { include: { payments: { include: { reversal: { include: { actor: { select: { name: true } } } } } } } } } });
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
      return db.$transaction(async tx => { const scope = await authorize(tx, siteId); const result = await tx.occupancy.create({ data: { siteId, unitId, name: name.trim(), kind, startedAt } }); await audit(tx, scope.userId, "OCCUPANT_CREATE", result.id, scope.organizationId, siteId); return result; });
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
    async collect(siteId: string, chargeId: string, amountKurus: number, idempotencyKey: string, method: "CASH" | "TRANSFER" = "CASH") {
      if (!["CASH", "TRANSFER"].includes(method) || !Number.isInteger(amountKurus) || amountKurus <= 0 || amountKurus > 2147483647 || !idempotencyKey.trim() || idempotencyKey.length > 128) throw new Error("INVALID_PAYMENT");
      return db.$transaction(async tx => {
        const scope = await authorize(tx, siteId);
        // Serialize all receipts for this charge, including concurrent partial payments.
        const rows = await tx.$queryRaw<{ amountKurus: number }[]>`SELECT "amountKurus" FROM "Charge" WHERE "siteId" = ${siteId} AND id = ${chargeId} FOR UPDATE`;
        if (!rows.length) throw new Error("CHARGE_NOT_FOUND");
        const previous = await tx.payment.findUnique({ where: { siteId_idempotencyKey: { siteId, idempotencyKey } } });
        if (previous) {
          if (previous.chargeId !== chargeId || previous.amountKurus !== amountKurus || previous.method !== method) throw new Error("IDEMPOTENCY_CONFLICT");
          return previous;
        }
        const payments = await tx.payment.findMany({ where: { siteId, chargeId }, include: { reversal: true } });
        if (amountKurus > chargeBalance({ amountKurus: rows[0].amountKurus, payments }).remainingKurus) throw new Error("OVERPAYMENT");
        const result = await tx.payment.create({ data: { siteId, chargeId, amountKurus, idempotencyKey, method } });
        await audit(tx, scope.userId, "PAYMENT_COLLECT", result.id, scope.organizationId, siteId);
        return result;
      });
    },
  };
}
