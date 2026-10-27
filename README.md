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

## S01-C güvenlik güncellemesi

Yeni ve mevcut hesaplar e-posta doğrulanmadan yönetim/finans yetkisi kullanamaz. Kayıttan sonra `/eposta-dogrula` üzerinden SMTP bağlantısını onaylayın. Doğrulama 1 saat, organizasyon daveti 48 saat geçerlidir. Mevcut hesaplara otomatik doğrulama veya demo yetki verilmez. `/uyeler` yetkili davet, rol değişimi ve üyelik iptali ekranıdır; `/davet?token=...` kabulü doğrulanmış hesap gerektirir. Davet edilen kullanıcı önce kayıt/giriş ve doğrulamayı tamamlayıp davet bağlantısını yeniden açmalıdır.

E-posta değişimi aynı sayfada mevcut parola ve yeni adrese gönderilen doğrulama ile yapılır; sonrasında yeniden giriş gerekir. Audit loglar iş kayıtlarıyla aynı transaction'da yazılır ve normal uygulama yollarında değiştirilemez.

Bulut DB rolleri, SMTP/HTTPS doğrulaması, giriş limiti sınırları, token temizliği ve yedekleme planı: [S01-C güvenlik belgesi](docs/SECURITY-S01C.md). Tahsilat ters kayıt servisi henüz yoktur; [tasarım ve test planı](docs/PAYMENT-REVERSALS.md).

## S01-D tahsilat ters kaydı

Doğrulanmış organizasyon ADMIN'i /panel tahsilat geçmişinden gerekçe ve onayla tam ters kayıt oluşturabilir. Bu işlem gerçek para iadesi yapmaz; özgün ödeme korunur. Net tahsilat=brüt−ters kayıt; yeniden ödeme kalan borca göre alınır. Finans geçmişi değiştirilemez/silinemez. [Model, kilit sırası ve testler](docs/PAYMENT-REVERSALS.md).

Entegrasyon testleri artık ayrı geçici PostgreSQL LOGIN rolleri ve izole migration şeması oluşturur. Yalnız test ortamındaki test yöneticisi rolü CREATE ROLE/şema/izin yönetimi yetkisine sahip olmalıdır. Bu yetki gerçek runtime hesabına verilmez. Testler finans fixture'larını silmez; sentetik veriler izole DB'de kalır.

## Bütçe kararı ve S02-A

Geliştirme yalnız GPT Codex Cloud ve mevcut GitHub ile sürer. DEVELOPMENT kod ve izole test kanıtlarını; STAGING gerçek servis entegrasyonunu; PRODUCTION canlı kullanım hazırlığını belirtir. STAGING/PRODUCTION bütçe nedeniyle ertelenmiştir ve yeni geliştirmeyi bloke etmez. Vercel, yönetimli DB, gerçek SMTP, alan adı, üretim dağıtımı veya ücretli operasyon hizmeti bu geliştirme aşamasının koşulu değildir. Tek takip belgesi: [ertelenmiş bulut operasyonları](docs/DEFERRED-CLOUD-OPERATIONS.md).

S02-A: Paneldeki **Apartman, daire ve kişi kayıtlarını düzenle** bağlantısı `/kayitlar?site=...` ekranına gider. Apartman adı/adres/açıklama, blok adı/açıklama, daire numarası/kat/tür/durum düzenlenebilir. Daireler blok, numara, kat, tür ve kullanım durumuyla filtrelenir. Person kayıtları açık seçimle birden çok daireye bağlanır; malik Ownership, kiracı tarihli Occupancy ilişkisidir. Eski kayıtlar korunur, adla birleştirme yapılmaz. Çıkış kaydı geçmişi silmez; yeniden giriş yeni dönemdir.
