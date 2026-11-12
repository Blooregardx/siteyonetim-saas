# S05-E — Full native rebuild ve binary compliance

Yalnız DEVELOPMENT. Başlangıç `3f21f383bbf005f4b9e5ed877cb3491f82ecacd0`.
[Taslak PR #30](https://github.com/Blooregardx/siteyonetim-saas/pull/30),
S05-D #29 henüz birleşmediği için `codex/s05-d-full-source-compliance` dalına
katmanlandı. Başlangıç main `b93b0eeaaeabdf898a6a2f9bf35cc9c1016a3d54`.
S05-A/B/C/D kanıtları, AGPL-3.0-only, uygulama Docker/Compose güvenliği ve
migration/auth/tenant/finans/audit davranışları korunur. Merge/yayın/deploy yoktur.

## Kararlar ve kapsam

| Karar | Sonuç | Kanıt ve sınır |
|---|---|---|
| DEVELOPMENT | PASS — kod/regresyon checkpoint’i | 0667a12 push ve PR CI başarılı; son dokümantasyon HEAD’i teslimde ayrıca doğrulanır |
| NATIVE TOOLCHAIN REPRODUCIBILITY | PASS — kontrollü tool/input kapsamı | [Bağımsız CI](https://github.com/Blooregardx/siteyonetim-saas/actions/runs/43196106551): 17 tool ve 4 cargo-c hash eşleşti; historical image byte eşitliği değil |
| FULL CONTROL/MODIFIED REBUILD | PASS | Tam native profil, aynı toolchain/38 archive yolu/366 compile command; farklı kaynak ve binary |
| ABI/SHARP COMPATIBILITY | PARTIAL | Export/import ve gerçek native PNG/JPEG/SVG PASS; eksiksiz type ABI kanıtı yok |
| RUST SOURCE/NOTICE EVIDENCE | PARTIAL | Dokuz açık kayıtta 2 source/notice PASS, 7 BLOCKED; N/A yok |
| STATIC LGPL RELINKING INPUTS | PARTIAL | Gerçek .a/.o ve map'ler var; original bundle eşleşmesi, tam dosya lisans kapsamı ve kalıcı sunum açık |
| DURABLE SOURCE PROVISION | PARTIAL | İki bağımsız runner filesystem kopyası/restore sentetik; aynı artifact backend'i kalıcı bağımsızlık değildir |
| BINARY DISTRIBUTION READINESS | BLOCKED | Genel lisans/kaynak/notice, image/SBOM ve uzun dönem sunum kapıları açık |
| INDEPENDENT INSTALLATION | BLOCKED — PENDING HUMAN VALIDATION | İnsan testi yapılmadı; otomatik selfhost testi yerine geçmez |

SOURCE RELEASE: ALPHA.2 PUBLISHED — UNCHANGED. Alpha.2 tag commit'i
`c20646fddbc8a7e3dcd45cbc01aacd531c225e4a`; yayımlanma 3 Kasım 2026.

## Native ortam ve gerçek girdiler

[Başlangıç kaydı](evidence/s05e/baseline.json), exact upstream commit
`ebb95f8add54eee8bed840e3fb587e4cbec857d7` için açık
[upstream job](https://github.com/lovell/sharp-libvips/actions/runs/36315646015/job/108609814156)
log'unu ve SHA-256'sını korur. Floating Rocky tag'i kullanılmadı.

| Girdi | Doğrulanan değer |
|---|---|
| Rocky immutable manifest/list | `sha256:ae0813ccb1bb83f4e0220acdd1539f52831517de334368e960824db7e37ee210` |
| Gerçek base config | `sha256:98ab72cce29f004554c86e88d6789b7f8d09fe90aee099ec56e9b71a2a7e406c` |
| Cloud prepared config | `sha256:aed21cee6ad62af8dcfe3fbe8abb19f0158f3b0f2847e63978e866c5f6953152` |
| RPM işlem/closure | 109 update + 8 epel + 124 build işlemi; 302 kurulu paket |
| GCC / binutils | 15.2.1-7.1.el8_10 / 2.44-3.el8 |
| Python / Meson / Ninja | 3.12.14 / 1.12.1 / 1.13.2 |
| Rust dağıtımı | 2026-09-27, rustc 1.101.0-nightly, `75a75c3e0a67d3fa3d03982775f5bb0356e7b510` |
| Cargo | 1.101.0-nightly, `3d7cf6e937d6127d0f49881bf689c560b36d35c4` |
| cargo-c | 0.10.25+cargo-0.99.0; 410 bootstrap registry archive'ı checksum kontrolünden geçti |
| Native kaynak | 28 arşiv ve 5 patch yeniden doğrulandı; glibc tarifinde 27 benzersiz kaynak seçilir, proxy-libintl dalı seçilmez |

[RPM byte hash ve konumları](evidence/s05e/historical-rpm-files.json),
[kurulu paketler](evidence/s05e/installed-rpms.tsv),
[gerçek tool hash/sürümleri](evidence/s05e/measured-tools.json),
[Rust archive girdileri](evidence/s05e/rust-component-inputs.json),
[toolchain kaydı](evidence/s05e/toolchain.json),
[gerçek config byte doğrulaması](evidence/s05e/toolchain-config-identity.json)
ve [native source hash'leri](evidence/s05e/native-source-integrity.json) ayrı korunur.
RPM header hash'i, RPM dosya SHA-256'sı ve image config digest'i birbirinin yerine kullanılmaz.

Publisher RPM imzaları kontrol edilir. EPEL-8 public key fingerprint'i
`94E279EB8D8F25B21810ADF121EA45AB2F86D6A1`.
Ninja matching sdist'ten GCC ile üretildi; upstream PyPI wheel compiler'ı veya
upstream image byte kimliğiyle özdeşlik iddia edilmez.

Docker containerd store, `inspect.Id` alanında manifest-list digest'i
raporlayabilir. `docker_identity.py`, local `docker save --platform=linux/amd64`
akışından config bytes'ını hash'ler, descriptor filename hash'ini ve rootfs
diff ID'lerini doğrular. Engine ID, manifest/list ve config ayrı kaydedilir;
beklenen config değiştirilerek bir kontrol atlatılmaz. Büyük layer'lar diske
çıkarılmaz; traversal/link/duplicate/yanlış platform ve eksik config reddedilir.

[Bağımsız yeniden üretim](evidence/s05e/independent-toolchain-reproduction.json)
artifact digest'i Cloud'da da doğrulandı. CI engine image ID ile canonical config
alanları ayrı saklanır. Aynı compiler/tool byte hash'leri, aynı image config
byte hash'i veya bit düzeyinde historical build anlamına gelmez.

## Tam CONTROL/MODIFIED sonucu

Sharp **0.35.5**, platform **1.3.4**, libvips **8.18.7** ve source commit
`24ad4d042940e6bf99a68871ba886ca8847c9c82` kullanıldı. S05-C reduced PNG/JPEG
profili kullanılmadı. Ancak Rust çözümlemesi S05-D'nin kontrollü generated lock'udur:
`5723e14ce316e9058c76257848e18ab52624c98d16f758b5f8a73b5007b2ab8b`.
Bu, bilinmeyen historical upstream post-update lock veya özgün npm binary'si
ile bit düzeyinde reproducible build kanıtı değildir.

| Dosya | Gerçek SHA-256 |
|---|---|
| CONTROL | `9765d980f837f70c36ad2bb5096002117076dcf0f017dc9306d82cd06a4772d2` |
| MODIFIED | `4dfa8a4e9a7b287249c08bb4dcfb06c30f70ad28c75a87cfb3ad3246a69f6db1` |

Yeni source/tree farkı yalnız `libvips/iofuncs/init.c` içindeki private
`used,retain` sabitidir. Public API/görsel algoritma değişmez. Marker CONTROL
binary'sinde yok, MODIFIED içinde vardır. Source before/after hash'leri
`10f0201e4853d5d40b3b88f6b2c81616e9c474ab3c10b029b96014fe0d0c2f78`
ve `9308a5118e7f4519eebfb3d442679a0ef200b4d0b2972bc4bb4be6501817a1ad`.
[Diff](evidence/s05e/source-change.diff),
[366 aynı compile command ve 38 dependency archive eşleşmesi](evidence/s05e/source-build-provenance.json),
[gerçek invocation/script hash'leri](evidence/s05e/experiment-invocations.json),
[linker komutları](evidence/s05e/linker-commands.json) korunur.

İki build network none, non-root, read-only rootfs, cap-drop ALL,
no-new-privileges, 2 CPU/6 GiB RAM ile çalıştı. Prefix kurulum yolları yalnız
scratch /target içine taşınmıştır; normal uygulama imajına dokunulmadı.
Kaynaklar/registry açılımları arşiv bytes'ıyla yeniden karşılaştırıldı.

### ABI ve Sharp

Özgün npm kütüphanesi, CONTROL ve düzeltilmiş MODIFIED için **3500 export**,
**558 versioned import** ölçüldü. Eksik/ek export veya CONTROL/MODIFIED
versioned symbol farkı **0**. S05-C'deki 1946 eksik export açığı bu kontrollü
full profilde gözlenmedi. SONAME `libvips-cpp.so.8.18.7`; ELF64 x86-64/glibc.

İmzası ve kurulu dosyaları doğrulanan libabigail **2.10.0** ile original/control,
control/modified ve `--fail-no-debug-info` komutları exit 0 verdi. Üç ELF'te de
`.debug_info` yoktur; bu exit code'dan eksiksiz type ABI onayı çıkarılmaz.
[ABI kaydı](evidence/s05e/abi-measurement.json) ve
[sembol karşılaştırması](evidence/s05e/symbol-comparison.json) bu sınırı korur.

Gerçek Sharp addon SHA-256:
`cf896cc1b7f3ae9c3e8eb3d7b2b198b8de2824ff7d0681d684bab5a825def335`.
Node 24.19.0, Linux x64/glibc 2.41 test host'unda CONTROL ve MODIFIED ayrı
süreçlerde PNG üretimi, JPEG resize/rotate ve sentetik SVG→PNG testlerini geçti.
Proc maps'te gerçek library ve addon dosyaları okunup hash'lendi; eski bundle
aynı süreçlerde yüklenmedi. [CONTROL](evidence/s05e/control-sharp.json),
[MODIFIED](evidence/s05e/modified-sharp.json),
[eski library ile başarılı işleme olsa da reddedilen negatif](evidence/s05e/original-negative-sharp.json).
Bu, bütün Linux dağıtımları/musl veya tam ABI testi değildir.

### Başarısız denemeler ve düzeltilen deney altyapısı

[Deneme geçmişi](evidence/s05e/attempt-history.json) silinmedi. `/tmp` 4.9 GiB
tmpfs dolduğu için mozjpeg ar oluşturma exit 2 verdi; kök diskte boşluk vardı.
64.773 dosya/link ve 5.188.697.189 regular byte disk scratch'e taşınırken eşleşti.
Source extractor mtime korumadığı için WebP gereksiz aclocal-1.17 istedi;
özgün arşiv zamanları korundu, pinned Automake değiştirilmedi. Hatalı ara
checkpoint ayrıca kayıtlıdır. Başarılı bağımlılıklar tekrar derlenmeden kullanıldı.

İlk MODIFIED `85deb6f21833b7c381f6b385a746670739eed3c9a54de928187af0d1a4f25fd3`
için **1073 export** eksildi: CONTROL kurulumu /target içine libvips.a ekleyince
ikinci upstream find/--exclude-libs onu da gizledi. Sharp WASM'a düştü; görüntü
başarısı ve LD_PRELOAD buna rağmen doğru native addon kanıtı değildi. Gate bunu
reddetti. Yalnız kayıtlı Vips install çıktıları prefix dışına korunarak taşındı;
38 bağımlılık archive yolu değiştirilmedi. Düzeltilmiş MODIFIED tek başına
tekrar derlendi. `s05e_clean_prefix.py` ve negatif testleri bu hatayı engeller.

## Rust notice ve statik lisanslar

[Dokuz kayıt araştırması](evidence/s05e/rust-notice-resolution.json): **2 PASS /
7 BLOCKED / 0 UNKNOWN / 0 N/A**. Bunlar yalnız S05-D'nin açık dokuz kaydıdır;
yeni compiled/link graph'ın tamamı için uyum sayısı değildir. r-efi 5.3.0 ve
6.0.0 exact crate **AUTHORS** metinleri, tam MIT izin/disclaimer ve
telif içerir. Yalnız exact crate/text hash'lerine bağlı inceleme uygulanır;
yalnız metadata ile PASS verilmez. PASS kaynak/bildirim edinimidir, hukuki onay değildir.

Kalanlar: block 0.1.6, difflib 0.4.0, malloc_buf 0.0.6, objc-foundation 0.1.1,
objc_id 0.1.1, winapi-i686-pc-windows-gnu 0.4.0 ve
winapi-x86_64-pc-windows-gnu 0.4.0. Platform/dev gerekçesiyle, gerçek compile/link
kanıtı olmadan N/A yapılmadılar. S05-D'nin daha önce kapattığı dört kayıt korunur.

[Exact native özgün metinler](evidence/s05e/native-license-evidence.json) altı
kaynak sürümü için yeniden edinildi. GLib 2.90.0'ın core REUSE `LICENSES/*`
metinleri, docs/reference/COPYING yerine ayrı korundu. gmain/gobject LGPL-2.1-or-later
header'ları; Pango 1.58.2 layout dosyasının GNU Library GPL v2-or-later bildirimi;
Cairo 1.18.6'nın LGPL-2.1/MPL-1.1 seçenekleri; libheif 1.23.5'in LGPL-3.0-or-later
header'ı ve librsvg 2.63.2/libvips 8.18.7 özgün metinleri dosya düzeyinde saklandı.
Libvips çekirdek LICENSE'ı ile platform paketinin LGPLv3 aggregate beyanı tek
sürüme indirgenmedi. Bu örnekler bütün derlenen dosyaların lisans kapsamını
kapatmaz; compliance kararları UNKNOWN / REQUIRES LEGAL REVIEW kalır.

[Statik giriş matrisi](evidence/s05e/static-lgpl-inputs.json): **40 archive dosya
kaydı, 39 benzersiz archive hash'i, 6908 ar member kaydı ve 732 core .o dosyası**.
Member sayısı ar symbol/string tablolarını ve kurulum/build kopyalarını içerir;
farklı component/crate veya gerçekten linklenen member sayısı değildir.
[Hash indeksi](evidence/s05e/static-inputs.json) ve gerçek .a/.o/map'ler korunur.
Özgün npm bundle'ın object set'i veya historical post-update lock kurtarıldı
iddiası yoktur. Statik LGPL yeniden bağlama girdileri bu yüzden PARTIAL'dır.

## Kaynak sunumu, saklama ve CI

[Yayın öncesi protokol](S05E-SOURCE-PROVISION-PROTOCOL.md) immutable OCI
manifest/config/layer, gerçek binary bytes'ı, image SBOM'u, source/patch/notice,
compiler/linker/relink girdilerini bağlar. [Gerçek sentetik CI checkpoint’i](evidence/s05e/restore-checkpoint.json),
ikisi copy ikisi restore olmak üzere dört farklı runner fingerprint’i doğrular; bozuk/kayıp kopya fallback olmadan reddedilir.
Tek GitHub artifact backend'i, iki bağımsız kalıcı sağlayıcı veya uzun dönem
source offer değildir. 14 günlük saklama ve source sunum yöntemi/süresi ayrı kalır.

[62 MiB mertebesindeki DEVELOPMENT relinking review artifact'ı](evidence/s05e/development-artifact.json)
Cloud workspace'te .a/.o, binary çiftini, map'leri ve özgün örnek notice'ları
korur. Büyük dosyalar Git'e eklenmedi. Bu artifact eksik kaynak paketidir;
complete-source protocol onu beklenen biçimde [BLOCKED](evidence/s05e/actual-candidate-source-gate.json)
verir. Workspace erişimi/ömrü garanti değildir. Gerçek tam paketin iki bağımsız
kalıcı kopyası/restore'u henüz yapılmadı. Gerçek source bundle yayımlanmadı.

Yeni .so'lar runtime/migration imajına eklenmedi. Toolchain config kimliği bir
uygulama image/SBOM kimliği olarak kullanılmaz. Mevcut selfhost CI'ın gerçek
imaj SBOM'ları ayrı kalır. Node/Debian, Prisma, diğer notice/source kapsamı,
hukuki inceleme ve uzun dönem kaynak sunumu genel BLOCKED kapısını korur.

[0667a12 regresyon checkpoint’i](evidence/s05e/regression-checkpoint.json):
25 birim, 36 PostgreSQL entegrasyon, 19 Playwright E2E; lint/strict TypeScript,
production build, Prisma generate/validate, 11 migration/schema diff, tenant/
finans/audit güvenliği, query-plan, source archive/preflight, temiz selfhost,
restart/kalıcılık, streaming/encrypted backup, ayrı cluster recovery ve migration
hatasında writers-stopped başarılı. Push ve PR CI ayrı doğrulandı. S05-C/S05-D
ağır işleri eski branch koşullarıyla atlandı; regresyon testleri çalıştı.

Mevcut uygulama/selfhost/recovery ve S05-A/B/C/D regresyonları korunur. Yeni
**72 S05-E testi**, gerçek pozitif/negatif native deneylerden ayrıdır. Son HEAD
push/PR CI sonucu tamamlanmadan bakımcı incelemesine hazır teslim ilan edilmez.
[Tekrar üretim](S05E-NATIVE-REBUILD-REPRODUCTION.md) ve PR checks güncel teslim
koşuludur. Önerilen S05-F: debug/type ABI kapsamı, actual crate/link/notice
matrisi, tam kaynak/relink paketi ve bağımsız kalıcı restore; Node/Debian/Prisma
kapılarını ayrı işlerle kapatmak.
