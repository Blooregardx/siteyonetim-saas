import { PrismaClient } from '@prisma/client';
import { readdirSync, readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
export async function gate() {
 const db = new PrismaClient();
 try {
  const rows = await db.$queryRaw`SELECT migration_name, checksum, finished_at, rolled_back_at FROM "_prisma_migrations" ORDER BY migration_name`;
  const names = readdirSync('prisma/migrations').filter(n => /^\d/.test(n)).sort();
  if (rows.length !== names.length || rows.some((r,i) => r.migration_name !== names[i] || !r.finished_at || r.rolled_back_at || r.checksum !== createHash('sha256').update(readFileSync(`prisma/migrations/${names[i]}/migration.sql`)).digest('hex'))) throw new Error('SCHEMA_VERSION');
  const [role] = await db.$queryRaw`SELECT rolsuper, rolcreatedb, rolcreaterole, has_schema_privilege(current_user,'public','CREATE') AS ddl FROM pg_roles WHERE rolname=current_user`;
  if (role.rolsuper || role.rolcreatedb || role.rolcreaterole || role.ddl) throw new Error('UNSAFE_ROLE');
 } finally { await db.$disconnect(); }
}
