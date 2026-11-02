import { PrismaClient } from '@prisma/client';
import { management } from '../../src/lib/management';
export async function capacityFixture(db:PrismaClient,size:100|1000|10000){
 const existing=await db.site.findFirst({where:{name:'S03E synthetic '+size},orderBy:{createdAt:'desc'},include:{organization:{include:{memberships:true}}}});
 if(existing)return {siteId:existing.id,organizationId:existing.organizationId!,userId:existing.organization!.memberships[0].userId};
 const id='s03e'+crypto.randomUUID().replaceAll('-','');await db.user.create({data:{id,email:id+'@example.invalid',name:'Sentetik kapasite',emailVerifiedAt:new Date()}});const api=management(db,async()=>({userId:id}));const org=await api.createOrganization('S03E sentetik '+size,'COMPANY'),site=await api.createSite(org.id,'S03E synthetic '+size),block=await api.createBlock(site.id,'A');
 await db.$executeRawUnsafe(`INSERT INTO "Unit" (id,"siteId","blockId",number) SELECT $1||'u'||lpad(i::text,5,'0'),$2,$3,i::text FROM generate_series(1,$4::int) i`,id,site.id,block.id,size);
 await db.$executeRawUnsafe(`INSERT INTO "Charge" (id,"siteId","unitId",period,"amountKurus","dueDate") SELECT $1||'c'||m||'x'||lpad(i::text,5,'0'),$2,$1||'u'||lpad(i::text,5,'0'),'2026-'||lpad(m::text,2,'0'),20000,make_date(2026,m,1) FROM generate_series(1,$3::int) i CROSS JOIN generate_series(5,10) m`,id,site.id,size);
 await db.$executeRawUnsafe(`INSERT INTO "Payment" (id,"siteId","chargeId","amountKurus","paidAt","idempotencyKey",method) SELECT $1||'p'||m||'x'||lpad(i::text,5,'0'),$2,$1||'c'||m||'x'||lpad(i::text,5,'0'),10000,make_date(2026,m,15)::timestamp,$1||'key'||m||'x'||i,'CASH' FROM generate_series(1,$3::int) i CROSS JOIN generate_series(5,10) m`,id,site.id,size);
 await db.$executeRawUnsafe(`INSERT INTO "PaymentReversal" (id,"siteId","paymentId","amountKurus","reasonCode","actorId","idempotencyKey","createdAt") SELECT $1||'pr'||m||'x'||i,$2,$1||'p'||m||'x'||lpad(i::text,5,'0'),10000,'ENTRY_ERROR',$1,gen_random_uuid()::text,make_date(2026,m,20)::timestamp FROM generate_series(1,$3::int) i CROSS JOIN generate_series(5,10) m WHERE i%10=0`,id,site.id,size);
 return {siteId:site.id,organizationId:org.id,userId:id};
}
