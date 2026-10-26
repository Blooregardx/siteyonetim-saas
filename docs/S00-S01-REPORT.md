# S00–S01 ortam ve geliştirme raporu — 27 Ekim 2026

## Ortam doğrulaması

- Yerel checkout origin: `Blooregardx/siteyonetim-saas`. GitHub bağlayıcısı okuma/yazma erişimini doğruladı; `git ls-remote origin HEAD` başarılı.
- Node 24.19.0; Prisma CLI ve @prisma/client 6.19.3, sürümler eşleşiyor.
- İlk kısıtlı komutlarda proxy bağlantısı EPERM verdi. Ağ erişimli komutla Prisma indirmesi çalıştı. Alan adı engeli devam etmiyor; TLS kontrolü kapatılmadı.
- `npx prisma validate` ve `npx prisma generate`: başarılı.
- İlk migration incelendi: site kapsamlı bileşik yabancı anahtarlar, dönem/daire benzersizliği, idempotency anahtarı ve pozitif tutar CHECK kısıtları mevcut.
- Geçici `postgres:17-alpine` konteyneri, localhost:55432, yalnızca `siteyonetim_test`/shadow veritabanları kullanıldı. İki migration başarıyla uygulandı. `migrate status`: güncel. `migrate diff --exit-code`: fark yok.
- Üretim veritabanına bağlantı veya migration, canlı dağıtım yapılmadı. Gerçek bulut servis kimlik bilgisi tanımlı değil; uydurulmadı. Echo/Nymax kullanılmadı.

## Gerçekten doğrulanan davranış

- PostgreSQL servisinden organizasyon/site, blok/daire, malik/kiracı, dönemsel aidat ve manuel tahsilat oluşturulabiliyor.
- Organizasyon portföyü ve site detayları servis üzerinden üyelik/rol kontrolüyle okunuyor.
- Yetkisiz ve oturumsuz erişim reddediliyor; farklı siteye ait blok referansı DB tarafından engelleniyor.
- Kısmi tahsilat, fazla ödeme reddi, iki paralel tahsilatın borcu aşmaması ve aynı isteğin paralel tekrarında tek kayıt test edildi.
- Bireysel ve şirket demo sayfaları production sunucusunda HTTP 200 ve güvenlik başlığı ile çalıştı. Görsel tarayıcı testi yapılmadı.

## Kontroller

- ESLint: geçti.
- TypeScript: geçti.
- Birim testleri: 4/4 geçti.
- PostgreSQL entegrasyon senaryosu: 1/1 geçti; senaryoda yetki, veri ayrımı, geçersiz dönem, mükerrer tahakkuk, malik/kiracı, eşzamanlı tahsilat ve idempotency kontrolleri var.
- Production build: geçti.
- İki production HTTP smoke kontrolü: geçti.
- İlk sandbox denemesinde test IPC soketi ve build alt süreci engellendi; ağ erişimli yeniden çalıştırmalar geçti. İlk başarısız denemeler başarı olarak sayılmadı.
- CI iş akışına ayrı test veritabanı ve entegrasyon testi eklendi. Uzak GitHub Actions sonucu bu yerel kontrollerden ayrıdır; bu rapor uzak CI başarısı iddia etmez.

## Değişen dosyalar

- `prisma/schema.prisma`: organizasyon ve malik/kiracı modelleri.
- `prisma/migrations/202610270001_organizations/migration.sql`: eklemeli migration.
- `src/lib/management.ts`: oturum callback'iyle yetkili okuma/yazma ve transaction kullanan tahsilat servisi.
- `tests/management.integration.ts`: gerçek PostgreSQL regresyon senaryosu.
- `src/app/page.tsx`, `src/app/globals.css`: bireysel/şirket demo görünüm geçişi.
- `package.json`, `.github/workflows/ci.yml`: entegrasyon komutu ve CI.
- `.gitignore`, `README.md`, `docs/ARCHITECTURE.md`, bu rapor: çalışma dosyaları ve kapsam belgeleri.

## Tamamlanmamış işler

S00–S01 başladı; tamamlanmış üretim ürünü değildir. Oturum sağlayıcısı, davet/üyelik yönetimi, CSRF korumalı HTTP/server action katmanı, gerçek veriye bağlı dashboard ve CRUD formları henüz yok. Servisteki güvenilir session callback'i testlerde sağlanıyor; uçtan uca gerçek kullanıcı girişi uygulanmadı. Apartman güncelleme/silme, sakin erişimi, doluluk bitiş/güncelleme ekranları, toplu dönem borçlandırma, audit log ve tahsilat ters kaydı da sonraki işlerdir. Yedekleme, izleme, üretim secret kurulumu ve tarayıcı uçtan uca testleri bekliyor.

Mevcut sitelerin organizasyonlara atanması için `Site.organizationId` geçiş planı gerekir. Uygulama servisini atlayan doğrudan veritabanı yazımları toplam fazla ödeme kuralını aşabilir. Üretim öncesinde DB rolleri ve denetim gereksinimleri ayrıca tamamlanmalıdır.
