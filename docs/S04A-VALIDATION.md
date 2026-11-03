# S04-A doğrulama kaydı

Durum: **INCOMPLETE**. DEVELOPMENT altyapı hazırlığıdır; STAGING/PRODUCTION kurulmadı. Başlangıç `50eed5527b78b2258322259dbea206f1c28f47a9`, dal `codex/s04-a-self-hosting`.

11 migration dizini doğrulandı; S03-F Charge/BulkChargeOperation immutable trigger migration'ı ve mevcut rol/satır kilidi testleri incelendi. Eski migration, schema, auth/tenant/finans servisleri, LICENSE ve geliştirme compose.yaml değiştirilmedi.

Yerel sonuçlar:

- Compose config --quiet başarılı.
- ESLint, strict TypeScript, birim 25/25 başarılı.
- Prisma generate (6.19.3), validate başarılı.
- Streaming backup Python 3/3 başarılı.
- Ayrı loopback PostgreSQL 17 alpine `siteyonetim_test` üzerinde 11 migration uygulandı, schema diff temiz. İlk hazır olma beklenmeden yapılan deneme başarısızdı; DB hazır olduktan sonra tekrarlandı.
- Host Next.js production build başarılı.
- PostgreSQL entegrasyon 29/29 başarılı: tenant/rol, finans değişmezliği, idempotency, kısmi/tam tahsilat, CSV ve panel regresyonları dahil.
- İlk Playwright koşusu 1 başarılı, 13 tarayıcı executable eksikliği nedeniyle başarısız; Chromium kuruldu ve tekrar koşusu 14/14 başarılı. Bu sonuç uygulama regresyonu kanıtı veya tam E2E başarısı değildir.
- Docker içinde npm ci, prisma generate ve Next.js production build ilk denemede başarılı; son runtime katmanı oluşturulamadı.
- Docker VFS ve 7.9 GiB workspace diski iki build denemesinde doldu. Göreve ait build önbelleği temizlendi; ikinci build durduruldu. TLS doğrulaması kapatılmadı; proxy CA yalnız BuildKit secret mount ile kullanıldı.
- Yeni PostgreSQL 17 bookworm konteyneri başlatıldı. İlk secret dosyaları postgres GID=999 için okunamadığından init eksik kaldı; sentetik hedefte izinler düzeltilip rol init işlemi ayrı çalıştırıldı, başarılı. Rehbere UID/GID ve 0640 gereksinimi eklendi. Temiz baştan tam Compose kabul provası hâlâ gereklidir.

Runtime imajının gerçekten başlaması, native Prisma dosyalarının çalışması, bu Compose rollerinin tam kullanıcı akışı, sağlık, kalıcılık ve bağlantı sınırları henüz kanıtlanmış değildir. E2E host production sunucusunda 14/14 geçti; sentetik restore yeni HEAD için tekrar doğrulanmalıdır. Mevcut tarihsel S03-F/OSS-04 başarıları yeni Docker imajı kanıtı sayılmaz.

CI'ye ayrı synthetic selfhost işi eklendi; image registry push yapmaz. Var olan checks işi korunur. Push/PR CI sonuçları PR üzerinden ayrıca takip edilmelidir; yerel sonuçlar CI yerine geçmez.

Gerçek SMTP/HTTPS, bağımsız kurulum, üretim kapasitesi, MFA/bot koruması ve işletim izleme açık kalır. Yerel build için Dockerfile sağlanması binary imaj dağıtım lisans uyumunu tamamlamaz; LGPL/MPL ve temel imaj bildirim/kaynak kontrolleri SELF-HOSTING-DOCKER ve THIRD-PARTY-LICENSES belgelerinde açık kapıdır. Yeni kaynak sunumu veya lisans uyumu tamamlandı iddiası yoktur. Merge, release, tag, registry push ve canlı deploy yapılmadı.

CI ilk selfhost denemesi secret dizininin sahipliği nedeniyle runner glob erişiminde durdu. Dizin sahipliği korunup yalnız dosyalar UID=1000/GID=999 yapıldı. DB healthcheck, init sırasında geçici Unix socket sunucusunu hazır saymamak için TCP loopback kullanır. Son HEAD CI durumu PR üzerinde takip edilir.
