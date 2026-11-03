# Docker Compose ile kendi sunucusunda kurulum — DEVELOPMENT

## Yeni kullanıcı başlangıcı — S04-D

[SiteYönetim’i Docker ile Kur — Adım Adım](COMMUNITY-INSTALLATION.md) kısa kurulum yolu, [TROUBLESHOOTING](TROUBLESHOOTING.md) güvenli hata teşhisidir. `sh scripts/selfhost-preflight.sh` ilk başlangıç öncesi salt okunur kontrol yapar; otomatik düzeltme veya volume silme yoktur. Mevcut teknik/S04-A–C işletim ayrıntıları aşağıda korunur. S04-A/B/C PR #21/#22/#23 main'e birleşti; alpha.2 henüz yayımlanmadı.

## S04-C — Şifreli mantıksal yedek ve korumalı güncelleme

Host operatörüne yönelik pg_dump → age akışı, atomik encrypted backup/manifest, lock, durum ve açık etkinleştirilen systemd timer/retention altyapısı eklendi. Ayrı boş/portsuz siteyonetim_test restore provası ve hata sonrası yazıcıları durduran güncelleme aracı vardır. Web kullanıcısına ham yedek veya Docker socket yetkisi verilmez. [İşletim ve anahtar rehberi](BACKUP-OPERATIONS.md), [güncelleme](SAFE-UPGRADE.md), [DEVELOPMENT doğrulaması](S04C-BACKUP-VALIDATION.md).

Bu günlük mantıksal backup kapsamıdır; WAL/PITR, anlık kurtarma ve production RPO/RTO ayrıca tasarlanıp sınanmalıdır. Anahtar kaybı yedeği açmayı engeller; fiziksel disk kaybına karşı ayrı depoda kopya gerekir. Ücretli sağlayıcı/Supabase zorunluluğu yoktur. Zamanlayıcı/silme varsayılan etkin değildir; gerçek deploy/güncelleme yapılmadı. Aşağıdaki tarihsel kanıtlar korunur.

## S04-B — Uygulama içi ilk kurulum

`/kurulum`, giriş yapmış ve e-postasını doğrulamış kullanıcı için Türkçe, mobil uyumlu başlangıç akışıdır: yönetim türü → organizasyon → ilk apartman/site → kapsamlı panel bağlantısı. Kayıt ve doğrulama mevcut ekranlardadır; SMTP olmadan doğrulama tamamlanmış sayılmaz. Panelde “İlk kuruluma başla / devam et”, doğrulama ekranında “İlk kuruluma devam et” bağlantısı vardır.

İlerleme PostgreSQL üyelik/organizasyon/site kayıtlarından türetilir; tarayıcı saklaması veya yeni setupCompleted alanı yoktur. Yenileme/yeniden giriş mevcut adımdan devam eder. Kurulum yazımlarında kullanıcı kilidi ve güncel yetki kontrolü tekrar gönderimleri tekilleştirir; normal panelin çoklu organizasyon/site oluşturması korunur. Mevcut RESIDENT ve legacy üyelikler yükseltilmez; davetliler veya mevcut kullanıcılar kuruluma zorla yönlendirilmez. Birden fazla yönetim organizasyonunda önce sitesi olmayan, sonra ID sırasındaki ilk organizasyon gösterilir; panelden kapsam seçimi ve normal işlemler korunur.

Bu akış Docker/PostgreSQL/HTTPS/SMTP kurmaz, secret göstermez veya değiştirmez. Sunucu altyapısı operatör sorumluluğundadır. Finansal kayıt veya global admin oluşturmaz. Yalnız DEVELOPMENT; [test kapsamı ve sınırlar](S04B-ONBOARDING-VALIDATION.md). S04-C güvenilir yedek işletimi ayrı aşamadır. Tarihsel kayıtlar aşağıda korunur.

Supabase kullanılmaz. Yazılım ücretsiz, PUBLIC ve AGPL-3.0-only kalır; ücretli barındırma, abonelik veya lisans anahtarı gerekmez. Sunucu, alan adı ve e-posta işletmeciye maliyet çıkarabilir. Bu altyapı üretim onayı değildir. Web kurulum sihirbazı S04-B, güvenilir zamanlanmış yedek işletimi S04-C kapsamıdır.

## İlk kurulum

Docker Engine ve Compose v2, Git ve güvenli bir Linux sunucusu gerekir. İncelenmiş kaynak commit'ini indirin. `compose.yaml` yalnız geliştirme DB'si olarak korunmuştur. Aşağıdaki komutlar yeni, boş hedef içindir; var olan volume'u silmeyin.

