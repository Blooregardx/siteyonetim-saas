import Link from "next/link";
import { AuthForm } from "@/components/auth-form";
export default async function Page({ searchParams }: { searchParams: Promise<{ token?: string }> }) {
 const { token } = await searchParams;
 return <div className="auth panel"><Link className="brand" href="/">SiteYönetim</Link><h1>Giriş yap</h1><AuthForm mode="login" token={token}/><nav><Link href="/giris">Giriş</Link><Link href="/kayit">Kayıt</Link><Link href="/sifre-sifirla">Şifremi unuttum</Link><Link href="/demo">Demo panel</Link></nav></div>;
}
