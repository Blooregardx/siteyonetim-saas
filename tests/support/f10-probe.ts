// SPDX-License-Identifier: AGPL-3.0-only
import type { Page,TestInfo } from '@playwright/test';
import { PrismaClient } from '@prisma/client';
import { writeFile } from 'node:fs/promises';
type Event={at:number;stage:string;page?:number;ms?:number;bytes?:number;rows?:number;ready?:string};
export async function f10Probe(page:Page,db:PrismaClient,size:number){
 if(process.env.F10_DIAGNOSTICS!=='1')return async()=>{};
 const events:Event[]=[],waits:unknown[]=[];let busy=false;let dropped=0;
 const record=(value:Event)=>{if(events.length<500)events.push(value);else dropped++;};
 const label=`f10_${size}_${crypto.randomUUID().slice(0,8)}`;
 await page.context().setExtraHTTPHeaders({'x-f10-probe':label});
 await page.exposeBinding('__f10Event',(_source,value:{stage:string;at:number;rows?:number;ready?:string;page?:number})=>{
  if(['dom.first-node','dom.rows25','dom.contentloaded','dom.load'].includes(value.stage))record({stage:value.stage,at:value.at,rows:value.rows,ready:value.ready,page:value.page});
 });
 await page.addInitScript(()=>{
  const send=(stage:string,rows?:number)=>{void (window as unknown as {__f10Event:(v:unknown)=>Promise<void>}).__f10Event({stage,at:Date.now(),rows,ready:document.readyState,page:Number(new URL(location.href).searchParams.get('chargesPage')??1)});};
  let body=false,rows=false;
  const observer=new MutationObserver(()=>{if(!body&&document.body?.childNodes.length){body=true;send('dom.first-node');}const table=[...document.querySelectorAll('table')].find(t=>t.caption?.textContent==='Aidat ve tahsilat geçmişi');const count=table?.tBodies[0]?.rows.length??0;if(!rows&&count===25&&document.querySelector('nav[aria-label="chargesPage sayfaları"]')){rows=true;send('dom.rows25',count);}});
  observer.observe(document,{childList:true,subtree:true});
  document.addEventListener('DOMContentLoaded',()=>send('dom.contentloaded'));
  window.addEventListener('load',()=>send('dom.load'));
 });
 const cdp=await page.context().newCDPSession(page);await cdp.send('Network.enable');
 const requests=new Map<string,number>();
 cdp.on('Network.requestWillBeSent',e=>{const u=new URL(e.request.url);if(e.type==='Document'&&u.pathname==='/panel'){const p=Number(u.searchParams.get('chargesPage')??1);requests.set(e.requestId,p);record({at:Date.now(),stage:'browser.navigation',page:p});}});
 cdp.on('Network.responseReceived',e=>{if(requests.has(e.requestId))record({at:Date.now(),stage:'browser.headers',page:requests.get(e.requestId)});});
 cdp.on('Network.dataReceived',e=>{if(requests.has(e.requestId))record({at:Date.now(),stage:'browser.body.chunk',page:requests.get(e.requestId),bytes:e.dataLength});});
 cdp.on('Network.loadingFinished',e=>{if(requests.has(e.requestId))record({at:Date.now(),stage:'browser.body.complete',page:requests.get(e.requestId),bytes:e.encodedDataLength});});
 cdp.on('Network.loadingFailed',e=>{if(requests.has(e.requestId))record({at:Date.now(),stage:e.canceled?'browser.body.canceled':'browser.body.failed',page:requests.get(e.requestId)});});
 const timer=setInterval(()=>{if(busy||waits.length>=160)return;busy=true;void db.$queryRaw<{state:string;waitType:string|null;wait:string|null;ms:number;shape:string}[]>`SELECT state,wait_event_type AS "waitType",wait_event AS wait,extract(epoch FROM(clock_timestamp()-query_start))*1000 AS ms,md5(query) AS shape FROM pg_stat_activity WHERE datname=current_database() AND pid<>pg_backend_pid() AND state<>'idle'`.then(rows=>{if(rows.length)waits.push({at:Date.now(),rows});}).catch(()=>record({at:Date.now(),stage:'probe.wait.error'})).finally(()=>{busy=false;});},200);
 return async(info:TestInfo)=>{clearInterval(timer);await cdp.detach().catch(()=>{});const result={label,size,status:info.status,dropped,events,waits};await writeFile(info.outputPath('f10-timeline.json'),JSON.stringify(result,null,2));console.log('[F10_BROWSER] '+JSON.stringify(result));};
}
