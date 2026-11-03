# S05-A dağıtım uyumluluğu doğrulaması

DEVELOPMENT: INCOMPLETE — son HEAD zorunlu CI sonuçları henüz doğrulanmadı.

SOURCE RELEASE STATUS: ALPHA.2 PUBLISHED — UNCHANGED

BINARY DISTRIBUTION READINESS: BLOCKED

INDEPENDENT INSTALLATION: PENDING HUMAN VALIDATION

## Başlangıç ve kapsam

Main HEAD ve doğrudan Alpha.2 tag commit'i `c20646fddbc8a7e3dcd45cbc01aacd531c225e4a` olarak GitHub API'den doğrulandı. Release 3 Kasım 2026 16:22:11 UTC'de yayımlanmış kaynak-only prerelease; assets boş. Açık #3/#5/#6/#16–19 bağımlılık PR'ları, aynı kapsamda açık PR yok. Başlangıç çalışma ağacı temiz; AGENTS.md, güvenlik kuralları ve istenen dağıtım dosyaları incelendi. Lisans ve tarihsel migration'lar değişmedi. Staging/production doğrulanmadı.

## Araç ve kanıt sınırları

Syft 1.18.1 Linux amd64 açık kaynak aracının tarball SHA-256 değeri upstream checksums dosyasıyla doğrulandı ve kolektöre sabitlendi: `066c251652221e4d44fcc4d115ce3df33a91769da38c830a8533199db2f65aab`. Bu bütünlük kontrolüdür, bağımsız yayıncı imzası değildir. CycloneDX JSON ve kimlik doğrulaması için Syft JSON, yalnız gerçek yerel Docker imajından üretilir. Runtime ve migrate ayrı taranır. CI mevcut selfhost build'lerini yeniden kullanır; yeni build eklemez. Artifacts dosyaları son HEAD push/PR job'larından incelenmelidir.

Kolektör boş kanıtla BLOCKED bekler; bu beklenti CI'da başarılı olsa bile binary dağıtım onayı değildir. Otomatik kontrol, bakımcının kaynak/notice kanıtını gerçekten incelemesinin yerini almaz. [Kapı sözleşmesi](BINARY-DISTRIBUTION-GATES.md).

## Ön bulgular — imaj kanıtı yerine kullanılamaz

Host lock kurulumu Sharp 0.35.5, `@img/sharp-libvips-linux-x64` 1.3.4 ve iç `versions.json`/Sharp API libvips 8.18.7 gösterdi. Paket sürümü 1.3.4 libvips sürümü değildir. Diğer platformların lock kayıtları runtime'da varlık kanıtı değildir. Gerçek imaj taraması ve checksum ayrı gereklidir.

| Bileşen | Kaynak/kanıt adayı | Karar / eksik |
|---|---|---|
| Sharp / libvips | https://github.com/lovell/sharp / https://github.com/lovell/sharp-libvips / https://github.com/libvips/libvips | BLOCKED: 8.18.7 kaynak eşleşmesi, build tarifi, tüm bundled bağımlılık source/notice ve yeniden bağlama provası tamamlanmadı |
| Node / bundled third party | https://github.com/nodejs/node | BLOCKED: kesin imaj Node sürümüyle kaynak ve tüm üçüncü taraf bildirim eşleşmesi gerekli |
| Debian libc/OpenSSL/diğerleri | https://sources.debian.org/ | BLOCKED: dpkg binary/source sürüm envanteri ve aynı kaynakların sağlanması doğrulanmalı; copyright tek başına yetmez |
| Prisma native engine | https://github.com/prisma/prisma-engines | BLOCKED: native engine commit/checksum ve uygulanabilir Apache NOTICE incelemesi gerekli |
| Next standalone, MIT/BSD/Apache | https://github.com/vercel/next.js | BLOCKED: tracing bildirimleri eksiksiz taşıyor varsayılmaz |
| MPL bileşenleri | Gerçek SBOM ile belirlenecek | UNKNOWN: geliştirme bağımlılığı runtime varlığı sayılmaz; migrate imajı build aşamasının tüm bağımlılıklarını içerir |

## Test ve kalan iş

Yeni beş test: tam sentetik kayıt, her zorunlu alanın eksikliği, yanlış sürüm, bilinmeyen lisans, yanlış imaj/boş SBOM. Yerelde ilk çalıştırma 5/5 geçti. Preflight 12/12 geçti. Son CI bağlantıları PR açıklamasında tutulur; geçmiş CI bu HEAD için başarı sayılmaz.

Zorunlu regresyon job'ları korunur: lint/strict TS, birim/PG entegrasyon/E2E, build, Prisma, migration/schema diff, tenant/finans/audit/query-plan, arşiv/preflight, selfhost/restart, streaming/encrypted backup ve ayrı cluster recovery, migration hatasında güvenli durma. Tamamlanmadan DEVELOPMENT hazır ilan edilemez.

Bağımsız insan testi yapılmadı; [katılımcı kontrol listesi](INDEPENDENT-INSTALLATION-CHECKLIST.md). Sonraki adım: iki imaj artifact'ını inceleyip libvips 8.18.7 ve bütün native alt bağımlılıklar için aynı sürüm kaynak/notice/relinking kanıt paketini hazırlamak; ardından Node/Debian source sunumunu doğrulamak. Registry/release/tag/npm/deploy/merge yoktur.
