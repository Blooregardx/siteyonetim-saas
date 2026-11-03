# S05-A dağıtım uyumluluğu doğrulaması

DEVELOPMENT: READY FOR MAINTAINER REVIEW — aşağıdaki doğrulanmış CI kontrol noktası için; bu belgeyi içeren son HEAD iki CI sonucu ayrıca PR kanıt kaydında doğrulanmalıdır.

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

## Gerçek yerel Alpha.2 runtime kanıtı

Yerel build Alpha.2 kaynak commit'ini içerir; S05-A son HEAD imajı değildir. İmaj `sha256:c9774700d694a20e2aa1f1d8a568d9a5fff123a7c81a979faa907096ba5d55b1`, base `node:24-bookworm-slim@sha256:c86ecead9e55a5210ac1727de38a4ca840bf03dcaf34dc9749addbf383b1920c`. Node **v24.22.2**, Debian **91** paket, üst düzey npm metadata **22**, Syft **310** bileşen: **PASS 0 / BLOCKED 241 / UNKNOWN 69 / NOT_APPLICABLE 0**. [Syft](evidence/s05a/alpha2-runtime.syft.json), [CycloneDX](evidence/s05a/alpha2-runtime.cdx.json), [dosya/native bağlantı envanteri](evidence/s05a/alpha2-runtime-filesystem.json), [kapı kayıtları](evidence/s05a/alpha2-runtime-gate.json). Tam kaynak/notice kanıtı olmadığı için hiçbir bileşene PASS atanmadı.

Gerçek runtime hem glibc hem musl x64 Sharp/libvips paketlerini taşıyor. glibc libvips 8.18.7 SHA-256 `4aa73553408c3964071728f4a231a8e86918e39bc49f1fbae75355f7ea933ea9`; musl binary `979b625437190a1970b835164e0e30d47dc60159ce6a394ce78cc40cb9d59ab8`. Musl bağlantısında libc.musl bulunamıyor; dosyanın taşınması kullanılabildiği anlamına gelmez. Prisma Debian OpenSSL3 engine SHA-256 `a2924eab1c78a0a7bb67edac5738939fa10589ef073af5542f53812a22e4a7d8`. Next 16.4.3, Prisma Client 6.19.3 imaj metadata'sında doğrulandı.

libvips upstream `v8.18.7` tag API'si `24ad4d042940e6bf99a68871ba886ca8847c9c82` commit'ini gösterdi: https://github.com/libvips/libvips/tree/24ad4d042940e6bf99a68871ba886ca8847c9c82 . Bu upstream sürüm adayıdır; binary build flags/patches/alt bağımlılık kaynak eşleşmesi veya kaynak sunma yükümlülüğünün tamamlandığını kanıtlamaz.

Syft gerçek şeması `source.metadata.imageID` kullanır; ilk gerçek tarama ile doğrulanıp kapı testleri düzeltildi. Syft JSON içindeki encoded imaj config/env/history kanıt dosyalarından çıkarıldı; yalnız kimlik/mimari alanları tutuldu. Migration imajı ve son HEAD push/PR artifacts ayrıca değerlendirilmelidir.

## Gerçek yerel Alpha.2 migration SBOM'u ve sınır

İmaj `sha256:a57f59594fb925382fbb722252277b52e73c6ec1d6c9698af94b35ea4ba28023`, aynı base digest: **866** bileşen, **PASS 0 / BLOCKED 777 / UNKNOWN 89 / NOT_APPLICABLE 0**. [Syft](evidence/s05a/alpha2-migrate.syft.json), [CycloneDX](evidence/s05a/alpha2-migrate.cdx.json), [kararlar](evidence/s05a/alpha2-migrate-gate.json). `axe-core` **4.14.0** gerçekten migration imajında bulundu; runtime envanterinde bulunmuyor. Dolayısıyla MPL değerlendirmesi migration dağıtımında uygulanabilir; yalnız dev etiketiyle dışlanamaz.

VFS yerel disk alanı migration container dosya/native incelemesinde tükendi; iki deneme de Docker nonzero verdi. Bu inceleme **INCOMPLETE/BLOCKED**, başarı sayılmadı. Yalnız bu görevin ürettiği host node_modules/geçici araç dosyaları ve kaldırılmış migration imajının kesin build cache ID'si temizlendi; genel prune veya mevcut PostgreSQL verisine dokunulmadı. Migration SBOM'u önceden üretildi ve korundu. Son HEAD CI daha geniş diskli runner'da dosya envanterini ayrıca üretmelidir.

Son yerel tekrar: kapı **6/6** (gerçek CLI 0/1/2 çıkışları dahil), preflight **12/12**, arşiv politikası **4/4**, streaming **3/3**, Prisma generate/validate ve kaynak/lisans/link doğrulaması geçti. Önceki npm check: lint/strict TypeScript ve **25/25** birim geçti; iki Docker production build'i başarılı. Yeni native aday filtresi JS dosyalarını binary saymaz; eski runtime dosya kanıtı daha geniş query-engine aday listesini korur. Son CI sonuçları tamamlanmadan DEVELOPMENT INCOMPLETE kalır.

## CI kimlik hata bulgusu

