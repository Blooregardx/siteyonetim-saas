import { Prisma, PrismaClient } from "@prisma/client";

// Only a server-side session verifier may supply this callback. Never use request user IDs.
export type SessionVerifier = () => Promise<{ userId: string } | null>;
export function management(db: PrismaClient, verifySession: SessionVerifier) {
  async function authorize(tx: Prisma.TransactionClient, siteId: string) {
    const session = await verifySession();
    if (!session) throw new Error("UNAUTHENTICATED");
    const site = await tx.site.findUnique({ where: { id: siteId } });
    const direct = await tx.membership.findUnique({ where: { siteId_userId: { siteId, userId: session.userId } } });
    const org = site?.organizationId ? await tx.organizationMembership.findUnique({ where: { organizationId_userId: { organizationId: site.organizationId, userId: session.userId } } }) : null;
    if (![direct?.role, org?.role].some(role => role === "ADMIN" || role === "MANAGER")) throw new Error("FORBIDDEN");
  }
  return {
    async createOrganization(name: string, kind: "INDIVIDUAL" | "COMPANY") {
      const session = await verifySession();
      if (!session) throw new Error("UNAUTHENTICATED");
      if (!name.trim() || name.length > 200 || !["INDIVIDUAL", "COMPANY"].includes(kind)) throw new Error("INVALID_ORGANIZATION");
      return db.organization.create({ data: { name: name.trim(), kind, memberships: { create: { userId: session.userId, role: "ADMIN" } } } });
    },
    async portfolio(organizationId: string) {
      return db.$transaction(async tx => {
        const session = await verifySession();
        if (!session) throw new Error("UNAUTHENTICATED");
        const member = await tx.organizationMembership.findUnique({ where: { organizationId_userId: { organizationId, userId: session.userId } } });
        if (!member || !["ADMIN", "MANAGER"].includes(member.role)) throw new Error("FORBIDDEN");
        return tx.organization.findUniqueOrThrow({ where: { id: organizationId }, include: { sites: { include: { _count: { select: { blocks: true, units: true } } } } } });
      });
    },
    async createSite(organizationId: string, name: string) {
      if (!name.trim() || name.length > 200) throw new Error("INVALID_NAME");
      return db.$transaction(async tx => {
        const session = await verifySession();
        if (!session) throw new Error("UNAUTHENTICATED");
        const member = await tx.organizationMembership.findUnique({ where: { organizationId_userId: { organizationId, userId: session.userId } } });
        if (!member || !["ADMIN", "MANAGER"].includes(member.role)) throw new Error("FORBIDDEN");
        return tx.site.create({ data: { organizationId, name: name.trim() } });
      });
    },
    async dashboard(siteId: string) {
      return db.$transaction(async tx => {
        await authorize(tx, siteId);
        return tx.site.findUniqueOrThrow({ where: { id: siteId }, include: { blocks: true, units: { include: { occupants: true } }, charges: { include: { payments: true } } } });
      });
    },
    async createBlock(siteId: string, name: string) {
      if (!name.trim() || name.length > 100) throw new Error("INVALID_NAME");
      return db.$transaction(async tx => { await authorize(tx, siteId); return tx.block.create({ data: { siteId, name: name.trim() } }); });
    },
    async createUnit(siteId: string, blockId: string, number: string) {
      if (!number.trim() || number.length > 30) throw new Error("INVALID_NUMBER");
      return db.$transaction(async tx => { await authorize(tx, siteId); return tx.unit.create({ data: { siteId, blockId, number: number.trim() } }); });
    },
    async recordOccupant(siteId: string, unitId: string, name: string, kind: "OWNER" | "TENANT", startedAt: Date) {
      if (!name.trim() || name.length > 200 || !["OWNER", "TENANT"].includes(kind) || !Number.isFinite(startedAt.getTime())) throw new Error("INVALID_OCCUPANT");
      return db.$transaction(async tx => { await authorize(tx, siteId); return tx.occupancy.create({ data: { siteId, unitId, name: name.trim(), kind, startedAt } }); });
    },
    async createCharge(siteId: string, unitId: string, period: string, amountKurus: number, dueDate: Date) {
      if (!/^\d{4}-(0[1-9]|1[0-2])$/.test(period) || !Number.isInteger(amountKurus) || amountKurus <= 0 || amountKurus > 2147483647 || !Number.isFinite(dueDate.getTime())) throw new Error("INVALID_CHARGE");
      return db.$transaction(async tx => { await authorize(tx, siteId); return tx.charge.create({ data: { siteId, unitId, period, amountKurus, dueDate } }); });
    },
    async collect(siteId: string, chargeId: string, amountKurus: number, idempotencyKey: string) {
      if (!Number.isInteger(amountKurus) || amountKurus <= 0 || amountKurus > 2147483647 || !idempotencyKey.trim() || idempotencyKey.length > 128) throw new Error("INVALID_PAYMENT");
      return db.$transaction(async tx => {
        await authorize(tx, siteId);
        // Serialize all receipts for this charge, including concurrent partial payments.
        const rows = await tx.$queryRaw<{ amountKurus: number }[]>`SELECT "amountKurus" FROM "Charge" WHERE "siteId" = ${siteId} AND id = ${chargeId} FOR UPDATE`;
        if (!rows.length) throw new Error("CHARGE_NOT_FOUND");
        const previous = await tx.payment.findUnique({ where: { siteId_idempotencyKey: { siteId, idempotencyKey } } });
        if (previous) {
          if (previous.chargeId !== chargeId || previous.amountKurus !== amountKurus) throw new Error("IDEMPOTENCY_CONFLICT");
          return previous;
        }
        const sum = await tx.payment.aggregate({ where: { siteId, chargeId }, _sum: { amountKurus: true } });
        if ((sum._sum.amountKurus ?? 0) + amountKurus > rows[0].amountKurus) throw new Error("OVERPAYMENT");
        return tx.payment.create({ data: { siteId, chargeId, amountKurus, idempotencyKey } });
      });
    },
  };
}
