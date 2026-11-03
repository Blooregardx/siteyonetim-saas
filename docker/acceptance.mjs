// Synthetic CI assertions only. Never invoked by the application entrypoint.
import assert from 'node:assert/strict';
import { statSync } from 'node:fs';
import { PrismaClient } from '@prisma/client';
import { configure } from './config.mjs';
import { gate } from './gate.mjs';
assert.equal(process.env.POSTGRES_DB, 'siteyonetim_test');
assert.notEqual(process.getuid(), 0);
configure('runtime');
assert.equal(statSync('/run/secrets/runtime_password').mode & 0o007, 0);
const db = new PrismaClient();
try {
 const [role] = await db.$queryRaw`SELECT current_user AS name, rolconnlimit, rolsuper, rolcreatedb, rolcreaterole, pg_has_role(current_user,'sy_migrator','MEMBER') AS migration_member FROM pg_roles WHERE rolname=current_user`;
 assert.equal(role.name, 'sy_runtime');
 assert.equal(role.rolconnlimit, 10);
 assert.equal(role.rolsuper || role.rolcreatedb || role.rolcreaterole || role.migration_member, false);
 await assert.rejects(db.$executeRawUnsafe('CREATE TABLE public.s04a_forbidden_ddl (id integer)'), e => e.meta?.code === '42501');
 if (process.argv[2] === 'before') {
  const [schema] = await db.$queryRaw`SELECT to_regclass('public._prisma_migrations')::text AS migrations`;
  assert.equal(schema.migrations, null);
 } else {
  await gate();
  assert.equal(await db.$queryRaw`SELECT count(*)::int AS count FROM "_prisma_migrations"`.then(r=>r[0].count), 11);
  if (process.argv[2] === 'write') await db.authAttempt.create({data:{key:'s04a-persistence-sentinel',count:7,expiresAt:new Date('2099-01-01T00:00:00Z')}});
  else assert.equal((await db.authAttempt.findUniqueOrThrow({where:{key:'s04a-persistence-sentinel'}})).count, 7);
 }
 console.log(`Synthetic runtime assertions passed: ${process.argv[2]}`);
} finally { await db.$disconnect(); }
