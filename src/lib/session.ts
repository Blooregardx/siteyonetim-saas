import "server-only";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { db } from "./db";
import { digest, token } from "./password";
export const cookieName = process.env.NODE_ENV === "production" ? "__Host-siteyonetim" : "siteyonetim";
export async function verifySession() {
  const raw = (await cookies()).get(cookieName)?.value;
  if (!raw) return null;
  const session = await db.session.findUnique({ where: { tokenHash: digest(raw) } });
  return session && session.expiresAt > new Date() ? { userId: session.userId } : null;
}
export async function requireSession() {
  const session = await verifySession();
  if (!session) redirect("/giris");
  return session;
}
export async function openSession(userId: string) {
  const raw = token(); const expiresAt = new Date(Date.now() + 7 * 86400000);
  await db.session.create({ data: { tokenHash: digest(raw), userId, expiresAt } });
  (await cookies()).set(cookieName, raw, { httpOnly: true, secure: process.env.NODE_ENV === "production", sameSite: "lax", path: "/", expires: expiresAt });
}