f15ff5c push/PR selfhost kontrolü image-ID uyuşmazlığında başarısız oldu. Artifact incelemesinde Docker inspect index ID ile Syft config ID'nin farklı olduğu doğrulandı. Kontrol gevşetilmedi: sabit inspect ID ile Docker arşivi export edilir; gerçek config içeriği SHA-256 ile hash'lenir ve Syft aynı arşivi tarar. Özgün inspect ID ayrıca saklanır. Bu düzeltmenin son HEAD CI sonuçları ayrıca beklenir.

## Özgün npm bildirimlerini koruma düzeltmesi

Alpha.2 runtime dosya kanıtında `/app/node_modules` altında hiçbir LICENSE/NOTICE/COPYING bulunmadı. Standalone tracing bildirim taşıyor varsayımı geçersiz. Yeni build adımı kurulu npm ağacındaki özgün bildirimleri yol ve SHA-256 envanteriyle `third-party-notices` dizinine kopyalar; runtime bu dizini taşır. Geliştirme araçlarının bildirimleri de dahildir; bu onların runtime binary'sinin varlığını göstermez. Kaynağında notice bulunmayan libvips paketine metin uydurulmaz. Symlink ve notice olmayan dosyalar kopyalanmaz. Test nested/scoped yol, özgün byte/hash, secret dışlama ve symlink davranışını doğrular. Bu teknik koruma tam notice/source uyumu iddiası değildir.

Runtime SBOM lisans metadatası Debian ca-certificates/libffi8 içinde MPL ifadeleri de içerir; axe-core'un runtime'da bulunmaması bütün runtime'ın MPL içermediği anlamına gelmez. Paket alt dosyası/lisans alternatifi uygulanabilirliği ayrıca incelenmelidir.

## Başarılı CI ve gerçek son imaj incelemesi

`3a3debc57a13752b5ced039b5eb5af340a92c786` için [push CI](https://github.com/Blooregardx/siteyonetim-saas/actions/runs/41684138876) ve [PR CI](https://github.com/Blooregardx/siteyonetim-saas/actions/runs/41684147458) checks+selfhost başarılı. Her iki workflow artifact seti indirildi ve incelendi; yerel migration dosya inceleme engeli CI'da kapandı. Önceki başarısız/eksik aşamalar yukarıda tarihsel olarak korunur.

| Son CI imajı | SBOM bileşeni | PASS | BLOCKED | UNKNOWN | N/A | Debian | npm metadata | Native aday | Notice dosyası |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Runtime | 310 | 0 | 241 | 69 | 0 | 91 | 22 | 6 | 606 |
| Migrate | 866 | 0 | 777 | 89 | 0 | 91 | 415 | 30 | 1121 |

Runtime artık 515 özgün npm notice dosyasını ayrı dizinde taşıyor; toplam 606 dosya Debian/Node bildirimlerini de içerir. Migrate toplamında hem asıl npm ağacı hem korunan kopyalar bulunur; 1121 benzersiz lisans/paket sayısı değildir. İki imajda Node v24.22.2. Push artifact config kimlikleri runtime `sha256:f2d57eb6c8d0d351e34f55336611ba9e1a4eff14a071fa478fffaec5715f10d7`, migrate `sha256:0a1684d27cf5025bba98b636db292f79efe674943de926089d6864bce7fa8382`; farklı build'lerin hash'leri eşit olmak zorunda değildir.

Doğrulanan testler: ESLint/strict TS; 25 birim; 36 PostgreSQL entegrasyon; 19 Playwright; production build; Prisma generate/validate; 11 migration/schema diff; tenant/finans/audit ve query-plan; 12 preflight, 4 arşiv politikası, 6 lisans kapısı, 1 notice koruma, 3 streaming testi. Selfhost temiz kurulum/restart, şifreli backup hata matrisi, ayrı cluster encrypted recovery ve başarısız migration sonrası writers-stopped testleri de iki CI'da başarılıdır. CI'da binary kapısının BLOCKED sonucunu üretmesi beklenir; bu test başarısı binary onayı değildir.

libvips kesin upstream commit'indeki [LICENSE](https://github.com/libvips/libvips/blob/24ad4d042940e6bf99a68871ba886ca8847c9c82/LICENSE) LGPL v2.1 metni olarak ayrıca doğrulandı; SHA-256 `dc626520dcd53a22f727af3ee42c770e56c97a64fe3adb063799d8ab032fe551`. Dağıtılan platform paketi LGPL-3.0-or-later beyan eder; çekirdek upstream LICENSE bütün bundled alt bağımlılıkları kapsayan kaynak/notice kanıtı sayılamaz. Aynı sürüm kaynak/build flags/patches/notice/relinking paketi ve Node/Debian kaynak sunumu açık kalır.

Son dokümantasyon commit'inin kesin SHA, kaynak arşivi ve push/PR CI bağlantıları [taslak PR #26](https://github.com/Blooregardx/siteyonetim-saas/pull/26) içinde tutulur. Bu belgeye yeni SHA yazmak yeni commit yaratacağından son HEAD kontrolü oradaki harici kanıt kaydındadır. İnsan kurulumu yapılmadı; binary dağıtımı BLOCKED kalır.
