import { PrismaClient } from "@prisma/client";
// Fixed table allowlist, bounded batches, no audit/financial/invitation history deletion.
export async function cleanupExpired(db: PrismaClient, now = new Date()) {
 const counts: Record<string, number> = {};
 for (const table of ["Session", "PasswordReset", "EmailVerification", "AuthAttempt"] as const) {
  counts[table] = await db.$executeRawUnsafe(`DELETE FROM "${table}" WHERE ctid IN (SELECT ctid FROM "${table}" WHERE "expiresAt" < $1 LIMIT 1000 FOR UPDATE SKIP LOCKED)`, now);
 }
 return counts;
}
