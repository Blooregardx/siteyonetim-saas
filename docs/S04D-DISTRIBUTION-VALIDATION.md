# S04-D — Temiz kurulum ve topluluk dağıtımı doğrulaması

**DEVELOPMENT: READY FOR MAINTAINER REVIEW — kod kabulü, son HEAD CI kapısı korunur.**

**SOURCE RELEASE READINESS: READY FOR SOURCE-ONLY MAINTAINER REVIEW.** Yayım onayı değildir; kesin source commit/archive, sürüm metadata kararı ve son HEAD CI ayrıca kapıdır.

**BINARY DISTRIBUTION READINESS: BLOCKED FOR BINARY DISTRIBUTION.** LGPL/MPL, Sharp/libvips ve temel imaj karşılık gelen kaynak/bildirim yükümlülükleri tamamlandı iddiası yoktur. Kaynak koddan yerel build, hazır imaj dağıtımı değildir.

Başlangıç main `f81ffe8df881f62a1331913b8bbd16b2f58bc945`; temiz çalışma ağacı, dal `codex/s04-d-community-distribution`. 11 migration, sy_migrator/sy_runtime ve opt-in sy_backup, named volume, audit/financial immutable mekanizmaları incelendi. Finans, auth/onboarding servisleri, tarihsel migration ve LICENSE değiştirilmez.

## Otomatik temiz kaynak kabulü — tamamlanan kod kontrol noktası

Doğrulanan `cd4cedc1cfb51574034c74ed2ea311105588991c` için iki CI completed/success:

