# S05-B Sharp/libvips kaynak doğrulaması

DEVELOPMENT: Son HEAD kararı, PR #27 içindeki son SHA push ve PR CI kayıtlarıyla verilir; aşağıdaki başarılı kontrol noktaları onun yerine kullanılmaz.
LIBVIPS SOURCE EVIDENCE: PARTIAL
RELINKING EVIDENCE: PARTIAL — aynı-byte alternatif dinamik yükleme; değiştirilmiş kaynak/static LGPL rebuild BLOCKED.
SOURCE RELEASE STATUS: ALPHA.2 PUBLISHED — UNCHANGED
BINARY DISTRIBUTION READINESS: BLOCKED
INDEPENDENT INSTALLATION: PENDING HUMAN VALIDATION

Başlangıç main `1b5ef3840ac416dfec9d5a3fe1f09ee3a8af9acf`; S05-A #26 2026-11-03 20:11:21 UTC'de birleşmiş. Başlangıç ağacı temizdi; aynı kapsamda açık PR yoktu. Alpha.2 kaynak-only yayın/tag `c20646fddbc8a7e3dcd45cbc01aacd531c225e4a` değişmedi. AGENTS.md ve istenen S05-A kaynak/kanıtları okundu. Tarihsel S05-A dosyaları değiştirilmez. Bu çalışma staging/production veya binary dağıtımı değildir.

## Kesin upstream kayıtları

- sharp-libvips v1.3.4 tag object: `158bf3bfb1e11de50032645873d52e5920c26986`; commit: `ebb95f8add54eee8bed840e3fb587e4cbec857d7`. GitHub tag verification API `verified:true / valid` döndürdü; yerel GPG güven zinciri doğrulaması yapılmış sayılmaz.
- Sharp v0.35.5 imzalı tag commit: `51a990faa26ade5586a4934ac9673c98d8893326` (GitHub verified).
- libvips v8.18.7 doğrudan tag commit: `24ad4d042940e6bf99a68871ba886ca8847c9c82`.

