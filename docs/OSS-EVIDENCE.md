# Güncel okuma notu — OSS-04

PR #7–#9 birleşmiş, AGPL main üzerinde; zorunlu checks etkin. Aşağıdaki OSS-01/01B/02 kayıtları kendi tarihindeki durumları korur. Son kanıt [OSS04-VALIDATION](OSS04-VALIDATION.md), başvuru taslakları [OSS-APPLICATION](OSS-APPLICATION.md), yayımlanmamış aday [sürüm notları](RELEASE-NOTES-v0.1.0-alpha.1.md) içindedir.

# Doğrulanabilir geliştirme ve bakım kanıtları

30 Ekim 2026 başlangıç anlık görüntüsü; sayılar sürekli güncellenen başarı iddiası değildir. OSS-01 geliştirme dalından türetilir; main'e merge edilmez.

| Kanıt | Bağlantı / durum |
|---|---|
| Başlangıç temeli | [37484de](https://github.com/Blooregardx/siteyonetim-saas/commit/37484de9e7561a37f7e947769b115cc77f28b80d) |
| Organizasyon/yetki | [e8c45e9](https://github.com/Blooregardx/siteyonetim-saas/commit/e8c45e93bf5377abff8dac60998bbf591d7d99f1) |
| DB oturum ve UI | [ce7ad44](https://github.com/Blooregardx/siteyonetim-saas/commit/ce7ad446f2c6afbc45f185d17f4a68fd8c078941) |
| E-posta/yetki/audit | [4edb9df](https://github.com/Blooregardx/siteyonetim-saas/commit/4edb9df51d9ff30ad1076a325ac3837fa044792d) |
| Tam ters kayıt | [775bd2c](https://github.com/Blooregardx/siteyonetim-saas/commit/775bd2ce94619587f28c55496648388f50b82cbd) |
| Kişi/daire ilişkileri | [04f83e6](https://github.com/Blooregardx/siteyonetim-saas/commit/04f83e6fc0814d2b0ee8fcc413d844c301b90cc7) |
| Önceki başarılı geliştirme CI | [40538830061](https://github.com/Blooregardx/siteyonetim-saas/actions/runs/40538830061); yalnız 04f83e6 için kanıt |
| Bağımlılık bakımı | [PR listesi](https://github.com/Blooregardx/siteyonetim-saas/pulls): başlangıçta 6 açık Dependabot PR; insan incelemesi veya çözülmüş kullanıcı sorunu sayılmaz |

Başlangıçta 8 dal, dallardan erişilen 13 commit, 0 yıldız/fork ve yayımlanmış release yoktu. İndirme, kurulu kullanıcı veya ekosistem etkisi doğrulanmadı. Proje erken geliştirme aşamasındadır. PR/CI dosyası varlığı testin geçtiği anlamına gelmez; OSS-01'in kendi kontrolleri PR üzerinde ayrıca raporlanır.

## Başvuru hazırlığı

[Resmî program](https://developers.openai.com/community/codex-for-oss) aktif bakım, anlamlı kullanım veya ekosistem önemini değerlendirir. Tarihsel OSS-01 başlangıcında lisans kararı, özel güvenlik kanalı, dal koruması ve ilk topluluk sürümü bekliyordu. Güncel OSS-01B durumu aşağıda ayrıdır. Başvuru yapılmadı; kabul garantisi yoktur.

Gelecek kanıtlar: gerçek PR incelemeleri, sorun sınıflandırma/çözümleri, sürüm notları, izole kurulum/geri yükleme sonuçları. Katkı veya kullanım sayıları üretilmez. Codex için önerilen bakım işleri test/PR incelemesi, güvenlik regresyonları, migration kontrolü ve belge tutarlılığıdır; finans değişiklikleri insan incelemesini korur.

## OSS-01 yerel doğrulama — 30 Ekim 2026

Taban `04f83e6`; uygulama/migration/test kaynakları değiştirilmedi. Node 24.19.0, Prisma 6.19.3, ayrı loopback PostgreSQL 17 test konteyneri ve sentetik SMTP kullanıldı.

| Kontrol | Sonuç |
|---|---|
| Prisma generate / validate | Başarılı |
| Sıfırdan migration | 7 migration başarılı; yalnız siteyonetim_test |
| ESLint / TypeScript | Başarılı |
| Birim | 8/8 başarılı |
| PostgreSQL entegrasyon | 16/16 başarılı; ayrı runtime/migration rol izinleri dahil |
| Next.js build | Başarılı |
| Playwright | 4/4 başarılı |
| npm audit | 0 bildirilen zafiyet; tüm risklerin yokluğu garantisi değil |
| Markdown yerel bağlantılar / YAML parse / diff whitespace | Başarılı |

Yerel `playwright install --with-deps chromium` root yetkisi nedeniyle başarısız oldu. Ardından `playwright install chromium` ile tarayıcı kuruldu; mevcut sistem kitaplıklarıyla 4 test geçti. Güvenlik denetimi atlanmadı: kötü origin isteğinin reddi E2E'nin beklenen davranışıdır. npm kurulumunda ESLint 9.39.5 için destek dışı uyarısı görüldü; bu PR bağımlılık sürümlerini değiştirmez, ayrı uyumluluk işi gerekir.

Bu sonuçlar yeni GitHub CI çalışmasının yerine geçmez; PR kontrolleri ayrıca incelenmelidir. Gerçek SMTP teslimi, canlı yük, bağımsız self-host kurulumu ve yedekten dönüş bu doğrulamanın parçası değildir. Tam geçmiş taraması önceki salt okunur denetimdir; OSS-01 yeni bir eksiksiz sızma testi iddiası taşımaz.

## OSS-01B GitHub son kontrolü — 30 Ekim 2026

Önceki denetim ve test kanıtları korunmuştur. Kullanıcının yaptığı ayarlar API üzerinden doğrulandı: depo PUBLIC, Private Vulnerability Reporting açık, main-protection (26175642) aktif; varsayılan dal main için silme/force-push engeli ve PR zorunluluğu var. Zorunlu CI kuralı henüz yok; onay sayısı 0 ve konuşma çözümü zorunlu değil. [Ayrıntılı güncel durum](GITHUB-SETTINGS.md).

OSS-01'in `eae64e3` commitine ait [PR CI](https://github.com/Blooregardx/siteyonetim-saas/actions/runs/40987146798) ve [push CI](https://github.com/Blooregardx/siteyonetim-saas/actions/runs/40987123938) başarılıdır. Bunlar OSS-01B commitinin CI sonucu yerine kullanılmaz; yeni sonuç PR #7 üzerinde ayrıca doğrulanır.

OSS-01B yalnız SECURITY, GitHub ayarları, yol haritası ve bu kanıt belgesini günceller. Uygulama, workflow, bağımlılıklar, migration ve test kaynakları değişmez. LICENSE oluşturulmaz; lisans kullanıcı kararı bekler. İlk topluluk sürümü, zorunlu CI ve bağımsız kurulum/geri yükleme doğrulaması açık kalır. Bu hazırlık PR'sinin birleştirilebilirliği, başvuru/üretim hazırlığından ayrı değerlendirilir.

## Güncel OSS-02 — 30 Ekim 2026

PR #7 geliştirme dalına `fe75208b5592124f91d846ac085f7df59fc615bd` commit'iyle birleştirildi. OSS-02 bu güncel tabandan ayrı dalda hazırlanır. Kullanıcı commitlerdeki eski yazar hesabının da kendisine ait olduğunu doğruladı ve AGPL-3.0-only lisanslamasını onayladı. Güncel bakımcı kimliği Blooregardx'tir; eski commitler değiştirilmez. Yukarıdaki lisans bekleme ifadeleri yalnız OSS-01/OSS-01B tarihsel kayıtlarıdır.

LICENSE GNU resmî metnidir; COPYRIGHT ve package metaverisi AGPL-3.0-only seçimini belirtir. Bağımlılık incelemesi THIRD-PARTY-LICENSES.md ve CSV envanterindedir. PR #7 dışındaki birleştirilmiş dış katkı PR'si incelemede görülmedi. Uygulama özellikleri ve DB şeması değişmez. Son OSS-02 test/CI sonuçları yeni PR'de doğrulanır; önceki başarılar yeni commitin kanıtı sayılmaz.

Main-protection korunur; zorunlu CI kontrolü henüz eksiktir. OSS-02 PR'sinin geliştirme dalına alınması sonrası main geçişi ayrı PR olmalıdır. Sıfırdan ve mevcut main şemasından yükseltme, 16 entegrasyon, 4 E2E ve build kanıtları son birleşecek commit için kontrol edilmelidir. Geçmiş migration dosyaları değiştirilmez, reset/seed/production deploy yapılmaz.

Başvuru öncesi kalanlar: OSS-02 lisanslı PR'nin birleşmesi, main geçişinin ayrı incelemesi, zorunlu CI, ilk topluluk sürümü ve doğrulanabilir bakım/kullanım kanıtlarının büyümesi. Bağımsız self-host/yedekten dönüş ve üretim işletimi doğrulanmış değildir. Ücretli altyapı başvuru şartı değildir; başvuru yapılmış veya kabul edilmiş sayılmaz.

### OSS-02 yerel doğrulama

30 Ekim 2026: ESLint/TypeScript, 8 birim, 16 PostgreSQL entegrasyon, 4 Playwright E2E, Prisma generate/validate ve production build başarılı. Temiz test DB'sinde 7 migration uygulandı. Ayrı test şemasında main'in ilk migration'ı ve sentetik eski kullanıcı/site kayıtları oluşturuldu; ilk migration baseline olarak işaretlenip kalan 6 migration uygulandı. Kullanıcı/site korundu, eski hesaba otomatik e-posta doğrulaması verilmedi. Bu sınırlı yükseltme provası tüm gerçek veri şekillerinin testi değildir.

LICENSE resmî GNU metniyle bayt düzeyinde eşit: SHA-256 `0d96a4ff68ad6d4b6f1f30f713b18d5184912ba8dd389f86aa7710db079abcb0`. İkinci indirme kontrolünde geçici HTTP 503 alındı; yeniden denemede karşılaştırma başarılı oldu. SPDX ve 479 kayıtlık CSV/kilit eşleşmesi, değişmeyen bağımlılık grafiği, Markdown bağlantıları ve diff whitespace doğrulandı. npm audit 0 bildirim döndürdü; bu kapsamlı güvenlik garantisi değildir. Tam paket/platform dağıtım uyumu için üçüncü taraf belgesindeki release kontrolleri açık kalır.

.mailmap kontrolü eski yazar kimliğini Blooregardx'e eşler; ham commit SHA/yazar metaverisi değişmez. GitHub'ın eski commit/PR önbelleği veya Contributors görünümünden diğer hesabın tamamen silindiği iddia edilmez. Kullanıcı geçmiş yazımına izin vermiştir; main koruması ve ayrı main PR sınırları nedeniyle bu OSS-02 geçmişi yeniden yazmaz.

## OSS-03 main geçişi ve OSS-04

[PR #9](https://github.com/Blooregardx/siteyonetim-saas/pull/9) main 55a27f1 ile sonuçlandı. [PR #7](https://github.com/Blooregardx/siteyonetim-saas/pull/7), [PR #8](https://github.com/Blooregardx/siteyonetim-saas/pull/8) birleşmiş; [OSS-03 CI](https://github.com/Blooregardx/siteyonetim-saas/actions/runs/40996143750) başarılı. Bunlar OSS-04 son commitinin CI sonucu yerine kullanılmaz. 30 Ekim 2026 başlangıcında 0 yıldız/0 fork, release/tag yoktu; indirme/aktif kullanıcı/üretim müşterisi/dış katkıcı veya dış kullanım kanıtı doğrulanmadı. Güncel sayılar başvuru öncesi tekrar okunmalıdır. Yeni bakım kanıtı izole kurulum, kurtarma betikleri ve tekrarlanabilir CI kontrolüdür; bağımsız insan kurulumu değildir.
