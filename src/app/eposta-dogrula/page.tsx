import Link from "next/link";
import { requireSession } from "@/lib/session";
import { EmailForm } from "@/components/email-form";
import { logout } from "@/app/auth-actions";
export default async function Page({searchParams}:{searchParams:Promise<{token?:string}>}) {
 await requireSession(); const {token}=await searchParams;
 return <div className="auth panel"><h1>E-posta doğrulama</h1><p>Organizasyon ve finans işlemleri için e-posta sahipliğinizi doğrulayın. Bağlantılar 1 saat geçerlidir; hesabınızla giriş yapmış olmalısınız.</p><EmailForm token={token}/><h2>E-posta adresini değiştir</h2><p>Yeni adres doğrulanana kadar mevcut adresiniz korunur.</p><EmailForm change/><Link href="/panel">Yönetim paneline geç</Link><form action={logout}><button>Çıkış yap</button></form></div>;
}
