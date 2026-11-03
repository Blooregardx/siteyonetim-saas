import Link from 'next/link';
import { redirect } from 'next/navigation';
import { db } from '@/lib/db';
import { requireSession, verifySession } from '@/lib/session';
import { onboarding } from '@/lib/onboarding';
import { OnboardingForm } from '@/components/onboarding-form';
export default async function SetupPage() {
 const session=await requireSession();
 const user=await db.user.findUniqueOrThrow({where:{id:session.userId},select:{emailVerifiedAt:true}});
 if(!user.emailVerifiedAt)redirect('/eposta-dogrula');
 const state=await onboarding(db,verifySession).progress();
 const completed=!!state.site;
 return <div className="auth panel setup"><Link href="/" className="brand">SiteYönetim</Link><h1>İlk kurulum</h1><p>Hoş geldiniz. Hesabınız doğrulandı. Yönetiminizi ve ilk apartmanınızı birkaç adımda hazırlayın.</p>
 <ol className="setup-steps" aria-label="Kurulum adımları"><li>Hesap doğrulandı</li><li>Yönetim türü</li><li>Organizasyon</li><li>İlk apartman/site</li><li>Tamamlandı</li></ol>
 <p>Bu sihirbaz uygulama içindeki başlangıcı kolaylaştırır. Sunucu, HTTPS ve e-posta altyapısını operatör hazırlar.</p>
 {completed?<><h2>Kurulum tamamlandı</h2><p>Organizasyon: <strong>{state.organization!.name}</strong></p><p>Apartman/site: <strong>{state.site!.name}</strong></p><Link className="setup-primary" href={`/panel?org=${state.organization!.id}&site=${state.site!.id}`}>Yönetim paneline geç</Link></>:state.organization?<><h2>{state.organization.name}</h2><p>Organizasyonunuz hazır. İlk apartman veya sitenizle devam edin.</p><OnboardingForm organizationId={state.organization.id}/></>:state.existingAccess?<><h2>Mevcut üyeliğiniz var</h2><p>Yetkileriniz değiştirilmedi. Davetiniz veya mevcut apartman erişiminiz için yönetim panelini kullanın.</p><Link href="/panel">Yönetim paneline geç</Link></>:<><p>Bir davet bekliyorsanız davet bağlantısıyla devam edebilirsiniz. Yeni bir yönetim başlatmak istiyorsanız aşağıdaki adımları kullanın.</p><OnboardingForm/></>}
 <nav><Link href="/panel">Yönetim paneline dön</Link></nav></div>;
}
