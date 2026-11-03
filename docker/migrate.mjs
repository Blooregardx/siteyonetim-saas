import { configure } from './config.mjs';
import { PrismaClient } from '@prisma/client';
import { readFileSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
let stage = 'configuration';
try {
 configure('migrator');
 for (const args of [['validate'], ['migrate','deploy'], ['migrate','diff','--from-url',process.env.DATABASE_URL,'--to-schema-datamodel','prisma/schema.prisma','--exit-code']]) {
  stage = args.slice(0, 2).filter(a => !a.startsWith('--')).join(':');
  const r = spawnSync('node', ['node_modules/prisma/build/index.js', ...args], {stdio:'pipe'});
  if (r.status !== 0) {
   const codes = `${r.stdout} ${r.stderr}`.match(/\bP[0-9]{4}\b/g) ?? [];
   console.error(`Migration stage ${stage} failed; Prisma codes: ${[...new Set(codes)].join(',') || 'none'}`);
   throw new Error('MIGRATION_FAILED');
  }
 }
 stage = 'grants';
 const db = new PrismaClient();
 try { for (const sql of readFileSync('docker/grants.sql','utf8').split(';').filter(s=>s.trim())) await db.$executeRawUnsafe(sql); }
 finally { await db.$disconnect(); }
 console.log('Migration, schema and runtime grants verified');
} catch (error) { console.error(`Failed stage: ${stage}; code: ${/^(P[0-9]{4}|ENOENT|EACCES)$/.test(error.code ?? '') ? error.code : 'unclassified'}`); console.error('SELFHOST_MIGRATION_FAILED: inspect target and schema using a trusted operator session'); process.exit(1); }
