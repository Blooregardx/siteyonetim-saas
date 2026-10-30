import { test,expect } from '@playwright/test';
import { PrismaClient } from '@prisma/client';
import { hashPassword } from '../../src/lib/password';
import { reportBusinessDate } from '../../src/lib/reports';
import { management } from '../../src/lib/management';
const url=process.env.TEST_DATABASE_URL;
if(!url||!['localhost','127.0.0.1'].includes(new URL(url).hostname)||new URL(url).pathname!='/siteyonetim_test'||process.env.DATABASE_URL!==url)throw new Error('Isolated test database required');
const db=new PrismaClient({datasourceUrl:url});
test.afterAll(async()=>{await db.$disconnect();});
test('mobil rapor, politika, tam tahsilat ve rol sınırları',async({page})=>{
 const user=await db.user.create({data:{name:'Rapor Yönetici',email:crypto.randomUUID()+'@example.invalid',emailVerifiedAt:new Date(),passwordHash:await hashPassword('TestParolasi123!')}});const api=management(db,async()=>({userId:user.id}));const org=await api.createOrganization('Sentetik Rapor','COMPANY');const site=await api.createSite(org.id,'Rapor Apartmanı');const block=await api.createBlock(site.id,'Rapor Blok');const unit=await api.createUnit(site.id,block.id,'1');const charge=await api.createCharge(site.id,unit.id,'2026-01',200000,new Date('2026-01-01'));await api.collect(site.id,charge.id,75000,'initial');
 await page.setViewportSize({width:390,height:844});await page.goto('/giris');await page.getByLabel('E-posta',{exact:true}).fill(user.email);await page.getByLabel('Parola (en az 12 karakter)').fill('TestParolasi123!');await page.getByRole('button',{name:'Giriş yap',exact:true}).click();await expect(page).toHaveURL(/panel/);
 const policy=page.getByRole('region',{name:'Tahsilat Ayarları',exact:true});await expect(policy).toBeVisible();await policy.locator('select[name=allowed]').selectOption('false');await policy.getByRole('button',{name:'Kaydet',exact:true}).click();await expect(policy.getByRole('status')).toContainText('başarıyla');
 await page.getByRole('link',{name:'Aidat detayı ve tahsilat',exact:true}).click();
 const receipt=page.locator('form').filter({has:page.locator('[name=operation][value=payment]')});await expect(receipt.locator('[name=amount]')).toHaveValue('1250.00');await expect(receipt.locator('[name=amount]')).toHaveAttribute('readonly','');
 // UI tampering cannot bypass the server's saved policy.
 await receipt.locator('[name=amount]').evaluate((e:HTMLInputElement)=>{e.readOnly=false;e.value='500';});await receipt.getByRole('button',{name:'Kaydet',exact:true}).click();await expect(receipt.getByRole('status')).toContainText('Kalan borç değişti');expect(await db.payment.count({where:{chargeId:charge.id}})).toBe(1);
 await page.reload();
 await receipt.getByRole('button',{name:'Kalan Borcun Tamamını Tahsil Et',exact:true}).click();await expect(receipt.locator('[name=amount]')).toHaveValue('1250.00');await receipt.getByRole('button',{name:'Kaydet',exact:true}).click();await expect(receipt).toHaveCount(0);
 await page.getByRole('link',{name:'Borç ve Tahsilat Raporları',exact:true}).click();await expect(page.getByRole('heading',{name:'Borç ve Tahsilat Raporları',exact:true})).toBeVisible();await expect(page.getByText(/Vade günü Europe\/Istanbul takvimine/)).toContainText(reportBusinessDate());await expect(page.getByRole('table')).toContainText('Tamamen ödendi');await expect(page.getByRole('table')).toContainText('Borç yok');
 const net=page.getByRole('region',{name:'Rapor özeti'}).locator('article').filter({has:page.getByText('Net tahsilat',{exact:true})});await expect(net).toContainText('2.000,00');
 await page.getByLabel('Ödeme durumu',{exact:true}).selectOption('UNPAID');await page.getByRole('button',{name:'Filtrele',exact:true}).click();await expect(page.getByText('Bu filtrelerde aidat bulunamadı.')).toBeVisible();
 await page.goto(`/raporlar?org=${org.id}&period=2026-13`);await expect(page.locator('p[role=alert]')).toContainText('Filtreler geçersiz');
 const other=await db.organization.create({data:{name:'Other',kind:'COMPANY'}});await page.goto(`/raporlar?org=${other.id}`);await expect(page.locator('p[role=alert]')).toContainText('yetkiniz yok');
 await db.organizationMembership.update({where:{organizationId_userId:{organizationId:org.id,userId:user.id}},data:{role:'MANAGER'}});await page.goto('/panel');await expect(policy).toContainText('Kısmi Ödeme Kabulü: Kapalı');await expect(policy.getByRole('button')).toHaveCount(0);
 await db.organizationMembership.update({where:{organizationId_userId:{organizationId:org.id,userId:user.id}},data:{role:'RESIDENT'}});await page.goto(`/raporlar?org=${org.id}`);await expect(page.locator('p[role=alert]')).toContainText('yetkiniz yok');
});
