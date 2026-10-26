"use server";
import { z } from "zod";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { db } from "@/lib/db";
import { hashPassword, checkPassword, digest, token } from "@/lib/password";
import { cookieName, openSession } from "@/lib/session";
import nodemailer from "nodemailer";
const credentials = z.object({ email: z.string().trim().toLowerCase().email().max(254), password: z.string().min(12).max(128) });
export type Result = { message: string };
// Atomic shared database limiter; client-supplied identity never authorizes data access.
async function limit(key: string) {
  const rows = await db.$queryRaw<{count:number}[]>`INSERT INTO "AuthAttempt" (key,count,"expiresAt") VALUES (${digest(key)},1,NOW()+INTERVAL '15 minutes') ON CONFLICT (key) DO UPDATE SET count = CASE WHEN "AuthAttempt"."expiresAt" < NOW() THEN 1 ELSE "AuthAttempt".count+1 END, "expiresAt" = CASE WHEN "AuthAttempt"."expiresAt" < NOW() THEN NOW()+INTERVAL '15 minutes' ELSE "AuthAttempt"."expiresAt" END RETURNING count`;
  if (rows[0].count > (key.endsWith(":global") ? 100 : 10)) throw new Error("RATE_LIMIT");
}
export async function authenticate(_state: Result, form: FormData): Promise<Result> {
  const parsed = credentials.safeParse(Object.fromEntries(form));
  if (!parsed.success) return { message: "Geçerli e-posta ve 12–128 karakterli parola girin." };
  const { email, password } = parsed.data;
  try {
    await limit("auth:global");
    await limit(`auth:${email}`);
    let user;
    if (form.get("mode") === "register") {
      const name = z.string().trim().min(2).max(100).parse(form.get("name"));
      user = await db.user.create({ data: { email, name, passwordHash: await hashPassword(password) } });
    } else {
      user = await db.user.findUnique({ where: { email } });
      const fallback = "0".repeat(64) + ":" + "0".repeat(128);
      const valid = await checkPassword(password, user?.passwordHash ?? fallback);
      if (!user || !valid) return { message: "Giriş bilgileri doğrulanamadı." };
    }
    await openSession(user.id);
  } catch { return { message: "İşlem tamamlanamadı. Bilgilerinizi kontrol edin veya daha sonra tekrar deneyin." }; }
  redirect("/panel");
}
export async function logout() {
  const jar = await cookies(); const raw = jar.get(cookieName)?.value;
  if (raw) await db.session.deleteMany({ where: { tokenHash: digest(raw) } });
  jar.delete(cookieName); redirect("/giris");
}
export async function resetPassword(_state: Result, form: FormData): Promise<Result> {
  try {
    const raw = form.get("token");
    if (raw) {
      const password = z.string().min(12).max(128).parse(form.get("password"));
      const tokenHash = digest(z.string().length(64).parse(raw));
      const passwordHash = await hashPassword(password);
      await db.$transaction(async tx => {
        const reset = await tx.passwordReset.findUnique({ where: { tokenHash } });
        if (!reset || reset.expiresAt < new Date()) throw new Error("INVALID_TOKEN");
        await tx.passwordReset.delete({ where: { tokenHash } });
        await tx.user.update({ where: { id: reset.userId }, data: { passwordHash } });
        await tx.session.deleteMany({ where: { userId: reset.userId } });
        await tx.passwordReset.deleteMany({ where: { userId: reset.userId } });
      });
      return { message: "Parola yenilendi. Giriş yapabilirsiniz." };
    }
    const email = z.string().trim().toLowerCase().email().max(254).parse(form.get("email"));
    await limit("reset:global");
    await limit(`reset:${email}`);
    if (!process.env.SMTP_URL || !process.env.APP_URL || !process.env.MAIL_FROM) return { message: "Parola kurtarma için posta servisi henüz yapılandırılmadı." };
    const user = await db.user.findUnique({ where: { email } });
    if (user) {
      const rawToken = token();
      await db.passwordReset.create({ data: { tokenHash: digest(rawToken), userId: user.id, expiresAt: new Date(Date.now()+1800000) } });
      await nodemailer.createTransport(process.env.SMTP_URL).sendMail({ from: process.env.MAIL_FROM, to: email, subject: "SiteYönetim parola yenileme", text: `${process.env.APP_URL}/sifre-sifirla?token=${rawToken}` });
    }
    return { message: "Hesap mevcutsa yenileme bağlantısı gönderildi." };
  } catch { return { message: "İşlem tamamlanamadı. Daha sonra tekrar deneyin." }; }
}