```sh
git clone https://github.com/Blooregardx/siteyonetim-saas.git
cd siteyonetim-saas
umask 077
cp .env.selfhost.example .env.selfhost
mkdir -m 700 secrets
openssl rand -hex 32 > secrets/db_password
openssl rand -hex 32 > secrets/migrator_password
openssl rand -hex 32 > secrets/runtime_password
: > secrets/smtp_url
chmod 600 .env.selfhost
# Standart Debian imajlarında node UID=1000, postgres GID=999:
sudo chown 1000:999 secrets/*
sudo chmod 640 secrets/*
```

`.env.selfhost` içinde POSTGRES_DB, HTTPS APP_URL ve MAIL_FROM ayarlayın. SMTP_URL değerini terminal geçmişine/komut satırına yazmadan güvenilir editörle `secrets/smtp_url` dosyasına girin. `smtps://` veya zorunlu STARTTLS kullanan `smtp://` gerekir. Dosyanın boş kalması demo incelemesine izin verir; kayıt/doğrulama/kurtarma tamamlanmış sayılmaz. Secret dosyalarını konteynerde UID 1000'in okuyabildiği en dar izinlerle sağlayın (rootless/user namespace eşlemesini doğrulayın); tüm dünyaya okuma izni vermeyin. DB başlangıcı da bu dosyaları okur. Compose secrets yerel diskte şifreli kasa değildir; host erişimini koruyun.

```sh
docker compose --env-file .env.selfhost -f compose.selfhost.yaml config --quiet
docker compose --env-file .env.selfhost -f compose.selfhost.yaml build
docker compose --env-file .env.selfhost -f compose.selfhost.yaml up -d db
docker compose --env-file .env.selfhost -f compose.selfhost.yaml run --rm migrate
docker compose --env-file .env.selfhost -f compose.selfhost.yaml up -d app
docker compose --env-file .env.selfhost -f compose.selfhost.yaml ps
```

`config` çıktısını secret içerebilen başka Compose yapılandırmalarıyla paylaşmayın; `--quiet` kullanın. `set -x`, env dump ve URL'li teşhis çıktısı kullanmayın. Migration hatası sabit hata mesajıyla kapanır; ayrıntılı incelemeyi güvenilir operatör yapar. Migration komutu otomatik reset/seed yapmaz; tekrar çalıştırılabilir. İlk init yalnız boş PGDATA üzerinde çalışır; mevcut volume'da parola dosyasını değiştirmek DB parolasını döndürmez. Rotasyon ayrı DBA işlemi gerektirir. Init yarım kalırsa uygulamayı başlatmayın; gerçek volume'u silerek düzeltmeyin.

## Roller ve hazır olma

Postgres başlangıç yöneticisi yalnız DB servisinde bulunur. `sy_migrator` şema sahibi ve DDL rolüdür, superuser/rol oluşturma yetkisi yoktur. Migration servisi validate → deploy → schema diff → açık tablo/sütun izinleri uygular. Runtime secret'ı migration servisine, migrator/DB secret'ları uygulamaya verilmez. `sy_runtime` DDL/sahiplik/rol üyeliği taşımaz. Finans/audit UPDATE/DELETE/TRUNCATE izinleri verilmez; mevcut immutable trigger'lar korunur. Satır kilitleri için gereken UPDATE(id) izinleri trigger'larla birlikte değerlendirilir. Tenant sınırı uygulama servislerindedir; RLS iddiası yoktur. Runtime sırrı yine kritik güvenlik sınırıdır.

Uygulama restart'ında migration çalışmaz. Başlangıç ve healthcheck mevcut migration adlarını, SHA-256 checksum'larını, tamamlanma durumunu ve runtime DDL yetkisizliğini doğrular. Eksik/başarısız/fazla migration sağlıklı görünmez. Bu kapı dışarıdan yapılan tüm DDL sapmalarını kanıtlamaz; migration servisinin schema diff kontrolünü her güncellemede çalıştırın. Runtime connection_limit=5; DB rolü 10, migrator 5 bağlantıyla sınırlıdır. Çoklu app ölçeklemede toplam kapasiteyi ayrıca hesaplayın.

App non-root, read-only root filesystem, cap_drop ALL ve no-new-privileges kullanır. Geçici CSV dosyaları sınırlı /tmp tmpfs üzerinde; kalıcı uygulama dosyası yoktur. PostgreSQL named volume kalıcıdır. `down -v` veri siler; işletim komutu olarak kullanmayın. DB portu yayınlanmaz; özel internal ağ yalnız app/migrate ile paylaşılır.

## HTTPS, hesap ve ilk organizasyon

