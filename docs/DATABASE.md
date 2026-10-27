# Veritabanı ve geçiş

Üç eklemeli migration vardır. Son migration User.passwordHash (nullable), Session, PasswordReset, AuthAttempt ve Payment.method ekler. Eski kullanıcılarda parola otomatik üretilmez; doğrulanmış posta kurtarma kanalı veya kontrollü hesap sahipliği doğrulaması gerekir. Geçerli parola olmadan eski hesabın girişine izin verilmez. Nakit/havale yöntemi saklanır; eski ödemeler CASH varsayımı taşır, bu geçmiş verinin gerçek ödeme yönteminin kanıtı değildir.

Session ve PasswordReset ham token yerine SHA-256 özetini saklar. Session 7 gün, reset 30 dakika geçerlidir. Süresi dolmuş oturumlar doğrulanmaz. Eski token/limit satırları için periyodik temizlik operasyonu kurulmalıdır.

## Eski Site.organizationId geçişi

Alan nullable korunmuştur; yetim kayıtlar silinmez veya tahmine dayalı şirkete atanmaz. Yeni siteler üyeliği doğrulanmış organizasyonda açılır. Geçiş için önce yedek alınmalı, site ADMIN üyeliği ve yönetim sözleşmesi doğrulanmalı, site→organizasyon eşlemesi onaylı operatör listesiyle hazırlanmalıdır. Transaction içinde yalnızca organizationId NULL olan beklenen satırlar güncellenmeli; satır sayısı denetlenmeli, üyelikler ve borç/ödeme kimlikleri korunmalıdır. Tüm siteler doğrulanmadan NOT NULL uygulanmamalıdır. Eski doğrudan üyelik servis düzeyinde korunur; yeni organizasyon panelinde otomatik gösterilmez.

## Kişi tasarımı

Mevcut Occupancy isim kopyası ve OWNER/TENANT ilişkisi taşır; otomatik kullanıcı hesabı veya erişim hakkı oluşturmaz. Gelecek eklemeli model: organizasyon kapsamlı Person, isteğe bağlı doğrulanmış User bağı, tarihli Ownership ve Occupancy.personId. Bir Person birden çok daireyle ilişkilenebilir. İsim eşitliği kişi birleştirmek için yeterli değildir. Önce nullable personId eklenmeli; operatör doğrulamalı eşleme ve tarih kontrolleri sonrası eski isim alanı kaldırılması ayrı migration olmalıdır. Mülkiyet ve fiili ikamet dönemleri ayrı tutulmalıdır. Bu aşamada kişi birleştirme veya veri kaybettiren dönüşüm uygulanmadı.

## S01-C eklemeli migration

`202610290001_security_audit`: User.emailVerifiedAt nullable (eski kullanıcılar doğrulanmaz), EmailVerification, organizasyon/rol kapsamlı Invitation ve append-only AuditLog ekler. Mevcut finans tabloları veya satırları değiştirilmez. Tokenlar yalnız özetle saklanır. AuditLog üzerindeki UPDATE/DELETE/TRUNCATE trigger'ı DDL yetkisi olmayan uygulama rollerinin geçmişi değiştirmesini engeller; actor/tenant/site/entity alanları geçmiş kimlik referansları olarak kalır. Migration sahibi ve uygulama rolü ayrımı SECURITY-S01C.md içindedir. Migration geri almak için tabloları veya audit geçmişini düşürmek yerine ileri düzeltme hazırlanmalıdır.

## S01-D tam ters kayıt

`202610300001_payment_reversals`: ReversalReason enum, Payment üzerindeki bileşik unique indeksler, PaymentReversal ve immutable Payment/Reversal trigger'ları. `202610300002_reversal_relation_key`: Prisma'nın bire bir bileşik ilişki doğrulaması için reversal tarafında bileşik unique indeks. İlk migration'ın uygulanmış SQL'i değiştirilmeden ikinci eklemeli migration kullanıldı. Eski finans verileri korunur; ters kayıt geriye dönük üretilmez.

Tutar eşitliği ve site kapsamı üç alanlı FK, tek ters kayıt paymentId unique, tekrar anahtarı site/key unique, gerekçe enum ve pozitif tutar/UUID CHECK ile korunur. Finans fixture'ları test bitiminde artık silinmez; yalnız izole test DB'de kalır. Tüm test DB'sinin yeniden oluşturulması ancak açıkça izole geliştirme/test işletimiyle yapılabilir; üretimde reset yoktur.
