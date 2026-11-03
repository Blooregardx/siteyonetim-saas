import { test, after } from 'node:test';
import assert from 'node:assert/strict';
import { PrismaClient } from '@prisma/client';
import { onboarding } from '../src/lib/onboarding';
import { management } from '../src/lib/management';
const url=process.env.TEST_DATABASE_URL;
if(!url||!['localhost','127.0.0.1'].includes(new URL(url).hostname)||new URL(url).pathname!='/siteyonetim_test'||process.env.DATABASE_URL!==url)throw new Error('Isolated test database required');
const db=new PrismaClient({datasourceUrl:url});
after(()=>db.$disconnect());
async function fixture(verified=true){const user=await db.user.create({data:{name:'Sentetik kurulum',email:crypto.randomUUID()+'@example.invalid',emailVerifiedAt:verified?new Date():null}});const verify=async()=>({userId:user.id});return {user,api:onboarding(db,verify),normal:management(db,verify)};}
const siteData=(organizationId:string)=>({organizationId,name:'İlk apartman',address:'Sentetik adres',description:'Sentetik açıklama'});

test('onboarding: oturum ve e-posta doğrulaması her okuma/yazmada zorunlu',async()=>{
 const {api,user}=await fixture(false);
 await assert.rejects(onboarding(db,async()=>null).progress(),/UNAUTHENTICATED/);
 await assert.rejects(api.progress(),/EMAIL_UNVERIFIED/);
 await assert.rejects(api.createOrganization({name:'Yasak',kind:'INDIVIDUAL'}),/EMAIL_UNVERIFIED/);
 assert.equal(await db.organizationMembership.count({where:{userId:user.id}}),0);
});
for(const kind of ['INDIVIDUAL','COMPANY'] as const)test(`onboarding: ${kind} ilk organizasyon, ADMIN/audit ve atomik ilk site`,async()=>{
 const {api,user}=await fixture();const state=await api.createOrganization({name:'  Sentetik yönetim  ',kind});assert.equal(state.organization!.kind,kind);assert.equal(state.organization!.name,'Sentetik yönetim');
 const org=state.organization!;assert.equal((await db.organizationMembership.findUniqueOrThrow({where:{organizationId_userId:{organizationId:org.id,userId:user.id}}})).role,'ADMIN');
 assert.equal(await db.auditLog.count({where:{actorId:user.id,action:'ORGANIZATION_CREATE',entityId:org.id}}),1);
 assert.equal((await onboarding(db,async()=>({userId:user.id})).progress()).organization!.id,org.id);
 const done=await api.createSite(siteData(org.id));assert.equal(done.site!.name,'İlk apartman');
 const site=await db.site.findUniqueOrThrow({where:{id:done.site!.id}});assert.equal(site.address,'Sentetik adres');assert.equal(site.description,'Sentetik açıklama');
 assert.equal(await db.auditLog.count({where:{actorId:user.id,action:'SITE_CREATE',siteId:site.id}}),1);
 assert.equal(await db.charge.count({where:{siteId:site.id}}),0);
 assert.equal(await db.payment.count({where:{siteId:site.id}}),0);
});
test('onboarding: tekrar/eşzamanlı istekler ve normal panel çoklu organizasyon uyumu',async()=>{
 const {api,user,normal}=await fixture();
 const states=await Promise.all(Array.from({length:4},()=>api.createOrganization({name:'Tek yönetim',kind:'INDIVIDUAL'})));
 assert.equal(new Set(states.map(s=>s.organization!.id)).size,1);const id=states[0].organization!.id;
 const sites=await Promise.all(Array.from({length:4},()=>api.createSite(siteData(id))));assert.equal(new Set(sites.map(s=>s.site!.id)).size,1);
 assert.equal(await db.organizationMembership.count({where:{userId:user.id}}),1);assert.equal(await db.site.count({where:{organizationId:id}}),1);
 assert.equal(await db.auditLog.count({where:{actorId:user.id,action:{in:['ORGANIZATION_CREATE','SITE_CREATE']}}}),2);
 await normal.createOrganization('İkinci normal organizasyon','COMPANY');assert.equal(await db.organizationMembership.count({where:{userId:user.id}}),2);
});
test('onboarding: yabancı kapsam, sahte alanlar ve hatalı girdiler reddedilir',async()=>{
 const a=await fixture(),b=await fixture();const foreign=(await b.api.createOrganization({name:'Yabancı','kind':'COMPANY'})).organization!;
 await assert.rejects(a.api.createSite(siteData(foreign.id)),/FORBIDDEN/);
 for(const input of [{name:'',kind:'COMPANY'},{name:'x'.repeat(201),kind:'COMPANY'},{name:'İsim',kind:'SUPERADMIN'},{name:'İsim',kind:'COMPANY',role:'ADMIN'},{name:'İsim',kind:'COMPANY',userId:b.user.id},{name:'İsim',kind:'COMPANY',step:5}])await assert.rejects(a.api.createOrganization(input));
 const org=(await a.api.createOrganization({name:'Kendi','kind':'INDIVIDUAL'})).organization!;
 for(const input of [{...siteData(org.id),name:''},{...siteData(org.id),address:'x'.repeat(501)},{...siteData(org.id),description:'x'.repeat(2001)},{...siteData(org.id),siteId:'forged'},{...siteData(org.id),userId:b.user.id}])await assert.rejects(a.api.createSite(input));
 assert.equal(await db.site.count({where:{organizationId:foreign.id}}),0);
});
test('onboarding: mevcut ADMIN/MANAGER ve RESIDENT üyelikleri yükseltilmez',async()=>{
 for(const role of ['ADMIN','MANAGER','RESIDENT'] as const){const {api,user,normal}=await fixture();const org=await normal.createOrganization('Mevcut','COMPANY');await db.organizationMembership.update({where:{organizationId_userId:{organizationId:org.id,userId:user.id}},data:{role}});
  const state=await api.createOrganization({name:'Mükerrer','kind':'INDIVIDUAL'});assert.equal(state.existingAccess,true);assert.equal(await db.organizationMembership.count({where:{userId:user.id}}),1);
  if(role==='RESIDENT'){assert.equal(state.organization,null);await assert.rejects(api.createSite(siteData(org.id)),/FORBIDDEN/);}else assert.equal((await api.createSite(siteData(org.id))).organization!.id,org.id);
  assert.equal((await db.organizationMembership.findUniqueOrThrow({where:{organizationId_userId:{organizationId:org.id,userId:user.id}}})).role,role);
 }
});
test('onboarding: legacy erişim ve kaldırılmış üyelik önceki kapsamı açmaz',async()=>{
 const {api,user}=await fixture();const legacy=await db.site.create({data:{name:'Sentetik legacy'}});await db.membership.create({data:{siteId:legacy.id,userId:user.id,role:'MANAGER'}});
 assert.equal((await api.createOrganization({name:'Yeni','kind':'COMPANY'})).organization,null);
 const other=await fixture();const org=(await other.api.createOrganization({name:'Silinen üyelik','kind':'INDIVIDUAL'})).organization!;
 await db.organizationMembership.delete({where:{organizationId_userId:{organizationId:org.id,userId:other.user.id}}});assert.equal((await other.api.progress()).organization,null);await assert.rejects(other.api.createSite(siteData(org.id)),/FORBIDDEN/);
});
