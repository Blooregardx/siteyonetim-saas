# S05-C Rust kaynak zinciri ve değiştirilmiş libvips

DEVELOPMENT: INCOMPLETE — bu belge kaydından sonraki son HEAD push/PR checks+selfhost sonuçları beklenir; nihai READY/INCOMPLETE kararı taslak PR ve teslim raporunda verilir.
RUST SOURCE EVIDENCE: PARTIAL
MODIFIED LIBVIPS REBUILD: PARTIAL — farklı-byte kaynak rebuild ve Sharp PNG yolu başarılı; tam özgün bundle/ABI eşleşmesi yok.
STATIC LGPL RELINKING INPUTS: BLOCKED
LIBVIPS CORRESPONDING SOURCE: PARTIAL
SOURCE RELEASE: ALPHA.2 PUBLISHED — UNCHANGED
BINARY DISTRIBUTION: BLOCKED
INDEPENDENT INSTALLATION: PENDING HUMAN VALIDATION

Başlangıç main `f2eaea1957126f510665197d952d7593fc755cf9`; S05-B #27 2026-11-04 00:11:39 UTC'de birleşmiş. GitHub main/merge commit ve temiz çalışma ağacı doğrulandı; aynı kapsamda açık PR yok. Alpha.2 release 2026-11-03 16:22:11 UTC, tag ve release target `c20646fddbc8a7e3dcd45cbc01aacd531c225e4a` değişmedi. AGENTS.md ve istenen S05-B dosyaları incelendi. Tarihsel S05-A/B evidence dosyaları değiştirilmez.

## Gerçek Rust kapsamı

