# S05-E — Native deney tekrar üretimi

Yalnız izole Linux x86-64 DEVELOPMENT ortamı. Registry push, release/tag,
deploy, gerçek veritabanı veya SMTP yoktur. En az 2 CPU, 8 GiB toplam RAM ve
40 GiB boş disk önerilir; deney 6 GiB/2 CPU ile sınırlandırılır. Docker vfs
katmanları ek disk tüketir. Kaynak/cache doğrulaması atlanmaz.

## Girdiler

`docs/evidence/s05e/baseline.json`, `historical-transaction.json`,
`historical-rpm-files.json`, `python-input-hashes.json`, `rust-component-inputs.json`
ve S05-B native manifest/patch dosyaları kontrol kökleridir. Upstream source
commit `ebb95f8add54eee8bed840e3fb587e4cbec857d7`, libvips
`24ad4d042940e6bf99a68871ba886ca8847c9c82`.

Online edinim ile offline build ayrı aşamalardır. Doğrulanmamış installer,
curl-to-shell veya kaynak indirme pipeline'ı çalıştırılmaz. Rocky repository
metadata'sı kullanılarak tarihsel listede belirtilen exact NEVRA'lar indirilir;
hepsi frozen dosya SHA-256 listesiyle ve Rocky/EPEL publisher imzasıyla
doğrulanır. `s05e_prepare_rpms.sh` ilk araştırmadaki **güncel aday** transaction'ı
toplar; tarihsel sysroot'un yerine geçmez. Tarihsel işlem sırası update 109,
epel 8, build-dependencies 124 RPM'dir. Ek provider/i686 paketleri kurulmaz.

`docker/s05e-toolchain.Dockerfile` için boş context hazırlayın: üç stage dizini,
bu dosyaların `rpm-hashes.json` haritası, fingerprint/hash'i kayıtlı EPEL-8
public key, dört doğrulanmış PyPI girdisi ve `python-hashes.json`. Ninja sdist
önceden güvenli arşiv kontrolünden geçmelidir; pinned hash'ten farklı içerik
kullanılmaz. Base digest manifesti exact Rocky ae0813... olmalıdır.

```sh
docker build --network=none -f docker/s05e-toolchain.Dockerfile -t s05e-toolchain-historical /isolated/context
```

Bu yalnız yerel tag'dir; publish yoktur. Çalıştırmadan önce gerçek image config
digest'ini kaydedin. Tarihsel RPM sürüm eşleştirmesi byte-reproducible image
iddiası değildir; layer/config timestamp'leri değişebilir.

## Rust, cargo-c ve registry cache

Resmi 2026-09-27 Rust manifest SHA-256:
`ad7c5ca64d80a5c7771089f741ab90c9eb5dcbc766ce81f2c90af8fc295b40cc`.
Üç component archive'ını kayıtlı hash'leriyle doğrulayın; compiler/std/cargo
regular-file açılımlarını da archive bytes'ına eşleyin. Cargo-c exact crate
`0.10.25+cargo-0.99.0`, SHA-256
`6b2ddde58a8a773ccce4b6384acacd3ce01373f52717dd2424633ed46755c627`.
Bundled Cargo.lock hash'i `38fb80318361597afc6f7206944fc0771c2ff42e983b0c161f0f63ba4ab4598b`.

Online `cargo fetch --locked` yalnız kaynak/cache edinimidir, build script
çalıştırmaz. cargo-c için 410 registry kaydı ve S05-D generated lockfile'ındaki
registry kaynaklarının gerçek `.crate` ve açılmış dosyaları doğrulanır.
Güvenilir Cargo'nun checksum kontrolü ayrıca fiziksel yeniden okumayla desteklenir.
S05-D lock'u değiştirmeyin; ayrı `generated-Cargo.lock` girdisi kullanın.

Doğrulanmış sysroot'ta, ağ kapalı/non-root/read-only/cap-drop ALL ve 2 CPU/6 GiB
ile `cargo install --offline --locked --path /source --root /out/cargo-c-historical-install`
çalıştırın. Source readonly, target/cache yalnız scratch dizinlerindedir.
`CARGO_BUILD_JOBS=2`; executable ve compiler/linker kaynak/sürüm/hash'lerini
ölçün. `capture_s05e_toolchain.py` gerçek tool output'larını ve başarılı/başarısız
bootstrap'ı ayrı kaydeder. Çalışan işlem exit 0 sayılmaz.

## Tam native deney

Girdi kökü `sources/*.tar`, `patches/{0..4}.patch`, `rust/{rustc,cargo,rust-std}.tar.xz`,
`rust/toolchain`, `rust/cargo-c-source`, `cargo-cache`, `historical/{update,epel,build-dependencies}`,
`cargo-c-historical-install` ve `generated-Cargo.lock` içerir. Script bu
dosyaları yeniden doğrular; eksikte full build başlatmaz.

```sh
python3 scripts/capture_s05e_toolchain.py --inputs /isolated/inputs --out docs/evidence/s05e --image sha256:LOCAL_CONFIG_DIGEST
python3 scripts/run_s05e_native.py --inputs /isolated/inputs --out /isolated/new-run --image sha256:LOCAL_CONFIG_DIGEST --minutes 75
```

Yukarıdaki capture yalnız **yeni** S05-E çalışma kopyasında kullanılmalıdır;
tarihsel A/B/C/D kayıtları veya yayımlanmış E evidence üzerine yazılmaz.
Preflight sonucu tek başına tam build/ABI/dağıtım PASS değildir. Docker daemon
bağlantısı koparsa aynı girdiler/config ile Created konteynerin durumu incelenir;
build sessizce yeniden denenmiş veya başarılı olmuş sayılmaz. Mevcut deneyde
ayrı watchdog ve Docker state kaydı kullanılır. Yeni runner iç timeout ile
sınırlandırılır. Başarısız aşama/loglar tutulur; source/profile değiştirilerek
reduced build'e düşürülmez.

CONTROL ve MODIFIED aynı native statik prefix'i kullanır; bağımlılık arşivleri
tekrar derlenip farklı koşullarla değiştirilmez. Her iki libvips build directory,
.o/.a, compiler output ve link map'i ayrı korunur. Kaynak marker diff'i yalnız
MODIFIED init.c'ye uygulanır. `--strip`, optimizasyon ve static symbol exclusion
upstream profilindedir. ABI, DWARF/type coverage ve Sharp PNG/JPEG/SVG/proc maps
ölçülmeden ABI/Sharp PASS verilmez. Yüklenen dosyanın hash'i ve eski bundle'ın
ayrıca yüklenip yüklenmediği açıkça kaydedilir.

## Saklama

Büyük kaynak/object/archive dosyaları Git'e eklenmez. Cloud scratch dosyalarının
oturum sonrasında kalacağı garanti değildir; CI artifact'ları da uzun dönem
source provision yerine geçmez. Her artifact için hash, kapsam ve retention
ayrı kaydedilmelidir. Gerçek source bundle ve iki bağımsız kalıcı kopya eksikse
STATIC LGPL RELINKING INPUTS / DURABLE SOURCE PROVISION en fazla PARTIAL kalır.
