# S05-D tam kaynak zinciri doğrulaması

DEVELOPMENT: INCOMPLETE — son HEAD push/PR CI kararı taslak PR ve nihai teslimde kaydedilir.
GENERATED CARGO.LOCK: PARTIAL
RUST COMPILE-LINK SCOPE: PARTIAL
RUST SOURCE/NOTICE EVIDENCE: PARTIAL — 4 PASS / 9 BLOCKED.
FULL LIBVIPS BUNDLE REBUILD: BLOCKED
STATIC LGPL RELINKING INPUTS: BLOCKED
DURABLE SOURCE PROVISION: DESIGN READY — offline tasarım ve inceleme paketi; gerçek saklama/sunum henüz uygulanmadı.
SOURCE RELEASE: ALPHA.2 PUBLISHED — UNCHANGED
BINARY DISTRIBUTION READINESS: BLOCKED
INDEPENDENT INSTALLATION: PENDING HUMAN VALIDATION

## Başlangıç ve kapsam

main b93b0eeaaeabdf898a6a2f9bf35cc9c1016a3d54 doğrulandı; #28 aynı merge commit'ine birleşmiş. Alpha.2 c20646fddbc8a7e3dcd45cbc01aacd531c225e4a, yayın/güncelleme zamanı 2026-11-03 16:22:11Z değişmedi. Aynı kapsamda PR bulunmadı; açık PR'ler Dependabot işleridir. AGENTS.md ve istenen S05-C/denetim dosyaları exact main commit'inden okundu.

Codex ortamı executor configuration capabilities hatası nedeniyle kabuk sağlamadı. Cloud durum aracı running bildirse de exec komutu iki kez kullanılabilir executor olmadığını bildirdi; yerel çalışma ağacı temizliği doğrulanmadı. GitHub Git API ile exact main tree'den ayrı dal oluşturuldu. Gerçek test ve indirmeler yalnız GitHub Actions'ta temiz checkout ile yürütülür. Tarihsel S05-A/B/C evidence, normal Dockerfile/Compose, 11 migration, auth/tenant/finans/audit ve AGPL değiştirilmez.

## A — Lockfile ve kapsam

Özgün lock SHA-256 e79e2a2735a0b5b151bb4133becd3008223fabedd34a8b787a872edab9854941 korunur. 366 kayıt (357 dış, 9 workspace) başlangıç kapsamıdır. S05-C'nin 162+2 upstream compile gözlemi tarihsel kayıttır; S05-D'ye compiler veya link kanıtı olarak taşınmaz.

Pinned sharp-libvips ebb95f8add54eee8bed840e3fb587e4cbec857d7 tarifinde sıralama: rsvg image GIF/WebP feature çıkarımı; librsvg-c/rsvg cairo PDF/PS çıkarımı; meson linux koşulu değişikliği; cargo update --workspace; librsvg 9106011 patch'i; Meson static setup/install ve cargo cbuild --locked --library-type staticlib --release -p librsvg-c. S05-D resolver source patch'i build çalışmadığı için uygulamaz ve bu farkı kaydeder.

Kolektör yalnız gözlenen rustc 1.101.0-nightly 75a75c3e0 sürümüne karşılık gelebilecek 2026-09-27/26 tarihli resmî dist manifestlerini inceler. Manifest SHA ve rustc/cargo/std archive hash'leri eşleşmeden kod çalıştırmaz; rastgele nightly veya rustup installer yoktur. Hash doğrulanmış regular dosyalar manuel yerleştirilir; kök dışı link/özel dosyası reddedilir; güvenli iç linkler dosya sisteminde oluşturulmadan atlanır. Gerçek rustc/cargo -vV, binary hash'leri ve exit code saklanır. Kaynak veya toolchain edinimi eksikse cargo update çalışmış gibi raporlanmaz.

