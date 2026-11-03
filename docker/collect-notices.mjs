// Preserve original installed npm notices, including transitive/tooling notices.
import { readdirSync, lstatSync, mkdirSync, copyFileSync, writeFileSync, readFileSync } from 'node:fs';
import { join, relative, resolve } from 'node:path';
import { createHash } from 'node:crypto';
import { pathToFileURL } from 'node:url';
export function collectNotices(source, destination) {
 const root = resolve(source), target = resolve(destination), records = [];
 if (target === root || target.startsWith(root + '/')) throw new Error('Notice output must be outside dependencies');
 function walk(dir) {
  for (const entry of readdirSync(dir)) {
   const path = join(dir, entry), stat = lstatSync(path);
   if (stat.isSymbolicLink()) continue;
   if (stat.isDirectory()) { walk(path); continue; }
   if (!/^(license|notice|copying|copyright)(\.|$)/i.test(entry)) continue;
   const name = relative(root, path), output = join(target, name);
   mkdirSync(resolve(output, '..'), { recursive:true });
   copyFileSync(path, output);
   records.push({path:name, sha256:createHash('sha256').update(readFileSync(path)).digest('hex')});
  }
 }
 walk(root);
 mkdirSync(target, {recursive:true});
 writeFileSync(join(target, 'inventory.json'), JSON.stringify({scope:'Original notices from all installed npm dependencies, including development tools; not proof of runtime presence or completeness', records}));
 return records;
}
if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) collectNotices(process.argv[2] ?? 'node_modules', process.argv[3] ?? 'third-party-notices');
