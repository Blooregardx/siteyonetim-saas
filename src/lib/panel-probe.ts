// SPDX-License-Identifier: AGPL-3.0-only
// Explicitly opt-in, synthetic loopback test database only. Never log SQL/params/headers.
import { AsyncLocalStorage } from 'node:async_hooks';
import { createHash,randomUUID } from 'node:crypto';
import { headers } from 'next/headers';
export function panelProbeEnabled(){
 try{const url=new URL(process.env.DATABASE_URL??'');return process.env.F10_DIAGNOSTICS==='1'&&process.env.TEST_DATABASE_URL===process.env.DATABASE_URL&&['localhost','127.0.0.1'].includes(url.hostname)&&url.pathname==='/siteyonetim_test';}catch{return false;}
}
type Scope={id:string;label:string;page:number;count:number};
const scope=new AsyncLocalStorage<Scope>();const active=new Set<Scope>();let queries=0;
function emit(value:Record<string,unknown>){console.log('[F10] '+JSON.stringify({at:Date.now(),...value}));}
export function panelMark(stage:string,extra:Record<string,number|string>={}){const s=scope.getStore();if(s&&s.count++<180)emit({id:s.id,label:s.label,page:s.page,stage,...extra});}
export async function panelStage<T>(stage:string,fn:()=>Promise<T>){const start=performance.now();panelMark(stage+'.start');try{return await fn();}catch(error){panelMark(stage+'.error',{error:error instanceof Error?error.name:'unknown',code:typeof error==='object'&&error&&'code'in error&&/^P\d{4}$/.test(String(error.code))?String(error.code):'none'});throw error;}finally{panelMark(stage+'.end',{ms:performance.now()-start});}}
export async function withPanelProbe<T>(params:Promise<Record<string,string|undefined>>,fn:()=>Promise<T>){
 if(!panelProbeEnabled())return fn();
 const label=(await headers()).get('x-f10-probe')??'';if(!/^f10_(100|1000|10000)_[a-f0-9]{8}$/.test(label))return fn();
 const p=await params;const s:Scope={id:randomUUID().slice(0,8),label,page:Number(p.chargesPage??1),count:0};
 return scope.run(s,async()=>{active.add(s);panelMark('request.received');try{return await fn();}finally{panelMark('server.component.returned');active.delete(s);}});
}
export function panelQuery(query:string,ms:number){if(active.size&&queries++<3000)emit({stage:'prisma.query',ids:[...active].slice(0,4).map(s=>s.id),command:query.match(/^\s*(\w+)/)?.[1]??'unknown',shape:createHash('sha256').update(query).digest('hex').slice(0,12),ms});}
