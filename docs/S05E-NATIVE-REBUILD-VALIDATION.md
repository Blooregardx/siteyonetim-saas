# S05-E — Full native rebuild ve binary compliance

Yalnız DEVELOPMENT. Başlangıç `3f21f383bbf005f4b9e5ed877cb3491f82ecacd0`.
main başlangıçta `b93b0eeaaeabdf898a6a2f9bf35cc9c1016a3d54`; S05-D #29
henüz açık/taslak olduğundan E PR'ı D dalına katmanlanır. Merge yapılmaz.
S05-A/B/C/D kanıtları ve AGPL-3.0-only lisansı korunur.

Bu belge deney devam ederken hazırlanmıştır; son durum aşağıdaki kanıtlara ve
son HEAD CI sonuçlarına göre güncellenecektir. DEVELOPMENT: BLOCKED (CI bekliyor).
BINARY DISTRIBUTION READINESS: BLOCKED. INDEPENDENT INSTALLATION: BLOCKED —
PENDING HUMAN VALIDATION. SOURCE RELEASE: ALPHA.2 PUBLISHED — UNCHANGED.

## Yeni fiziksel kanıtlar

- [Başlangıç ve upstream kayıtları](evidence/s05e/baseline.json): exact upstream
  commit, açık workflow job log'u ve log SHA-256. Tarihsel upstream lockfile
  kurtarıldı iddiası yoktur.
- Özgün Rocky immutable manifest: `sha256:ae0813ccb1bb83f4e0220acdd1539f52831517de334368e960824db7e37ee210`.
  Güncel floating tag farklı bir imajdır ve onun yerine kullanılmaz.
- [241 tarihsel RPM işlemi](evidence/s05e/historical-transaction.json),
  [yeniden edinilen RPM byte hash'leri](evidence/s05e/historical-rpm-files.json),
  [302 kurulu paket](evidence/s05e/installed-rpms.tsv),
  [gerçek tool sürüm ve hash ölçümleri](evidence/s05e/measured-tools.json).
  RPM header hash'i ile dosya SHA-256 değeri ayrı alanlardır. Yeni edinilmiş,
  imzası doğrulanmış aynı NEVRA, upstream'in tarihsel RPM byte attestation'ı değildir.
- GCC 15.2.1-7.1.el8_10, binutils 2.44-3.el8; Python 3.12.14;
  Meson 1.12.1 ve Ninja 1.13.2. Ninja doğrulanmış sdist'ten GCC ile üretildi;
  upstream PyPI wheel compiler'ının aynısı olduğu iddia edilmez.
- [Rust/Cargo resmi archive hash'leri](evidence/s05e/rust-component-inputs.json):
  2026-09-27 dağıtımı, rustc `75a75c3e0a67d3fa3d03982775f5bb0356e7b510`,
  Cargo `3d7cf6e937d6127d0f49881bf689c560b36d35c4`.
- cargo-c `0.10.25+cargo-0.99.0`, 410 registry arşivi doğrulandı; tarihsel
  sysroot'ta ağ kapalı bootstrap exit 0. [Executable hash'leri](evidence/s05e/toolchain.json).
- [28 native kaynak](evidence/s05e/native-source-integrity.json) ve beş özgün
  patch yeniden hash kontrolünden geçti. Kaynak açılımları ve Rust registry
  kaynak dosyaları da arşiv bytes'ıyla karşılaştırılır.

## Deney kapsamı ve sınırlar

Tam kaynak profili Sharp 0.35.5 / platform 1.3.4 / libvips 8.18.7 içindir.
S05-C azaltılmış PNG/JPEG tarifi kullanılmaz. S05-D kontrollü lockfile hash'i
`5723e14ce316e9058c76257848e18ab52624c98d16f758b5f8a73b5007b2ab8b`
sabitlenir; upstream'in bilinmeyen post-update lockfile'ıyla özdeş sayılmaz.
Deney kaynak kodu/profil yeniden üretimini, bit düzeyinde historical binary
reproducibility'den ayrı tutar.

Network none, root olmayan kullanıcı, read-only rootfs, cap-drop ALL,
no-new-privileges, 2 CPU/6 GiB RAM ile ayrı scratch ortamı kullanılır.
Standart uygulama Dockerfile/Compose güvenliği değişmez. Meson'un /usr/share,
/etc ve /var kurulum yolları yalnız deney prefix'ine taşınır; bu türetilmiş
config ve tam invocation ayrıca saklanır. Kaynak script'leri uzaktan çalıştırılmaz.

CONTROL tamamlandıktan sonra aynı dondurulmuş statik bağımlılık girdileriyle
libvips yeniden derlenir. MODIFIED değişikliği, init.c içindeki private
`used,retain` sabitidir: public API veya görsel işlem algoritması değişmez.
Gerçek farklı kaynak/binary hash'i olmadan modified rebuild kararı verilmez.
1946 export açığının yeniden ölçümü, versioned symbol karşılaştırması, ABI
tip kapsamı, PNG/JPEG/SVG ve proc maps doğrulaması ayrı sonuçlar olacaktır.

## Rust bildirimi

[Dokuz kaydın yeni araştırması](evidence/s05e/rust-notice-resolution.json):
2 PASS / 7 BLOCKED / 0 UNKNOWN / 0 N/A. r-efi 5.3.0 ve 6.0.0 exact crate
arşivlerindeki AUTHORS, tam özgün MIT izin metni/disclaimer ve telif içerir.
Önceki filename-only sınırlaması, yalnız bu sürümlere/hash'lere bağlı kural ile
giderildi. PASS yalnız kaynak/bildirim edinimidir; hukuki onay değildir.
block, difflib, malloc_buf, objc-foundation, objc_id ve iki winapi target crate
yalnız metadata/header veya başka sürüm metniyle kapatılmaz. Compile/link
kanıtı olmadan platform dışı veya dev gerekçesiyle N/A yapılmaz.

## Kaynak sunumu ve CI

[Yayın öncesi protokol](S05E-SOURCE-PROVISION-PROTOCOL.md) ve
[tekrar üretme adımları](S05E-NATIVE-REBUILD-REPRODUCTION.md) geçerlidir.
OCI layer/config/digest, gerçek binary bytes'ı, SBOM, source/patch/notice,
toolchain ve relinking inventory fiziksel olarak eşleştirilir. Yalnız dolu
metin alanı veya yeşil CI hukuki PASS vermez. İki bağımsız runner kopyası ve
iki yeni runner restore'u küçük sentetik paket üzerinde CI'da çalışır.
Tek GitHub artifact backend'i ve 14 günlük saklama, kalıcı kaynak sunumu değildir.

Mevcut uygulama/selfhost/recovery ve S05-A/B/C/D testleri korunur. Yeni zorunlu
S05-E testleri negatif source/archive, exact notice, sahte sonuç ve yanlış
OCI/SBOM/binary eşleşmelerini kapsar. Başarısız deney ayrı raporlanır;
uygulama CI başarısı binary dağıtım onayı sayılmaz.