İki ayrı kaynak kopyasında aynı cargo update --workspace komutu, önce/sonra lock hash'leri, eklenen/silinen/değişen kayıtlar ve checksum farkları kaydedilir. Eşleşen iki yeni çözüm bile tarihsel upstream index/lock kanıtı değildir; en fazla PARTIAL. Generated lock gerçekten oluşmadıysa generated-Cargo.lock dosyası oluşturulmaz. Metadata/tree yalnız RESOLVED verir. Sınırlı ağsız cargo build denemesi, gerçek compiler-artifact JSON ve fiziksel rlib/ELF hash/member girdileriyle COMPILED kaydedebilir. Bu tek target'ın derlenmesidir; final library/binary link kanıtı değildir. Metadata ile compiled feature listeleri ayrı tutulur. Link-map ve NOT SELECTED protokolü tamamlanmadığından bu iki iddia reddedilir.

[Cargo sonucu](evidence/s05d/cargo-resolution.json) ve [scope](evidence/s05d/rust-compile-link-scope.json) gerçek CI çıktısından aktarıldı. İlk prepared NOT_RUN kayıtları Git geçmişindedir; boş/uydurma generated lock üretilmedi.

## B — Eksik bildirimler

[13 kayıt](evidence/s05d/rust-license-resolution.json) özgün checksum'larıyla yeniden indirilir; Cargo.toml/license-file ve kaynak başlıkları incelenir. Dosya adının LICENSE olmaması tek başına ihlal sayılmaz. MPL-2.0 Source Code Form içindeki Exhibit-A benzeri özgün başlık/edinme URL'si, exact arşiv dosyası/hash'iyle bağlanarak bildirim edinimi kanıtı olabilir.

Varsa .cargo_vcs_info commit'i ve path'i exact crate'ten alınır; GitHub exact commit tree'sindeki Rust source blob SHA'larıyla karşılaştırılır. Üst dizindeki özgün lisans metinleri aynı commit'ten edinilir; farklı tag/main metni ikame edilmez. Eşleşmeyen kaynak veya eksik revision UNKNOWN/BLOCKED kalır. PASS yalnız kaynak/bildirim edinimini anlatır; tam dağıtım koşulları ve hukuki onay ayrıca açıktır. Eksik .a/.o veya kaynak sunumu yükümlülüğü bu kararla kapanmaz.

## C — Full native bundle önkoşulları

[Full bundle kaydı](evidence/s05d/full-bundle-rebuild.json) ve [static girdiler](evidence/s05d/static-relinking-inputs.json) gerçek aşamayı bildirir. S05-B'nin 28 native source/hash ve patch manifest'i referanstır; S05-D'de yeniden edinilmemiş arşivler reverified sayılmaz.

Özgün Linux x64 Dockerfile Rocky 8 floating tag, dnf update, gcc-toolset-15, floating nightly/cargo-c ve pip Meson/Ninja kullanıyor. Exact base digest, RPM sürümleri/hash'leri ve bütün compiler/cargo-c girdileri doğrulanmadan bu uzak installer/download-pipe tarifi yürütülmez. A/B sonucu değerlendirildikten sonra bu eksikler full CONTROL/MODIFIED build önkoşulunu bloke eder. Kaynakların sürümlerinin listelenmesi full build'in çalıştığı anlamına gelmez.

S05-C reduced PNG/JPEG build'i full profile yerine kullanılmaz. Full build çalışmadığında control/modified hash, export farkı, ABI ve Sharp sonucu null/NOT_RUN kalır; 1946 eksik export'un giderildiği iddia edilmez. Full success protokolü uygulanana kadar denetçi dolu sahte compiler/linker/ABI alanlarıyla VERIFIED verilmesini reddeder. [Tekrar ve gereken girdiler](LIBVIPS-FULL-REBUILD-REPRODUCTION.md).

## D — Kaynak sunumu ve testler

[Kalıcı kaynak planı](CORRESPONDING-SOURCE-DISTRIBUTION-PLAN.md) sürüm/digest/SBOM/kaynak/patch/bildirim/toolchain/static girdiler zincirini, lisansa göre yöntem/süreyi, kopyalama/erişim kontrolünü ve manuel kararları tanımlar. GitHub Release/Pages/artifact kalıcılık garantisi değildir. Hiçbir gerçek source bundle veya binary yayımlanmaz.

