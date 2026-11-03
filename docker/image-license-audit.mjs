// Read-only filesystem evidence. Never grants binary distribution clearance.
import { dynamicElf } from './elf-evidence.mjs';
import { existsSync, readFileSync, readdirSync, lstatSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
const packages = [], notices = [], binaries = [];
const hash = p => createHash('sha256').update(readFileSync(p)).digest('hex');
function walk(root) {
 if (!existsSync(root)) return;
 for (const entry of readdirSync(root)) {
  const path = `${root}/${entry}`;
  const st = lstatSync(path);
  if (st.isSymbolicLink()) continue;
  if (st.isDirectory()) { walk(path); continue; }
  if (entry === 'package.json') {
   try { const p = JSON.parse(readFileSync(path, 'utf8')); if (p.name && p.version) packages.push({path, name:p.name, version:p.version, license:p.license ?? null}); } catch { /* non-package JSON is not evidence */ }
  }
  if (/^(license|notice|copying|copyright)([._-]|$)/i.test(entry)) notices.push({path, sha256:hash(path)});
  if (/\.node$|\.so(\.|$)|\.wasm$|^query-engine(?:-|$)|^schema-engine(?:-|$)/.test(entry)) {
   let links;
   try { links = execFileSync('ldd', [path], {encoding:'utf8', stdio:['ignore','pipe','ignore']}).trim(); } catch { links = 'UNRESOLVED_OR_NOT_DYNAMIC'; }
   const bytes=readFileSync(path);
   const elf=bytes.length>=20 && bytes.subarray(0,4).toString('hex')==='7f454c46' ? {magic:'7f454c46',class:bytes[4],machine:bytes.readUInt16LE(18)} : null;
   let dynamic;
   try { dynamic=dynamicElf(bytes); } catch { dynamic={status:'UNRESOLVED',needed:[]}; }
   binaries.push({path, sha256:hash(path), elf, dynamic, links});
  }
 }
}
walk('/app/node_modules'); walk('/app/third-party-notices'); walk('/usr/share/doc');
if (existsSync('/usr/local/LICENSE')) notices.push({path:'/usr/local/LICENSE',sha256:hash('/usr/local/LICENSE')});
const debian = execFileSync('dpkg-query', ['-W', '-f=${Package}\t${Version}\t${source:Package}\t${source:Version}\n'], {encoding:'utf8'}).trim().split('\n');
console.log(JSON.stringify({binaryDistributionReadiness:'BLOCKED', scope:'filesystem inventory, not complete legal or source evidence; symlinks excluded', nodeVersion:process.version, debian, packages, notices, binaries}));
