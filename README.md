# SiteYönetim

Site ve apartman yönetimi için ücretsiz, topluluk katkılarına açık ve kendi sunucusunda barındırılabilir yazılım geliştirme projesi. Depo PUBLIC kalır; ticari abonelik veya ücretli lisans modeli planlanmaz. Next.js App Router, React, strict TypeScript, PostgreSQL ve Prisma 6 mimarisi korunur.

> **Lisans: AGPL-3.0-only.** Bu yazılımı çalıştırabilir, inceleyebilir, değiştirebilir ve lisans koşullarıyla paylaşabilirsiniz. Değiştirilmiş ağ sürümünüzün kullanıcılarına karşılık gelen kaynak kodunu ücretsiz edinme olanağı sunun; dağıtım yükümlülüklerini de koruyun. [Tam lisans](LICENSE), [haklar ve yükümlülükler](docs/LICENSING.md), [üçüncü taraf bileşenler](docs/THIRD-PARTY-LICENSES.md).

Bakımcı: [Blooregardx](https://github.com/Blooregardx). Yazılım ücretsizdir; sunucu barındırma hizmeti veya ücretsiz altyapı garantisi verilmez.

## Güncel durum

Erken geliştirme sürümüdür; üretime hazır olarak işaretlenmemiştir. Kayıt/giriş, e-posta doğrulama, organizasyon ve rol yönetimi, apartman/blok/daire ve kişi ilişkileri, aidat, kısmi tahsilat ve tam tahsilat ters kaydı uygulanmıştır. Ters kayıt gerçek para iadesi değildir. [Güncel özellikler ve eksikler](docs/FEATURES.md).

`/panel` PostgreSQL ve gerçek oturum ister. `/demo` ve `/demo?view=company` açıkça işaretli, veritabanından bağımsız örneklerdir. Otomatik demo hesap/seed yoktur. Gerçek kişi verilerini issue, test veya demo içine eklemeyin.

## Geliştirme ve kendi sunucusunda kurulum

Node.js 24, npm ve PostgreSQL 17 kullanılır. [Kurulum ve işletim rehberi](docs/SELF-HOSTING.md) ortam değişkenlerini, HTTPS/SMTP, migration, yedekleme ve güncelleme sınırlarını açıklar. Mevcut Compose dosyası yalnız yerel geliştirme veritabanıdır; üretim dağıtımı değildir. Bu hazırlık çalışması ücretli servis veya canlı dağıtım gerektirmez.

```sh
npm ci
cp .env.example .env
# .env içine yalnız kendi izole geliştirme bağlantınızı yazın.
npm run db:generate
npm run db:validate
npm run db:deploy
npm run dev
```

`db:deploy` seçilen veritabanını değiştirir; bağlantıyı önce doğrulayın. Demo dışındaki yönetim işlemleri e-posta doğrulaması gerektirir; SMTP olmadan bu adım tamamlanmaz.

## Kontroller

```sh
npm run check
npm run build
```

Entegrasyon ve Playwright yalnız loopback `siteyonetim_test` veritabanında çalışır. [Katkı rehberi](CONTRIBUTING.md) test sırasını ve izole rol gereksinimlerini açıklar. CI migration, birim, entegrasyon, build ve tarayıcı kontrollerini çalıştırır. Başarılı CI, gerçek SMTP teslimi veya üretim güvenliği kanıtı değildir.

## Katkı ve güvenlik

- [CONTRIBUTING](CONTRIBUTING.md): katkı ve inceleme süreci
- [Topluluk ilkeleri](CODE_OF_CONDUCT.md)
- [SECURITY](SECURITY.md): özel güvenlik bildirimi ve destek sınırları
- [Yol haritası](docs/ROADMAP.md), [mimari](docs/ARCHITECTURE.md), [veritabanı](docs/DATABASE.md)
- [GitHub ayarları](docs/GITHUB-SETTINGS.md), [doğrulanabilir bakım kanıtları](docs/OSS-EVIDENCE.md)

Geçmiş S00/S01 raporları tarihsel kayıttır. Güncel özellik durumu FEATURES, öncelikler ROADMAP içindedir. STAGING/PRODUCTION tamamlanmış değildir; [ertelenmiş operasyonlar](docs/DEFERRED-CLOUD-OPERATIONS.md) güvenlik gereksinimi olarak geçerliliğini korur.
