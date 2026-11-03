import { Prisma, PrismaClient } from '@prisma/client';
import { z } from 'zod';
import { actor, organizationAccess } from './security';
import { createOrganizationIn, createSiteIn } from './organization-creation';
import { siteInput } from './property-validation';
import type { SessionVerifier } from './management';

export const onboardingOrganization = z.object({name:z.string().trim().min(1,'Organizasyon adı gerekli.').max(200,'En fazla 200 karakter girin.'),kind:z.enum(['INDIVIDUAL','COMPANY'],{error:'Yönetim türünü seçin.'})}).strict();
export const onboardingSite = siteInput.extend({organizationId:z.string().min(1)}).strict();
export type SetupProgress = {organization:{id:string;name:string;kind:'INDIVIDUAL'|'COMPANY'}|null;site:{id:string;name:string}|null;existingAccess:boolean};
async function progress(tx: Prisma.TransactionClient, userId: string):Promise<SetupProgress> {
 const memberships = await tx.organizationMembership.findMany({where:{userId},orderBy:{organizationId:'asc'},include:{organization:{include:{sites:{orderBy:{id:'asc'},take:1,select:{id:true,name:true}}}}}});
 const managing = memberships.filter(m=>m.role==='ADMIN'||m.role==='MANAGER');
 const selected = managing.find(m=>m.organization.sites.length===0) ?? managing[0];
 if (selected) return {organization:{id:selected.organization.id,name:selected.organization.name,kind:selected.organization.kind},site:selected.organization.sites[0]??null,existingAccess:true};
 const legacy = await tx.membership.findFirst({where:{userId},select:{siteId:true}});
 return {organization:null,site:null,existingAccess:memberships.length>0||!!legacy};
}
export function onboarding(db: PrismaClient, verify: SessionVerifier) {
 async function write<T>(operation:(tx:Prisma.TransactionClient,userId:string)=>Promise<T>) {
  return db.$transaction(async tx=>{
   const session=await verify();
   if(!session)throw new Error('UNAUTHENTICATED');
   // Exclusive actor lock precedes the shared actor lock: no lock upgrades/deadlocks.
   // Normal management mutations take the same actor row's SHARE lock.
   await tx.$queryRaw`SELECT id FROM "User" WHERE id=${session.userId} FOR UPDATE`;
   const user=await actor(tx,verify);
   if(user.id!==session.userId)throw new Error('UNAUTHENTICATED');
   return operation(tx,user.id);
  });
 }
 return {
  async progress() { return db.$transaction(async tx=>progress(tx,(await actor(tx,verify)).id)); },
  async createOrganization(input:unknown) {
   const data=onboardingOrganization.parse(input);
   return write(async(tx,userId)=>{
    const current=await progress(tx,userId);
    if(current.existingAccess)return current;
    await createOrganizationIn(tx,userId,data.name,data.kind);
    return progress(tx,userId);
   });
  },
  async createSite(input:unknown) {
   const {organizationId,...data}=onboardingSite.parse(input);
   return write(async(tx,userId)=>{
    await organizationAccess(tx,userId,organizationId);
    const current=await progress(tx,userId);
    if(current.organization?.id!==organizationId)throw new Error('FORBIDDEN');
    if(!current.site)await createSiteIn(tx,userId,organizationId,data);
    return progress(tx,userId);
   });
  }
 };
}
