import Link from "next/link";
import { requireSession } from "@/lib/session";
import { MemberForm } from "@/components/member-form";
export default async function Page({searchParams}:{searchParams:Promise<{token?:string}>}) {
 await requireSession();const {token}=await searchParams;
 return <div className="auth panel"><h1>Organizasyon daveti</h1><p>Davet edilen e-posta adresiyle kayıt ve giriş yapın; önce e-postanızı doğrulayın. Davetler 48 saat geçerlidir.</p><Link href="/eposta-dogrula">E-posta doğrulama</Link>{token&&<MemberForm values={{operation:"accept",token}}>Daveti kabul et</MemberForm>}<Link href="/panel">Panele dön</Link></div>;
}