Host ters proxy'sini 127.0.0.1:3000'e yönlendirin. Güvenilir sertifika, HTTPS yönlendirmesi, güvenlik güncellemeleri ve yalnız proxy üzerinden erişim işletmeci sorumluluğudur. Uzak proxy için loopback binding'i gelişigüzel 0.0.0.0'a çevirmeyin; özel ağ/firewall tasarlayın. HTTP yalnız mevcut izole localhost sentetik test sözleşmesinde kullanılabilir; bu Compose gerçek kullanımda HTTPS origin ister.

HTTPS üzerinden demo ve giriş sayfasını kontrol edin; oturumsuz `/panel` yönetim verisi göstermemelidir. SMTP/TLS ve SPF/DKIM/DMARC teslimini kendi ortamınızda doğrulayın. Sonra kendi hesabınızı kaydedin, e-postanızı doğrulayın ve ilk organizasyonunuzu oluşturun. Otomatik admin veya genel demo parolası yoktur. Bu görev gerçek e-posta/sertifika sağlayıcısını doğrulamaz.

## Yedek ve güvenli güncelleme

[Mevcut sentetik kanıtı](BACKUP-RESTORE.md) koruyun. Yedekler kullanıcı, parola özeti, token ve finans/audit verisi içerir. Özel erişimli dizinde, doğrulanmış şifreleme anahtarı ve ayrı erişim politikasıyla saklayın. Operatör RPO/RTO, saklama süresi, rotasyon, silme ve anahtar kurtarma politikasını yazılı belirlemelidir. Yedekleri Git'e eklemeyin.

Yazıcıları durdurup `pg_dump -Fc` akışını şifreli hedefe alın; parola argümanına yazılmadan DB servisinde yerel operatör kimliği kullanılabilir. Örnek (çıktı hassastır):

```sh
umask 077
mkdir -p backups
docker compose --env-file .env.selfhost -f compose.selfhost.yaml exec -T db sh -c 'pg_dump -U postgres -d "$POSTGRES_DB" -Fc' > backups/pre-update.dump
```

Bu örnek dosya şifreli değildir: diskin şifreli ve erişimin özel olduğunu doğrulayın veya doğrudan onaylı şifreleme aracına aktarın; pipeline'da iki sürecin de hata durumunu kontrol edin. Yedeği plaintext depoda bırakmayın. Checksum, commit, PG sürümü, migration listesi, rol/ACL manifesti ve anahtar kimliğini ayrı güvenli kayıtta tutun. `pg_dump` global rol/parola taşımaz; `sy_migrator` sahipliği ve `sy_runtime` tablo/sütun ACL'leri için ayrı rol hazırlığı gerekir. Global rol dump'ı parola özeti içerebilir; public paylaşılmaz.

Restore yalnız ayrı, boş PostgreSQL 17 hedefine; önce LOGIN yetkileri kısıtlı aynı isimli roller hazırlanır. `pg_restore --exit-on-error --single-transaction` kullanın; owner/ACL'leri sessizce atmayın. Bütün tablolar, migration checksum'ları, trigger/constraint/index ve sütun ACL'leri; tenant ve finans/audit probu doğrulanmadan hedefe trafik vermeyin. İzole prova araçlarının yalnız `siteyonetim_test` korumasını kaldırmayın. Gerçek hedefte otomatik DROP/TRUNCATE/reset/restore bu çalışma kapsamında yoktur.

Güncellemeden önce yedek ve ayrı hedefte kurtarma provası, yeni kaynak build'i, migration diff ve kabul testleri gerekir. App'i durdurun, ayrı migrate işlemi başarılı olunca yeni app'i başlatın. Eski imaja dönmek şemayı geri almaz; yeni yazımlar varsa eski yedeğe dönüş veri kaybettirebilir. Başarısız güncellemede yazıcıları kapalı tutup ileri düzeltme veya onaylı kurtarma planı uygulayın; otomatik down migration yoktur.

## Dağıtım lisansı sınırı

Yerel kaynak build'i ile önceden hazırlanmış binary imajı dağıtımı aynı işlem değildir. LICENSE değiştirilmedi. Değiştirilmiş ağ sürümü için AGPL §13 karşılık gelen kaynak erişimi; binary dağıtımda ilgili §§4–6 ve üçüncü taraf koşulları değerlendirilmelidir. [Envanter](THIRD-PARTY-LICENSES.md) Sharp/libvips LGPL bileşenlerinde kaynak, yeniden bağlama ve özgün bildirim doğrulamasını açık bırakır; MPL dosyalarının kaynak/bildirim şartları da kontrol edilmelidir. Debian/Node/OpenSSL imaj bileşenleri envantere ayrıca alınmalıdır. Standalone tracing tüm bildirimleri paketliyor varsayılmaz. Registry push/release yapılmaz; imaj dağıtımı ve tam lisans uyumu onaylanmış değildir.
