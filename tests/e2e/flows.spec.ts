import { test, expect, type Page } from '@playwright/test';
import { SMTPServer } from 'smtp-server';
import { PrismaClient } from '@prisma/client';
const url = process.env.TEST_DATABASE_URL;
if (!url || !['localhost','127.0.0.1'].includes(new URL(url).hostname) || new URL(url).pathname !== '/siteyonetim_test' || process.env.DATABASE_URL !== url) throw new Error('Isolated test database required');
const db = new PrismaClient({ datasourceUrl: url });
let mail = '';
const smtp = new SMTPServer({ authOptional: true, disabledCommands: ['STARTTLS'], onData(stream, _session, callback) { let body = ''; stream.on('data', chunk => {body += chunk.toString();}); stream.on('end', () => {mail = body; callback();}); } });
test.beforeAll(async () => new Promise<void>(resolve => smtp.listen(2525, '127.0.0.1', resolve)));
test.afterAll(async () => { await db.$disconnect(); await new Promise<void>(resolve => smtp.close(resolve)); });
function mailLink(path:string) {
 return mail.replace(/=\r?\n/g,'').replace(/=3D/g,'=').match(new RegExp(`http://127\\.0\\.0\\.1:3000/${path}\\?token=[a-f0-9]{64}`))?.[0];
}
async function verifyLatest(page:Page) {
 await expect(page).toHaveURL(/eposta-dogrula/);
 await expect.poll(()=>mailLink('eposta-dogrula')).toBeTruthy();
 const link=mailLink('eposta-dogrula')!;
 await page.goto(link);await page.getByRole('button',{name:'E-postayı doğrula',exact:true}).click();
 await expect(page.getByRole('status').first()).toContainText('E-posta doğrulandı.');
 await page.goto(link);await page.getByRole('button',{name:'E-postayı doğrula',exact:true}).click();
 await expect(page.getByRole('status').first()).toContainText('İşlem tamamlanamadı.');
 await page.goto('/panel');await expect(page).toHaveURL(/panel/);
}
test('oturum, sahte kimlik reddi, organizasyon ayrımı ve gerçek kayıt akışı', async ({page,browser}) => {
 let lastAction: { headers: Record<string,string>; body: string } | undefined;
 page.on('request', req => { if (req.headers()['next-action']) lastAction = { headers: req.headers(), body: req.postData() ?? '' }; });
 const email = `${crypto.randomUUID()}@example.invalid`;
 await page.goto('/panel'); await expect(page).toHaveURL(/giris/);
 await page.goto('/kayit');
 await page.getByLabel('Ad soyad').fill('Test Yönetici'); await page.getByLabel('E-posta',{exact:true}).fill(email);
 await page.getByLabel('Parola (en az 12 karakter)').fill('TestParolasi123!');
 await page.evaluate(()=>{const input=document.createElement('input');input.name='userId';input.value='forged-admin';document.querySelector('form')!.append(input);});
 await page.getByRole('button',{name:'Kayıt ol',exact:true}).click(); await verifyLatest(page);
 await expect(page.getByText('İlk organizasyonunuzu oluşturun')).toBeVisible();
 const user = await db.user.findUniqueOrThrow({where:{email}}); expect(user.id).not.toBe('forged-admin');
 await page.getByLabel('Organizasyon adı',{exact:true}).fill('Tarayıcı Test Şirketi');
 const orgForm=page.locator('form').filter({has:page.locator('[name="operation"][value="organization"]')});
 await orgForm.getByRole('button',{name:'Kaydet',exact:true}).click();
 await expect(page.getByRole('heading',{name:'Apartmanlar ve siteler'})).toBeVisible();
 async function submit(operation:string, fields:Record<string,string>) {
  const form=page.locator('form').filter({has:page.locator(`[name="operation"][value="${operation}"]`)}).first();
  for(const [name,value] of Object.entries(fields)) {const input=form.locator(`[name="${name}"]`);if(await input.evaluate(e=>e.tagName)==='SELECT') await input.selectOption({label:value}); else await input.fill(value);}
  await form.getByRole('button',{name:'Kaydet',exact:true}).click(); await expect(form.getByRole('status')).toHaveText('Kayıt başarıyla tamamlandı.');
 }
 await submit('site',{name:'Test Apartmanı'}); await expect(page.getByRole('heading',{name:'Blok ve daire yönetimi'})).toBeVisible();
 await submit('block',{name:'A'});
 expect(lastAction).toBeDefined();
 const csrf = await page.request.post('/panel', { headers: { ...lastAction!.headers, origin: 'https://untrusted.example.invalid' }, data: lastAction!.body });
 expect(csrf.status()).toBeGreaterThanOrEqual(400);
 await submit('unit',{blockId:'A',number:'1'});
 await submit('occupant',{unitId:'1',name:'Örnek Malik',kind:'Malik',startedAt:'2026-10-01'});
 await submit('charge',{unitId:'1',period:'2026-10',amount:'100',dueDate:'2026-10-31'});
 await submit('payment',{amount:'40',method:'Nakit'}); await expect(page.getByText(/Kısmi ödeme/)).toBeVisible();
 const member=await db.organizationMembership.findFirstOrThrow({where:{userId:user.id}});
 await page.getByRole('button',{name:'Ters kayıt oluştur',exact:true}).click();
 const confirmation=page.getByRole('form',{name:'Ters kayıt onayı'});
 await expect(confirmation).toContainText('Bu işlem banka veya nakit iadesi yapmaz.');
 const original=await db.payment.findFirstOrThrow({where:{site:{organizationId:member.organizationId}}});
 await db.organizationMembership.update({where:{organizationId_userId:{organizationId:member.organizationId,userId:user.id}},data:{role:'MANAGER'}});
 await confirmation.evaluate(form=>{for(const [name,value] of [['role','ADMIN'],['userId','forged-admin']]){const input=document.createElement('input');input.name=name;input.value=value;form.append(input);}});
 await confirmation.getByRole('button',{name:'Onayla ve ters kaydet',exact:true}).click();
 await expect(confirmation.getByRole('status')).toContainText('yetkiniz');
 expect(await db.paymentReversal.count({where:{paymentId:original.id}})).toBe(0);
 await page.reload();await expect(page.getByRole('button',{name:'Ters kayıt oluştur',exact:true})).toHaveCount(0);
 await db.organizationMembership.update({where:{organizationId_userId:{organizationId:member.organizationId,userId:user.id}},data:{role:'ADMIN'}});
 await page.reload();await page.getByRole('button',{name:'Ters kayıt oluştur',exact:true}).click();
 await page.getByRole('button',{name:'Vazgeç',exact:true}).click();expect(await db.paymentReversal.count({where:{paymentId:original.id}})).toBe(0);
 await page.getByRole('button',{name:'Ters kayıt oluştur',exact:true}).click();
 await page.getByRole('button',{name:'Onayla ve ters kaydet',exact:true}).click();await expect(page.getByRole('note')).toContainText('Ters kaydedildi');
 const netCard=page.locator('.stats article').filter({has:page.getByText('Net tahsilat',{exact:true})});await expect(netCard.locator('strong')).toHaveText(/0,00/);
 expect(await db.payment.findUniqueOrThrow({where:{id:original.id}})).toEqual(original);
 const fullPayment=page.locator('form').filter({has:page.locator('[name="operation"][value="payment"]')});await fullPayment.locator('[name=amount]').fill('100');await fullPayment.getByRole('button',{name:'Kaydet',exact:true}).click();
 await expect(page.getByText(/ · Ödendi/)).toBeVisible();
 await page.setViewportSize({width:390,height:844});
 const bulk=page.getByRole('region',{name:'Toplu aidat',exact:true});
 await bulk.getByLabel('Aidat dönemi',{exact:true}).fill('2026-12');
 await bulk.getByLabel('Daire başına tutar (TL)',{exact:true}).fill('125,50');
 await bulk.getByLabel('Son ödeme tarihi',{exact:true}).fill('2026-12-31');
 const countBefore=await db.charge.count({where:{siteId:original.siteId}});
 await bulk.getByRole('button',{name:'Önizle',exact:true}).click();
 await expect(bulk.getByRole('heading',{name:'Önizleme',exact:true})).toBeVisible();
 expect(await db.charge.count({where:{siteId:original.siteId}})).toBe(countBefore);
 await expect(bulk.getByRole('table')).toContainText('Yeni oluşturulacak');
 await bulk.getByRole('button',{name:'Onayla ve aidatları oluştur',exact:true}).click();
 await expect(bulk.getByRole('status')).toContainText('1 daireye aidat oluşturuldu');
 expect(await db.charge.count({where:{siteId:original.siteId}})).toBe(countBefore+1);
 await bulk.getByRole('button',{name:'Önizle',exact:true}).click();
 await expect(bulk.getByRole('button',{name:'Onayla ve aidatları oluştur',exact:true})).toBeDisabled();
 await page.setViewportSize({width:1280,height:720});
 await page.goto(`/kayitlar?site=${original.siteId}`);
 await submit('site-update',{name:'Düzenlenmiş Apartman',address:'Sentetik test adresi',description:'Test açıklaması'});
 await submit('block-update',{name:'Yeni A',description:'Blok açıklaması'});
 await submit('unit-update',{number:'12',floor:'3',sectionType:'İş yeri',usageStatus:'Boş'});
 await page.getByLabel('Daire ara',{exact:true}).fill('12');await page.getByRole('button',{name:'Filtrele',exact:true}).click();await expect(page.getByRole('heading',{name:'Yeni A / Daire 12'})).toBeVisible();
 await submit('person',{name:'İlişki Test Kişisi'});
 const relation=page.locator('form').filter({has:page.locator('[name="operation"][value="person-link"]')});
 const personOption=relation.locator('option').filter({hasText:'İlişki Test Kişisi'});await relation.locator('[name=personId]').selectOption(await personOption.getAttribute('value')??'');
 await relation.locator('[name=unitId]').selectOption({label:'Yeni A / 12'});await relation.locator('[name=kind]').selectOption('TENANT');await relation.locator('[name=startedAt]').fill('2026-01-01');await relation.getByRole('button',{name:'Kaydet',exact:true}).click();await expect(relation.getByRole('status')).toHaveText('Kayıt başarıyla tamamlandı.');
 const endForm=page.locator('form').filter({has:page.locator('[name="operation"][value="relation-end"]')}).filter({has:page.locator('[name="kind"][value="TENANT"]')}).first();await endForm.locator('[name=endedAt]').fill('2026-03-31');await endForm.getByRole('button',{name:'Kaydet',exact:true}).click();await expect(endForm).toHaveCount(0);
 await expect(page.getByText(/İlişki Test Kişisi.*2026-03-31/)).toBeVisible();
 await page.goto('/panel');


 const cookies=await page.context().cookies(); const session=cookies.find(c=>c.name==='__Host-siteyonetim'); expect(session?.httpOnly).toBe(true); expect(session?.sameSite).toBe('Lax');
 const other=await db.organization.create({data:{name:'Başka organizasyon',kind:'COMPANY'}});
 await page.goto(`/panel?org=${other.id}`); await expect(page.getByText(/404/)).toBeVisible();
 const anonymous=await browser.newContext();const anon=await anonymous.newPage();await anon.goto('/panel');await expect(anon).toHaveURL(/giris/);await anonymous.close();
 await page.goto('/panel');await page.getByRole('button',{name:'Çıkış yap'}).click();await expect(page).toHaveURL(/giris/);
 await page.getByLabel('E-posta',{exact:true}).fill(email);await page.getByLabel('Parola (en az 12 karakter)').fill('TestParolasi123!');await page.getByRole('button',{name:'Giriş yap',exact:true}).click();await expect(page).toHaveURL(/panel/);
 const newEmail=`${crypto.randomUUID()}@example.invalid`;
 await page.goto('/eposta-dogrula');const change=page.locator('form').filter({has:page.locator('[name="email"]')});
 await change.getByLabel('Yeni e-posta').fill(newEmail);await change.getByLabel('Mevcut parola').fill('YanlisParola123!');await change.getByRole('button').click();await expect(change.getByRole('status')).toContainText('İşlem tamamlanamadı.');
 await change.getByLabel('Yeni e-posta').fill(newEmail);await change.getByLabel('Mevcut parola').fill('TestParolasi123!');await change.getByRole('button').click();await expect(change.getByRole('status')).toContainText('Doğrulama bağlantısı gönderildi.');
 const changeLink=mailLink('eposta-dogrula')!;await page.goto(changeLink);await page.getByRole('button',{name:'E-postayı doğrula',exact:true}).click();await expect(page.getByRole('status').first()).toContainText('E-posta doğrulandı.');
 await page.goto('/panel');await expect(page).toHaveURL(/giris/);
 expect((await db.user.findUniqueOrThrow({where:{id:user.id}})).email).toBe(newEmail);
});

