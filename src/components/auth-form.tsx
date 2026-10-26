"use client";
import { useActionState } from "react";
import { authenticate, resetPassword } from "@/app/auth-actions";
export function AuthForm({ mode, token }: { mode: "login" | "register" | "reset"; token?: string }) {
  const [state, action, pending] = useActionState(mode === "reset" ? resetPassword : authenticate, { message: "" });
  return <form action={action}><input type="hidden" name="mode" value={mode}/>{token && <input type="hidden" name="token" value={token}/>}
    {mode === "register" && <label>Ad soyad<input name="name" required maxLength={100} autoComplete="name"/></label>}
    {!token && <label>E-posta<input name="email" type="email" required autoComplete="email"/></label>}
    {(mode !== "reset" || token) && <label>Parola (en az 12 karakter)<input name="password" type="password" required minLength={12} maxLength={128} autoComplete={mode === "login" ? "current-password" : "new-password"}/></label>}
    <button disabled={pending}>{pending ? "İşleniyor…" : mode === "register" ? "Kayıt ol" : mode === "login" ? "Giriş yap" : "Parolayı yenile"}</button><p role="status">{state.message}</p></form>;
}
