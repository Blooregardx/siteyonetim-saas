'use server';
import { z } from 'zod';
import { redirect } from 'next/navigation';
import { revalidatePath } from 'next/cache';
import { db } from '@/lib/db';
import { verifySession } from '@/lib/session';
import { onboarding } from '@/lib/onboarding';
export type SetupResult = {message:string;errors:Record<string,string>};
export async function setup(_state:SetupResult,form:FormData):Promise<SetupResult> {
 const data=Object.fromEntries([...form.entries()].filter(([key])=>!key.startsWith('$ACTION_')));
 const {operation,...input}=data;
 try {
  const api=onboarding(db,verifySession);
  if(operation==='organization')await api.createOrganization(input);
  else if(operation==='site')await api.createSite(input);
  else return {message:'Geçersiz işlem. Sayfayı yenileyin.',errors:{}};
 } catch(error) {
  if(error instanceof z.ZodError) return {message:'Alanları kontrol edin.',errors:Object.fromEntries(error.issues.map(i=>[String(i.path[0]),i.path[0]==='name'?'Ad gerekli; en fazla 200 karakter girin.':i.path[0]==='address'?'Adres en fazla 500 karakter olabilir.':i.path[0]==='description'?'Açıklama en fazla 2000 karakter olabilir.':'Seçimi kontrol edin.']))};
  if(error instanceof Error && error.message==='UNAUTHENTICATED')redirect('/giris');
  if(error instanceof Error && error.message==='EMAIL_UNVERIFIED')redirect('/eposta-dogrula');
  return {message:'İşlem tamamlanamadı. Oturumunuzu ve güncel yetkinizi kontrol edip sayfayı yenileyin.',errors:{}};
 }
 revalidatePath('/kurulum');revalidatePath('/panel');redirect('/kurulum');
}
