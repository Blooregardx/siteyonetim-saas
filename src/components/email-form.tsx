"use client";
import { useActionState } from "react";
import { emailAction } from "@/app/auth-actions";
export function EmailForm({token, change = false}:{token?:string;change?:boolean}) {
 const [state,action,pending] = useActionState(emailAction,{message:""});
 return <form action={action}>{token ? <input type="hidden" name="token" value={token}/> : change && <><label>Yeni e-posta<input type="email" name="email" required/></label><label>Mevcut parola<input type="password" name="password" required maxLength={128} autoComplete="current-password"/></label></>}<button disabled={pending}>{pending ? "İşleniyor…" : token ? "E-postayı doğrula" : change ? "Yeni adresi doğrula" : "Bağlantıyı yeniden gönder"}</button><p role="status">{state.message}</p></form>;
}
