import nodemailer from "nodemailer";
export function mailConfiguration() {
 const { SMTP_URL, MAIL_FROM, APP_URL } = process.env;
 if (!SMTP_URL || !MAIL_FROM || !APP_URL) throw new Error("MAIL_NOT_CONFIGURED");
 const app = new URL(APP_URL); const smtp = new URL(SMTP_URL);
 const loopback = (host: string) => ["127.0.0.1", "localhost"].includes(host);
 const testUrl = process.env.TEST_DATABASE_URL;
 const isolated = testUrl && loopback(new URL(testUrl).hostname) && new URL(testUrl).pathname === "/siteyonetim_test" && process.env.DATABASE_URL === testUrl;
 const localTest = isolated && loopback(app.hostname) && loopback(smtp.hostname);
 if (app.username || app.password || app.search || app.hash || app.pathname !== "/" || (app.protocol !== "https:" && !(localTest && app.protocol === "http:"))) throw new Error("INVALID_APP_URL");
 if (!["smtp:","smtps:"].includes(smtp.protocol) || /[\r\n]/.test(MAIL_FROM)) throw new Error("INVALID_SMTP");
 return { appUrl: app.origin, sender: MAIL_FROM, smtpUrl: SMTP_URL, requireTLS: !localTest && smtp.protocol === "smtp:" };
}
export async function sendLink(email: string, path: string, raw: string, subject: string) {
 const config = mailConfiguration();
 // Explicit transport options ensure STARTTLS cannot silently downgrade outside isolated tests.
 const smtp = new URL(config.smtpUrl);
 const secureTransport = nodemailer.createTransport({ host: smtp.hostname, port: Number(smtp.port || (smtp.protocol === "smtps:" ? 465 : 587)), secure: smtp.protocol === "smtps:", requireTLS: config.requireTLS, auth: smtp.username ? { user: decodeURIComponent(smtp.username), pass: decodeURIComponent(smtp.password) } : undefined });
 await secureTransport.sendMail({from:config.sender,to:email,subject,text:`${config.appUrl}/${path}?token=${raw}`});
}
