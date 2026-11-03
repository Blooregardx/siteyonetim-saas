# SiteYönetim

Site ve apartman yönetimi için **ücretsiz, açık kaynaklı ve kendi sunucusunda kurulabilir** yazılım. Next.js, strict TypeScript, PostgreSQL 17 ve Prisma 6 kullanır. Supabase, abonelik veya lisans anahtarı gerekmez. Sunucu, alan adı ve e-posta maliyeti işletmeciye bağlıdır.

**EARLY DEVELOPMENT / ALPHA — PRODUCTION-READY DEĞİLDİR.** Yayımlanmış sürüm v0.1.0-alpha.1'dir; yeni S03/S04 geliştirmeleri incelenmiş main kaynak commit'lerindedir. Alpha.2 yalnız hazırlık adayıdır; bu çalışma release/tag veya hazır Docker imajı yayımlamaz.

## İlk kez kuruyorsanız

[SiteYönetim’i Docker ile Kur — Adım Adım](docs/COMMUNITY-INSTALLATION.md)

Linux/Docker → güvenli örnek yapılandırma/secret → salt okunur ön kontrol → DB → ayrı migration → app health → HTTPS/SMTP → hesap doğrulama ve `/kurulum`. Host Node/npm kurulumu Docker yolunda gerekmez. Otomatik admin/demo parolası yoktur. `/demo` açıkça işaretli sentetik örnektir; `/panel` gerçek oturum ve yetki gerektirir.

- [Sorun giderme ve güvenli log paylaşımı](docs/TROUBLESHOOTING.md)
- [Şifreli yedek, anahtar ve ayrı restore](docs/BACKUP-OPERATIONS.md)
- [Korumalı güncelleme](docs/SAFE-UPGRADE.md)
- [Özellikler ve eksikler](docs/FEATURES.md), [yol haritası](docs/ROADMAP.md)

Docker altyapısı S04-A, uygulama içi kurulum S04-B, backup/update araçları S04-C ile main'e alındı. Otomatik temiz kaynak provası bağımsız insan kurulumu değildir. [S04-D kanıtı ve dağıtım sınırları](docs/S04D-DISTRIBUTION-VALIDATION.md).

## Katkı ve güvenlik

[CONTRIBUTING](CONTRIBUTING.md), [SECURITY](SECURITY.md), [topluluk ilkeleri](CODE_OF_CONDUCT.md). Geliştirmede Node 24 ve izole PostgreSQL 17 kullanılır. Testler yalnız siteyonetim_test ve sentetik veridedir; gerçek müşteri verisini issue/PR/log'a eklemeyin. Gönüllü alpha geliştirme desteği vardır, SLA/LTS taahhüdü yoktur.

**AGPL-3.0-only.** [LICENSE](LICENSE), [COPYRIGHT](COPYRIGHT), [kaynak sunma yükümlülükleri](docs/LICENSING.md). Kaynak kod-only dağıtım ile binary/container dağıtımı farklıdır. **BLOCKED FOR BINARY DISTRIBUTION:** Sharp/libvips, LGPL/MPL ve temel imaj bildirim/karşılık gelen kaynak kanıtları tamamlanmadı. [İnceleme](docs/THIRD-PARTY-LICENSES.md).

Bakımcı: [Blooregardx](https://github.com/Blooregardx). [Alpha.2 yayın ve hazırlık kaydı](docs/ALPHA2-READINESS.md), [önceki README tarihçesi](docs/README-BEFORE-S04D.md). Staging/production, gerçek SMTP/TLS, bağımsız insan kurulumu ve WAL/PITR ayrı doğrulama gerektirir.

## S05-A geliştirme denetimi

SOURCE RELEASE STATUS: ALPHA.2 PUBLISHED — UNCHANGED. Hazır imaj dağıtımı BLOCKED; bağımsız insan kurulumu PENDING HUMAN VALIDATION. Bu geliştirme çalışmasının son HEAD test kararı [S05-A raporunda](docs/S05A-DISTRIBUTION-COMPLIANCE-VALIDATION.md), [binary kapıları](docs/BINARY-DISTRIBUTION-GATES.md) ve [insan kurulum formunda](docs/INDEPENDENT-INSTALLATION-CHECKLIST.md) izlenir. Önceki hazırlık kararları tarihsel kayıttır.
