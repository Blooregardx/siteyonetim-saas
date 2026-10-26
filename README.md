# SiteYönetim

Next.js App Router, React, strict TypeScript, PostgreSQL ve Prisma 6 ile Türkçe yönetim uygulaması. Gerçek oturum ve PostgreSQL kayıt formları uygulanmıştır; S00–S01 eksikleri için [raporu](docs/S00-S01-REPORT.md) okuyun. Üretime hazır olarak işaretlenmemiştir.

## Bulut geliştirme

Node 24 ortamında `npm ci`, `npm run db:generate` çalıştırın. Bulut secret ayarlarında DATABASE_URL tanımlayın. `.env.example` değişkenleri belgeler; gerçek erişim bilgilerini Git'e eklemeyin. Onaylı geliştirme veritabanında `npm run db:deploy` sonrası `npm run dev` veya `npm run build && npm start` kullanın. Kullanıcının bilgisayarında servis çalıştırılması gerekmez. Üretimde HTTPS zorunludur.

`/kayit`, `/giris`, `/sifre-sifirla` genel sayfalardır. `/panel` gerçek oturum ister; organizasyon oluşturma ile ilk kurulum başlar. `/demo` ve `/demo?view=company` veritabanından bağımsız örneklerdir. Otomatik demo kullanıcı/seed yoktur.

Parola kurtarma için SMTP_URL, MAIL_FROM, HTTPS APP_URL gerekir. Posta sağlayıcısı olmayan ortamda eksik yapılandırma açıkça bildirilir.

## Kontroller

`npm run db:validate`, `npm run db:generate`, `npm run check`, `npm run build`.

Entegrasyon: yalnızca izole localhost/127.0.0.1 `siteyonetim_test` DB üzerinde migration uygulayın. `TEST_DATABASE_URL=... npm run test:integration` çalıştırın. Tarayıcı: `npx playwright install chromium`, aynı test DB adresini DATABASE_URL ve TEST_DATABASE_URL olarak tanımlayıp `npm run test:e2e` çalıştırın. Production build önceden hazır olmalıdır. Playwright test DB'de sentetik fixture bırakır; yalnızca bu test veritabanı gerektiğinde sıfırlanabilir. Üretim üzerinde çalıştırmayın.

CI PostgreSQL servisi, migration, birim/entegrasyon/build ve Playwright kontrollerini içerir. Uzak CI sonucu yerel test sonucundan ayrıdır.

[Veri modeli ve geçiş](docs/DATABASE.md), [güvenlik](docs/SECURITY.md), [özellikler](docs/FEATURES.md), [kararlar](docs/DECISIONS.md), [yol haritası](docs/ROADMAP.md).