Yeni offline testler zorunlu checks'e eklenir; mevcut tüm uygulama/selfhost ve S05-A/B/C testleri korunur. Ağ/toolchain/source deneyi yalnız S05-D push'ında ve deney kodu/CI değiştiğinde ayrı, 25 dakika sınırlı non-gating job'dır. Yalnız belge/kanıt aktarım commit'inde tekrar Rust indirip build yapılmaz; önceki exact deney commit'i/artifact'ı ve değişmeyen betik blob'ları bağlanır. Kolektör PARTIAL/BLOCKED için exit 1 verir; job/step failure gizlenmez. PR'de ağır iş tekrar edilmez. Artifact 14 gün saklanır ve kalıcı sunum sayılmaz. Tekrarlanan yüzlerce MB toolchain/cache kopyası yüklenmez: küçük receipt/notice/metadata ve 13 crate arşivi tutulur, exact toolchain URL/hash ve yeniden edinim bilgisi manifesttedir. Rust component binary arşivleri ve expanded toolchain artifact'a dahil değildir; bu eksiklik tam relinking/source paketi sağlandı diye sunulmaz. Ağır full build önkoşulları yoksa native build'in atlandığı ayrıca raporlanır. Son HEAD mandatory testleri bitmeden DEVELOPMENT READY denmez.


## Ölçülen S05-D sonuçları

Kaynak deney commit'i acb6f2aea7bec9630559514b69a7147f2a8e4a21, [run 43148233821](https://github.com/Blooregardx/siteyonetim-saas/actions/runs/43148233821), job 130951054438. İş beklenen exit 1 ile failure kaydetti; bu tam build başarısı değildir. [Artifact](https://github.com/Blooregardx/siteyonetim-saas/actions/runs/43148233821/artifacts/13912292674) 6520902 byte, ZIP SHA-256 a6b53d07235faff89ec291fa70d30094c37e2b11b9f419dd15461da1bbfb7853. [Receipt](evidence/s05d/experiment-receipt.json), exact collector/verifier SHA-256 ve aktarılmış dosya hash'lerini bağlar. Sonraki belge/test commit'i bu deney kodunu değiştirmez; son HEAD zorunlu push/PR CI sonuçları ayrıca PR gövdesine ve nihai rapora yazılır.

|Alan|Gerçek sonuç|
|---|---|
|Özgün lock|366 package, 357 dış + 9 workspace; SHA e79e2a2735a0b5b151bb4133becd3008223fabedd34a8b787a872edab9854941|
|Generated lock|362 package, 353 dış + 9 workspace; SHA 5723e14ce316e9058c76257848e18ab52624c98d16f758b5f8a73b5007b2ab8b|
|İki cargo update|Exit 0 / 0; output hash'leri eşit|
|Lock farkı|0 eklenen, 4 silinen: color_quant 1.1.0, gif 0.14.2, image-webp 0.2.4, weezl 0.1.12; 2 dependency-list değişikliği; 0 checksum değişikliği|
|Metadata/tree|Exit 0 / 0; workspace-default çözümleme, final compile/link kanıtı değil|
|Son diagnostic kapsam|307 RESOLVED, 1 COMPILED, 0 LINKED, 0 NOT SELECTED, 54 UNKNOWN|
|Önceki diagnostic kapsam|307 RESOLVED, 1 COMPILED (unicode-ident 1.0.26), 54 UNKNOWN; final binary'ye LINKED değil|
|Diagnostic cargo build|Exit 101: linker cc not found; proc-macro2/quote build-script link aşaması durdu|
|Full native CONTROL/MODIFIED|NOT RUN/BLOCKED; SHA/ABI/export/Sharp alanları null/NOT_RUN|
|Full static LGPL object/archive|BLOCKED; diagnostic rlib full .a/.o setinin yerine geçmez|

