import { PrismaClient, Role } from "@prisma/client";
import { z } from "zod";
import { digest, token } from "./password";
import { actor, audit, organizationAccess } from "./security";
import type { SessionVerifier } from "./management";
const emailSchema = z.string().trim().toLowerCase().email().max(254);
const roleSchema = z.enum(["ADMIN", "MANAGER", "RESIDENT"]);
export function accounts(db: PrismaClient, verify: SessionVerifier) {
 return {
  async requestVerification(email?: string) {
   const session = await verify();
   if (!session) throw new Error("UNAUTHENTICATED");
   const raw = token();
   const target = await db.$transaction(async tx => {
    await tx.$queryRaw`SELECT id FROM "User" WHERE id = ${session.userId} FOR UPDATE`;
    const user = await tx.user.findUniqueOrThrow({where:{id:session.userId}});
    const target = emailSchema.parse(email ?? user.email);
    await tx.emailVerification.deleteMany({where:{userId:user.id}});
    await tx.emailVerification.create({data:{tokenHash:digest(raw),userId:user.id,email:target,expiresAt:new Date(Date.now()+3600000)}});
    return target;
   });
   return { email: target, token: raw };
  },
  async confirmEmail(raw: string) {
   const session = await verify();
   if (!session) throw new Error("UNAUTHENTICATED");
   const tokenHash = digest(z.string().regex(/^[a-f0-9]{64}$/).parse(raw));
   await db.$transaction(async tx => {
    await tx.$queryRaw`SELECT id FROM "User" WHERE id = ${session.userId} FOR UPDATE`;
    const proof = await tx.emailVerification.findUnique({where:{tokenHash}});
    if (!proof || proof.userId !== session.userId || proof.expiresAt <= new Date()) throw new Error("INVALID_TOKEN");
    const user = await tx.user.findUniqueOrThrow({where:{id:session.userId}});
    await tx.emailVerification.delete({where:{tokenHash}});
    await tx.user.update({where:{id:user.id},data:{email:proof.email,emailVerifiedAt:new Date()}});
    if (user.email !== proof.email) {
     await tx.session.deleteMany({where:{userId:user.id}});
     await tx.passwordReset.deleteMany({where:{userId:user.id}});
    }
   });
  },
  async invite(organizationId: string, email: string, role: Role) {
   const target = emailSchema.parse(email); roleSchema.parse(role);
   const raw = token();
   const invitation = await db.$transaction(async tx => {
    const user = await actor(tx,verify);
    const member = await organizationAccess(tx,user.id,organizationId);
    if (member.role !== "ADMIN" && role !== "RESIDENT") throw new Error("FORBIDDEN");
    const invitation = await tx.invitation.create({data:{organizationId,email:target,role,invitedBy:user.id,tokenHash:digest(raw),expiresAt:new Date(Date.now()+2*86400000)}});
    await audit(tx,user.id,"MEMBER_INVITE",invitation.id,organizationId);
    return invitation;
   });
   return { id: invitation.id, email: target, token: raw };
  },
  async accept(raw: string) {
   const tokenHash = digest(z.string().regex(/^[a-f0-9]{64}$/).parse(raw));
   await db.$transaction(async tx => {
    const user = await actor(tx,verify);
    const initial = await tx.invitation.findUnique({where:{tokenHash}});
    if (!initial) throw new Error("INVALID_INVITATION");
    // Recheck the issuer's current grant authority, serialized with cancellation/removal.
    const issuer = await organizationAccess(tx,initial.invitedBy,initial.organizationId);
    const invitation = await tx.invitation.findUniqueOrThrow({where:{tokenHash}});
    const issuerUser = await tx.user.findUnique({where:{id:initial.invitedBy}});
    if (!issuerUser?.emailVerifiedAt || (issuer.role !== "ADMIN" && invitation.role !== "RESIDENT")) throw new Error("FORBIDDEN");
    if (invitation.email !== user.email || invitation.revokedAt || invitation.acceptedAt || invitation.expiresAt <= new Date()) throw new Error("INVALID_INVITATION");
    // Existing members must use explicit role-change authorization; never silently elevate.
    await tx.organizationMembership.create({data:{organizationId:invitation.organizationId,userId:user.id,role:invitation.role}});
    await tx.invitation.update({where:{id:invitation.id},data:{acceptedAt:new Date()}});
    await audit(tx,user.id,"MEMBER_ACCEPT",invitation.id,invitation.organizationId);
   });
  },
  async cancel(organizationId: string, id: string) {
   await db.$transaction(async tx => {
    const user = await actor(tx,verify);
    const member = await organizationAccess(tx,user.id,organizationId);
    const invitation = await tx.invitation.findFirst({where:{id,organizationId,acceptedAt:null,revokedAt:null}});
    if (!invitation || (member.role !== "ADMIN" && (invitation.invitedBy !== user.id || invitation.role !== "RESIDENT"))) throw new Error("FORBIDDEN");
    await tx.invitation.update({where:{id},data:{revokedAt:new Date()}});
    await audit(tx,user.id,"INVITATION_REVOKE",id,organizationId);
   });
  },
  async changeMember(organizationId: string, targetId: string, role: Role | null) {
   if (role !== null) roleSchema.parse(role);
   await db.$transaction(async tx => {
    const user = await actor(tx,verify);
    await organizationAccess(tx,user.id,organizationId,true);
    const target = await tx.organizationMembership.findUniqueOrThrow({where:{organizationId_userId:{organizationId,userId:targetId}}});
    const targetUser = await tx.user.findUniqueOrThrow({where:{id:targetId}});
    if (role && !targetUser.emailVerifiedAt) throw new Error("EMAIL_UNVERIFIED");
    if (target.role === "ADMIN" && role !== "ADMIN" && targetUser.emailVerifiedAt) {
     const admins = await tx.organizationMembership.count({where:{organizationId,role:"ADMIN",user:{emailVerifiedAt:{not:null}}}});
     if (admins <= 1) throw new Error("LAST_ADMIN");
    }
    if (role) await tx.organizationMembership.update({where:{organizationId_userId:{organizationId,userId:targetId}},data:{role}});
    else {
     await tx.organizationMembership.delete({where:{organizationId_userId:{organizationId,userId:targetId}}});
     // Remove organization-owned direct grants too; legacy unrelated sites are untouched.
     await tx.membership.deleteMany({where:{userId:targetId,site:{organizationId}}});
     await tx.invitation.updateMany({where:{organizationId,invitedBy:targetId,acceptedAt:null,revokedAt:null},data:{revokedAt:new Date()}});
    }
    await tx.membership.deleteMany({where:{userId:targetId,site:{organizationId}}});
    await audit(tx,user.id,role ? `MEMBER_ROLE_${role}` : "MEMBER_REMOVE",targetId,organizationId);
   });
  },
 };
}
