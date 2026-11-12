# S05-D tam kaynak zinciri doğrulaması

DEVELOPMENT: INCOMPLETE — son HEAD push/PR CI kararı taslak PR ve nihai teslimde kaydedilir.
GENERATED CARGO.LOCK: BLOCKED
RUST COMPILE-LINK SCOPE: BLOCKED
RUST SOURCE/NOTICE EVIDENCE: BLOCKED — S05-D araştırma işi henüz çalışmadı.
FULL LIBVIPS BUNDLE REBUILD: BLOCKED
STATIC LGPL RELINKING INPUTS: BLOCKED
DURABLE SOURCE PROVISION: PARTIAL — tasarım/test sonucu bekleniyor.
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

İki ayrı kaynak kopyasında aynı cargo update --workspace komutu, önce/sonra lock hash'leri, eklenen/silinen/değişen kayıtlar ve checksum farkları kaydedilir. Eşleşen iki yeni çözüm bile tarihsel upstream index/lock kanıtı değildir; en fazla PARTIAL. Generated lock gerçekten oluşmadıysa generated-Cargo.lock dosyası oluşturulmaz. Metadata/tree yalnız RESOLVED verir. Bu sürümde compiler-artifact/link-map protokolü uygulanmadığından COMPILED, LINKED ve NOT SELECTED iddiaları reddedilir.

[Cargo sonucu](evidence/s05d/cargo-resolution.json) ve [scope](evidence/s05d/rust-compile-link-scope.json) başlangıçta NOT_RUN/BLOCKED kaydıdır; gerçek CI çıktısı ayrı artifact'tır ve inceleme sonrası S05-D'ye aktarılır.

## B — Eksik bildirimler

[13 kayıt](evidence/s05d/rust-license-resolution.json) özgün checksum'larıyla yeniden indirilir; Cargo.toml/license-file ve kaynak başlıkları incelenir. Dosya adının LICENSE olmaması tek başına ihlal sayılmaz. MPL-2.0 Source Code Form içindeki Exhibit-A benzeri özgün başlık/edinme URL'si, exact arşiv dosyası/hash'iyle bağlanarak bildirim edinimi kanıtı olabilir.

Varsa .cargo_vcs_info commit'i ve path'i exact crate'ten alınır; GitHub exact commit tree'sindeki Rust source blob SHA'larıyla karşılaştırılır. Üst dizindeki özgün lisans metinleri aynı commit'ten edinilir; farklı tag/main metni ikame edilmez. Eşleşmeyen kaynak veya eksik revision UNKNOWN/BLOCKED kalır. PASS yalnız kaynak/bildirim edinimini anlatır; tam dağıtım koşulları ve hukuki onay ayrıca açıktır. Eksik .a/.o veya kaynak sunumu yükümlülüğü bu kararla kapanmaz.

## C — Full native bundle önkoşulları

[Full bundle kaydı](evidence/s05d/full-bundle-rebuild.json) ve [static girdiler](evidence/s05d/static-relinking-inputs.json) gerçek aşamayı bildirir. S05-B'nin 28 native source/hash ve patch manifest'i referanstır; S05-D'de yeniden edinilmemiş arşivler reverified sayılmaz.

Özgün Linux x64 Dockerfile Rocky 8 floating tag, dnf update, gcc-toolset-15, floating nightly/cargo-c ve pip Meson/Ninja kullanıyor. Exact base digest, RPM sürümleri/hash'leri ve bütün compiler/cargo-c girdileri doğrulanmadan bu uzak installer/download-pipe tarifi yürütülmez. A/B sonucu değerlendirildikten sonra bu eksikler full CONTROL/MODIFIED build önkoşulunu bloke eder. Kaynakların sürümlerinin listelenmesi full build'in çalıştığı anlamına gelmez.

S05-C reduced PNG/JPEG build'i full profile yerine kullanılmaz. Full build çalışmadığında control/modified hash, export farkı, ABI ve Sharp sonucu null/NOT_RUN kalır; 1946 eksik export'un giderildiği iddia edilmez. Full success protokolü uygulanana kadar denetçi dolu sahte compiler/linker/ABI alanlarıyla VERIFIED verilmesini reddeder. [Tekrar ve gereken girdiler](LIBVIPS-FULL-REBUILD-REPRODUCTION.md).

## D — Kaynak sunumu ve testler

[Kalıcı kaynak planı](CORRESPONDING-SOURCE-DISTRIBUTION-PLAN.md) sürüm/digest/SBOM/kaynak/patch/bildirim/toolchain/static girdiler zincirini, lisansa göre yöntem/süreyi, kopyalama/erişim kontrolünü ve manuel kararları tanımlar. GitHub Release/Pages/artifact kalıcılık garantisi değildir. Hiçbir gerçek source bundle veya binary yayımlanmaz.

Yeni offline testler zorunlu checks'e eklenir; mevcut tüm uygulama/selfhost ve S05-A/B/C testleri korunur. Ağ/toolchain/source deneyi yalnız S05-D push'ında ayrı, 25 dakika sınırlı non-gating job'dır. Kolektör PARTIAL/BLOCKED için exit 1 verir; job/step failure gizlenmez. PR'de ağır iş tekrar edilmez. Artifact 14 gün saklanır ve kalıcı sunum sayılmaz. Tekrarlanan yüzlerce MB toolchain/cache kopyası yüklenmez: küçük receipt/notice/metadata ve 13 crate arşivi tutulur, exact toolchain URL/hash ve yeniden edinim bilgisi manifesttedir. Rust component binary arşivleri ve expanded toolchain artifact'a dahil değildir; bu eksiklik tam relinking/source paketi sağlandı diye sunulmaz. Ağır full build önkoşulları yoksa native build'in atlandığı ayrıca raporlanır. Son HEAD mandatory testleri bitmeden DEVELOPMENT READY denmez.
