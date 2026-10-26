# SiteYönetim SaaS

Site ve apartman yönetimi için Next.js App Router, TypeScript, Prisma ve PostgreSQL tabanlı başlangıç projesi.

## Mevcut kapsam

- Türkçe, mobil uyumlu örnek yönetim paneli: daireler, aidatlar, tahsilatlar ve duyuru.
- Site üyelikleri ve roller, bloklar, daireler, dönemsel aidatlar, ödemeler ve duyurular için ilişkisel veri modeli ve ilk migration.
- Kuruş üzerinden hesaplama, kısmi ödeme ve gecikme hesapları; birim testleri.
- ESLint, TypeScript, derleme ve PostgreSQL migration kontrolü için GitHub Actions; Dependabot.

**Bu bir başlangıç sürümüdür.** Panel `src/lib/demo.ts` dosyasındaki örnek verileri gösterir; tarih Ekim 2026 olarak sabittir. Veritabanına bağlı değildir. Kullanıcı girişi, yetkilendirme, gerçek CRUD işlemleri ve ödeme entegrasyonu henüz uygulanmamıştır. Panelde gerçek kişisel veri kullanmayın. Hazır bir üretim SaaS ürünü olarak değerlendirmeyin.

## Hızlı başlangıç

Node.js 24 ve npm kullanın:

```bash
npm ci
cp .env.example .env
npm run dev
```

`http://localhost:3000` adresini açın. Demo panel için veritabanı gerekmez.

### Yerel PostgreSQL ve veri modeli

Docker Compose kurulu olmalıdır. Compose parolası yalnızca yerel geliştirme içindir; port sadece localhost'a açılır.

```bash
docker compose up -d db
npm run db:generate
npm run db:deploy
```

Şema değişikliği için `npm run db:migrate -- --name aciklayici_ad`, modeli incelemek için `npm run db:studio` kullanın. `.env` dosyasını Git'e eklemeyin. Uzak PostgreSQL kullanırken sağlayıcının TLS ve bağlantı gereksinimlerini uygulayın.

## Kontroller

```bash
npm run db:validate
npm run check
npm run build
npm start
```

`db:validate` için `.env` veya `DATABASE_URL` gerekir. CI geçici PostgreSQL üzerinde migration uygular; uygulamanın PostgreSQL bağlantılı bir iş akışı henüz yoktur.

## Yapı

- `src/app`: panel, görünüm ve temel güvenlik başlıkları
- `src/lib`: örnek veri, para hesaplamaları ve testler
- `prisma`: şema ve migration
- `docs/ARCHITECTURE.md`: veri modeli sınırları ve geliştirme sırası
- `SECURITY.md`: güvenlik bildirimi ve üretim gereksinimleri

Kod için henüz açık kaynak lisansı seçilmemiştir.