[Makine manifest'i](evidence/s05b/libvips-source-manifest.json), kaynak URL/hash'leri, özgün bildirim dosyaları/hash'leri, beş dış patch, exact build tarifleri ve platform toolchain dosyalarını içerir. Tag arşivinden ilk okunan tarifler exact commit arşiviyle byte/hash olarak karşılaştırıldı. Büyük kaynak arşivleri yalnız geçici çalışma alanına indirildi; depoya eklenmedi. Kaynak arşiv hash'i gözlenen byte bütünlüğüdür; binary'nin bu kaynaktan üretildiğinin imzalı ispatı değildir.

## Kaynak matrisi ve kapsam

Pinned versions.properties **28** girdi içerir: libvips + **27** doğrudan native alt bileşen. İlk 29 tahmini düzeltilmiştir. Kesin kaynak URL'leri upstream posix.sh tarifinden sürüm değişkenleriyle çıkarıldı; 28 arşiv indirildi ve checksum'landı. İlk glib/librsvg incelemesi `..` içeren iç bağlantıları reddetti; bağlantı hedefleri arşiv kökü içinde normalize edilip yalnız regular dosyalar okunarak, hiçbir link takip edilmeden veya arşiv extract edilmeden güvenli inceleme tamamlandı. Traversal/kök dışı bağlantılar reddedilir. **73 özgün LICENSE/COPYING/NOTICE/telif dosyası** byte'larıyla korundu. Bunlar 73 ayrı lisans veya tamamlanmış hukuki inceleme sayısı değildir.

Her kaydın isim/sürüm, kaynak URL/hash, notice dosyası/hash, linkage ve eksik kanıt alanları manifest'tedir. Kaynak arşivi edinme kontrolü PASS **28**, BLOCKED **0**; binary-source provenance kararı PASS **0**, BLOCKED **28**. Üst paketin lisansı alt bileşenlere uygulanmadı. Özgün lisans metinleri ile upstream THIRD-PARTY-NOTICES birlikte incelenmelidir; dosya bazında SPDX/alternatif seçimi için manuel inceleme açık kalır.

Librsvg Cargo.lock ayrıca arşivden alındı. Registry/git Rust bağımlılıkları manifest'te ayrı UNKNOWN kayıtlarıdır; lock checksum'ları indirilmiş crate checksum'u gibi sunulmaz. Bunların kaynak/notice paketleri henüz indirilmedi. libvips tarball'ındaki vendored alt kod/dosyaların tamamı için dosya düzeyinde köken incelemesi de tamamlanmadı. Bu yüzden 28 girdinin bütün transitif bağımlılık ağını kapattığı iddia edilmez.

## Build ve lisans farkı

Upstream recipe libvips 8.18.7'yi açıkça kullanır; beş harici patch indirildi/hash'lendi; inline sed değişiklikleri exact posix.sh içinde korunur. libvips-cpp SONAME patch'i, libvips C çekirdeğinin statik bağlanması, nodelete, excluded static symbols ve runtime flags kayıttadır. glibc: Rocky8/glibc2.28/gcc-toolset15; musl: Alpine3.20/musl1.2.5. Bunlar tarif beyanıdır; üretim anındaki kesin compiler build numarası değildir. Floating base/paketler/nightly Rust ve Cargo/meson araçları bit düzeyinde yeniden üretimi engelleyen açıklardır. Upstream shell veya rustup script'i çalıştırılmadı.

libvips çekirdek LICENSE dosyası LGPL v2.1 metnidir. Birleşik npm paketi LGPL-3.0-or-later beyan eder. Pinned upstream THIRD-PARTY-NOTICES, LGPLv2/v2.1 `any later version` yoluyla LGPLv3 kullanımını açıklar ve cairo için MPL1.1, bazı alt bileşenler için izin verici lisanslar listeler. Bu beyan dosya bazında kaynak lisans metinleri ve derlenen parçalarla karşılaştırılmadan bütün parçalar aynı lisansa indirgenmez. LGPL çekirdek metni tek başına birleşik binary bildirimlerini karşılamaz.

## Yeni imaj ve değiştirme kanıtı

Yeni runtime/migrate imajları mevcut temiz selfhost CI build'lerinden ayrı ayrı incelenir. `libvips.json`, config digest, gerçek binary yolu/hash'i, ELF64 machine62, paket/sürüm, versions.json, ldd ve glibc/musl uyumluluğunu kaydeder. S05-A hash'leri yeni kanıt olarak kopyalanmadı. Musl paketleri otomatik silinmez. Artifact'lar son HEAD push ve PR koşularındadır; kesin SHA ve sonuçlar PR açıklamasında tutulur.

[Değiştirme provası](LIBVIPS-RELINKING.md) aynı byte'lı alternatif shared object yüklemesini sınar. Tam değiştirilmiş libvips/static LGPL alt bağımlılık rebuild veya bit reproducibility yapılmadı. Yerel diskte yalnız yaklaşık 910 MiB boşluk bulunduğundan ek VFS imaj build'i başlatılmadı; CI build'leri yeniden kullanılır. Prova sonucu görülmeden VERIFIED verilmez.

S05-A kapısı Sharp/@img native kayıtlarını yalnız dolu metin alanlarıyla PASS yapamaz. Yeni doğrulayıcı exact commit/sürüm/build dosya anchor'larını, tüm dependency setini, yerel özgün notice hash'lerini, patch'leri ve imaj kimliğini denetler. Kaynak, binary provenance, relinking ve bakımcı kararı ayrı tutulur. Manifest'teki açıklamalar veya otomatik testler hukuki onay değildir. Eksik native build/source ve Node/Debian kanıtları varken genel dağıtım kapalı kalır.

## Testler ve açık işler

Yeni testler doğru yapısal manifest'i PARTIAL kabul etme; yanlış commit/checksum/build manifest; eksik kaynak/lisans/relinking; bozuk/boş/traversal arşiv; yanlış imaj; dolu metinle yanlış PASS; genel dağıtımın açılmaması durumlarını kapsar. Mevcut lint/strict TS, 25 birim, 36 PG entegrasyon, 19 E2E, production build, Prisma/11 migration, tenant/finans/audit/query-plan, kaynak/preflight, temiz selfhost/restart, şifreli backup matrisi/ayrı recovery ve migration hatasında güvenli durma korunur.

S05-C önerisi: statik LGPL alt parçalar ve Rust transitif kaynaklarını tamamlamak; kesin toolchain ve build provenance ile değiştirilmiş ABI uyumlu libvips rebuild/relink deneyi yapmak. Node/Debian corresponding-source ve bildirim yükümlülükleri ayrıca açık kalır. İnsan kurulumu yapılmadı. Yeni release/tag, registry push, npm publish, deploy veya merge yoktur.

## Ara kontrol noktası ve npm bağı

`789840f7ffffe2fc72035c4c0e2fb0a271b46310` için [push](https://github.com/Blooregardx/siteyonetim-saas/actions/runs/41721418745) ve [PR](https://github.com/Blooregardx/siteyonetim-saas/actions/runs/41721429700) checks+selfhost başarılı. Yeni imajlar doğrudan incelendi; [runtime](evidence/s05b/baseline-789840f-app.json) ve [migration](evidence/s05b/baseline-789840f-migrate.json) snapshot'ları ayrı tutuldu. Bunlar S05-A hash'lerinden türetilmedi. İki platform binary'sinin yeni ölçülen hash'leri S05-A ile aynı çıktı; bu sonuç yalnız yeni byte incelemesiyle kaydedildi.

İlk LD_LIBRARY_PATH deneyinde iki imaj da PNG üretti ama alternatif kütüphane yüklenmedi; deney BLOCKED. Yeni probe addon ve libvips için ELF DT_NEEDED/RPATH/RUNPATH/SONAME alanlarını kaydeder; ayrıca LD_PRELOAD deneyi yapar. Alternatif dosya yüklenirken asıl dosyanın da yüklenmesi başarı sayılmaz. Bu ikinci deneyin sonucu son HEAD CI artifact/PR kaydındadır. Başarı halinde bile yalnız aynı-byte dinamik değiştirme yolu PARTIAL olabilir; değiştirilmiş kaynak/static LGPL rebuild VERIFIED sayılmaz.

Npm platform arşivleri ayrıca indirildi. SHA-512 SRI ve npm registry ECDSA imzaları OpenSSL ile doğrulandı (public key ID pinli). [Registry doğrulama kaydı](evidence/s05b/npm-verification.json) tarball SHA-256, gitHead ve iç binary SHA-256'larını içerir. glibc `4aa73553408c3964071728f4a231a8e86918e39bc49f1fbae75355f7ea933ea9`, musl `979b625437190a1970b835164e0e30d47dc60159ce6a394ce78cc40cb9d59ab8`; yeni imaj ölçümleriyle eşleşir. Npm publish aracı metadata'sı Node24.21.0/npm11.19.0 gösterir; bunlar C/C++ compiler sürümü değildir.

Npm SLSA subject digest'leri indirilen arşivlerle; commit/ref/workflow beyanları exact v1.3.4 commit'iyle eşleşti. [Upstream build koşusu](https://github.com/lovell/sharp-libvips/actions/runs/36315646015) GitHub API'de aynı commit için başarılıdır. Tam Sigstore Fulcio/Rekor güven zinciri doğrulaması yapılmadı: signed bundle korunur, ancak beyanın eşleşmesi bağımsız publisher identity veya bütün static alt bileşenlerin corresponding-source kanıtı diye sunulmaz.

Kaynak cache'i yeniden okunarak 28 arşiv SHA-256 ve arşiv içi notice eşleşmesi doğrulandı. [Makine raporu](evidence/s05b/source-archive-verification.json) PARTIAL/BLOCKED kararlarını korur. CI büyük kaynakları tekrar indirmez; exact build anchor'larını ve yerel özgün notice/patch dosyalarını tekrar hash'ler. Cache ile kaynak byte doğrulaması için `verify_libvips_sources.py --cache` kullanılabilir; cache hash kontrolünü atlamaz. Araştırma aracı kanonik manifest'i otomatik overwrite etmez; ayrı taslak üretir. Yeni test sayısı 14, S05-A kapı testleri 7'dir.

## Sharp addon tarifi ve probe düzeltmesi

Sharp 0.35.5 exact commit arşivi ayrıca indirildi/hash'lendi; özgün Apache LICENSE ve src/binding.gyp byte'ları korundu. Native 73 bildirime ek olarak Sharp LICENSE dosyası da manifest'tedir. Mozjpeg kısa recipe commit'i GitHub API ile `08265790774cd0714832c9e675522acbe5581437` tam commit'ine çözüldü; orijinal archive URL/hash kaydı değiştirilmedi.

`d84d05e` checks başarılı, selfhost yeni addon incelemesinde başarısız oldu: gerçek dosya adı `sharp-linux-x64-0.35.5.node`, probe ise sürümsüz ad varsaymıştı. Yeni probe dosya adını tahmin etmek yerine paketin `sharp.node` export'unu çözer. Başarısız job başarılı sayılmadı; son HEAD iki tam CI yeniden doğrulanmalıdır.

İkinci probe düzeltmesi: paket export'u `index.cjs` shim'idir; ELF dosyası olarak okunmaz. Gerçek lib/*.node dosyası ayrı bulunur, export ve native dosyanın hash'leri ayrı tutulur. İki ELF parser testi JavaScript ve bozuk header tablosunu reddeder. İzole probe scratch tmpfs `exec` gerektirir; normal app Compose değişmez. Eski yerel S05-A imajında yapılan tanılama source manifest'in yeni imaj kanıtı olarak kullanılmadı. Son yeni CI'da LD_LIBRARY_PATH ve LD_PRELOAD sonuçları ayrı doğrulanır.

## Başarılı yeni imaj kontrol noktası

`dc50c65bfc5a5f1dae4d0dc67e1c402ef52c7a7e` için [push CI](https://github.com/Blooregardx/siteyonetim-saas/actions/runs/41725468214) ve [PR CI](https://github.com/Blooregardx/siteyonetim-saas/actions/runs/41725475512) checks+selfhost başarılı. [Runtime snapshot](evidence/s05b/baseline-dc50c65-app.json), [migration snapshot](evidence/s05b/baseline-dc50c65-migrate.json) yeni CI imajlarından indirildi. Runtime config `sha256:3bf88820a91084ce8eb10e9ca9e5b21d804a5b5b6fbe9ac76491fe18e5cc0728`, migration config `sha256:841b9960129e54b927cbabbc24d80fbd42beb9765d3e7eed1574774256e34e9e`.

Her ikisinde Sharp 0.35.5, platform paketleri1.3.4, libvips8.18.7, ELF64 x86-64 ve 28 versions.json girdisi doğrulandı. LD_LIBRARY_PATH deneyi özgün dosyayı map etti: BLOCKED. LD_PRELOAD deneyi alternatif kopyayı map etti, özgün dosya mapped değildi, 1×1 PNG üretildi, exit0: yalnız PARTIAL. Orijinal/kopya hash'leri eşit; değiştirilmiş kaynak derlemesi değil. Addon DT_NEEDED libvips-cpp.so.8.18.7 ve DT_RPATH, libvips-cpp DT_RUNPATH=$ORIGIN gözlendi. Son genel filesystem envanteri musl addon dahil tüm native adaylarda ELF/dinamik alanları ayrıca kaydeder; çözümlenemeyenler UNRESOLVED kalır.

Kaynak edinme/byte kontrolü: native28 PASS, Sharp1 PASS. Binary-source eşleşmesi/onayı: PASS0, BLOCKED29 (native28+Sharp1). Cargo.lock kaynak kayıtları UNKNOWN357; bunların hepsinin binary'de bulunduğu iddia edilmez. Derlenmiş target/features alt kümesi belirlenmedi. Özgün metinler native73+Sharp1; per-file lisans/derleme kapsamı manuel incelemesi açık.

Kontrol noktasında ESLint/strict TS, 25 birim, 36 PG entegrasyon, 19 Playwright, production build, Prisma validate/generate, 11 migration/schema diff, tenant/finans/audit/query-plan, 12 preflight/4 archive/7 distribution gate/14 kaynak testi, 1 notice ve 2 ELF parser testi başarılı. Temiz selfhost/restart, şifreli backup hata matrisi, ayrı cluster encrypted recovery ve başarısız migration güvenli durma da iki job'da geçti.

Son dokümantasyon ve envanter commit'i sonrası iki CI yeniden doğrulanır. İmaj kendi içerdiği manifest'e kendi config digest'ini yazamaz; güncel son SHA, image config digest ve artifact bağları [taslak PR #27](https://github.com/Blooregardx/siteyonetim-saas/pull/27) harici kanıt kaydındadır. Buradaki dc50c65 snapshot'ları son dokümantasyon imajıyla aynı digest'te diye sunulmaz.
