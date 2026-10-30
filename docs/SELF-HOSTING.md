# Kendi sunucusunda kurulum ve işletim

Hedef ücretsiz kendi sunucusunda barındırmadır. Lisans AGPL-3.0-only; [tam metin](../LICENSE) ve [yükümlülükler](LICENSING.md) geçerlidir. Erken geliştirme sürümü için teknik yol gösterir, canlı kullanım onayı değildir. Yazılım aboneliği planlanmaz; sunucu/e-posta/alan adı masrafları işletmeciye göre değişebilir. Bu görev herhangi bir servis kurmaz.

## Gereksinimler ve yapılandırma

Node 24, npm, PostgreSQL 17 ve Node sunucusuna HTTPS sağlayan ters proxy gerekir. Prisma 6 korunur. SMTP e-posta doğrulama/parola kurtarma/davet akışları için gereklidir. Eksik SMTP ile demo incelenebilir fakat gerçek yönetim doğrulaması tamamlanmaz.

- DATABASE_URL: ilgili PostgreSQL bağlantısı; gerçek ortamda sertifika doğrulamalı TLS/ağ sınırı ve minimum runtime rolü.
- APP_URL: HTTPS origin; kullanıcı bilgisi, yol, query veya fragment yok.
- SMTP_URL: `smtps://` veya zorunlu STARTTLS ile `smtp://`; gerçek bilgileri secret olarak verin.
- MAIL_FROM: kontrol ettiğiniz gönderici; SMTP teslimi ve SPF/DKIM/DMARC işletmeci tarafından doğrulanır.
- TEST_DATABASE_URL: yalnız izole loopback `siteyonetim_test`; gerçek uygulama veritabanına verilmez.

`.env.example` kopyalanabilir; `.env` public erişime açılmaz/commit edilmez. Compose yalnız localhost'a bağlı geliştirme DB'sidir; örnek parolayı canlı sistemde kullanmayın. Tam uygulama/HTTPS dağıtım Compose'u henüz sunulmuyor.

## Kurulum sırası

1. İncelenmiş commit/sürümü seçin. Önce izole ortamda prova yapın; otomatik seed/demo kullanıcı yoktur.
2. `npm ci` ve `npm run db:generate` çalıştırın.
3. DB/SMTP/APP_URL değişkenlerini güvenli ortamda verin. `npm run db:validate` çalıştırın.
4. Ayrı migration rolüyle DATABASE_URL enjekte ederek `npm run db:deploy` uygulayın. Bu komut şemayı değiştirir; hedefi doğrulayın. MIGRATION_DATABASE_URL adı Prisma tarafından otomatik okunmaz.
5. `npm run check` ve `npm run build` çalıştırın. Çalıştırma ortamında minimum runtime DB rolünü kullanın.
6. `npm start -- --hostname 127.0.0.1` ile Node sunucusunu HTTPS ters proxy arkasında çalıştırın; süreç yöneticisini işletmeci seçer. Üretimde NODE_ENV=production kullanılmalıdır. Node/DB portlarını doğrudan internete açmayın.
7. Yeni hesabı kaydedin ve e-postayı doğrulayın; ilk organizasyonu oluşturun. Genel demo hesabı veya otomatik yönetici yoktur.

## Veri güvenliği ve güncelleme

DB rol izinleri için [SECURITY-S01C](SECURITY-S01C.md), veri geçişi için [DATABASE](DATABASE.md) okunmalıdır. Yeni tablolar ve güncelleme işlemleri için izinler migration başına gözden geçirilir; eski rol listesini körlemesine uygulamayın. Test yöneticisinin CREATE ROLE yetkisini runtime'a vermeyin.

Güncellemeden önce şifreli yedek alın ve izole geri yüklemeyi doğrulayın. Yeni migration'ları aynı başlangıç şemasında sentetik verilerle deneyin; sonrasında uygulama/DB sürüm uyumunu ve sağlık kontrolünü doğrulayın. Eski uygulamaya dönmek migration'ı geri almaz; veri kaybı içeren reset/down migration çalıştırmayın. Kurtarma planını uygulamadan önce belirleyin.

Token temizliği için ayrı sınırlı rol ve zamanlayıcı gerekir; `npm run security:cleanup` varsayılan inceleme, `-- --apply` yazma modudur. Finans/audit silinmez. Parola/token içeren loglar tutulmaz. Saklama, erişim ve olay müdahalesi işletmeci sorumluluğudur.

MFA, güvenilir IP/bot koruması, kapasite/alarmlar ve gerçek sağlayıcı testleri tamamlanmadı. [Ertelenmiş operasyonlar](DEFERRED-CLOUD-OPERATIONS.md) ücretli sağlayıcı zorunluluğu değildir; kendi altyapısında da karşılanması gereken güvenlik işleridir.

## Kaynak sağlama

Değiştirilmiş ağ sürümünü çalıştırıyorsanız uzaktan etkileşen tüm kullanıcılara o sürümün karşılık gelen kaynak kodunu ücretsiz edinme olanağını belirgin biçimde sunun (§13). Genel upstream bağlantısı, yerel değişiklikleri ve gereken derleme/kurulum betiklerini içermiyorsa yeterli değildir. İşletmeci kaynak arşivini kendi erişilebilir adresinde, sürüm/commit ile eşleştirerek sağlayabilir. Bu görev arayüz özelliği eklemez; kaynak sunumu işletim kontrol listesine dahildir. Sırları, kişisel verileri ve gerçek .env dosyasını kaynak paketine eklemeyin.

Kopya veya binary/konteyner dağıtırken §§4–6, üçüncü taraf bildirimleri ve ilgili LGPL/MPL koşulları da değerlendirilmelidir. Yazılım ücretsizdir; sunucu/SMTP/depolama hizmetlerinin ücretsiz olması garanti edilmez. Üretim hazırlığı ayrıca doğrulanmalıdır.
