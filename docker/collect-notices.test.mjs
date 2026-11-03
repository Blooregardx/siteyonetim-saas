import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, writeFileSync, readFileSync, symlinkSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { collectNotices } from './collect-notices.mjs';
test('preserves original notice bytes and nested paths; skips symlinks and secrets', () => {
 const root = mkdtempSync(join(tmpdir(), 's05a-notices-'));
 try {
  const source = join(root, 'modules'), output = join(root, 'notices');
  mkdirSync(join(source, '@scope', 'fixture'), {recursive:true});
  writeFileSync(join(source, '@scope', 'fixture', 'LICENSE'), 'original copyright\n');
  writeFileSync(join(source, 'NOTICE.txt'), 'original notice\n');
  writeFileSync(join(source, 'COPYING-LESSER'), 'original lesser notice\n');
  writeFileSync(join(source, '.env'), 'SYNTHETIC_SECRET');
  symlinkSync(join(source, 'NOTICE.txt'), join(source, 'COPYING'));
  const records = collectNotices(source, output);
  assert.equal(records.length, 3);
  assert.equal(readFileSync(join(output, '@scope', 'fixture', 'LICENSE'), 'utf8'), 'original copyright\n');
  assert.equal(records.every(r => /^[a-f0-9]{64}$/.test(r.sha256)), true);
  assert.throws(() => collectNotices(source, join(source, 'output')));
 } finally { rmSync(root, {recursive:true, force:true}); }
});
