import { randomBytes, scrypt as derive, timingSafeEqual, createHash } from "node:crypto";
import { promisify } from "node:util";
const scrypt = promisify(derive);
export const digest = (value: string) => createHash("sha256").update(value).digest("hex");
export const token = () => randomBytes(32).toString("hex");
export async function hashPassword(password: string) {
  const salt = token();
  const hash = await scrypt(password, salt, 64) as Buffer;
  return `${salt}:${hash.toString("hex")}`;
}
export async function checkPassword(password: string, stored: string) {
  const [salt, hex] = stored.split(":");
  if (!salt || !hex || hex.length !== 128) return false;
  const candidate = await scrypt(password, salt, 64) as Buffer;
  return timingSafeEqual(candidate, Buffer.from(hex, "hex"));
}
