# Alpha.2 kaynak sürüm hazırlığı

**TASLAK — YAYIMLANMADI**

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


## Güncel yayımlama durumu — S03-F / 2 Kasım 2026

[PR #10](https://github.com/Blooregardx/siteyonetim-saas/pull/10) main'e birleştirildi ve [v0.1.0-alpha.1 GitHub Pre-release](https://github.com/Blooregardx/siteyonetim-saas/releases/tag/v0.1.0-alpha.1) yayımlandı. Sürüm **EARLY DEVELOPMENT / ALPHA — NOT PRODUCTION READY** durumundadır.

OpenAI Codex for Open Source başvurusu kullanıcı tarafından gönderildi; kabul sonucu bekleniyor. S03-A–E, PR #11–#15 ile main’e birleşti (son birleşme `afd7ea7bcfe693f06daeea9d48b38b8e1fe27fcc`); mevcut alpha.1 ön sürümüne dahil değildir. Bu dokümantasyon düzeltmesi yeni release/tag veya başvuru oluşturmaz.

## F-10 geliştirme kontrol noktası

- [x] [Kök neden ve sınırlı sorgu düzeltmesi](F10-INVESTIGATION.md): üç bağımsız mobil kabul koşusu, filtre/toplam ve finans korunumu.
- [x] ace4983 için push ve PR CI tam başarılı; 25/29/14, plan sınırı, 11 migration ve restore dahil.
- [ ] Birleştirilecek/yayımlanacak **son HEAD** için iki CI sonucunu yeniden doğrula. PR #20 taslak ve açık kalır; merge/tag/release ayrı kullanıcı kararıdır.

## Alpha.2 için ayrı bakımcı kapısı

- [ ] [S03-F denetimi](S03F-SECURITY-REGRESSION.md) ve [hazırlık kararı](ALPHA2-READINESS.md) incelensin; son commitin push ve PR CI sonuçları doğrulansın.
- [ ] S03-F PR’si kullanıcı kararıyla birleştirilsin; yayımlanacak kesin commit ve kaynak arşivi yeniden kontrol edilsin.
- [ ] [Türkçe](ALPHA2-RELEASE-NOTES-TR.md) / [İngilizce](ALPHA2-RELEASE-NOTES-EN.md) taslaklar, bilinen açıklar ve üçüncü taraf bildirimleri gözden geçirilsin.
- [ ] Ayrı yayımlama onayı alınsın. Bu görev tag/release oluşturmaz; package/lock sürümü `0.1.0-alpha.1` kalır. Mevcut alpha.1 değiştirilmez.

DEVELOPMENT test başarısı STAGING/PRODUCTION onayı değildir. SMTP teslimi, bağımsız insan kurulumu, canlı güvenlik/yük, MFA ve işletim kapıları açık kalır.

## Tarihsel yayımlama öncesi kontrol listesi

Aşağıdaki aday durumu, “tag/release yoktur”, “başvuru gönderilmemiş” ifadeleri ve işaretlenmemiş bakımcı kapıları yayımlama öncesindeki kayıttır. Güncel bekleyen yayımlama işleri olarak okunmamalıdır. Geçmiş kontrol kanıtları geriye dönük değiştirilmedi; üretim/binary dağıtımına ilişkin ek gereksinimler açık kalır.

Aday: **v0.1.0-alpha.1**; statü: **EARLY DEVELOPMENT / ALPHA — NOT PRODUCTION READY**. Bu belge yayımlama yetkisi vermez. Şu anda tag/release yoktur; kullanıcı onayı olmadan oluşturulmaz. Kontrol anı 30 Ekim 2026; yayımlama öncesi yeniden kontrol edilir.

## Tamamlanan hazırlık

- [x] PR #7, #8, #9 main'e ulaşmış; PUBLIC, main-protection ve GitHub Actions checks kuralı doğrulandı.
- [x] AGPL-3.0-only, COPYRIGHT, katkı/güvenlik rehberleri ve bağımlılık envanteri mevcut.
- [x] Paket/lock kök sürümleri alpha adayına hazırlanmış; bağımlılık sürümleri değişmedi.
- [x] Temiz kaynak ve yeni Node 24/PostgreSQL 17 ortamında kurulum/migration/build/E2E provası.
- [x] Ayrı hedefe sentetik yedekten dönüş; veri/audit/finans/migration ve tenant kontrolleri.
- [x] Kaynak kod temelli dağıtım kapsamı ve mevcut eksikler sürüm notlarında yazılı.
- [x] TR/EN başvuru taslakları hazırlanmış; başvuru gönderilmemiş.

## Tarihsel yayımlama öncesi bakımcı kapısı — o aşamada tamamlanmamıştı

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
