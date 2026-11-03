'use client';
import Link from 'next/link';
import { useActionState, useState } from 'react';
import { setup } from '@/app/kurulum/actions';
export function OnboardingForm({organizationId}:{organizationId?:string}) {
 const [state,action,pending]=useActionState(setup,{message:'',errors:{}});
 const [step,setStep]=useState(organizationId?4:2);
 const [kind,setKind]=useState('INDIVIDUAL');
 const error=(field:string)=>state.errors[field]?<span id={`${field}-error`} role="alert">{state.errors[field]}</span>:null;
 return <form action={action} className="setup-form">
  <input type="hidden" name="operation" value={organizationId?'site':'organization'}/>
  {organizationId?<input type="hidden" name="organizationId" value={organizationId}/>:<input type="hidden" name="kind" value={kind}/>}
  <fieldset disabled={pending}>
   <legend>Adım {step} / 5 — {step===2?'Yönetim türü':step===3?'Organizasyon':'İlk apartman veya site'}</legend>
   {step===2?<><p>Yönetiminize uygun türü seçin. Her iki seçenek de ücretsizdir.</p><label><input type="radio" checked={kind==='INDIVIDUAL'} onChange={()=>setKind('INDIVIDUAL')}/>Bireysel apartman/site yöneticisi</label><label><input type="radio" checked={kind==='COMPANY'} onChange={()=>setKind('COMPANY')}/>Profesyonel yönetim şirketi</label><button type="button" onClick={()=>setStep(3)}>Devam</button></>:<>
    <label htmlFor="setup-name">{organizationId?'Apartman/site adı':'Organizasyon adı'}</label><input id="setup-name" name="name" required maxLength={200} aria-invalid={!!state.errors.name} aria-describedby={state.errors.name?'name-error':undefined}/>{error('name')}
    {organizationId&&<><label htmlFor="setup-address">Adres (isteğe bağlı)</label><textarea id="setup-address" name="address" maxLength={500} aria-invalid={!!state.errors.address} aria-describedby={state.errors.address?'address-error':undefined}/>{error('address')}<label htmlFor="setup-description">Açıklama (isteğe bağlı)</label><textarea id="setup-description" name="description" maxLength={2000} aria-invalid={!!state.errors.description} aria-describedby={state.errors.description?'description-error':undefined}/>{error('description')}</>}
    {step===3?<button type="button" onClick={()=>setStep(2)}>Geri</button>:<Link href="/panel">Geri — yönetim paneli</Link>}
    <button type="submit" disabled={pending}>{pending?'Kaydediliyor…':organizationId?'Kurulumu tamamla':'Organizasyonu oluştur ve devam et'}</button>
   </>}
  </fieldset><p role="status">{state.message}</p>
 </form>;
}
