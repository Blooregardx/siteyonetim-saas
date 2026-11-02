"use server";
import { management } from '@/lib/management';
import { db } from '@/lib/db';
import { verifySession } from '@/lib/session';
import { BulkInput } from '@/lib/bulk-charges';
import { revalidatePath } from 'next/cache';
export async function bulkAction(input:BulkInput, confirmation?:{snapshot:string;key:string}) {
 try {
  const api=management(db,verifySession);
  if(!confirmation)return {preview:await api.previewBulkCharges(input)};
  const result=await api.commitBulkCharges(input,confirmation.snapshot,confirmation.key);
  revalidatePath('/panel');return {result};
 } catch(error) {
  const code=error instanceof Error?error.message:'';
  return {error:code.startsWith('BULK_CONFLICT:')?'Bu dairelerde mevcut aidat var: '+code.slice(14)+'. Yeni önizleme yapın.':code==='STALE_PREVIEW'?'Daire bilgileri değişti. Yeni önizleme yapın.':code==='IDEMPOTENCY_CONFLICT'?'İşlem anahtarı farklı bilgilerle kullanılmış. Yeni önizleme yapın.':['FORBIDDEN','UNAUTHENTICATED'].includes(code)?'Bu işlem için yetkiniz veya geçerli oturumunuz yok.':'İşlem tamamlanamadı. Alanları kontrol edin ve yeni önizleme yapın.'};
 }
}
export async function searchBulkUnits(siteId:string,query:string,page:number,selected?:string[]){
 try{const api=management(db,verifySession);const result=selected?await api.selectedUnitsPage(siteId,selected,page):await api.siteUnitsPage(siteId,{q:query,page});return {rows:result.rows.map(u=>({id:u.id,number:u.number,block:u.block.name})),total:result.total,page:result.page};}
 catch{return {error:'Daireler yüklenemedi. Yetkinizi ve aramayı kontrol edin.'};}
}
