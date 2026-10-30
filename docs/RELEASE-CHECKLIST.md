# İlk topluluk geliştirme sürümü kontrol listesi

Aday: **v0.1.0-alpha.1**; statü: **EARLY DEVELOPMENT / ALPHA — NOT PRODUCTION READY**. Bu belge yayımlama yetkisi vermez. Şu anda tag/release yoktur; kullanıcı onayı olmadan oluşturulmaz. Kontrol anı 30 Ekim 2026; yayımlama öncesi yeniden kontrol edilir.

## Tamamlanan hazırlık

- [x] PR #7, #8, #9 main'e ulaşmış; PUBLIC, main-protection ve GitHub Actions checks kuralı doğrulandı.
- [x] AGPL-3.0-only, COPYRIGHT, katkı/güvenlik rehberleri ve bağımlılık envanteri mevcut.
- [x] Paket/lock kök sürümleri alpha adayına hazırlanmış; bağımlılık sürümleri değişmedi.
- [x] Temiz kaynak ve yeni Node 24/PostgreSQL 17 ortamında kurulum/migration/build/E2E provası.
- [x] Ayrı hedefe sentetik yedekten dönüş; veri/audit/finans/migration ve tenant kontrolleri.
- [x] Kaynak kod temelli dağıtım kapsamı ve mevcut eksikler sürüm notlarında yazılı.
- [x] TR/EN başvuru taslakları hazırlanmış; başvuru gönderilmemiş.

## Yayımlama öncesi bakımcı kapısı — henüz tamamlanmadı

- [ ] OSS-04 PR'sini inceleyip birleştirme kararını ver; son commitin CI sonucunu doğrula.
- [ ] Son commit, paket/lock sürümü ve kullanılacak v0.1.0-alpha.1 adının çakışmadığını doğrula.
- [ ] Kaynak arşivini node_modules/.next/.env/yedek/fixture içermeyecek biçimde kontrol et; secret taramasını son committe tekrarla.
- [ ] LICENSE/COPYRIGHT ve üçüncü taraf rehberi arşivde; gerçek üçüncü taraf içerik eklenmişse ona ait LICENSE/NOTICE/kaynak koşulları karşılanmış olmalı.
- [ ] Sürüm notlarında bağımsız insan kurulumu, gerçek SMTP veya production hazırlığı iddiası olmadığını kontrol et.
- [ ] Kullanıcıdan **ayrı yayımlama onayı** al; ancak sonrasında prerelease/tag oluşturma işlemini planla. Bu görevde oluşturma.

## Üretim veya binary/konteyner dağıtımı için ek kapı

Bu aday bunlara hazır değildir: bağımsız kullanıcı kurulumu, TLS/proxy ve gerçek SMTP/SPF/DKIM/DMARC, minimum DB rollerinin işletim doğrulaması, şifreli yedek/PITR ve RPO/RTO tatbikatı, üretim güvenliği/yük/bot testleri, MFA değerlendirmesi, işletim/izleme/alarmlar; dağıtılan bütün LGPL/MPL bileşenlerin gerçek sürüm kaynakları ve bildirimleri. Hiçbiri ücretli sağlayıcı açılarak otomatik tamamlanmış sayılmaz.

## Ayrı bakım işleri

ESLint 9 destek uyarısı; Actions v4 Node çalışma zamanı ve ubuntu-latest değişimi; PostgreSQL 17-alpine etiketinin güncelleme/digest politikası. Büyük sürüm yükseltmesi bu hazırlığa eklenmez. Tarihsel migration SQL'i kozmetik nedenle değiştirilmez.
