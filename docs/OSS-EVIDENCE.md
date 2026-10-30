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
