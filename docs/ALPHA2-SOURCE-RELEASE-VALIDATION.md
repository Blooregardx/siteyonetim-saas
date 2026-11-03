# Alpha.2 kaynak sürüm doğrulaması

**TASLAK — YAYIMLANMADI**

**EARLY DEVELOPMENT / ALPHA — NOT PRODUCTION READY**

Başlangıç main SHA: `54215e73b2744c5cd24962e3956c017ad0a7fc21` (#24 birleşmesi). GitHub/public ve yerel origin/main eşleşti. Açık PR’lerde başka Alpha.2 hazırlığı yoktu. Alpha.1 tag: `497c21cf701bf1690f135bb9b0502a7ee203a56e`; mevcut prerelease korunur. Alpha.2 tag/release bulunmadı.

Package, lock kökü ve lock packages[""] sürümleri: **0.1.0-alpha.2**. private: true ve AGPL-3.0-only korunur. Bağımlılıklar ve 11 tarihsel migration değişmez. CI `verify-source-readiness.py` metadata eşitliğini/private/lisansı; `verify_distribution.py` aynı koşulları gerçek arşiv içinden doğrular.

## Aday commit ve değişmez kanıt kaydı

Aday, bu belgeyi içeren dalın son HEAD SHA’sıdır; kesin yayın commit’i değildir. Son SHA, gerçek codeload SHA-256, dosya sayısı ve son HEAD push/PR CI bağlantıları **taslak PR açıklamasında ve Codex nihai raporunda** birlikte kaydedilir. Commit kendi SHA/arşiv hash’ini içeremez; hash’i belgeye eklemek yeni commit ve yeni arşiv yaratır. Bu nedenle bu belge doğrulama sözleşmesidir; önceki S04-D hash’i Alpha.2 kanıtı değildir.

DEVELOPMENT: **INCOMPLETE — son HEAD CI sonuçları dış kanıt kaydında doğrulanmalı**.
SOURCE RELEASE READINESS: **INCOMPLETE — son HEAD arşiv ve CI kapıları dış kanıt kaydında doğrulanmalı**.
BINARY DISTRIBUTION READINESS: **BLOCKED FOR BINARY DISTRIBUTION**.

Yeni commit gelirse önceki sonuçlar yeterli değildir: SHA, arşiv hash’i/dosya sayısı, temiz checkout ve iki CI yeniden doğrulanır. Başarısız/çalıştırılmayan test başarılı sayılamaz.

## Alpha.1 sonrası doğrulanmış kapsam

Git first-parent geçmişi ve GitHub merged PR kayıtları eşleştirildi; aşağıdaki uygulama dosyaları incelendi. Tasarlanmış işler özellik sayılmadı.

| Aşama | Birleşmiş PR | Kod / sürüm kanıtı |
|---|---|---|
| S03-A toplu aidat | [#11](https://github.com/Blooregardx/siteyonetim-saas/pull/11) | src/lib/bulk-charges.ts, src/app/panel/bulk-actions.ts |
| S03-B borç/tahsilat | [#12](https://github.com/Blooregardx/siteyonetim-saas/pull/12) | src/lib/reports.ts, src/lib/report-queries.ts |
| S03-C gelir/gider | [#13](https://github.com/Blooregardx/siteyonetim-saas/pull/13) | src/lib/income-expenses.ts |
| S03-D finansal rapor | [#14](https://github.com/Blooregardx/siteyonetim-saas/pull/14) | src/lib/financial-reporting.ts, src/app/raporlar/csv/route.ts |
| S03-E panel ölçeği | [#15](https://github.com/Blooregardx/siteyonetim-saas/pull/15) | src/lib/dashboard-reads.ts |
| S03-F güvenlik/performans | [#20](https://github.com/Blooregardx/siteyonetim-saas/pull/20) | financial_immutability migration, scripts/verify-dashboard-query-plan.ts, F10-INVESTIGATION.md |
| S04-A Docker | [#21](https://github.com/Blooregardx/siteyonetim-saas/pull/21) | Dockerfile, compose.selfhost.yaml, S04A-VALIDATION.md |
| S04-B kurulum | [#22](https://github.com/Blooregardx/siteyonetim-saas/pull/22) | src/lib/onboarding.ts, S04B-ONBOARDING-VALIDATION.md |
| S04-C şifreli backup/recovery | [#23](https://github.com/Blooregardx/siteyonetim-saas/pull/23) | scripts/backup_ops.py, scripts/safe_upgrade.py, S04C-BACKUP-VALIDATION.md |
| S04-D topluluk | [#24](https://github.com/Blooregardx/siteyonetim-saas/pull/24) | scripts/clean_install_ci.py, scripts/verify_distribution.py, S04D-DISTRIBUTION-VALIDATION.md |

Kanıt belgeleri docs/ altındadır. TR/EN notları taslaktır; tarih/son release commit’i atanmadı.

## Arşiv ve CI yöntemi

Public GitHub’dan tam 40 haneli SHA ile yeni geçici checkout ve aynı SHA için codeload tar.gz indirilir. Mevcut `verify_distribution.py` her dosyayı Git tree blob SHA-1/mode ile karşılaştırır; dosya kümesi tam eşit olmalı. LICENSE canonical SHA-256, COPYRIGHT varlığı, 11 migration, Docker/Compose, kurulum/backup/update dosyaları ve package/lock/private kontrol edilir. Traversal/link/özel dosya, gerçek env, secrets, anahtar, backup/dump, upload/kullanıcı verisi ve build artefaktları politikayla reddedilir. Anahtar pattern taraması sınırlı bir kontroldür, kapsamlı secret/köken ispatı değildir.

Son arşivin gerçek SHA-256 değeri bütünlüğü tanımlar; yayımlayan kişinin kimliğini kanıtlayan imza değildir. Hazır binary/imaj/çalıştırılabilir dağıtım paketi eklenmez.

Mevcut checks/selfhost gevşetilmez: ESLint, strict TS, birim, PG entegrasyon/tenant/finans/audit, Playwright, production build, Prisma validate/generate, 11 migration/schema diff, iki dashboard query-plan modu, streaming testleri, preflight/archive politika, temiz Docker selfhost, backup hata matrisi, ayrı cluster encrypted recovery, restore sonrası health ve migration hatasında writers-stopped kapıları korunur. Yalnız izole siteyonetim_test/sentetik veri; gerçek SMTP/müşteri verisi yoktur.

## Kaynak/lisans envanteri ve karar sınırı

Arşivde tracked uygulama/test kaynakları (src/, tests/), Prisma schema/11 migration, scripts/, docker/ ve systemd örnekleri, Dockerfile/Compose tarifleri, manifest/lock, CI/depo yapılandırması ve dokümantasyon bulunur. Kesin dosya envanteri adayın `git ls-tree -r --name-only SHA` çıktısıdır; arşiv doğrulaması birebir eşitliği zorunlu kılar. npm bağımlılık kodu, node_modules, base image, libvips/Sharp binaryleri veya browser eklenmez; tarifler hazır imaj değildir.

LICENSE, COPYRIGHT, docs/LICENSING.md, docs/THIRD-PARTY-LICENSES.md, docs/DEPENDENCY-LICENSES.csv, CONTRIBUTING.md ve SECURITY.md incelendi; değiştirilmeden korunur. Özgün kod AGPL-3.0-only; üçüncü taraf envanteri/bildirimleri arşivde kalır. Yeni vendored üçüncü taraf kod/binary eklenmedi; eklenirse ayrı yükümlülük incelemesi gerekir. Kaynak-only bakımcı incelemesi hazır Docker imajı yayım izni değildir. Sharp/libvips LGPL/MPL ve Node/Debian corresponding-source/notice/relinking kanıtları tamamlanmış sayılmaz.

## Güvenlik ve işletim sınırları

Alpha.1 → Alpha.2 salt paket yükseltmesi değildir. [SAFE-UPGRADE](SAFE-UPGRADE.md) ve [BACKUP-OPERATIONS](BACKUP-OPERATIONS.md): incelenmiş ileri migration zinciri, şifreli yedek, ayrı boş cluster restore provası, kontrollü güncelleme gerekir. Reset/down migration, tarihsel SQL değişimi, canlı otomatik migration, mevcut DB üzerine restore veya otomatik eski imaj başlatma yoktur.

Test edilmiş otomasyon Linux x86-64/Node24/PG17/Prisma6/Docker Compose v2 içindir. ARM/macOS/Windows/rootless, bağımsız insan kurulumu, gerçek HTTPS/SMTP, staging/production, MFA/bot/internet yükü, WAL/PITR, production RPO/RTO ve ticari operasyon/SLA doğrulanmadı. age anahtar kaybı geri dönüşü engeller; ayrı güvenli anahtar/backup kopyası gerekir. OFFSET/sayfalar arası snapshot sınırları sürer; production garantisi verilmez.

Ayrı bakımcı kaynak incelemesi, merge kararı ve daha sonra ayrı yayın onayı gerekir. Bu görev yalnız taslak PR hazırlar; tag/GitHub Release/npm publish/registry push/deploy yapmaz.
