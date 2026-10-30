# OSS-04 doğrulama kanıtı — 30 Ekim 2026

Başlangıç main `55a27f18ed4c014f1b3044db6e181382879d38f2`. PR #7/#8/#9 birleşmiş; PUBLIC/main, AGPL-3.0-only, main-protection ve GitHub Actions checks (15368) zorunluluğu API'den doğrulandı. Başlangıçta tag/release, dış kullanım kanıtı yok; 0 yıldız/0 fork. Güncel bakımcı Blooregardx noreply; geçmiş veya lisans değiştirilmedi.

## Ortam ve yöntem

Mevcut çalışma ağacından ayrı `git archive` kaynak kopyası; .env, node_modules ve .next aktarılmadı. Yeni node:24-bookworm-slim konteyneri, Node 24.22.2/npm 11.19.1; PostgreSQL 17-alpine ayrı kaynak ve boş hedef konteynerleri; Prisma 6.19.3. Node imajı digest'i `sha256:c86ecead9e55a5210ac1727de38a4ca840bf03dcaf34dc9749addbf383b1920c`. Test imajları yayımlanmadı. OpenSSL/CA ve Playwright Linux kitaplıkları kuruldu; proxy/CA korunup TLS doğrulaması açık bırakıldı. Fiziksel olarak ayrı sunucu veya bağımsız insan kurulumu değildir.

SELF-HOSTING sırasıyla npm ci, generate, validate, migration, check/build ve npm start (Playwright webServer) çalıştırıldı. Loopback HTTP/sentetik SMTP yalnız test istisnasıydı. Gerçek HTTPS ters proxy, SMTP teslimi veya sağlayıcı kurulmadı. Migration/test yöneticisi ayrıldı; normal uygulama E2E'si ayrıca NOSUPERUSER/NOCREATEDB/NOCREATEROLE runtime rolüyle çalıştırıldı. Bu izinler bütün sağlayıcılarda doğrulanmış minimum rol şablonu değildir.

## Sonuçlar

| Kontrol | Yerel izole sonuç |
|---|---|
| npm ci | Temiz bağımlılıklar başarılı; ESLint destek uyarısı |
| Prisma generate / validate | Başarılı |
| Temiz migration | 7/7 başarılı |
| ESLint / TypeScript | Başarılı; yeni recovery probu dahil |
| Birim | 8/8 başarılı |
| PostgreSQL entegrasyon | 16/16 başarılı; tenant, eşzamanlı tahsilat, rollback, ayrı LOGIN izinleri |
| Next.js production build | Başarılı, yalnız yerel çalıştırma |
| Playwright | 4/4 başarılı; yerel demo, kayıt/giriş, doğrulama, org, sınır/izolasyon, SMTP reset/davet |
| Runtime rolüyle ek E2E | 4/4 başarılı |
| migrate status / schema diff | Güncel / fark yok |
| npm audit | 0 bildirim; tüm güvenlik risklerinin yokluğu anlamına gelmez |
| Sentetik backup/restore | Aşağıdaki tüm veriler ve katalog tanımları eşit |

Son belge/SPDX/secret/Markdown ve GitHub CI kontrolleri OSS-04 PR'sinin son commitinde ayrıca raporlanır; önceki PR başarıları yeni CI yerine kullanılmaz. Büyük sürüm yükseltmesi veya tarihsel migration değişikliği yoktur.

## Kurtarma kanıtı

Durağan kaynak veritabanından pg_dump custom format; ayrı boş PG17 hedefte pg_restore --exit-on-error --single-transaction. Gerekli sentetik runtime rolü hedefte önceden oluşturuldu; veri/grant/schema dump'tan geldi. Yeni verify-backup-restore.py betiğiyle bütün tablo satırlarının sıralı JSON SHA-256 ve sayıları karşılaştırıldı; index/constraint/trigger tanımları da eşleşti. Betik boş hedef şartını doğrular ve dump'ı geçici dizin kapanınca siler.

Dump SHA-256: `1da87b37d58526309fbf10d5d3ee23cb7b17900e615769d460486c85771ecf9b`. Bu, bir tatbikatın anlık dump'ıdır; her yeni pg_dump aynı byte hash'ini vermek zorunda değildir. Dump ve fixture Git'e eklenmedi.

| Tablo | Karşılaştırılan satır |
|---|---|
| Announcement | 0 |
| AuditLog | 188 |
| AuthAttempt | 12 |
| Block | 19 |
| Charge | 15 |
| EmailVerification | 0 |
| Invitation | 6 |
| Membership | 3 |
| Occupancy | 7 |
| Organization | 26 |
| OrganizationMembership | 25 |
| Ownership | 8 |
| PasswordReset | 0 |
| Payment | 23 |
| PaymentReversal | 11 |
| Person | 10 |
| Session | 7 |
| Site | 22 |
| Unit | 21 |
| User | 32 |
| _prisma_migrations | 7 |

Toplam **21 tablo, 442 satır** eşit. Kaynak ve hedefte recovery-probe başarılı: brüt 6500, ters 4000, net 2500, borç 7500 kuruş; ilgili sitede 10 audit ve 7 migration. Başka tenant erişimi/ters kaydı, tekrarlı ters kayıt ve Payment/Reversal/Audit UPDATE reddi doğrulandı. Geri yüklenmiş hedef migrate status/diff de güncel/farksız.

## Açık sınırlar

Bağımsız kullanıcı kurulumu, gerçek SMTP/HTTPS, üretim yük/güvenlik testi, MFA, işletim/izleme, şifreli saklama/PITR/RPO/RTO ve gerçek afet kurtarma tamamlanmadı. Kaynak-only alpha hazırlığı üretim hazırlığı değildir. Binary/konteyner üçüncü taraf uyum kapısı açıktır. [Release kontrol listesi](RELEASE-CHECKLIST.md), [kurulum](SELF-HOSTING.md), [kurtarma adımları](BACKUP-RESTORE.md).

Son dal kontrolleri: alpha.1 paket/lock sürüm eşliği, değişmeyen bağımlılık grafiği ve lisans hash'i; 479 CSV kaydı, yerel Markdown linkleri, 10 TR/EN taslağının karakter sınırı, Python sözdizimi ve workflow YAML başarılı. Yeni probe dahil lint/TypeScript/8 birim ve build tekrar geçti. Kurtarma aracı aynı konteyner ve dolu hedef senaryolarını beklenen hata ile reddetti; bu güvenlik denemeleri başarılı negatif testlerdir. Secret desen taramasında yeni içerikte eşleşme yok.
