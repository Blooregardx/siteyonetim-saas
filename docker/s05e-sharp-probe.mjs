// SPDX-License-Identifier: AGPL-3.0-only
// Synthetic scratch probe only. Never used by the normal application image.
import { createHash } from 'node:crypto';
import { readFileSync, realpathSync } from 'node:fs';
import { createRequire } from 'node:module';
import { resolve } from 'node:path';

const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const packageFile = resolve(process.env.S05E_PACKAGE_JSON || 'package.json');
const require = createRequire(packageFile);
const expected = process.env.S05E_LIBRARY_SHA256;
const oldHash = process.env.S05E_ORIGINAL_SHA256;
const target = realpathSync(process.env.S05E_LIBRARY_PATH);
const result = { scope: 'isolated synthetic Sharp probe', status: 'BLOCKED', node: process.version, platform: process.platform, arch: process.arch, tests: {}, loadedLibraries: [] };
try {
  if (!/^[a-f0-9]{64}$/.test(expected || '') || hash(readFileSync(target)) !== expected) throw new Error('TARGET_BINARY_HASH');
  const sharp = require('sharp');
  if (require('sharp/package.json').version !== '0.35.5') throw new Error('SHARP_VERSION');
  const png = await sharp({ create: { width: 8, height: 8, channels: 4, background: { r: 30, g: 120, b: 200, alpha: 1 } } }).png().toBuffer();
  const pngMeta = await sharp(png).metadata();
  if (pngMeta.width !== 8 || pngMeta.height !== 8 || pngMeta.format !== 'png') throw new Error('PNG_RESULT');
  result.tests.png = { status: 'PASS', sha256: hash(png) };
  const jpeg = await sharp(png).resize(4, 4).rotate(90).jpeg().toBuffer();
  const jpegMeta = await sharp(jpeg).metadata();
  if (jpegMeta.width !== 4 || jpegMeta.height !== 4 || jpegMeta.format !== 'jpeg') throw new Error('JPEG_RESULT');
  result.tests.jpeg = { status: 'PASS', sha256: hash(jpeg) };
  const svg = Buffer.from('<svg xmlns="http://www.w3.org/2000/svg" width="6" height="5"><rect width="6" height="5" fill="red"/></svg>');
  const svgPng = await sharp(svg).png().toBuffer();
  const svgMeta = await sharp(svgPng).metadata();
  if (svgMeta.width !== 6 || svgMeta.height !== 5) throw new Error('SVG_RESULT');
  result.tests.svg = { status: 'PASS', sha256: hash(svgPng) };
  const lines = readFileSync('/proc/self/maps', 'utf8').split('\n').filter(line => line.includes('libvips'));
  result.maps = lines;
  const paths = [...new Set(lines.map(line => line.trim().split(/\s+/).slice(5).join(' ').replaceAll('\\040', ' ')))];
  for (const path of paths) result.loadedLibraries.push({ path, realPath: realpathSync(path), sha256: hash(readFileSync(path)) });
  result.targetLoaded = result.loadedLibraries.some(r => r.realPath === target && r.sha256 === expected);
  result.originalLibraryLoaded = result.loadedLibraries.some(r => r.sha256 === oldHash);
  if (!result.targetLoaded || result.originalLibraryLoaded) throw new Error('ACTUAL_LIBRARY_BINDING');
  result.status = 'PASS';
} catch (error) {
  // Only controlled diagnostic labels; never dump environment or arbitrary exceptions.
  const allowed = ['TARGET_BINARY_HASH', 'SHARP_VERSION', 'PNG_RESULT', 'JPEG_RESULT', 'SVG_RESULT', 'ACTUAL_LIBRARY_BINDING'];
  result.failure = allowed.includes(error.message) ? error.message : 'NATIVE_PROBE_FAILED';
}
console.log(JSON.stringify(result, null, 2));
process.exitCode = result.status === 'PASS' ? 0 : 1;
