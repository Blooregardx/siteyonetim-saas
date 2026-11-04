import { dynamicElf } from './elf-evidence.mjs';
import { dirname } from 'node:path';
import { readFileSync, existsSync, copyFileSync, mkdtempSync, rmSync, readdirSync } from 'node:fs';
import { createRequire } from 'node:module';
import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';
const sha = b => createHash('sha256').update(b).digest('hex');
const temporaryMountNoexec=readFileSync('/proc/mounts','utf8').split('\n').some(line=>{const fields=line.split(' ');return fields[1]==='/tmp' && fields[3].split(',').includes('noexec');});
const binaries = [];
for (const platform of ['linux-x64','linuxmusl-x64']) {
 const root = `/app/node_modules/@img/sharp-libvips-${platform}`;
 if (!existsSync(`${root}/package.json`)) continue;
 const meta = JSON.parse(readFileSync(`${root}/package.json`));
 const versions = JSON.parse(readFileSync(`${root}/versions.json`));
 const path = `${root}/lib/libvips-cpp.so.${versions.vips}`;
 const bytes = readFileSync(path);
 const linked = spawnSync('ldd',[path],{encoding:'utf8'});
 const links = linked.stdout || 'LINKER_REJECTED';
 binaries.push({platform,path,sha256:sha(bytes),package:meta.name,packageVersion:meta.version,versions,elf:{magic:bytes.subarray(0,4).toString('hex'),class:bytes[4],machine:bytes.readUInt16LE(18)},dynamic:dynamicElf(bytes),links,linkerExitCode:linked.status,compatibleWithHost:platform==='linux-x64' && Boolean(process.report.getReport().header.glibcVersionRuntime)});
}
const temp = mkdtempSync('/tmp/s05b-libvips-');
const resolver=createRequire('/app/package.json');
const packageRoot=dirname(resolver.resolve('@img/sharp-linux-x64/package'));
const nativeFiles=readdirSync(packageRoot+'/lib').filter(name=>name.endsWith('.node'));
if(nativeFiles.length!==1)throw new Error('AMBIGUOUS_NATIVE_ADDON');
const addonPath=packageRoot+'/lib/'+nativeFiles[0];
const exportPath=resolver.resolve('@img/sharp-linux-x64/sharp.node');
const addonBytes=readFileSync(addonPath);
const addon={path:addonPath,exportPath,exportSha256:sha(readFileSync(exportPath)),sha256:sha(addonBytes),dynamic:dynamicElf(addonBytes)};
let relocation;
try {
 const selected = binaries.find(b=>b.compatibleWithHost);
 if (!selected) throw new Error('NO_COMPATIBLE_BINARY');
 const target = `${temp}/libvips-cpp.so.${selected.versions.vips}`;
 copyFileSync(selected.path,target);
 const probe = preload => { const child = spawnSync(process.execPath,['-e',`const sharp=require('/app/node_modules/sharp'); sharp({create:{width:2,height:2,channels:3,background:'#123456'}}).resize(1,1).png().toBuffer().then(b=>{const maps=require('fs').readFileSync('/proc/self/maps','utf8'); console.log(JSON.stringify({imageProduced:b.length>0,alternativeLoaded:maps.includes(process.env.S05B_LIBRARY_DIR+'/libvips-cpp.so.'),originalLoaded:maps.includes(process.env.S05B_ORIGINAL_LIBRARY)}))}).catch(()=>process.exit(1));`],{env:{...process.env,LD_LIBRARY_PATH:temp,S05B_LIBRARY_DIR:temp,S05B_ORIGINAL_LIBRARY:selected.path,...(preload?{LD_PRELOAD:target}:{})},encoding:'utf8',timeout:30000});
 const result=child.status===0?JSON.parse(child.stdout):{};return {...result,exitCode:child.status}; };
 const ldLibraryPathProbe=probe(false), preloadProbe=probe(true);
 const result=preloadProbe.alternativeLoaded && !preloadProbe.originalLoaded ? preloadProbe : ldLibraryPathProbe;
 relocation={...result,ldLibraryPathProbe,preloadProbe,originalSha256:selected.sha256,replacementSha256:sha(readFileSync(target)),decision:result.alternativeLoaded && !result.originalLoaded && result.imageProduced ? 'PARTIAL' : 'BLOCKED',scope:'identical-byte alternate directory load, not a modified-library or static-sublibrary rebuild'};
} catch { relocation={decision:'BLOCKED',error:'ALTERNATE_LIBRARY_PROBE_FAILED'}; }
finally { rmSync(temp,{recursive:true,force:true}); }
console.log(JSON.stringify({temporaryMountNoexec,node:process.version,sharpVersion:JSON.parse(readFileSync('/app/node_modules/sharp/package.json')).version,binaries,addon,relocation,binarySourceDecision:'BLOCKED',relinkingDecision:relocation.alternativeLoaded && !relocation.originalLoaded && relocation.imageProduced ? 'PARTIAL' : 'BLOCKED'}));
