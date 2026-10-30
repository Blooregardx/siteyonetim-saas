import { validateDashboardParams } from '@/lib/dashboard-validation';
import { invalidDashboardRequest } from '@/lib/dashboard-errors';
import Link from 'next/link';
import { notFound } from 'next/navigation';
import { db } from '@/lib/db';
import { requireSession,verifySession } from '@/lib/session';
import { management } from '@/lib/management';
import { CollectionForm } from '@/components/collection-form';
import { ReversalForm } from '@/components/reversal-form';
import { Pager } from '@/components/dashboard-navigation';
import { formatMoney } from '@/lib/finance';
import { reversalReasons } from '@/lib/reversals';
import { paymentStatuses } from '@/lib/reports';
export default async function Page({params,searchParams}:{params:Promise<{chargeId:string}>;searchParams:Promise<Record<string,string|undefined>>}){
 await requireSession();const {chargeId}=await params;const rawParams=await searchParams;const query=(()=>{try{return validateDashboardParams(rawParams,['site','page']);}catch{notFound();}})();if(!query.site)notFound();const result=await management(db,verifySession).chargeDetails(query.site,chargeId,query.page).catch(e=>{if(invalidDashboardRequest(e))notFound();throw e;});const {site,charge:c,payments,role}=result;
 return <main className="report-page panel" style={{margin:'24px auto',width:'100%'}}><Link prefetch={false} href={`/panel?org=${site.organizationId??''}&site=${site.id}`}>Panele ve tüm aidat geçmişine dön</Link><h1>Daire {c.number} · {c.period}</h1><p>{site.name} · {c.block} · {paymentStatuses[c.status]}</p><p>Tahakkuk: {formatMoney(c.amountKurus)} · Brüt: {formatMoney(c.grossKurus)} · Ters kayıt: {formatMoney(c.reversedKurus)} · Net tahsilat: {formatMoney(c.netKurus)} · Kalan: {formatMoney(c.remainingKurus)} · {c.status==='PAID'?'Ödendi':c.status==='PARTIAL'?'Kısmi ödeme':'Ödenmedi'}</p>{c.remainingKurus>0&&<CollectionForm key={c.id} siteId={site.id} chargeId={c.id} remainingKurus={c.remainingKurus} partialPaymentsAllowed={site.partialPaymentsAllowed} idempotencyKey={crypto.randomUUID()}/>}
 <h2>Tahsilat geçmişi ve tam ters kayıtlar</h2><p>Her sayfada en fazla 25 tahsilat. Güncel bakiye bütün geçmiş üzerinden hesaplanır.</p>{!payments.length&&<p>Bu sayfada tahsilat bulunamadı.</p>}{payments.map(p=><section key={p.id} aria-label="Tahsilat kaydı"><p>{p.paidAt.toLocaleDateString('tr-TR',{timeZone:'Europe/Istanbul'})} · {formatMoney(p.amountKurus)} · {p.method==='CASH'?'Nakit':'Havale/EFT'}</p>{p.reversal?<p role="note">Ters kaydedildi · {formatMoney(p.reversal.amountKurus)} · {reversalReasons[p.reversal.reasonCode]} · {p.reversal.createdAt.toLocaleString('tr-TR',{timeZone:'Europe/Istanbul'})} · İşlemi yapan: {p.reversal.actor.name}</p>:role==='ADMIN'&&<ReversalForm siteId={site.id} paymentId={p.id} amountKurus={p.amountKurus} idempotencyKey={crypto.randomUUID()}/>}</section>)}<Pager path={`/panel/aidatlar/${c.id}`} params={query} name="page" {...result}/><Link prefetch={false} href="/raporlar">Borç ve Tahsilat Raporları</Link></main>;
}