[Gerçek generated lockfile](evidence/s05d/generated-Cargo.lock) saklandı. İki ayrı source kopyası aynı binary/komut/ortam ile, ortak Cargo registry cache'i kullanılarak çözüldü; bağımsız tarihsel registry snapshot'ı sağlanmadı. Bu yüzden GENERATED CARGO.LOCK PARTIAL; tarihsel upstream lock kurtarıldı denmez. Generated lock ve bütün PASS notice text hash'leri aktarım sırasında bağımsız JavaScript SHA-256 hesaplamasıyla tekrar eşleştirildi.

### Exact toolchain

2026-09-27 resmî dist manifest SHA-256 ad7c5ca64d80a5c7771089f741ab90c9eb5dcbc766ce81f2c90af8fc295b40cc pinned; rustc/cargo/std arşivleri bu manifest hash zinciriyle doğrulandı, installer çalıştırılmadı. [rustc çıktısı](evidence/s05d/rustc.stdout): 1.101.0-nightly, commit 75a75c3e0a67d3fa3d03982775f5bb0356e7b510, LLVM 23.1.1. [Cargo çıktısı](evidence/s05d/cargo.stdout): 1.101.0-nightly, commit 3d7cf6e937d6127d0f49881bf689c560b36d35c4 (2026-09-25). Actual rustc binary SHA 22723c9886eec654945230d0f865f6ddc52c91b4831a027dea6d650ecbc81002; cargo binary SHA 96c2dd303135a1fd8735145997192ff59a4ea1af9c94f9b656b30a7728a9b60f. Pinned execution base node:24-bookworm-slim@sha256:c86ecead9e55a5210ac1727de38a4ca840bf03dcaf34dc9749addbf383b1920c; özgün Rocky/GCC15 native builder değildir.