[Scope manifest'i](evidence/s05c/rust-build-scope.json), özgün Cargo.lock SHA-256 ve her kayıt için isim/sürüm, kaynak/checksum, target/features bağlamı, dependency türü, kanıt satırı ve eksikleri içerir. S05-B'nin 357 dış registry/git kaydı, Cargo.lock'un bütün package blokları değildir: ayrıca 9 workspace/path kaydı bulunur.

Upstream sharp-libvips commit `ebb95f8add54eee8bed840e3fb587e4cbec857d7`, başarılı glibc [run 36315646015](https://github.com/lovell/sharp-libvips/actions/runs/36315646015), job 108609814156 log'u GitHub connector üzerinden okundu. CLI redirect erişimi Forbidden verdi; log'a erişilemedi diye varsayılmadı. [Derleme gözlemleri](evidence/s05c/upstream-build-observations.json) yalnız `Project name:librsvg` ile onun cargo-cbuild komutu arasındadır. Docker toolchain kurulurken cargo-c için derlenen 348 satır dışlandı. Librsvg aşamasındaki 164 compile satırı, 357 dış kaydın 162'si ve iki workspace/path paketidir. Paket adı/sürümü ve log zaman damgası kanıtlandı; generated Cargo package ID ve per-crate feature/normal-build-dev rolü log'da bulunmadığından UNKNOWN/null bırakıldı.

|357 dış kayıt kararı|Sayı|
|---|---:|
|COMPILED — EVIDENCED|162|
|RESOLVED — NOT PROVEN COMPILED|0|
|NOT SELECTED — EVIDENCED|0|
|UNKNOWN|195|

Eksik compile satırı, derlenmediğinin kanıtı değildir. COMPILED, final shared-object'e link edildiğinin veya kaynak/binary bit eşleşmesinin kanıtı da değildir. Path kayıtları ayrıca tutulur; iki yerel paket librsvg/librsvg-c 2.63.2 gözlenmiştir.

Önemli fark: pinned recipe image gif/webp ve cairo pdf/ps feature'larını çıkarıp **cargo update --workspace** çalıştırır. Sonra `cargo cbuild --locked --library-type staticlib --release -p librsvg-c` çalışır. Bu `--locked`, arşivdeki özgün 357 kaydın aynen kullanıldığını kanıtlamaz; güncellenmiş lockfile elde değil. Log'daki 162 registry ad/sürüm, özgün lock'taki aynı kayıtlarla eşleşir; kaynak checksum bağının otoritesi özgün lock olarak açıkça etiketlenir. [Target gözlemleri](evidence/s05c/upstream-target-observations.json) rustup default host x86_64-unknown-linux-gnu ve rustc 1.101.0-nightly 75a75c3e0/2026-09-26 gösterir. Kayıtlı cbuild komutunda açık --target yoktur; gözlenmemiş ortam override'ları için tam provenance iddia edilmez.

Kontrollü cargo metadata/tree deneyi ayrı artifact'tır. [Gerçek sonuç](evidence/s05c/cargo-resolution-result.json): metadata exit 101; [stderr](evidence/s05c/cargo-metadata.stderr.txt) lock güncellemesi gerektiğini bildirir. Önce/sonra lock hash'i aynıdır; tree bu başarısızlıktan sonra çalıştırılmaz. [rustc -vV](evidence/s05c/cargo-rustc.txt) 1.92.0, commit ded5c06cf21d2b93bffd5d884aa6e96934ee4234, LLVM 21.1.3 gösterir. Rust 1.92.0 exact OCI digest'iyle, declared MSRV 1.92 karşılanarak özgün lock ve aynı feature metin değişiklikleriyle --locked/--filter-platform kullanılır. Dependency graph, compilation değildir. Komut lock güncellemesi isterse hata kaydedilir; sessizce yeni lock üretilmez. Bu kontrol tarihsel derleme kanıtını veya UNKNOWN kayıtları otomatik değiştirmez.

## Crate kaynakları

[Kaynak manifest'i](evidence/s05c/rust-source-manifest.json) gerçek indirilen .crate SHA-256 ile Cargo checksum'u ayrı alanlarda tutar. Yerelde 357 aday için 344 kaynak/bildirim edinme PASS, 13 BLOCKED; bu sayılar hukuki onay veya tüm adayların binary'de bulunduğu anlamına gelmez. Derlenen 162 dış adayın 160 kaydı kaynak/bildirim ediniminde PASS, 2 kaydı BLOCKED: mutants 0.0.4 (MIT metadata) ve selectors 0.40.0 (MPL-2.0 metadata) arşivlerinde tanınan özgün bildirim dosyası bulunmadı. Derlenen gözlemler önce indirilir. Cargo.toml lisans beyanı, özgün LICENSE/COPYING/NOTICE byte/hash'leri ve build.rs yolları korunur; kaynak/lisans kapsamı ayrıca incelenmelidir.

Kaynaklar HTTPS static.crates.io'dan alınır; cache her kullanımda hash'lenir. Arşiv extract edilmez/link takip edilmez; traversal/kök dışı link ve oversized notice reddedilir. Derleme deneyine gereken libvips arşivi ayrıca yalnız regular dosyalarla, 512 MiB genişleme sınırıyla çıkarılır. Büyük source/binary dosyaları Git'e eklenmez. Git/path kaydı registry gibi indirilemez; kesin revision/archive/tree kanıtı olmadan PASS yoktur.

## Statik LGPL ve ayrı lisanslar

[Statik analiz](evidence/s05c/static-lgpl-analysis.json), dokuz LGPL/MPL ilgili native kayıt için source archive/file hash ve gerçek kaynak başlığından örnek içerir. Dosya örneği bütün derlenen dosyaların lisansı sayılamaz: **REQUIRES LEGAL REVIEW**. Üst paketin LGPL 3 beyanı bütün alt dosyalara uygulanmaz; core LGPL 2.1/later; proxy-libintl ve Pango örneklerinde GNU Library GPL 2/later, upstream later-version seçimi, cairo MPL ve diğer lisanslar ayrı kalır.

Pinned recipe libvips C çekirdeği ve birçok kütüphaneyi libvips-cpp'ye statik bağlar. Orijinal eşleşen GLib/GObject/Pango/librsvg vb. .a/.o seti edinilip doğrulanmadı. Upstream dev paketi headers/C++ source deklarasyonu, tam statik relinking girdileri kanıtı değildir. Yeni reduced-profile libvips.a üretilebilse bile orijinal bütün statik bundle'ı kapatmaz.

## Değiştirilmiş kaynak deneyi

[Rebuild manifest'i](evidence/s05c/rebuild-manifest.json), [toolchain spec](evidence/s05c/toolchain-spec.json) ve [tekrar rehberi](LIBVIPS-REBUILD-REPRODUCTION.md) hazırlanmıştır. İlk iki deneme environment hazırlığında BuildKit secret boyutu ve apt CA dosya izni nedeniyle durdu. Düzeltmelerden sonra [push run 41751407159](https://github.com/Blooregardx/siteyonetim-saas/actions/runs/41751407159) gerçek control/modified build, PNG ve fiziksel kanıt doğrulamasını tamamladı; checks+selfhost da başarılı. [PR run 41751413619](https://github.com/Blooregardx/siteyonetim-saas/actions/runs/41751413619) checks+selfhost başarılı. Bunlar deney commit 4d740ff kanıtlarıdır; son dokümantasyon/kod HEAD test sonucu ayrıca beklenir.

Hedef exact libvips 8.18.7 kaynak SHA ve pinned SONAME patch; ayrı Node 24-bookworm base digest, signed Debian snapshot 20261103 ve Meson 1.9.1 wheel SHA ile environment. Snapshot InRelease hash'leri ayrıca pinli; apt signature/TLS kontrolü açık, yalnız tarihsel metadata expiry kontrolü kapalıdır. GCC 12.2.0/Meson 1.9.1/Ninja 1.11.1 beklenir; gerçek linker/dpkg sürümleri artifact'ta kaydedilir. Orijinal GCC 15/Rust nightly statik paketiyle aynı ortam değildir. Rust 1.101.0-bookworm tag probe bulunamadı; floating nightly veya rustup shell installer kullanılmadı.

Sınırlı PNG/JPEG profilinde SVG/librsvg kapalıdır; normal uygulama imajının yerine konmaz. Aynı ortamda control ve modified kaynaklar derlenir. init.c'ye `used,retain` internal sabit marker eklenir; algoritma/API değiştirilmez ve upstream LGPL başlığı korunur. Source diff/SHA, eski/control/new binary SHA, gerçek SONAME ve nm exports, marker byte'ı, PNG dosya CRC/IHDR/zlib içeriği ve gerçek Sharp addon yükleme durumu sınanır. Yalnız LD_PRELOAD veya farklı hash yeterli değildir: yeni dosya mapped, eski dosya mapped değil, loaded-file hash actual new binary ile aynı olmalıdır. Control→modified ABI ve dağıtılan bundle→modified ABI ayrı raporlanır. Genel/read-only Compose güvenliği gevşetilmez.

## Ölçülen deney sonucu

|Kanıt|Sonuç|
|---|---|
|Sharp / platform paketi / libvips|0.35.5 / 1.3.4 / 8.18.7|
|Gerçekte yeniden ölçülen dağıtılan glibc binary SHA-256|`4aa73553408c3964071728f4a231a8e86918e39bc49f1fbae75355f7ea933ea9`|
|Control rebuild SHA-256|`96b2937bb906e8aa99e0bfa9811c90cd1f5ed9d41f473f091bafc5dd922e5fe6`|
|Değiştirilmiş rebuild SHA-256|`480bd66dabe1d6e69c515faf333fcd220f701f3432c498ca010786953f109d05`|
|Environment config digest|`sha256:45a6916290b4a7264c5f38c4af81009a5edbf6da6ee5b963c292e9857912a134`|
|Environment SBOM|Syft JSON 1.18.1, 558 bileşen; uygulama runtime/migration SBOM'u değildir|
|GCC / linker / Meson / Ninja / Python|12.2.0 / GNU ld 2.40 / 1.9.1 / 1.11.1 / 3.11.2|
|Target / Rust|x86_64-linux-gnu; reduced build'de Rust kullanılmaz|
|Control → modified|1576 export adı eşit, SONAME libvips-cpp.so.8.18.7; tam tip/layout ABI ispatı değildir|
|Dağıtılan bundle → modified|1946 özgün export adı eksik; tam ABI eşdeğerliği iddia edilmez|
|Gerçek Sharp testi|2×2 sentetik #123456 → resize 1×1 PNG, decode/metadata ve CRC/zlib pixel kontrolü PASS|
|Yüklenen kütüphane|Yeni dosya mapped, eski npm libvips dosyası mapped değil; loaded SHA yeni binary ile eşit|
|Statik girdiler|Yeni control/modified libvips.a artifact'ta; özgün tam statik bundle girdileri BLOCKED|
|Bit düzeyinde reproducibility|NOT TESTED|

[Ham ölçümler](evidence/s05c/runs/41751407159/rebuild-result.json), [source diff](evidence/s05c/runs/41751407159/source-change.patch), [ham maps](evidence/s05c/runs/41751407159/sharp-maps.txt), [dpkg sürümleri](evidence/s05c/runs/41751407159/dpkg-packages.txt) ve [karar](evidence/s05c/runs/41751407159/validation.json) ayrı tutulur. Artifact ID 13286701379, ZIP 228686247 byte, SHA-256 `c0e545ff15dd971b544466df58412f042b1ec144b7e3764dd23a4487e43ecbf4`. Fiziksel source/ELF/PNG/maps dosyaları artifact'tan güvenli seçilerek yeniden okundu; PARTIAL için beklenen exit 1 alındı. Sonraki HEAD deneyi native addon dosyasını ve kesin paket sürümlerini ayrıca bağlar; yeni imaj/digest bu tarihsel deneyle karıştırılmaz.

## CI, retention ve açık işler

Mevcut iki zorunlu job korunur. Yeni 30 kaynak/scope/rebuild testi zorunlu checks içindedir: yanlış lock/checksum/crate/notice/source/target/toolchain, fiziksel ELF mimari ve ABI farkı, aynı-byte kopya, ham maps ve eski kütüphane, foreign SBOM, eksik statik girdiler ve yanlış genel PASS reddedilir. Mevcut S05-A 7 ve S05-B 14 test korunur. Ağ/derleme deneyi ayrı **non-gating rebuild-experiment** job'ıdır; yalnız push'ta çalışır, PR'de ikinci ağır build yapılmaz. `continue-on-error` deney işini zorunlu regresyondan ayırır; başarısız step/job ve artifact BLOCKED sonucu saklanır, başarısız deney başarılı diye sayılmaz. Son HEAD push/PR checks+selfhost bitmeden DEVELOPMENT hazır denmez.

CI artifact'ları 14 gün tutulur. Başarılı deneyde kaynak/patch, iki build tree, .a/.o/install girdileri, binary'ler, log ve toolchain bilgileri tar olarak; source crate cache'i ayrı hash-kontrollü tar olarak korunur. Başarısızlıkta ulaşılmış aşama/log/partial çıktılar tutulur. Bu geçici saklama, gelecekteki binary dağıtımında uzun süreli corresponding-source sağlama yükümlülüğü değildir; kalıcı mirror/offer/relink paketi hâlâ eksik.

S05-D: generated post-update Cargo.lock ve exact feature/role/link subset'ini tamamlamak; tüm static LGPL object/source girdileriyle orijinal profile uygun yeniden derleme, tam Sigstore ve uzun süreli source sunumu. Node/Debian, Prisma ve diğer genel dağıtım kapıları açık kalır. İnsan kurulumu yapılmadı. Merge/tag/release/npm/registry/deploy yoktur.
