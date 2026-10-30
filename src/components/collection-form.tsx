"use client";
import { useState } from 'react';
import { DataForm } from './data-form';
import { formatMoney } from '@/lib/finance';
export function CollectionForm({siteId,chargeId,remainingKurus,partialPaymentsAllowed,idempotencyKey}:{siteId:string;chargeId:string;remainingKurus:number;partialPaymentsAllowed:boolean;idempotencyKey:string}){
 const full=`${Math.floor(remainingKurus/100)}.${String(remainingKurus%100).padStart(2,'0')}`;
 const [fullBalance,setFullBalance]=useState(!partialPaymentsAllowed);
 const [amount,setAmount]=useState(partialPaymentsAllowed?'':full);
 return <DataForm operation="payment" values={{siteId,chargeId,idempotencyKey,fullBalance:String(!partialPaymentsAllowed||fullBalance)}}><p>Kalan borç: {formatMoney(remainingKurus)}{!partialPaymentsAllowed?' · Kısmi ödeme kapalı; kalan tutarın tamamı alınır.':''}</p><label>Tahsilat (TL)<input name="amount" inputMode="decimal" required readOnly={!partialPaymentsAllowed} value={partialPaymentsAllowed?amount:full} onChange={e=>{setAmount(e.target.value);setFullBalance(false);}}/></label><button type="button" onClick={()=>{setAmount(full);setFullBalance(true);}}>Kalan Borcun Tamamını Tahsil Et</button><label>Yöntem<select name="method"><option value="CASH">Nakit</option><option value="TRANSFER">Havale/EFT</option></select></label></DataForm>;
}
