"use client";
import { useState } from 'react';
import { DataForm } from './data-form';
export function ManualReversalForm({siteId,entryId,idempotencyKey}:{siteId:string;entryId:string;idempotencyKey:string}){
 const [open,setOpen]=useState(false);
 return open?<div><p>Orijinal kayıt korunur. Bu işlem gerçek banka veya nakit iadesi yapmaz.</p><DataForm operation="financial-reversal" values={{siteId,entryId,idempotencyKey}}><label>Ters kayıt gerekçesi<textarea name="reason" required minLength={3} maxLength={1000}/></label><label><input type="checkbox" name="confirmed" value="yes" required/>Ters kaydı onaylıyorum</label></DataForm><button onClick={()=>setOpen(false)}>Vazgeç</button></div>:<button onClick={()=>setOpen(true)}>Manuel işlemi ters kaydet</button>;
}
