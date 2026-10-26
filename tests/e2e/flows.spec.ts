import { test, expect } from '@playwright/test';
import { SMTPServer } from 'smtp-server';
import { PrismaClient } from '@prisma/client';
const url = process.env.TEST_DATABASE_URL;
if (!url || !['localhost','127.0.0.1'].includes(new URL(url).hostname) || new URL(url).pathname !== '/siteyonetim_test' || process.env.DATABASE_URL !== url) throw new Error('Isolated test database required');
const db = new PrismaClient({ datasourceUrl: url });
let mail = '';
const smtp = new SMTPServer({ authOptional: true, disabledCommands: ['STARTTLS'], onData(stream, _session, callback) { let body = ''; stream.on('data', chunk => {body += chunk.toString();}); stream.on('end', () => {mail = body; callback();}); } });
test.beforeAll(async () => new Promise<void>(resolve => smtp.listen(2525, '127.0.0.1', resolve)));
test.afterAll(async () => { await db.$disconnect(); await new Promise<void>(resolve => smtp.close(resolve)); });
test('oturum, sahte kimlik reddi, organizasyon ayrımı ve gerçek kayıt akışı', async ({page,browser}) => {
 let lastAction: { headers: Record<string,string>; body: string } | undefined;
 page.on('request', req => { if (req.headers()['next-action']) lastAction = { headers: req.headers(), body: req.postData() ?? '' }; });
 const email = `${crypto.randomUUID()}@example.invalid`;
 await page.goto('/panel'); await expect(page).toHaveURL(/giris/);
 await page.goto('/kayit');
 await page.getByLabel('Ad soyad').fill('Test Yönetici'); await page.getByLabel('E-posta',{exact:true}).fill(email);
 await page.getByLabel('Parola (en az 12 karakter)').fill('TestParolasi123!');
 await page.evaluate(()=>{const input=document.createElement('input');input.name='userId';input.value='forged-admin';document.querySelector('form')!.append(input);});
 await page.getByRole('button',{name:'Kayıt ol',exact:true}).click(); await expect(page).toHaveURL(/panel/);
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
 const cookies=await page.context().cookies(); const session=cookies.find(c=>c.name==='__Host-siteyonetim'); expect(session?.httpOnly).toBe(true); expect(session?.sameSite).toBe('Lax');
 const other=await db.organization.create({data:{name:'Başka organizasyon',kind:'COMPANY'}});
 await page.goto(`/panel?org=${other.id}`); await expect(page.getByText(/404/)).toBeVisible();
 const anonymous=await browser.newContext();const anon=await anonymous.newPage();await anon.goto('/panel');await expect(anon).toHaveURL(/giris/);await anonymous.close();
 await page.goto('/panel');await page.getByRole('button',{name:'Çıkış yap'}).click();await expect(page).toHaveURL(/giris/);
 await page.getByLabel('E-posta',{exact:true}).fill(email);await page.getByLabel('Parola (en az 12 karakter)').fill('TestParolasi123!');await page.getByRole('button',{name:'Giriş yap',exact:true}).click();await expect(page).toHaveURL(/panel/);
});

test('SMTP kurtarma, tek kullanımlı token ve oturum iptali', async ({page}) => {
 const email = `${crypto.randomUUID()}@example.invalid`;
 await page.goto('/kayit'); await page.getByLabel('Ad soyad').fill('Reset Test'); await page.getByLabel('E-posta',{exact:true}).fill(email); await page.getByLabel('Parola (en az 12 karakter)').fill('TestParolasi123!');await page.getByRole('button',{name:'Kayıt ol',exact:true}).click();await expect(page).toHaveURL(/panel/);
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
