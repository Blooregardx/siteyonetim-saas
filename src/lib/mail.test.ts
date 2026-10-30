import { test } from "node:test";
import assert from "node:assert/strict";
import { mailConfiguration } from "./mail";
test("SMTP ve HTTPS yapılandırması güvenli biçimde doğrulanır",()=>{
 const keys=["SMTP_URL","MAIL_FROM","APP_URL","DATABASE_URL","TEST_DATABASE_URL"] as const;
 const saved=Object.fromEntries(keys.map(k=>[k,process.env[k]]));
 try {
  delete process.env.TEST_DATABASE_URL;
  process.env.SMTP_URL="smtp://smtp.example.invalid:587";process.env.MAIL_FROM="test@example.invalid";process.env.APP_URL="http://app.example.invalid";
  assert.throws(()=>mailConfiguration(),/INVALID_APP_URL/);
  process.env.APP_URL="https://app.example.invalid";assert.equal(mailConfiguration().requireTLS,true);
  process.env.SMTP_URL="smtps://smtp.example.invalid:465";assert.equal(mailConfiguration().requireTLS,false);
  process.env.MAIL_FROM="sender\r\nBcc: invalid";assert.throws(()=>mailConfiguration(),/INVALID_SMTP/);
  delete process.env.SMTP_URL;assert.throws(()=>mailConfiguration(),/MAIL_NOT_CONFIGURED/);
 } finally { for(const key of keys) {if(saved[key]===undefined) delete process.env[key];else process.env[key]=saved[key];} }
});
