import { Prisma } from "@prisma/client";
import type { SessionVerifier } from "./management";
export async function actor(tx: Prisma.TransactionClient, verify: SessionVerifier) {
 const session = await verify();
 if (!session) throw new Error("UNAUTHENTICATED");
 // Email changes serialize against all authorized mutations.
 await tx.$queryRaw`SELECT id FROM "User" WHERE id = ${session.userId} FOR SHARE`;
 const user = await tx.user.findUnique({ where: { id: session.userId } });
 if (!user) throw new Error("FORBIDDEN");
 if (!user.emailVerifiedAt) throw new Error("EMAIL_UNVERIFIED");
 return user;
}
export async function lockOrganization(tx: Prisma.TransactionClient, organizationId: string) {
 await tx.$queryRaw`SELECT id FROM "Organization" WHERE id = ${organizationId} FOR UPDATE`;
}
export async function organizationAccess(tx: Prisma.TransactionClient, userId: string, organizationId: string, adminOnly = false) {
 await lockOrganization(tx, organizationId);
 const member = await tx.organizationMembership.findUnique({ where: { organizationId_userId: { organizationId, userId } } });
 if (!member || (adminOnly ? member.role !== "ADMIN" : !["ADMIN", "MANAGER"].includes(member.role))) throw new Error("FORBIDDEN");
 return member;
}
export async function audit(tx: Prisma.TransactionClient, actorId: string, action: string, entityId: string, organizationId?: string | null, siteId?: string) {
 await tx.auditLog.create({ data: { actorId, action, entityId, organizationId, siteId } });
}
