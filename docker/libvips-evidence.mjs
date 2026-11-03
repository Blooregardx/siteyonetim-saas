import { readFileSync, existsSync, copyFileSync, mkdtempSync, rmSync } from 'node:fs';
import { createRequire } from 'node:module';
import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';
const sha = b => createHash('sha256').update(b).digest('hex');
function dynamic(bytes) {
 const phoff=Number(bytes.readBigUInt64LE(32)), size=bytes.readUInt16LE(54), count=bytes.readUInt16LE(56);
 const headers=[];
 for(let i=0;i<count;i++){const o=phoff+i*size;headers.push({type:bytes.readUInt32LE(o),offset:Number(bytes.readBigUInt64LE(o+8)),address:Number(bytes.readBigUInt64LE(o+16)),length:Number(bytes.readBigUInt64LE(o+32))});}
 const section=headers.find(h=>h.type===2), entries=[];
 if(!section)return {needed:[],status:'NO_DYNAMIC_SECTION'};
 for(let o=section.offset;o<section.offset+section.length;o+=16){const tag=Number(bytes.readBigInt64LE(o));if(tag===0)break;entries.push({tag,value:Number(bytes.readBigUInt64LE(o+8))});}
 const address=entries.find(e=>e.tag===5)?.value, load=headers.find(h=>h.type===1 && address>=h.address && address<h.address+h.length);
 if(!load)return {needed:[],status:'STRING_TABLE_UNRESOLVED'};
 const base=load.offset+address-load.address;
 const strings=tag=>entries.filter(e=>e.tag===tag).map(e=>{const o=base+e.value;return bytes.subarray(o,bytes.indexOf(0,o)).toString();});
 return {needed:strings(1),soname:strings(14),rpath:strings(15),runpath:strings(29),status:'PARSED_ELF64_LE'};
}
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
 binaries.push({platform,path,sha256:sha(bytes),package:meta.name,packageVersion:meta.version,versions,elf:{magic:bytes.subarray(0,4).toString('hex'),class:bytes[4],machine:bytes.readUInt16LE(18)},dynamic:dynamic(bytes),links,linkerExitCode:linked.status,compatibleWithHost:platform==='linux-x64' && Boolean(process.report.getReport().header.glibcVersionRuntime)});
}
const temp = mkdtempSync('/tmp/s05b-libvips-');
const addonPath=createRequire('/app/package.json').resolve('@img/sharp-linux-x64/sharp.node');
const addonBytes=readFileSync(addonPath);
const addon={path:addonPath,sha256:sha(addonBytes),dynamic:dynamic(addonBytes)};
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
console.log(JSON.stringify({node:process.version,sharpVersion:JSON.parse(readFileSync('/app/node_modules/sharp/package.json')).version,binaries,addon,relocation,binarySourceDecision:'BLOCKED',relinkingDecision:relocation.alternativeLoaded && !relocation.originalLoaded && relocation.imageProduced ? 'PARTIAL' : 'BLOCKED'}));
