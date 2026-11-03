// SPDX-License-Identifier: AGPL-3.0-only
/** Read-only bounded-work proof after capacity E2E. Never creates/resets fixtures. */
import assert from 'node:assert/strict';
import { PrismaClient } from '@prisma/client';
import { management } from '../src/lib/management';
const base=process.env.TEST_DATABASE_URL;
if(!base||process.env.DATABASE_URL!==base)throw Error('Matching isolated test URLs required');
const url=new URL(base);if(!['localhost','127.0.0.1'].includes(url.hostname)||url.pathname!='/siteyonetim_test')throw Error('Isolated test database required');
url.searchParams.set('connection_limit','1');
const db=new PrismaClient({datasourceUrl:url.toString(),log:[{level:'query',emit:'event'}]});
let captured:{query:string;params:unknown[]}|undefined;
db.$on('query',event=>{if(event.query.startsWith('WITH scoped AS')&&event.query.includes('filtered AS MATERIALIZED'))captured={query:event.query,params:JSON.parse(event.params)};});
function literal(value:unknown){if(typeof value==='string')return "'"+value.replaceAll("'","''")+"'";if(typeof value==='boolean')return value?'TRUE':'FALSE';if(typeof value==='number'&&Number.isSafeInteger(value))return String(value);throw Error('Unexpected diagnostic parameter type');}
type Node={ 'Node Type':string;'Relation Name'?:string;'Actual Loops'?:number;Plans?:Node[] };
function readsPayments(node:Node):boolean{return node['Relation Name']==='Payment'||!!node.Plans?.some(readsPayments);}
function balanceLoops(node:Node):number[]{return [...(node['Node Type']==='Aggregate'&&readsPayments(node)?[node['Actual Loops']??0]:[]),...(node.Plans??[]).flatMap(balanceLoops)];}
async function main(){
 const site=await db.site.findFirstOrThrow({where:{name:'S03E synthetic 10000'},include:{organization:{include:{memberships:true}}}});
 const api=management(db,async()=>({userId:site.organization!.memberships[0].userId}));const result=await api.siteChargesPage(site.id,{page:2});assert.equal(result.total,60000);assert.equal(result.rows.length,25);
 assert.ok(captured);const {query,params}=captured;
 await db.$executeRawUnsafe('PREPARE f10_bounded_plan AS '+query);
 const execute='EXECUTE f10_bounded_plan('+params.map(literal).join(',')+')';
 for(const mode of ['force_custom_plan','force_generic_plan']){
  await db.$executeRawUnsafe('SET plan_cache_mode='+mode);
  // Existing S03-E service target is 3 seconds, not a relaxed E2E timeout.
  await db.$executeRawUnsafe("SET statement_timeout='3s'");
  const plans=await db.$queryRawUnsafe<{'QUERY PLAN':{Plan:Node;'Execution Time':number}[]}[]>('EXPLAIN (ANALYZE,BUFFERS,FORMAT JSON) '+execute);
  const plan=plans[0]['QUERY PLAN'][0];const loops=balanceLoops(plan.Plan);assert.ok(loops.length>0);assert.ok(loops.every(count=>count===25));
  console.log(JSON.stringify({mode,total:result.total,pageRows:result.rows.length,paymentAggregateLoops:loops,executionMs:plan['Execution Time']}));
 }
}
main().finally(()=>db.$disconnect()).catch(()=>{console.error('F10 bounded query-plan verification failed; inspect the isolated test privately');process.exitCode=1;});
