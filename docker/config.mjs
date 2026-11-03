import { readFileSync } from 'node:fs';
export function configure(role) {
 const password = readFileSync(`/run/secrets/${role}_password`, 'utf8').trim();
 if (!/^[a-f0-9]{64}$/.test(password)) throw new Error('INVALID_SECRET');
 const name = process.env.POSTGRES_DB;
 if (!/^[a-z][a-z0-9_]{0,62}$/.test(name ?? '')) throw new Error('INVALID_DB_NAME');
 process.env.DATABASE_URL = `postgresql://sy_${role}:${password}@db:5432/${name}?schema=public&connection_limit=5&pool_timeout=10`;
 if (role === 'runtime') {
  const u = new URL(process.env.APP_URL);
  if (u.protocol !== 'https:' || u.username || u.password || u.pathname !== '/' || u.search || u.hash) throw new Error('HTTPS_ORIGIN_REQUIRED');
  const smtp = readFileSync('/run/secrets/smtp_url', 'utf8').trim();
  if (smtp) {
   const s = new URL(smtp);
   if (!['smtp:', 'smtps:'].includes(s.protocol) || !process.env.MAIL_FROM || /[\r\n]/.test(process.env.MAIL_FROM)) throw new Error('INVALID_MAIL');
   process.env.SMTP_URL = smtp;
  }
 }
}
