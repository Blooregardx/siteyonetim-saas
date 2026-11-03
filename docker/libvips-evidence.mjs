import { readFileSync, existsSync, copyFileSync, mkdtempSync, rmSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { execFileSync, spawnSync } from 'node:child_process';
const sha = b => createHash('sha256').update(b).digest('hex');
const binaries = [];
for (const platform of ['linux-x64','linuxmusl-x64']) {
 const root = `/app/node_modules/@img/sharp-libvips-${platform}`;
 if (!existsSync(`${root}/package.json`)) continue;
 const meta = JSON.parse(readFileSync(`${root}/package.json`));
 const versions = JSON.parse(readFileSync(`${root}/versions.json`));
 const path = `${root}/lib/libvips-cpp.so.${versions.vips}`;
 const bytes = readFileSync(path);
 let links;
 try { links = execFileSync('ldd',[path],{encoding:'utf8',stdio:['ignore','pipe','ignore']}); } catch { links='LINKER_REJECTED'; }
 binaries.push({platform,path,sha256:sha(bytes),package:meta.name,packageVersion:meta.version,versions,elf:{magic:bytes.subarray(0,4).toString('hex'),class:bytes[4],machine:bytes.readUInt16LE(18)},links,compatibleWithHost:platform==='linux-x64' && Boolean(process.report.getReport().header.glibcVersionRuntime)});
}
const temp = mkdtempSync('/tmp/s05b-libvips-');
let relocation;
try {
 const selected = binaries.find(b=>b.compatibleWithHost);
 if (!selected) throw new Error('NO_COMPATIBLE_BINARY');
 const target = `${temp}/libvips-cpp.so.${selected.versions.vips}`;
 copyFileSync(selected.path,target);
 const child = spawnSync(process.execPath,['-e',`const sharp=require('/app/node_modules/sharp'); sharp({create:{width:2,height:2,channels:3,background:'#123456'}}).resize(1,1).png().toBuffer().then(b=>{const maps=require('fs').readFileSync('/proc/self/maps','utf8'); console.log(JSON.stringify({imageProduced:b.length>0,alternativeLoaded:maps.includes(process.env.S05B_LIBRARY_DIR+'/libvips-cpp.so.')}))}).catch(()=>process.exit(1));`],{env:{...process.env,LD_LIBRARY_PATH:temp,S05B_LIBRARY_DIR:temp},encoding:'utf8',timeout:30000});
 const result=child.status===0?JSON.parse(child.stdout):{};
 relocation={...result,exitCode:child.status,originalSha256:selected.sha256,replacementSha256:sha(readFileSync(target)),decision:'PARTIAL',scope:'identical-byte alternate directory load, not a modified-library or static-sublibrary rebuild'};
} catch { relocation={decision:'BLOCKED',error:'ALTERNATE_LIBRARY_PROBE_FAILED'}; }
finally { rmSync(temp,{recursive:true,force:true}); }
console.log(JSON.stringify({node:process.version,sharpVersion:JSON.parse(readFileSync('/app/node_modules/sharp/package.json')).version,binaries,relocation,binarySourceDecision:'BLOCKED',relinkingDecision:'PARTIAL'}));
