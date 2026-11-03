import { test } from 'node:test';
import assert from 'node:assert/strict';
import { dynamicElf } from './elf-evidence.mjs';
test('JavaScript export shims are not parsed as ELF', () => {
 assert.equal(dynamicElf(Buffer.from("module.exports = require('./lib/versioned.node');" )).status,'NOT_ELF64_LE');
});
test('truncated ELF header tables cannot read outside the binary', () => {
 const bytes=Buffer.alloc(64); bytes.write('7f454c46',0,'hex');bytes[4]=2;bytes[5]=1;
 bytes.writeBigUInt64LE(4096n,32);bytes.writeUInt16LE(56,54);bytes.writeUInt16LE(1,56);
 assert.equal(dynamicElf(bytes).status,'INVALID_ELF_BOUNDARIES');
});
