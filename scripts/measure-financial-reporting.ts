/** Synthetic benchmark only. Adds isolated fixtures; never resets or edits financial history. */
import { PrismaClient } from '@prisma/client';
import { execFileSync } from 'node:child_process';
import { readFile,writeFile,unlink,mkdir } from 'node:fs/promises';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
import { performance } from 'node:perf_hooks';
import { availableParallelism } from 'node:os';
import assert from 'node:assert/strict';
import { management } from '../src/lib/management';
const url=process.env.TEST_DATABASE_URL;
if(!url||!['localhost','127.0.0.1'].includes(new URL(url).hostname)||new URL(url).pathname!='/siteyonetim_test')throw new Error('Dedicated local TEST_DATABASE_URL required');
const capture:{query:string;params:string}[]=[];
const db=new PrismaClient({datasourceUrl:url,log:[{emit:'event',level:'query'}]});
db.$on('query',e=>{if(e.query.includes('WITH balances')||e.query.includes('WITH events')||e.query.includes('WITH filtered'))capture.push({query:e.query,params:e.params});});
const prefix='bench'+crypto.randomUUID().replaceAll('-','');
const temporary=[resolve('src/lib/.s03d-baseline-income-'+prefix+'.ts'),resolve('src/lib/.s03d-baseline-management-'+prefix+'.ts')];
const median=(v:number[])=>[...v].sort((a,b)=>a-b)[Math.floor(v.length/2)];
async function timed<T>(fn:()=>Promise<T>){const start=performance.now();const value=await fn();return {value,ms:performance.now()-start};}
async function main(){
 if(process.argv.includes('--dashboard-only')||process.argv.includes('--csv-only')){
  const path='docs/performance/s03d-measurements.json';const saved=JSON.parse(await readFile(path,'utf8'));
  for(const result of saved.results){
   const site=await db.site.findFirstOrThrow({where:{name:'Performans '+result.units},orderBy:{createdAt:'desc'},include:{organization:{include:{memberships:true}}}});
   const api=management(db,async()=>({userId:site.organization!.memberships[0].userId}));
   if(process.argv.includes('--csv-only')){
    for(const [name,fn] of [['debtCsv',()=>api.exportDebtCsv({organizationId:site.organizationId!,siteId:site.id,period:'2026-10'})],['movementCsv',()=>api.exportMovementCsv({organizationId:site.organizationId!,siteId:site.id,month:'2026-10'})]] as const){
     const rss=process.memoryUsage().rss;let peak=rss;const interval=setInterval(()=>{peak=Math.max(peak,process.memoryUsage().rss);},10);
     try{const r=await timed(fn);peak=Math.max(peak,process.memoryUsage().rss);result[name]={ms:r.ms,rows:r.value.rows,bytes:r.value.size,rssBeforeMiB:rss/1048576,sampledPeakRssMiB:peak/1048576,sampledRssDeltaMiB:(peak-rss)/1048576};await r.value.dispose();}finally{clearInterval(interval);}
    }if(result.units===10000){await assert.rejects(api.exportDebtCsv({organizationId:site.organizationId!,siteId:site.id}),/EXPORT_LIMIT/);result.debtAllPeriodsLimit='EXPORT_LIMIT for 60000 charges';}continue;
   }
   const rss=process.memoryUsage().rss;let peak=rss;const interval=setInterval(()=>{peak=Math.max(peak,process.memoryUsage().rss);},10);
   try{const r=await timed(()=>api.dashboard(site.id));peak=Math.max(peak,process.memoryUsage().rss);result.dashboard={unchanged:true,ms:r.ms,units:r.value.units.length,charges:r.value.charges.length,payments:r.value.charges.reduce((n,c)=>n+c.payments.length,0),rssBeforeMiB:rss/1048576,sampledPeakRssMiB:peak/1048576,sampledRssDeltaMiB:(peak-rss)/1048576};}
   catch(error){result.dashboard={unchanged:true,error:error instanceof Error?error.message:'Benchmark failed'};}finally{clearInterval(interval);}
  }
  if(process.argv.includes('--csv-only'))saved.environment.csvMethod='CSV-only repeat on the same final fixtures after aggregate overflow checks; separate Node process, 10 ms RSS sampling including final RSS. Not network time.';
  else saved.environment.dashboardMethod='Separate warm process; unchanged dashboard() service wall time and 10 ms RSS samples including final RSS. Not HTTP rendering or browser memory.';
  await writeFile(path,JSON.stringify(saved,null,2)+'\n');console.log(saved.results.map((r:{units:number;dashboard:unknown})=>({units:r.units,dashboard:r.dashboard})));return;
 }

 await writeFile(temporary[0],execFileSync('git',['show','f8b2ff1b6857c8a1e22dae3a04704e2c8bed15b0:src/lib/income-expenses.ts'],{encoding:'utf8'}));
 await writeFile(temporary[1],execFileSync('git',['show','f8b2ff1b6857c8a1e22dae3a04704e2c8bed15b0:src/lib/management.ts'],{encoding:'utf8'}).replace('"./income-expenses"',JSON.stringify('./'+temporary[0].split('/').pop())));
 const legacy=(await import(pathToFileURL(temporary[1]).href)).management as typeof management;
 const results:unknown[]=[];const plans:unknown[]=[];
 const settings=await db.$queryRawUnsafe('SELECT version(),current_setting(\'shared_buffers\') AS shared_buffers,current_setting(\'work_mem\') AS work_mem');
 for(const units of [100,1000,10000]){
  const id=prefix+'n'+units;
  await db.user.create({data:{id,email:id+'@example.invalid',name:'Sentetik performans',emailVerifiedAt:new Date()}});
  const api=management(db,async()=>({userId:id})),before=legacy(db,async()=>({userId:id}));const org=await api.createOrganization('Sentetik '+units,'COMPANY');const site=await api.createSite(org.id,'Performans '+units);const block=await api.createBlock(site.id,'A');const category=await api.createCategory(site.id,{type:'EXPENSE',name:'Sentetik gider'});const income=await api.createCategory(site.id,{type:'INCOME',name:'Sentetik gelir'});
  await db.$executeRawUnsafe(`INSERT INTO "Unit" (id,"siteId","blockId",number) SELECT $1||'u'||i,$2,$3,i::text FROM generate_series(1,$4::int) i`,id,site.id,block.id,units);
  await db.$executeRawUnsafe(`INSERT INTO "Charge" (id,"siteId","unitId",period,"amountKurus","dueDate") SELECT $1||'c'||m||'x'||i,$2,$1||'u'||i,'2026-'||lpad(m::text,2,'0'),20000,make_date(2026,m,1) FROM generate_series(1,$3::int) i CROSS JOIN generate_series(5,10) m`,id,site.id,units);
  await db.$executeRawUnsafe(`INSERT INTO "Payment" (id,"siteId","chargeId","amountKurus","paidAt","idempotencyKey",method) SELECT $1||'p'||m||'x'||i,$2,$1||'c'||m||'x'||i,10000,make_date(2026,m,15)::timestamp,$1||'key'||m||'x'||i,'CASH' FROM generate_series(1,$3::int) i CROSS JOIN generate_series(5,10) m`,id,site.id,units);
  await db.$executeRawUnsafe(`INSERT INTO "PaymentReversal" (id,"siteId","paymentId","amountKurus","reasonCode","actorId","idempotencyKey","createdAt") SELECT $1||'pr'||m||'x'||i,$2,$1||'p'||m||'x'||i,10000,'ENTRY_ERROR',$1,gen_random_uuid()::text,make_date(2026,m,20)::timestamp FROM generate_series(1,$3::int) i CROSS JOIN generate_series(5,10) m WHERE i%10=0`,id,site.id,units);
  await db.$executeRawUnsafe(`INSERT INTO "FinancialEntry" (id,"organizationId","siteId",type,"categoryId",description,"amountKurus","businessDate",method,reference,"actorId","idempotencyKey","requestHash") SELECT $1||'e'||m||'x'||i,$2,$3,CASE WHEN i%3=0 THEN 'EXPENSE' ELSE 'INCOME' END::"FinancialEntryType",CASE WHEN i%3=0 THEN $4 ELSE $5 END,'Sentetik ölçüm',2000,make_date(2026,m,15),'CASH','',$1,gen_random_uuid()::text,'synthetic' FROM generate_series(1,$6::int) i CROSS JOIN generate_series(5,10) m`,id,org.id,site.id,category.id,income.id,units);
  await db.$executeRawUnsafe(`INSERT INTO "FinancialEntryReversal" (id,"organizationId","siteId","entryId","amountKurus",reason,"actorId","idempotencyKey","createdAt") SELECT $1||'er'||m||'x'||i,$2,$3,$1||'e'||m||'x'||i,2000,'Sentetik ters kayıt',$1,gen_random_uuid()::text,make_date(2026,m,20)::timestamp FROM generate_series(1,$4::int) i CROSS JOIN generate_series(5,10) m WHERE i%20=0`,id,org.id,site.id,units);
  await db.$executeRawUnsafe('ANALYZE');
  const debt={organizationId:org.id,siteId:site.id,period:'2026-10'};const movement={organizationId:org.id,siteId:site.id,month:'2026-10'};
  const measurements:Record<string,unknown>={units,charges:units*6,movementRowsPerMonth:units*2+Math.floor(units/10)+Math.floor(units/20)};
  for(const [name,oldFn,newFn] of [
   ['debtFirst',()=>before.debtReport(debt),()=>api.debtReport(debt)],
   ['debtDeep',()=>before.debtReport({...debt,page:Math.max(1,Math.ceil(units/25)-1)}),()=>api.debtReport({...debt,page:Math.max(1,Math.ceil(units/25)-1)})],
   ['movementFirst',()=>before.movementReport(movement),()=>api.movementReport(movement)],
   ['movementDeep',()=>before.movementReport({...movement,page:Math.max(1,Math.floor(units*2/25)-1)}),()=>api.movementReport({...movement,page:Math.max(1,Math.floor(units*2/25)-1)})],
  ] as const){
   const coldOld=await timed(async()=>await oldFn()),coldNew=await timed(async()=>await newFn());assert.deepEqual(coldOld.value.summary,coldNew.value.summary);assert.deepEqual(coldOld.value.rows.map(r=>r.id),coldNew.value.rows.map(r=>r.id));
   const a:number[]=[],b:number[]=[];for(let i=0;i<3;i++){a.push((await timed(async()=>await oldFn())).ms);b.push((await timed(async()=>await newFn())).ms);}
   measurements[name]={firstBeforeMs:coldOld.ms,firstAfterMs:coldNew.ms,warmBeforeMs:median(a),warmAfterMs:median(b),beforeSamples:a,afterSamples:b};
   if(units===10000&&name.endsWith('First'))for(const [label,fn] of [['before',oldFn],['after',newFn]] as const){capture.length=0;await fn();const queries=[...capture];for(const q of queries){const plan=await db.$queryRawUnsafe('EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) '+q.query,...JSON.parse(q.params));plans.push({name,label,plan});}}
  }
  const oldCompare=async()=>{const values=[];for(let m=5;m<=10;m++)values.push((await before.movementReport({...movement,month:'2026-'+String(m).padStart(2,'0')})).summary);return values;};
  const oldTimes:number[]=[],newTimes:number[]=[];for(let i=0;i<3;i++){oldTimes.push((await timed(oldCompare)).ms);newTimes.push((await timed(()=>api.monthlyComparison({...movement,months:6}))).ms);}measurements.comparison={sequentialBaselineMs:median(oldTimes),groupedMs:median(newTimes),beforeSamples:oldTimes,afterSamples:newTimes};
  for(const [name,fn] of [['debtCsv',()=>api.exportDebtCsv(debt)],['movementCsv',()=>api.exportMovementCsv(movement)]] as const){const rss=process.memoryUsage().rss;let peak=rss;const interval=setInterval(()=>{peak=Math.max(peak,process.memoryUsage().rss);},10);try{const result=await timed(fn);measurements[name]={ms:result.ms,rows:result.value.rows,bytes:result.value.size,rssBeforeMiB:rss/1048576,sampledPeakRssMiB:peak/1048576,sampledRssDeltaMiB:(peak-rss)/1048576};await result.value.dispose();}finally{clearInterval(interval);}}
  results.push(measurements);
 }
 await mkdir('docs/performance',{recursive:true});await writeFile('docs/performance/s03d-measurements.json',JSON.stringify({environment:{node:process.version,cpuAvailable:availableParallelism(),postgres:settings,cache:'First call is not a guaranteed cold cache; fixture insertion/ANALYZE warmed PostgreSQL. Three warmed samples, median. No other intentional writers.'},results},null,2)+'\n');await writeFile('docs/performance/s03d-explain.json',JSON.stringify(plans,null,2)+'\n');
 console.log(JSON.stringify(results,null,2));
}
main().finally(async()=>{await db.$disconnect();for(const path of temporary)await unlink(path).catch(()=>{});}).catch(error=>{console.error(error);process.exitCode=1;});
