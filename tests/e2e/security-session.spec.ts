// SPDX-License-Identifier: AGPL-3.0-only
import { test,expect } from '@playwright/test';
import { PrismaClient } from '@prisma/client';
import { digest } from '../../src/lib/password';
import { management } from '../../src/lib/management';
const url=process.env.TEST_DATABASE_URL;
if(!url||!['localhost','127.0.0.1'].includes(new URL(url).hostname)||new URL(url).pathname!='/siteyonetim_test'||process.env.DATABASE_URL!==url)throw new Error('Isolated test database required');
const db=new PrismaClient({datasourceUrl:url});test.afterAll(async()=>db.$disconnect());
test('session cookie: forgery, expiry, revocation, removal and demotion take effect on next request',async({page,context})=>{
 const user=await db.user.create({data:{name:'Synthetic session',email:crypto.randomUUID()+'@example.invalid',emailVerifiedAt:new Date()}}),api=management(db,async()=>({userId:user.id}));
 const org=await api.createOrganization('Session matrix','COMPANY'),endpoint=`/raporlar/csv?org=${org.id}`;
 const cookie=async(raw:string)=>{await context.clearCookies();await context.addCookies([{name:'__Host-siteyonetim',value:raw,url:'https://127.0.0.1:3000/',secure:true,httpOnly:true,sameSite:'Lax'}]);};
 await page.goto('/panel');await expect(page).toHaveURL(/\/giris/);
 await cookie(crypto.randomUUID());expect((await page.request.get(endpoint)).status()).toBe(401);
 const raw=crypto.randomUUID(),session=await db.session.create({data:{userId:user.id,tokenHash:digest(raw),expiresAt:new Date(Date.now()-1000)}});await cookie(raw);expect((await page.request.get(endpoint)).status()).toBe(401);
 await db.session.update({where:{tokenHash:session.tokenHash},data:{expiresAt:new Date(Date.now()+600000)}});expect((await page.request.get(endpoint)).status()).toBe(200);
 await db.user.update({where:{id:user.id},data:{emailVerifiedAt:null}});expect((await page.request.get(endpoint)).status()).toBe(403);await db.user.update({where:{id:user.id},data:{emailVerifiedAt:new Date()}});
 await db.organizationMembership.update({where:{organizationId_userId:{organizationId:org.id,userId:user.id}},data:{role:'RESIDENT'}});expect((await page.request.get(endpoint)).status()).toBe(403);
 await db.organizationMembership.delete({where:{organizationId_userId:{organizationId:org.id,userId:user.id}}});expect((await page.request.get(endpoint)).status()).toBe(403);
 await db.organizationMembership.create({data:{organizationId:org.id,userId:user.id,role:'ADMIN'}});expect((await page.request.get(endpoint)).status()).toBe(200);
 await db.session.delete({where:{tokenHash:session.tokenHash}});expect((await page.request.get(endpoint)).status()).toBe(401);await page.goto('/panel');await expect(page).toHaveURL(/\/giris/);
 await cookie(raw);expect((await page.request.get(endpoint)).status()).toBe(401);
});
