# Teknik güvenlik özeti

Bildirim ve destek sınırları için [kök politika](../SECURITY.md), ayrıntılı rol/SMTP/token/işletim gereksinimleri için [SECURITY-S01C](SECURITY-S01C.md) geçerlidir.

Uygulananlar: scrypt parola türetimi; özetlenmiş 256 bit oturum/tokenlar; HttpOnly/SameSite=Lax, üretimde Secure ve __Host- çerezi; Next.js Server Actions origin/POST denetimi; Zod doğrulama; parametreli SQL; doğrulanmış kullanıcı ve organizasyon yetkisi; işlemle atomik audit; finans satır kilitleri/idempotency ve tam ters kayıt. Parola yenileme ve adres değişimi oturumları iptal eder. Demo ayrıdır.

Global giriş limiti kaldırılmıştır. E-posta başına 10/15 dakika giriş/kayıt/kurtarma, kullanıcı bazlı doğrulama yeniden gönderim sınırı vardır. Hedefli kilitleme ve rastgele adreslerle yük saldırısı riski sürer. MFA, oturum yönetim ekranı ve güvenilir edge/bot koruması yoktur.

SMTP TLS ve HTTPS APP_URL zorunludur; düz protokol istisnası yalnız izole loopback test koşullarındadır. Gerçek SMTP teslimi veya sağlayıcı DB rol kurulumu test başarısından çıkarılamaz. Runtime DB sırrı, DBA yetkisi, yedekler ve loglar ayrı güvenlik sınırlarıdır.

E-posta doğrulaması, davet/rol yönetimi, audit, token temizliği ve tam ters kayıt uygulanmıştır; bunlar bekleyen özellik değildir. Gerçek para iadesi ve kısmi ters kayıt yoktur. Canlı işletim için [kurulum rehberi](SELF-HOSTING.md) ve [ertelenmiş operasyonlar](DEFERRED-CLOUD-OPERATIONS.md) incelenmelidir.
