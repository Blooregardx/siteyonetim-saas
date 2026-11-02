# v0.1.0-alpha.2 — Hazırlık kararı

**READY FOR MAINTAINER REVIEW** — kaynak kod temelli alpha için yerel DEVELOPMENT kontrolleri başarılı; denetlenen kapsamda doğrulanmış P0/P1 engeli bulunmadı. Bu belge yayımlama yetkisi değildir.

Kanıt: 25/25 birim, 28/28 PostgreSQL entegrasyon, 14/14 Playwright; lint/typecheck/build/generate/validate; temiz 11 migration, 7→11 ve 10→11 yükseltme; 26 tablo/308.493 satır restore + hash/katalog/ACL/runtime izin eşitliği; üç streaming testi; lisans/SPDX ve 37 Markdown/130 yerel bağlantı kontrolü. Audit production 0, dev 16 moderate paket düğümü / tek advisory; P2’ler açıkça belgelenmiştir.

Karar kapısı: son commitin **hem push hem PR CI** koşusu başarılı olmalıdır; gerçek bağlantı ve sonuçlar PR açıklamasında/nihai raporda kaydedilir. Koşular bitmeden veya başarısızsa PR birleştirmeye/yayımlamaya hazır kabul edilmez. Bakımcı son commit ve CI kaynağını ayrıca doğrulamalıdır.

Aday yalnız proje kaynak kodu temelli erken alpha’dır. Yeni tag/GitHub release/binary/konteyner oluşturulmadı. Mevcut v0.1.0-alpha.1 etiketi ve package/lock `0.1.0-alpha.1` sürümü korunur. Main’e doğrudan yazım, force-push, geçmiş/migration yeniden yazımı yapılmaz.

- [Güvenlik ve regresyon kanıtı](S03F-SECURITY-REGRESSION.md)
- [Türkçe sürüm notu taslağı](ALPHA2-RELEASE-NOTES-TR.md)
- [İngilizce sürüm notu taslağı](ALPHA2-RELEASE-NOTES-EN.md)
- [Bakımcı kontrol listesi](RELEASE-CHECKLIST.md)

## Ayrı işletim durumları

- DEVELOPMENT: yalnız sentetik ve izole yerel PostgreSQL 17/SMTP/Chromium doğrulamaları; nihai sonuç kanıt raporunda.
- STAGING: dağıtılmadı, ertelendi.
- PRODUCTION: dağıtılmadı, hazır değil.

Gerçek SMTP teslimi, bağımsız insan kurulumu, canlı güvenlik/üretim yükü, MFA, minimum rol işletimi, yedek şifreleme/saklama/PITR/RPO/RTO, TLS/proxy ve tam izleme/alarmlar doğrulanmadı. Dev minimatch uyarısı, auth trafik koruması, yerel E2E/transaction süre hassasiyeti ve OFFSET/ayrı snapshot sınırlamaları açıktır. LGPL/MPL bileşenleri içeren binary/konteyner dağıtımının ek koşulları karşılanmış sayılmaz. [Ertelenmiş işler](DEFERRED-CLOUD-OPERATIONS.md).

DEVELOPMENT başarısı STAGING/PRODUCTION hazırlığı anlamına gelmez. Önce PR’nin bakımcı incelemesi ve ayrı merge kararı; ardından kesin yayın commit’i, kaynak arşivi/sır/lisans kontrolü ve **ayrı kullanıcı yayımlama onayı** gerekir. Bu görev bunlardan hiçbirini otomatik gerçekleştirmez.
