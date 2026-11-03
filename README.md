# SiteYönetim

## S04-A güncel karar

Supabase kullanılmayacak. Ücretsiz, PUBLIC, AGPL-3.0-only ve kendi sunucusunda kurulum önceliği korunur; ücretli servis zorunlu değildir. Sunucu/alan adı/e-posta maliyeti işletmeciye bağlıdır. Ayrı `compose.selfhost.yaml` ve [Docker kurulum rehberi](docs/SELF-HOSTING-DOCKER.md) eklendi; `compose.yaml` geliştirme içindir. DEVELOPMENT doğrulaması üretim onayı değildir. S04-B web kurulum sihirbazı, S04-C yedek işletimi ayrı aşamalardır. Aşağıdaki eski durum raporları tarihsel bağlamıyla korunur. S04-A sonuçları S04A-VALIDATION belgesindedir.

Site ve apartman yönetimi için ücretsiz, topluluk katkılarına açık ve kendi sunucusunda barındırılabilir yazılım geliştirme projesi. Depo PUBLIC kalır; ticari abonelik veya ücretli lisans modeli planlanmaz. Next.js App Router, React, strict TypeScript, PostgreSQL ve Prisma 6 mimarisi korunur.

> **Lisans: AGPL-3.0-only.** Bu yazılımı çalıştırabilir, inceleyebilir, değiştirebilir ve lisans koşullarıyla paylaşabilirsiniz. Değiştirilmiş ağ sürümünüzün kullanıcılarına karşılık gelen kaynak kodunu ücretsiz edinme olanağı sunun; dağıtım yükümlülüklerini de koruyun. [Tam lisans](LICENSE), [haklar ve yükümlülükler](docs/LICENSING.md), [üçüncü taraf bileşenler](docs/THIRD-PARTY-LICENSES.md).

Bakımcı: [Blooregardx](https://github.com/Blooregardx). Yazılım ücretsizdir; sunucu barındırma hizmeti veya ücretsiz altyapı garantisi verilmez.

## Güncel durum

**EARLY DEVELOPMENT / ALPHA — NOT PRODUCTION READY.** Main geçişi PR #9 ile tamamlandı. `v0.1.0-alpha.1` kaynak kod temelli ön sürüm olarak yayımlandı. S03-A–E, PR #11–#15 ile main’e alındı; mevcut alpha.1 etiketine dahil değildir. `v0.1.0-alpha.2` yalnız hazırlık adayıdır; [S03-F kararı](docs/ALPHA2-READINESS.md) ayrı bakımcı onayı gerektirir. [Sürüm notu taslağı](docs/RELEASE-NOTES-v0.1.0-alpha.1.md) ve [yayın kontrol listesi](docs/RELEASE-CHECKLIST.md). Kayıt/giriş, e-posta doğrulama, organizasyon ve rol yönetimi, apartman/blok/daire ve kişi ilişkileri, aidat, kısmi tahsilat ve tam tahsilat ters kaydı uygulanmıştır. Ters kayıt gerçek para iadesi değildir. [Güncel özellikler ve eksikler](docs/FEATURES.md).

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

## OSS-04 doğrulama durumu

Temiz kaynak ve ayrı Node 24/PostgreSQL 17 konteynerlerinde otomatik kurulum ve sentetik yedekten dönüş provası yapıldı. Bu aynı bakımcı tarafından yürütülen izole testtir; bağımsız insan kurulumu, gerçek SMTP teslimi veya üretim işletimi değildir. [Kanıtlar](docs/OSS04-VALIDATION.md), [geri yükleme](docs/BACKUP-RESTORE.md), [başvuru hazırlığı](docs/OSS-APPLICATION.md). Başvuru gönderilmedi.