Önceki [compile scope](evidence/s05d/runs/43146675005/rust-compile-link-scope.json) ve [compiler stderr](evidence/s05d/runs/43146675005/compiler.stderr) ayrı tutulur. unicode-ident rlib SHA 5d817c54f08432159bce7321923b6a298b3278aadee81c02c99b23fbf61e054a, [önceki artifact](https://github.com/Blooregardx/siteyonetim-saas/actions/runs/43146675005/artifacts/13912111602). Aradaki [43147512037 snapshot'ında](evidence/s05d/runs/43147512037/rust-compile-link-scope.json) erken linker hatasında COMPILED kaydı oluşmadı; son tekrar yine unicode-ident rlib'ini üretti. Eksik compiler-artifact satırı derlenmediğinin kanıtı sayılmadı; her iki tarihsel kanıt ayrı tutuldu.

### 13 eski BLOCKED kaydın sonucu

|Paket|S05-D kaynak/bildirim edinimi|Kanıt/eksik|
|---|---|---|
|mutants 0.0.4|PASS|14011d08c42a7cd368698fe28f77eb4cd0b65bf0 exact commit; Rust source blob eşleşmesi ve özgün Martin Pool MIT metni|
|selectors 0.40.0|PASS|67faaab3ff7aa66780ec1d0f51ca47e177b812d3; 16 Rust dosyası eşleşti; satıra bölünmüş özgün MPL Exhibit-A başlıkları mevcut|
|anes 0.1.6|PASS|378ac7461ecac29fde9e10df7b08359d1315a9ad; unique path prefix exact source blob'larıyla çıkarıldı; 28 Rust dosyası + MIT/Apache metinleri|
|defmt-parser 1.0.0|PASS|4a8cdb44891ed57b8ff5a023b6bec7137c48708f; 4 source dosyası + özgün MIT/Apache metinleri|
|block 0.1.6|BLOCKED|Exact 0.1.6 tag/source eşleşti; yeterli özgün bildirim edinilmedi|
|difflib 0.4.0|BLOCKED|VCS revision yok; v0.4.0 ve 0.4.0 tag sorguları 404|
|malloc_buf 0.0.6|BLOCKED|Exact tag ve source eşleşti; yeterli özgün bildirim edinilmedi|
|objc-foundation 0.1.1|BLOCKED|Exact tag ve source eşleşti; yeterli özgün bildirim edinilmedi|
|objc_id 0.1.1|BLOCKED|Exact tag ve source eşleşti; yeterli özgün bildirim edinilmedi|
|r-efi 5.3.0 / 6.0.0|BLOCKED|Her exact commit'te 58 Rust source blob eşleşti; yeterli uygulanabilir bildirim metni edinilmedi|
|winapi-i686-pc-windows-gnu / winapi-x86_64-pc-windows-gnu 0.4.0|BLOCKED|VCS revision yok; v0.4.0 ve 0.4.0 tag sorguları 404|

Bu kararlar lisans ihlali iddiası veya hukuki PASS değildir. Source-form MPL başlığı dosya adı kuralının sınırlamasını giderir; binary Source Code Form sağlama ve alıcıya bildirim yükümlülüğü açık kalır. Bazı crate'lerin başka platformlara ait olması, dağıtılmadığının kanıtı sayılmadı; N/A eklenmedi.

### Başarısız/atlanmış işler ve açık kaynak sunumu

İlk shallow checkout baseline guard'ı eksik parent object nedeniyle durdu; explicit exact baseline fetch ile düzeltildi. İlk toolchain incelemesi sıkı 128 MiB member sınırında durdu; yalnız hash-pinned toolchain için 768 MiB/file ve 2 GiB toplam sınırı tanımlandı. İç symlink kaynak fixture'ları arşiv kökü doğrulanarak oluşturulmadan atlandı. Bu düzeltmeler kontrolleri devre dışı bırakmaz; crate/default archive sınırları sıkı kalır.

Full Rocky/GCC15/cargo-c native builder pin/RPM kaydı, 28 native source'un yeni build'de fiziksel edinimi, full linker map/object/archive seti, CONTROL/MODIFIED libvips ve Sharp testleri tamamlanmadı. Eski S05-C hash'leri yeni full build hash'i diye doldurulmadı. Geçici 14 gün artifact kaynak sunumu değildir; Node/Debian/Prisma genel kapıları ve bağımsız insan kurulumu açık kalır.

S05-E önerisi: exact Rocky/GCC15/cargo-c/Meson/Ninja sysroot ve bütün source/patch/toolchain girdilerini sabitlemek; full static CONTROL/MODIFIED build ve linker/ABI/Sharp prova protokolünü tamamlamak; 9 eksik notice ve kalıcı sunum planının operasyonel kapasitesini manuel incelemek.


## Geliştirme regresyonu ve son belge aktarımı

Deney commit acb6f2ae için [push checks+selfhost](https://github.com/Blooregardx/siteyonetim-saas/actions/runs/43148233821) ve [PR checks+selfhost](https://github.com/Blooregardx/siteyonetim-saas/actions/runs/43148239523) başarılı. 33 yeni S05-D testi; S05-A 7, S05-B 14, S05-C 31 kontrolü; 25 unit, 36 PostgreSQL integration ve 19 E2E testi geçti. Prisma validate/generate, 11 migration/schema diff, strict TypeScript/ESLint, production build, query-plan, preflight/source archive ve backup/recovery kontrolleri başarılı. Production npm audit 0; mevcut dev dependency advisory sayısı 7 moderate. Finans/auth/tenant/audit ve dependency sürümleri değiştirilmedi.

Source experiment job sonucu failure olarak korunur: kolektör PARTIAL/BLOCKED için exit 1, diagnostic Cargo build exit 101. Bu bir full upstream build başarısı değildir. PR'de ağır kaynak işi atlandı. Bu son belge/veri aktarımı collector/verifier kodunu değiştirmez; receipt codeSha256 offline testlerle doğrulanır. Son aktarım HEAD'inin push/PR zorunlu CI sonucu PR gövdesi ve nihai teslimde ayrıca doğrulanır; bu belge başındaki INCOMPLETE satırı CI öncesi kayıt anını gösterir.

Full native builder pinleri ve derleme/relink kanıtı eksik olsa da başarılı zorunlu geliştirme testleri ayrı değerlendirilir. Genel dağıtım, source sunumu ve hukuki onay bu testlerle açılmaz. Bakımcı incelemesi dışında merge/tag/release/registry/npm/deploy işlemi yoktur.