test('SMTP kurtarma, tek kullanımlı token ve oturum iptali', async ({page}) => {
 const email = `${crypto.randomUUID()}@example.invalid`;
 await page.goto('/kayit'); await page.getByLabel('Ad soyad').fill('Reset Test'); await page.getByLabel('E-posta',{exact:true}).fill(email); await page.getByLabel('Parola (en az 12 karakter)').fill('TestParolasi123!');await page.getByRole('button',{name:'Kayıt ol',exact:true}).click();await verifyLatest(page);
 await page.goto('/sifre-sifirla');await page.getByLabel('E-posta',{exact:true}).fill(email);await page.getByRole('button',{name:'Parolayı yenile'}).click();await expect(page.getByRole('status')).toHaveText('Hesap mevcutsa yenileme bağlantısı gönderildi.');
 await expect.poll(()=>mail).toContain('/sifre-sifirla?token=');
 const link = mail.replace(/=\r?\n/g,'').replace(/=3D/g,'=').match(/http:\/\/127\.0\.0\.1:3000\/sifre-sifirla\?token=[a-f0-9]{64}/)?.[0];expect(link).toBeTruthy();
 await page.goto(link!);await page.getByLabel('Parola (en az 12 karakter)').fill('YeniTestParola123!');await page.getByRole('button',{name:'Parolayı yenile'}).click();await expect(page.getByRole('status')).toHaveText('Parola yenilendi. Giriş yapabilirsiniz.');
 await page.goto('/panel');await expect(page).toHaveURL(/giris/);
 await page.goto(link!);await page.getByLabel('Parola (en az 12 karakter)').fill('BaskaParola123!');await page.getByRole('button',{name:'Parolayı yenile'}).click();await expect(page.getByRole('status')).toContainText('İşlem tamamlanamadı');
 await page.goto('/giris');await page.getByLabel('E-posta',{exact:true}).fill(email);await page.getByLabel('Parola (en az 12 karakter)').fill('YeniTestParola123!');await page.getByRole('button',{name:'Giriş yap',exact:true}).click();await expect(page).toHaveURL(/panel/);
});
test('HTTP demo ve güvenlik başlıkları', async ({request}) => {
 for(const path of ['/demo','/demo?view=company','/giris']) {const response=await request.get(path);expect(response.status()).toBe(200);expect(response.headers()['x-content-type-options']).toBe('nosniff');expect(response.headers()['x-frame-options']).toBe('DENY');}
});

