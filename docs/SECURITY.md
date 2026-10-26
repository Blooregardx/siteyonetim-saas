# Güvenlik

Parolalar rastgele salt ile Node scrypt üzerinden türetilir; ham parola saklanmaz. 256 bit rastgele oturum tokenı HttpOnly, SameSite=Lax, üretimde Secure ve __Host- önekli çerezde tutulur; veritabanında yalnızca özeti vardır. Üretim HTTPS gerektirir. Çıkış oturumu siler; parola yenileme tüm oturumları iptal eder. Reset tokenı tek kullanımlıdır ve transaction içinde tüketilir. İmzalanmış istemci kullanıcı kimliği veya istemciden gelen userId kullanılmaz; SessionVerifier doğrudan veritabanı oturumuna bağlıdır. Özel signing secret gerekmez; tokenlar sunucuda rastgele üretilir.

Next.js Server Actions POST/origin-host denetimi ve kapalı action protokolü kullanılır; allowedOrigins genişletilmedi. React metni escape eder, Prisma parametreli sorgu üretir; kilit ve limit sorguları tagged template ile parametrelidir. Formlar Zod ve servis katmanında doğrulanır. Hatalarda veritabanı ayrıntıları gösterilmez. Tüm yönetim yazımları servis yetkisi gerektirir; panel de organizasyon üyeliğini doğrular.

Giriş/kayıt e-posta başına 15 dakikada 10; tüm uygulama için 100 giriş/kayıt denemesi sınırı vardır. Kurtarma ayrı limit kullanır. Limiter PostgreSQL upsert ile paylaşımlı ve atomiktir. Bu başlangıç politikası büyük trafik için kaba olup hesap kilitleme/servis engelleme riski taşır; üretimde güvenilir edge IP limiti, alarm ve risk bazlı kontrol eklenmelidir. Proxy'den doğrulanmamış IP başlığına güvenilmez.

SMTP, APP_URL ve MAIL_FROM olmadan kurtarma gönderilmez ve kullanıcıya eksik yapılandırma gösterilir. İzole SMTP test sunucusunda gönderim, tek kullanımlı bağlantı ve oturum iptali Playwright ile doğrulandı; gerçek bulut posta sağlayıcısına teslim doğrulanmadı. APP_URL üretimde HTTPS olmalıdır. Posta ve veritabanı parolaları bulut secret yönetiminde saklanmalı; TLS kapatılmamalıdır.

MFA, e-posta sahiplik doğrulaması, üyelik davetleri, audit log, finansal ters kayıt, oturum yönetim ekranı ve operasyonel izleme henüz yoktur. Uygulama DB hesabı yalnızca gerekli yetkilerle sınırlandırılmalıdır. Bu sürüm canlı üretim onayı değildir.