| Koşu | checks | temiz clone selfhost + recovery |
|---|---|---|
| [Push 41653356341](https://github.com/Blooregardx/siteyonetim-saas/actions/runs/41653356341) | Başarılı | Başarılı |
| [PR 41653421470](https://github.com/Blooregardx/siteyonetim-saas/actions/runs/41653421470) | Başarılı | Başarılı |

İki selfhost logunda ayrı public Git clone ve gerçek GitHub codeload tar.gz **222 kaynak dosyası** ile aynı commit tree'ye blob/mode bazında eşleşti. Arşiv SHA-256: `8f67bd9071fa98792a9e2d824becd5f3bdb809904c39e4b6ffbe425a2e93bc4c`. Bu hash yalnız bu kod kontrol noktasıdır; dokümantasyon commit'i farklı hash üretir. Son HEAD'in yeniden çalıştırılmış iki CI bağlantısı ve arşiv hash'i [taslak PR #24](https://github.com/Blooregardx/siteyonetim-saas/pull/24) açıklamasında ayrıca kaydedilir; tamamlanmamış job başarı sayılmaz.

Checks: preflight **12/12**, archive policy **4/4**, ESLint/strict TypeScript, **25/25 birim, 36/36 entegrasyon, 19/19 E2E**, production build, Prisma generate/validate, 11 migration/schema diff, source/license/npm audit, iki dashboard query-plan modu, streaming **3/3** ve tarihsel sentetik restore başarılı. Selfhost: gerçek preflight ok=true (SMTP/MAIL_FROM/TLS uyarılarıyla demo-only), negatif kurulum senaryoları, standalone runtime/demo/panel/kurulum, roller, native Prisma/DDL reddi ve restart kalıcılığı başarılı. Backup hata matrisi **12/12** ve yeni encrypted recovery **26 tablo/100.048 satır**; katalog/ACL eşitliği, finans/tenant/audit, restored health ve gerçek başarısız migration'da writers stopped başarılı.

Runtime inventory: Node v24.22.2; 91 Debian paket kaydı; Node LICENSE ve libc6/OpenSSL copyright mevcut. Next16.4.3, Sharp0.35.5, libvips platform paketi1.3.4, PrismaClient6.19.3 kurulu; taranan paket **köklerinde** LICENSE/NOTICE/COPYING dosyası bulunmadı. Bu bütün nested bildirimlerin yokluğu veya tam SBOM değildir; karşılık gelen kaynak/relinking/bildirim kanıtını kapatmaz. Binary kapısı halen BLOCKED.

Bağımsız insan kurulum katılımı **yoktur**. Linux x86-64 ephemeral GitHub runner ve host araçları yeniden kullanılmıştır; uygulama kaynakları, dependency dizini veya önceden hazırlanmış app image'i yeniden kullanılmamıştır. Yerel VFS gerçek kurulum kanıtı olarak kullanılmadı. Alpha.2 tag/release veya binary dağıtımı yapılmadı.

## GitHub güncel durum denetimi

3 Kasım 2026 API kontrolü: PR #11–15, #20 (S03-F), #21 (S04-A), #22 (S04-B), #23 (S04-C) birleşmiş. Önceki “taslak/açık kalır” ifadeleri yalnız o aşamanın teslim kaydıdır; ilgili güncel belgelerin başına birleşme durumu ve tarihsel bağlam kondu. S04-D PR'si ayrı taslak olarak açılacaktır.

Yayımlanmış yalnız `v0.1.0-alpha.1` GitHub prerelease var; etiketi `497c21cf701bf1690f135bb9b0502a7ee203a56e` commit'ine işaret ediyor. Alpha.2 tag/release yok. Package/lock 0.1.0-alpha.1 ve AGPL-3.0-only aynı; sürüm değişikliği yapılmaz. Ayrı yayım kararında 0.1.0-alpha.2 metadata önerilir; alpha.1 üzerine yeni kaynak yayımlanmaz. GitHub private vulnerability reporting etkin olarak yeniden doğrulandı; SLA/LTS/yanıt süresi icat edilmedi.

## Temiz otomatik prova yöntemi

Selfhost job ephemeral GitHub Linux runner'da yalnız bootstrap için actions/checkout kullanır. `clean_install_ci.py`, seçilen head SHA'sını public GitHub'dan **yeni geçici Git clone**'a fetch eder; kaynak workspace/node_modules/.next/.env veya önceden hazırlanmış app imajını kullanmaz. Aynı runner'ın önceden kurulu Git, curl, Python, Docker daemon/Compose ve apt ile kurulmuş age aracı kullanılır; resmi base image/tool cache'i tamamen bağımsız makine/insan kurulumu sayılmaz.

Gerçek codeload tar.gz aynı SHA için ayrıca indirilir. Arşiv extract edilmeden bütün regular blob hash/mode'ları seçilmiş Git tree ile karşılaştırılır: LICENSE canonical SHA, COPYRIGHT, örnekler, build/Compose, migration'lar ve betikler gerekli. Env/secret/age private key/backup/dump/build artefakt dosya adları, symlink/hardlink/path traversal ve temel private-key pattern'leri reddedilir. Bu sınırlı otomatik politika, bütün kaynak kökeni veya bütün gizli bilgi biçimleri için matematiksel kanıt değildir.

Kurulum ve eski selfhost kabulü clone içinden çalışır; tek app/migrate build'i vardır. Aynı clone'un host backup matrisi ve encrypted recovery betiği hazır imajları yeniden kullanır. Önceden bulunan aynı test project/volume/app imajı reddedilir. Cleanup yalnız bu run'ın başta var olmadığı doğrulanan s04a-ci sentetik project'i ve o etiketteki named volume ile recovery betiğinin UUID kaynaklarındadır. Genel prune, kullanıcı cache'i veya gerçek volume onarımı yoktur.

**Bağımsız üçüncü taraf insan kurulumu yapılmadı.** Yeni dizin veya ephemeral runner, insan deneyimi kanıtı değildir. Bağımsız katılımcı geri bildirimi ayrı açık işletim kapısıdır.

## Yeni kontroller ve hata kapsamı

Salt okunur preflight: Linux/Docker/Compose, dosyalar, env syntax, 11 migration kaynağı, PG17 config, eşleşen DB adları, UID1000/GID999/izin/tip/boyut, portsuz DB/loopback app, app güvenlik seçenekleri, HTTPS origin, SMTP/MAIL_FROM eksikliği, port availability ve kaynak/Docker disk eşiği. Secret içerikleri açılmaz/yazdırılmaz; SMTP/TLS teslimi sınanmaz. Default SMTP eksikliği demo-only uyarıdır; --require-mail hata sayar. Yanlış durumda chmod/chown/start/delete/repair yoktur.

Yerel preflight matrisi **12/12**: missing env/secret, permissions, UID/GID, symlink, wrong DB, public ports, PG major, HTTPS, gerçek dolu loopback portu, simulated low disk/daemon/config failure. Docker/Compose JSON ve UID/GID birim testlerinde açık metadata stublarıdır; gerçek CI preflight'i gerçekten oluşturulan dosyaları/daemon'ı kontrol eder. Arşiv politikası **4/4**: tam/ignored env dışarıda, yanlış tracked env reddi, stream sınırındaki key pattern reddi, eksik/değişmiş arşiv reddi.

Gerçek selfhost negatifleri: invalid Dockerfile nonzero (ikinci app build'i yok), DB başlamadan ret, migration öncesi ret, yanlış DB adı, runtime CREATE yanlış yetkisi, NOLOGIN/yarım rol ve tek unfinished sentetik migration kaydı. Cleanup yalnız bu test kaydını kaldırır; 11 tarihsel satır/dosya korunur. Bu kontroller tüm eski PGDATA biçimlerinin onarımı değildir. Port/disk/HTTPS/SMTP negatifleri preflight testindedir; restore/şifreleme anahtarı eksikliği mevcut S04-C gerçek recovery matrisindedir.

Runtime imaj notice audit'i yalnız sürüm/lisans metadatası ve dosya varlığıdır; binary clearance değildir. Sharp/libvips tam source/notice ve LGPL relinking bilgisi, MPL kapsanan dosya kaynakları, Node/Debian/OpenSSL bileşen envanteri dağıtım öncesi açık kalır. Yeni registry push yoktur.

## Yerel ilk kontroller

ESLint/strict TypeScript ve 25 birim başarılı. Preflight 12/12, arşiv politikası 4/4 ve canonical AGPL/479 dependency metadata/51 Markdown-249 yerel link kontrolü geçti. Bu sayı belge eklenince değişebilir. Gerçek yerel preflight ENV_FILE_MISSING, DISK_RESERVE_INSUFFICIENT ve DOCKER_DISK_RESERVE_INSUFFICIENT ile reddetti; VFS uyarısı verdi. Yerel gerçek kurulum denenmiş/başarılı sayılmaz; büyük build burada tekrarlanmaz.

## Zorunlu regresyon ve beklenen kanıt

Mevcut checks: ESLint/strict TypeScript, 25 birim, 36 PG entegrasyon, 19 E2E, production build, Prisma generate/validate, 11 migration/schema diff, tenant/finans/session, iki dashboard query-plan modu, streaming Python 3/3 ve tarihsel synthetic restore korunur. Selfhost: standalone demo/panel/onboarding smoke, non-root/runtime DDL reddi, restart persistence; S04-C: 12 encrypted failure test ve ayrı cluster encrypted restore, ACL/financial/tenant/health ve gerçek başarısız migration güvenli durma korunur. Yeni sonuçlar son HEAD CI'dan kaydedilecektir; çalışan job başarı sayılmaz.

## Açık kapılar ve yayım önerisi

Yalnız source-only alpha.2 adayı bakımcı incelemesine sunulabilir; kesin source commit/archive ve son CI, sürüm metadata değişikliği ve ayrı kullanıcı yayım kararı gerekir. Hazır binary/container dağıtımı engellidir. LICENSE resmî AGPL-3.0-only metni değişmez; kaynak-only otomatik başarı tam hukuki/platform denetimi veya yeni kaynak sunumu iddiası değildir.

Gerçek SMTP/HTTPS/proxy, bağımsız insan kurulumu, Windows/macOS/ARM/rootless, staging/production, MFA/bot/yük/operasyon alarmları ve WAL/PITR ayrıca doğrulanmalıdır. Günlük mantıksal backup RPO/RTO garantisi değildir; ayrı anahtar ve fiziksel backup kopyası gerekir. Alpha.1 etiketi, package/lock, gerçek kullanıcı verisi/SMTP, release/tag/deploy/registry ve merge bu görevde değiştirilmez.
