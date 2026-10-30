# Katkı rehberi

Katkılar belgeler, erişilebilirlik, çeviri, sentetik testler ve kod incelemesi dahil değerlidir. Önce [topluluk ilkelerini](CODE_OF_CONDUCT.md), [güvenlik politikasını](SECURITY.md) ve [AGENTS](AGENTS.md) kurallarını okuyun.

## Katkı lisansı

Projenin özgün kodu ve belgeleri AGPL-3.0-only altındadır. Birleştirilmek üzere gönderdiğiniz katkıyı da AGPL-3.0-only altında sağladığınızı belirtin. Yalnız lisanslama yetkiniz olan içeriği gönderin; üçüncü taraf kaynakları ve lisanslarını açıklayın, özgün bildirimlerini koruyun. Bakımcı uyumsuz veya yetkisi belirsiz içeriği birleştirmez. Telif devri/CLA talep edilmez; katkıcı kendi haklarını korur. Bu kural geçmişte başka kişilerin verdiği hakları geriye dönük değiştirmez. [Lisans rehberi](docs/LICENSING.md).

## İş ve PR akışı

Önce ilgili issue'ları arayın. Hata için commit, beklenen/gözlenen davranış ve sentetik tekrar adımları verin. Büyük değişiklikte tasarımı issue'da tartışın. Güvenlik açıkları public issue konusu değildir.

PR #9 ile özellikler main’e alındı; yeni katkılar güncel main’den türetilir ve main’i hedefler. OSS-01/02 PR’lerinin geliştirme tabanı tarihsel iş akışıdır. İlgisiz dalları birleştirmeyin. Tek amaçlı bir dal/PR açın; problemi, sonucu, test kanıtını ve kalan riski yazın. Bakımcı kapsam/yetki/veri güvenliği incelemesi yapar; başarısız kontroller atlanmaz. Otomatik merge ve geçmiş yeniden yazımı kullanılmaz. Değişiklik istekleri çözülmeden birleştirilmez.

## Geliştirme ve kontroller

Node 24, PostgreSQL 17, Prisma 6 kullanın. `npm ci`, `npm run db:generate`, `npm run db:validate`, `npm run check`, `npm run build` çalıştırın. `.env.example` yalnız değişken belgesidir; sırları commit etmeyin.

Entegrasyon/E2E yalnız localhost veya 127.0.0.1 üzerindeki ayrı `siteyonetim_test` DB'de çalışır. Önce bu DB üzerinde migration uygulayın. Komut ortamında DATABASE_URL ve TEST_DATABASE_URL aynı izole URL olmalıdır:

```sh
npm run db:deploy
npm run test:integration
npx playwright install --with-deps chromium
npm run test:e2e
```

Bu komutlardan önce değişkenleri kendi izole test ortamınızda tanımlayın; production URL kullanmayın. Entegrasyon izin testleri geçici LOGIN rollerini/şemaları oluşturabilen test yöneticisi gerektirir; bu yetki runtime rolüne verilmez. E2E loopback sentetik SMTP kullanır ve sentetik fixture bırakır. Gerçek e-posta gönderilmez. Kontrol çalışmıyorsa nedeni ve hangi kontrolün eksik olduğunu PR'de belirtin; geçtiğini iddia etmeyin.

## Korunacak sınırlar

Next.js/TypeScript/PostgreSQL/Prisma mimarisi, sunucu oturumu, tenant ayrımı, transaction/audit, kuruş hesabı, satır kilidi/idempotency ve finans geçmişi korunur. Migration veri kaybetmemelidir. Demo `/demo` içindedir. Ücretli servis, gerçek müşteri verisi veya production deploy katkı koşulu değildir.

## Bakım süreci

Bakımcı issue'ları güvenlik dışı hata/özellik/belge olarak değerlendirir; etiketler henüz otomatik oluşturulmaz. Sürüm notları uygulanan değişiklikleri ve yükseltme risklerini belirtir. Destek/yanıt süresi garantisi yoktur; sürdürülebilir küçük PR'lar tercih edilir.
