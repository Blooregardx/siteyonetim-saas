# Veritabanı ve geçiş

Üç eklemeli migration vardır. Son migration User.passwordHash (nullable), Session, PasswordReset, AuthAttempt ve Payment.method ekler. Eski kullanıcılarda parola otomatik üretilmez; doğrulanmış posta kurtarma kanalı veya kontrollü hesap sahipliği doğrulaması gerekir. Geçerli parola olmadan eski hesabın girişine izin verilmez. Nakit/havale yöntemi saklanır; eski ödemeler CASH varsayımı taşır, bu geçmiş verinin gerçek ödeme yönteminin kanıtı değildir.

Session ve PasswordReset ham token yerine SHA-256 özetini saklar. Session 7 gün, reset 30 dakika geçerlidir. Süresi dolmuş oturumlar doğrulanmaz. Eski token/limit satırları için periyodik temizlik operasyonu kurulmalıdır.

## Eski Site.organizationId geçişi

Alan nullable korunmuştur; yetim kayıtlar silinmez veya tahmine dayalı şirkete atanmaz. Yeni siteler üyeliği doğrulanmış organizasyonda açılır. Geçiş için önce yedek alınmalı, site ADMIN üyeliği ve yönetim sözleşmesi doğrulanmalı, site→organizasyon eşlemesi onaylı operatör listesiyle hazırlanmalıdır. Transaction içinde yalnızca organizationId NULL olan beklenen satırlar güncellenmeli; satır sayısı denetlenmeli, üyelikler ve borç/ödeme kimlikleri korunmalıdır. Tüm siteler doğrulanmadan NOT NULL uygulanmamalıdır. Eski doğrudan üyelik servis düzeyinde korunur; yeni organizasyon panelinde otomatik gösterilmez.

## Kişi tasarımı

Mevcut Occupancy isim kopyası ve OWNER/TENANT ilişkisi taşır; otomatik kullanıcı hesabı veya erişim hakkı oluşturmaz. Gelecek eklemeli model: organizasyon kapsamlı Person, isteğe bağlı doğrulanmış User bağı, tarihli Ownership ve Occupancy.personId. Bir Person birden çok daireyle ilişkilenebilir. İsim eşitliği kişi birleştirmek için yeterli değildir. Önce nullable personId eklenmeli; operatör doğrulamalı eşleme ve tarih kontrolleri sonrası eski isim alanı kaldırılması ayrı migration olmalıdır. Mülkiyet ve fiili ikamet dönemleri ayrı tutulmalıdır. Bu aşamada kişi birleştirme veya veri kaybettiren dönüşüm uygulanmadı.
