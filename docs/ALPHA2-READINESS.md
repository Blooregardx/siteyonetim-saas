# v0.1.0-alpha.2 — Hazırlık kararı

**BLOCKED** — 10.000 daire / 60.000 aidat ikinci sayfa regresyonu son push ve PR CI koşularında başarısız oldu. Yerel 14/14 veya önceki başarılı push bu zorunlu kontrolün yerine geçmez. PR taslak kalmalı; alpha.2 yayımlanmamalıdır.

Engel güvenlik açığı veya finansal veri kaybı olarak kanıtlanmadı: HTTP 200 ve doğru URL’den sonra sayfanın pager/veri bölümü 5 saniyelik assertion süresinde görünmüyor; hata anında document loading ve sıfır tablo satırı kaydedildi. URL assertion’ındaki örtülü load bekleyişi ayrıca kaldırıldı, fakat içerik sorunu iki yeni koşuda sürdü. Alt neden henüz doğrulanmadı. Timeout artırımı, retry ekleme veya test atlama yapılmadı.

Başarılı kanıtlar: yerel 25/25 birim, 28/28 PostgreSQL entegrasyon, 14/14 E2E; lint/typecheck/build/generate/validate; temiz 11 migration, 7→11 ve 10→11 yükseltme; 26 tablo/308.493 satır restore + hash/katalog/ACL/runtime izin eşitliği; üç streaming testi; lisans/SPDX ve 37 Markdown/130 yerel bağlantı kontrolü. İlk push CI da 25/28/14 ve 26/258.144 restore ile başarılıydı. Buna karşılık aynı commitin PR koşusu ve sonraki commitin iki koşusu 13/14 E2E ile başarısızdı; son başarısız koşularda restore adımı çalışmadı.

Audit production 0, dev 16 moderate paket düğümü / tek advisory. Denetlenen kapsamda doğrulanmış P0/P1 yoktur; P2’ler açıkça belgelenmiştir. **Başarısız zorunlu test tek başına bu kararın engelidir.**

Kapanış: sentetik fixture yeniden kullanılmalı; HTTP gövdesinin tamamlanması, server render/DB sorguları ve tarayıcı lifecycle’ı zaman damgalarıyla ilişkilendirilmeli. Alt nedene yönelik küçük güvenli düzeltme ve tam regresyon gerekir. Son commitin hem push hem PR CI başarısı gerekli; rastgele tekrarlarla bir yeşil sonuç elde etmek kapanış değildir. Güncel gerçek bağlantı/sonuçlar PR açıklamasında ve nihai raporda yer alır. Bu belge yayımlama yetkisi değildir.

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
