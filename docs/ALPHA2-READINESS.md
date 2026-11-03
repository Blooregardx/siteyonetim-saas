# Alpha.2 kaynak sürüm hazırlığı

**SOURCE RELEASE STATUS: ALPHA.2 PUBLISHED — UNCHANGED**

[Alpha.2 kaynak-only yayını](https://github.com/Blooregardx/siteyonetim-saas/releases/tag/v0.1.0-alpha.2) 3 Kasım 2026 16:22:11 UTC'de `c20646fddbc8a7e3dcd45cbc01aacd531c225e4a` commit'inden yayımlandı. Aşağıdaki checklist ve aday kararları tarihsel hazırlık kayıtlarıdır. Binary dağıtımı BLOCKED; bağımsız insan kurulumu PENDING HUMAN VALIDATION.

**EARLY DEVELOPMENT / ALPHA — NOT PRODUCTION READY**

REL-ALPHA2-PREP güncel kontrol noktası: main `54215e73b2744c5cd24962e3956c017ad0a7fc21`; #24 dahil S03-A–F/S04-A–D birleşti. Package/lock 0.1.0-alpha.2, private: true. Alpha.1 korunur; Alpha.2 tag/release yoktur.

DEVELOPMENT ve SOURCE RELEASE READINESS: **INCOMPLETE — son HEAD push ve PR CI kanıtı bekleniyor**. Sonuçlar [doğrulama sözleşmesi](ALPHA2-SOURCE-RELEASE-VALIDATION.md) uyarınca PR açıklamasında kesin SHA ile kaydedilir. Tarihsel READY sonuçları yeni HEAD için kullanılamaz.

**BINARY DISTRIBUTION READINESS: BLOCKED FOR BINARY DISTRIBUTION.** LGPL/MPL, Sharp/libvips ve Node/Debian corresponding-source/notice kapıları açıktır.

- [x] Sürüm metadata’sı birlikte güncellendi; bağımlılık/migration değişmedi.
- [ ] Son HEAD push ve PR checks/selfhost başarılı; gerçek codeload SHA-256/dosya sayısı kaydedilmiş olmalı.
- [ ] Bakımcı kaynak/lisans/TR-EN taslaklarını incelesin.
- [ ] Kesin release commit’i ve tarih ayrı kararla seçilsin; yeni commit varsa tüm kanıtlar yenilensin.
- [ ] Ayrı yayın onayı alınsın. Bu görev tag/release/npm/registry/deploy yapmaz.

Gerçek HTTPS/SMTP, bağımsız insan kurulumu, WAL/PITR, production RPO/RTO, ticari operasyonlar doğrulanmadı. Alpha.1 güncellemesi için [SAFE-UPGRADE](SAFE-UPGRADE.md) ve [BACKUP-OPERATIONS](BACKUP-OPERATIONS.md) uygulanır; reset/down/aktif DB üzerine restore veya otomatik eski imaj yoktur.

## Önceki geliştirme kayıtları — tarihsel bağlam

## Güncel karar — READY FOR MAINTAINER REVIEW

Korunan `e9ed54a786ba3d33e382b6b1208241464b9c5653` commit'i normal fast-forward push ile aynı dala gönderildi; author/committer Blooregardx ve onaylı noreply adresi, eski SHA'lar değişmedi. [Push CI](https://github.com/Blooregardx/siteyonetim-saas/actions/runs/41564379171) ve [PR CI](https://github.com/Blooregardx/siteyonetim-saas/actions/runs/41564385740) tam başarılı: 25/25 birim, 29/29 entegrasyon, 14/14 E2E, build, Prisma generate/validate, temiz 11 migration/schema diff, iki query-plan modu (yalnız Charge kapsamı, 25 ödeme döngüsü), Python 3/3 ve 26 tablo/258.298 satır sentetik restore/ACL/runtime probu. 10.000 daire mobil ilk/ikinci panel push'ta 420/920 ms, PR'da 395/406 ms; üretim SLA'sı değildir.

F-10 için BLOCKED engeli bu DEVELOPMENT kontrol noktasıyla kaldırıldı. Yeni dokümantasyon HEAD'inin hem push hem PR CI'ı da başarılı olmadan bu karar merge/yayımlama için kullanılamaz; son sonuçlar PR açıklamasında doğrulanır. Bu kontrol noktasında PR #20 taslak/açıktı; yukarıdaki S04-D denetiminde birleşmiş olduğu doğrulandı. Alpha.2 tag/release veya staging/production deploy yapılmadı; kullanıcı kararı gerekir. Önceki BLOCKED/READY kayıtları aşağıda tarihsel kanıttır. [Ayrıntılı kanıt](F10-INVESTIGATION.md).

## Tarihsel yeniden açılış — 91dbba7 / BLOCKED

91dbba7 push CI 13/14 E2E ile başarısız oldu; önceki READY kontrol noktası yeniden açıldı. Charge-only kapsam ve sayfa sonrası metadata join düzeltmesi yerelde 25/29/14 ve üç bağımsız 4/4 kabul koşusunu geçti. Yeni commit’in iki CI sonucu beklenir. Aşağıdaki önceki kapanış/READY ifadeleri tarihsel kontrol noktasıdır. [Başarısızlık ve yeni kanıtlar](F10-INVESTIGATION.md). PR taslak kalır; yayın/merge yoktur.


## Tarihsel ace4983 ilk READY kontrol noktası

**READY FOR MAINTAINER REVIEW** — F-10’un kanıtlanan aidat okuma darboğazı giderildi. Düzeltme `ace4983b96b949584d382c0bae468c2e29466bbb` için [push CI](https://github.com/Blooregardx/siteyonetim-saas/actions/runs/41555386707) ve [PR CI](https://github.com/Blooregardx/siteyonetim-saas/actions/runs/41555393666) bütün adımlarıyla başarılıdır. Bu yalnız kaynak kod temelli alpha’nın DEVELOPMENT bakımcı incelemesi kararıdır; yayın/merge yetkisi değildir.

Kanıt: 25/25 birim, **29/29 entegrasyon**, 14/14 E2E; üç bağımsız kabul koşusu 4/4+4/4+4/4; her ölçekte 390×844, ayrık 25 kayıt/tam özet ve çalışan finans/arama kontrolleri. Plan, 60.000 toplam aidatta yalnız 25 ödeme aggregate döngüsünü iki plan türünde doğrular. Build/generate/validate, 11 migration/schema diff, streaming 3/3 başarılı. Yerel restore 26/371.530; iki başarılı CI restore’u 26/258.298 satır, hash/katalog/ACL/runtime izin eşitliğiyle başarılı. [F-10 kök neden ve ölçümler](F10-INVESTIGATION.md).

Sonraki commitler için iki CI kapısı korunur: **son HEAD’in hem push hem PR CI’ı başarılı olmadan** bu karara dayanarak merge/yayımlama yapılmaz. Güncel son HEAD bağlantıları PR açıklaması ve nihai raporda doğrulanır. PR #20 kullanıcı isteğiyle taslak kalır.

## Tarihsel BLOCKED kararı — e02576f / düzeltme öncesi

Aşağıdaki kayıt önceki gözlemi korur; güncel karar yukarıdadır.

> **BLOCKED** — 10.000 daire / 60.000 aidat ikinci sayfa regresyonu son push ve PR CI koşularında başarısız oldu. Yerel 14/14 veya önceki başarılı push bu zorunlu kontrolün yerine geçmez. PR taslak kalmalı; alpha.2 yayımlanmamalıdır.
>
> Engel güvenlik açığı veya finansal veri kaybı olarak kanıtlanmadı: HTTP 200 ve doğru URL’den sonra sayfanın pager/veri bölümü 5 saniyelik assertion süresinde görünmüyor; hata anında document loading ve sıfır tablo satırı kaydedildi. URL assertion’ındaki örtülü load bekleyişi ayrıca kaldırıldı, fakat içerik sorunu iki yeni koşuda sürdü. Alt neden henüz doğrulanmadı. Timeout artırımı, retry ekleme veya test atlama yapılmadı.
>
> Başarılı kanıtlar: yerel 25/25 birim, 28/28 PostgreSQL entegrasyon, 14/14 E2E; lint/typecheck/build/generate/validate; temiz 11 migration, 7→11 ve 10→11 yükseltme; 26 tablo/308.493 satır restore + hash/katalog/ACL/runtime izin eşitliği; üç streaming testi; lisans/SPDX ve 37 Markdown/130 yerel bağlantı kontrolü. İlk push CI da 25/28/14 ve 26/258.144 restore ile başarılıydı. Buna karşılık aynı commitin PR koşusu ve sonraki commitin iki koşusu 13/14 E2E ile başarısızdı; son başarısız koşularda restore adımı çalışmadı.
>
> Audit production 0, dev 16 moderate paket düğümü / tek advisory. Denetlenen kapsamda doğrulanmış P0/P1 yoktur; P2’ler açıkça belgelenmiştir. **Başarısız zorunlu test tek başına bu kararın engelidir.**
>
> Kapanış: sentetik fixture yeniden kullanılmalı; HTTP gövdesinin tamamlanması, server render/DB sorguları ve tarayıcı lifecycle’ı zaman damgalarıyla ilişkilendirilmeli. Alt nedene yönelik küçük güvenli düzeltme ve tam regresyon gerekir. Son commitin hem push hem PR CI başarısı gerekli; rastgele tekrarlarla bir yeşil sonuç elde etmek kapanış değildir. Güncel gerçek bağlantı/sonuçlar PR açıklamasında ve nihai raporda yer alır. Bu belge yayımlama yetkisi değildir.

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