test('SMTP daveti, doğrulanmış kabul ve üyelik iptalinin açık oturuma etkisi',async({page,browser})=>{
 async function register(p:Page,email:string) {
  await p.goto('/kayit');await p.getByLabel('Ad soyad').fill('Davet Test');await p.getByLabel('E-posta',{exact:true}).fill(email);await p.getByLabel('Parola (en az 12 karakter)').fill('TestParolasi123!');await p.getByRole('button',{name:'Kayıt ol',exact:true}).click();await verifyLatest(p);
 }
 const ownerEmail=`${crypto.randomUUID()}@example.invalid`;const targetEmail=`${crypto.randomUUID()}@example.invalid`;
 await register(page,ownerEmail);
 await page.getByLabel('Organizasyon adı',{exact:true}).fill('Davet Tarayıcı Şirketi');await page.locator('select[name=kind]').selectOption('COMPANY');
 await page.locator('form').filter({has:page.locator('[name="operation"][value="organization"]')}).getByRole('button',{name:'Kaydet',exact:true}).click();
 await expect(page.getByRole('heading',{name:'Apartmanlar ve siteler'})).toBeVisible();
 await page.goto('/uyeler');
 const invite=page.locator('form').filter({has:page.locator('[name="operation"][value="invite"]')});
 await invite.getByLabel('E-posta',{exact:true}).fill(targetEmail);await invite.getByLabel('Rol',{exact:true}).selectOption('MANAGER');await invite.getByRole('button').click();await expect(invite.getByRole('status')).toHaveText('İşlem tamamlandı.');
 await expect.poll(()=>mailLink('davet')).toBeTruthy();const invitation=mailLink('davet')!;
 const context=await browser.newContext();const target=await context.newPage();await register(target,targetEmail);await target.goto(invitation);await target.getByRole('button',{name:'Uygula'}).click();await expect(target.getByRole('status')).toHaveText('İşlem tamamlandı.');
 const user=await db.user.findUniqueOrThrow({where:{email:targetEmail}});const membership=await db.organizationMembership.findFirstOrThrow({where:{userId:user.id}});expect(membership.role).toBe('MANAGER');
 await target.goto(`/panel?org=${membership.organizationId}`);await expect(target.getByRole('heading',{name:'Şirket portföyü'})).toBeVisible();
 await page.reload();const remove=page.locator('form').filter({has:page.locator('[name="operation"][value="remove"]')}).filter({has:page.locator(`[name="userId"][value="${user.id}"]`)});await remove.getByRole('button').click();await expect(remove).toHaveCount(0);
 await target.goto(`/panel?org=${membership.organizationId}`);await expect(target.getByText(/404/)).toBeVisible();await context.close();
});
