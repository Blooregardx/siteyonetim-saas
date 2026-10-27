"use client";
import { useActionState, useState } from "react";
import { save } from "@/app/panel/actions";
import { reversalReasons } from "@/lib/reversals";
import { formatMoney } from "@/lib/finance";
export function ReversalForm({siteId,paymentId,amountKurus,idempotencyKey}:{siteId:string;paymentId:string;amountKurus:number;idempotencyKey:string}) {
 const [confirm,setConfirm]=useState(false);
 const [reason,setReason]=useState<keyof typeof reversalReasons>("ENTRY_ERROR");
 const [state,action,pending]=useActionState(save,{message:""});
 if(!confirm) return <div><label>Gerekçe<select aria-label="Ters kayıt gerekçesi" value={reason} onChange={e=>setReason(e.target.value as keyof typeof reversalReasons)}>{Object.entries(reversalReasons).map(([code,label])=><option key={code} value={code}>{label}</option>)}</select></label><button type="button" onClick={()=>setConfirm(true)}>Ters kayıt oluştur</button></div>;
 return <form action={action} aria-label="Ters kayıt onayı"><p>{formatMoney(amountKurus)} tutarındaki tahsilatın tamamı ters kaydedilecek. Gerekçe: {reversalReasons[reason]}. Orijinal kayıt korunur. Bu işlem banka veya nakit iadesi yapmaz.</p>{Object.entries({operation:"reversal",siteId,paymentId,reasonCode:reason,idempotencyKey,confirmed:"yes"}).map(([name,value])=><input key={name} type="hidden" name={name} value={value}/>)}<button disabled={pending}>{pending ? "İşleniyor…" : "Onayla ve ters kaydet"}</button><button type="button" disabled={pending} onClick={()=>setConfirm(false)}>Vazgeç</button><p role="status">{state.message}</p></form>;
}
