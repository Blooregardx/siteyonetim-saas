// Read-only ELF64 little-endian dynamic metadata; never executes input.
export function dynamicElf(bytes) {
 if(bytes.length<64 || bytes.subarray(0,4).toString('hex')!=='7f454c46' || bytes[4]!==2 || bytes[5]!==1)return {needed:[],status:'NOT_ELF64_LE'};
 const phoff=Number(bytes.readBigUInt64LE(32)), size=bytes.readUInt16LE(54), count=bytes.readUInt16LE(56);
 if(size<56 || phoff+size*count>bytes.length)return {needed:[],status:'INVALID_ELF_BOUNDARIES'};
 const headers=[];
 for(let i=0;i<count;i++){const o=phoff+i*size;headers.push({type:bytes.readUInt32LE(o),offset:Number(bytes.readBigUInt64LE(o+8)),address:Number(bytes.readBigUInt64LE(o+16)),length:Number(bytes.readBigUInt64LE(o+32))});}
 const section=headers.find(h=>h.type===2), entries=[];
 if(section && section.offset+section.length>bytes.length)return {needed:[],status:'INVALID_ELF_BOUNDARIES'};
 if(!section)return {needed:[],status:'NO_DYNAMIC_SECTION'};
 for(let o=section.offset;o<section.offset+section.length;o+=16){const tag=Number(bytes.readBigInt64LE(o));if(tag===0)break;entries.push({tag,value:Number(bytes.readBigUInt64LE(o+8))});}
 const address=entries.find(e=>e.tag===5)?.value, load=headers.find(h=>h.type===1 && address>=h.address && address<h.address+h.length);
 if(!load)return {needed:[],status:'STRING_TABLE_UNRESOLVED'};
 const base=load.offset+address-load.address;
 const strings=tag=>entries.filter(e=>e.tag===tag).map(e=>{const o=base+e.value;return bytes.subarray(o,bytes.indexOf(0,o)).toString();});
 return {needed:strings(1),soname:strings(14),rpath:strings(15),runpath:strings(29),status:'PARSED_ELF64_LE'};
}
