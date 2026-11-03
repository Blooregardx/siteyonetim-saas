/** Text and server-produced numeric cells deliberately have different trust rules. */
export function csvText(value:string){const safe=/^[\s\p{Cc}\p{Cf}]*[=+\-@]/u.test(value)?"'"+value:value;return '"'+safe.replaceAll('"','""')+'"';}
export function csvMoney(kurus:number){if(!Number.isSafeInteger(kurus))throw new Error('UNSAFE_FINANCIAL_TOTAL');const n=BigInt(kurus),a=n<0n?-n:n;return `${n<0n?'-':''}${a/100n},${String(a%100n).padStart(2,'0')}`;}
export function csvLine(cells:{text:string}[]|({text:string}|{money:number})[]){return cells.map(c=>'text'in c?csvText(c.text):csvMoney(c.money)).join(';')+'\r\n';}
export const EXPORT_BATCH_SIZE=1000;
export const EXPORT_MAX_ROWS=50000;
export const EXPORT_MAX_BYTES=128*1024*1024;

export function exportByteSize(current:number,value:string){
 if(!Number.isSafeInteger(current)||current<0)throw new Error('EXPORT_LIMIT');
 const next=current+Buffer.byteLength(value);
 if(next>EXPORT_MAX_BYTES)throw new Error('EXPORT_LIMIT');
 return next;
}
