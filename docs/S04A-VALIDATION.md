# S04-A doğrulama kaydı

## Güncel Docker kabulü — READY FOR MAINTAINER REVIEW

Yalnız DEVELOPMENT. Doğrulanan kod commit'i `63858a29691660b65d0208dbca6983d7676a88c1`:

| Koşu | checks | selfhost |
|---|---|---|
| [Push 41570998772](https://github.com/Blooregardx/siteyonetim-saas/actions/runs/41570998772) | Başarılı | Başarılı |
| [PR 41571004440](https://github.com/Blooregardx/siteyonetim-saas/actions/runs/41571004440) | Başarılı | Başarılı |

Her iki koşu tamamlandı; devam eden işler başarı sayılmadı. Bu belge commit'inin son HEAD push/PR sonuçları ayrıca [taslak PR #21](https://github.com/Blooregardx/siteyonetim-saas/pull/21) açıklamasında kaydedilir; son HEAD'in iki CI başarısı bakımcı kapısıdır. PR açık ve taslak kalır; bu karar merge/yayımlama yetkisi değildir.

### Selfhost işinin gerçek kapsamı

- Runtime ve migration Docker imajları build edildi. Next.js standalone sunucusu çalıştı; `/demo` HTTP erişimi ve app healthcheck başarılı.
- Production runtime imajında gerçek Prisma Client/native motor ile PostgreSQL sorguları çalıştı. UID root değil; runtime secret dosyasında dünya erişimi yok. UID=1000/GID=999 ve 0640 dosyalar hem DB init hem ilgili konteynerlerce okunabildi.
- PostgreSQL 17 boş named volume ile başladı. Docker inspect DB port binding'inin boş olduğunu doğruladı.
- `sy_migrator` ile validate/deploy/schema diff/grant işlemleri başarılı. `sy_runtime` kimliği, superuser/DB/rol oluşturma yetkisizliği ve migrator rolüne üye olmaması sorguyla doğrulandı. Gerçek CREATE TABLE girişimi SQLSTATE 42501 ile reddedildi.
- Migration öncesi runtime Prisma bağlantısı başarılı ve migration tablosu yoktu; ardından uygulama başlangıcı hata kodu 1 ile reddedildi. Böylece mount/native/bağlantı hatası beklenen migration reddi olarak kabul edilmez.
- Migration sonrası 11 migration adı/checksum/tamamlanma durumu gate tarafından doğrulandı. Şema diff temiz; app ve sağlık başarılı.
- Oturumsuz panel `/giris` hedefine yönlenir. App Router loading sınırında HTTP 200 içindeki gerçek `__next-page-redirect` meta etiketi doğrulanır; yalnız 200 yanıtı başarı sayılmaz. Doğrudan HTTP redirect durumunda da hedef `/giris` olmalıdır.
- Runtime rolüyle sentetik AuthAttempt sentinel satırı yazıldı. DB restart ve health sonrasında aynı satır/değer ile 11 migration checksum'ı tekrar doğrulandı. Veri ve migration geçmişi korundu.
- Runtime rol connection limit=10 sorguyla doğrulandı; Prisma yapılandırması connection_limit=5. Eşzamanlı yük altında limit tüketimi/çoklu instance kapasitesi sınanmadı.

### Checks: regresyon ve ayrı restore kanıtı

Prisma generate/validate, 11 migration/schema diff, kaynak/lisans hazırlık kontrolü, npm audit, ESLint, TypeScript, 25/25 birim, 29/29 PostgreSQL entegrasyon, production build, 14/14 Playwright, iki dashboard query-plan modu ve streaming backup Python 3/3 başarılı.

Sentetik backup/restore ayrı PostgreSQL 17 servislerinde **26 tablo / 258.298 satır** eşleştirdi; migration geçmişi, şema nesneleri ve tablo/sütun ACL'leri dahil. Restore sonrası uygulama probu: 11 migration, brüt 6500, ters 4000, net 2500, kalan 7500 kuruş, 15 audit; tenantIsolation=true ve immutableHistory=true. Global rol/parolalar pg_dump tarafından taşınmaz; sentetik ACL rolü hedefte ayrıca hazırlanır.

Tenant, finans, oturum/rol, CSV ve panel regresyonları `checks` işinde doğrulanmıştır. Bunlar selfhost imajında tam tarayıcı akışı veya selfhost volume'undan restore kanıtı değildir. Selfhost işi SMTP yapılandırmaz, gerçek e-posta veya kişi verisi kullanmaz.

### Logla bulunan ve düzeltilen nedenler

Başlangıç `249effe` için [push](https://github.com/Blooregardx/siteyonetim-saas/actions/runs/41568654524) ve [PR](https://github.com/Blooregardx/siteyonetim-saas/actions/runs/41568660030) checks başarılı, selfhost başarısızdı. Sonraki teşhis logu validate/deploy/diff sonrasında grants aşamasını gösterdi: `.dockerignore` tüm SQL dosyalarını dışlarken `docker/grants.sql` istisnası eksikti. Dar istisna eklendi; grant işlemi sonraki loglarda başarılı.

Gerçek Prisma ön kontrolü, tırnaksız YAML tmpfs listesinin virgülden iki mount'a ayrılmasını yakaladı (`invalid mount path: mode=1777`); tek tırnaklı öğeye düzeltildi. Runner'da bulunmayan rg bağımlılığı ve panel için yanlış yalnız-HTTP-redirect beklentisi giderildi. Panelin streaming yönlendirmesi mevcut host production build'de yeniden üretildi. Auth/finans uygulama kodu veya güvenlik sınırları değiştirilmedi; başarısız işler retry ile gizlenmedi.

Yerel VFS/disk kısıtı nedeniyle büyük build tekrarlanmadı. Chromium önbelleği, kullanıcı dosyaları veya başka proje kaynakları silinmedi.

### Açık işletim ve dağıtım sınırları

STAGING/PRODUCTION deploy, gerçek HTTPS/SMTP teslimi, bağımsız insan kurulumu, internet yükü/rate-limit/MFA ve işletim izleme doğrulanmadı. Tam kullanıcı akışının doğrudan selfhost imajında tarayıcı kabulü, selfhost volume'undan restore ve bağlantı doygunluk testi ayrı ek kanıtlardır. S04-B sihirbaz ve S04-C yedek işletimi ayrı aşamalardır.

PUBLIC/AGPL-3.0-only, Supabase kullanmama ve ücretsiz yazılım kararı korundu. Finans servisleri, tarihsel migration'lar, schema, LICENSE ve geliştirme compose.yaml değişmedi. LGPL/MPL ve temel imaj bildirim/karşılık gelen kaynak yükümlülükleri hâlâ binary dağıtım kapısıdır; lisans uyumu veya yeni kaynak sunumu tamamlandı iddiası yoktur. Registry push, release/tag veya merge yapılmadı.

## Tarihsel yerel INCOMPLETE kaydı

Aşağıdaki ilk hazırlık sonuçları tarihsel olarak korunur; güncel Docker/CI kabulü yukarıdadır.


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
