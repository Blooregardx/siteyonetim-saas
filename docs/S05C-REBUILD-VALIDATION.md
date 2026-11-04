# S05-C Rust kaynak zinciri ve değiştirilmiş libvips

DEVELOPMENT: INCOMPLETE — son HEAD iki zorunlu CI sonucu bekleniyor.
RUST SOURCE EVIDENCE: PARTIAL
MODIFIED LIBVIPS REBUILD: BLOCKED — hazırlanmış deney henüz çalıştırılmadı.
STATIC LGPL RELINKING INPUTS: BLOCKED
LIBVIPS CORRESPONDING SOURCE: PARTIAL
SOURCE RELEASE: ALPHA.2 PUBLISHED — UNCHANGED
BINARY DISTRIBUTION: BLOCKED
INDEPENDENT INSTALLATION: PENDING HUMAN VALIDATION

Başlangıç main `f2eaea1957126f510665197d952d7593fc755cf9`; S05-B #27 2026-11-04 00:11:39 UTC'de birleşmiş. GitHub main/merge commit ve temiz çalışma ağacı doğrulandı; aynı kapsamda açık PR yok. Alpha.2 release 2026-11-03 16:22:11 UTC, tag ve release target `c20646fddbc8a7e3dcd45cbc01aacd531c225e4a` değişmedi. AGENTS.md ve istenen S05-B dosyaları incelendi. Tarihsel S05-A/B evidence dosyaları değiştirilmez.

## Gerçek Rust kapsamı

[Scope manifest'i](evidence/s05c/rust-build-scope.json), özgün Cargo.lock SHA-256 ve her kayıt için isim/sürüm, kaynak/checksum, target/features bağlamı, dependency türü, kanıt satırı ve eksikleri içerir. S05-B'nin357 dış registry/git kaydı, Cargo.lock'un bütün package blokları değildir: ayrıca9 workspace/path kaydı bulunur.

Upstream sharp-libvips commit `ebb95f8add54eee8bed840e3fb587e4cbec857d7`, başarılı glibc [run36315646015](https://github.com/lovell/sharp-libvips/actions/runs/36315646015), job108609814156 log'u GitHub connector üzerinden okundu. CLI redirect erişimi Forbidden verdi; log'a erişilemedi diye varsayılmadı. [Derleme gözlemleri](evidence/s05c/upstream-build-observations.json) yalnız `Project name:librsvg` ile onun cargo-cbuild komutu arasındadır. Docker toolchain kurulurken cargo-c için derlenen348 satır dışlandı. Librsvg aşamasındaki164 compile satırı,357 dış kaydın162'si ve iki workspace/path paketidir. Paket adı/sürümü ve log zaman damgası kanıtlandı; generated Cargo package ID ve per-crate feature/normal-build-dev rolü log'da bulunmadığından UNKNOWN/null bırakıldı.

|357 dış kayıt kararı|Sayı|
|---|---:|
|COMPILED — EVIDENCED|162|
|RESOLVED — NOT PROVEN COMPILED|0|
|NOT SELECTED — EVIDENCED|0|
|UNKNOWN|195|

Eksik compile satırı, derlenmediğinin kanıtı değildir. COMPILED, final shared-object'e link edildiğinin veya kaynak/binary bit eşleşmesinin kanıtı da değildir. Path kayıtları ayrıca tutulur; iki yerel paket librsvg/librsvg-c2.63.2 gözlenmiştir.

Önemli fark: pinned recipe image gif/webp ve cairo pdf/ps feature'larını çıkarıp **cargo update --workspace** çalıştırır. Sonra `cargo cbuild --locked --library-type staticlib --release -p librsvg-c` çalışır. Bu `--locked`, arşivdeki özgün357 kaydın aynen kullanıldığını kanıtlamaz; güncellenmiş lockfile elde değil. Log'daki162 registry ad/sürüm, özgün lock'taki aynı kayıtlarla eşleşir; kaynak checksum bağının otoritesi özgün lock olarak açıkça etiketlenir. [Target gözlemleri](evidence/s05c/upstream-target-observations.json) rustup default host x86_64-unknown-linux-gnu ve rustc1.101.0-nightly75a75c3e0/2026-09-26 gösterir. Kayıtlı cbuild komutunda açık --target yoktur; gözlenmemiş ortam override'ları için tam provenance iddia edilmez.

Kontrollü cargo metadata/tree deneyi ayrı artifact'tır. Rust1.92.0 exact OCI digest'iyle, declared MSRV1.92 karşılanarak özgün lock ve aynı feature metin değişiklikleriyle --locked/--filter-platform kullanılır. Dependency graph, compilation değildir. Komut lock güncellemesi isterse hata kaydedilir; sessizce yeni lock üretilmez. Bu kontrol tarihsel derleme kanıtını veya UNKNOWN kayıtları otomatik değiştirmez.

## Crate kaynakları

[Kaynak manifest'i](evidence/s05c/rust-source-manifest.json) gerçek indirilen .crate SHA-256 ile Cargo checksum'u ayrı alanlarda tutar. Yerelde357 aday için344 kaynak/bildirim edinme PASS,13 BLOCKED; bu sayılar hukuki onay veya tüm adayların binary'de bulunduğu anlamına gelmez. Derlenen gözlemler önce indirilir. Cargo.toml lisans beyanı, özgün LICENSE/COPYING/NOTICE byte/hash'leri ve build.rs yolları korunur; kaynak/lisans kapsamı ayrıca incelenmelidir.

Kaynaklar HTTPS static.crates.io'dan alınır; cache her kullanımda hash'lenir. Arşiv extract edilmez/link takip edilmez; traversal/kök dışı link ve oversized notice reddedilir. Derleme deneyine gereken libvips arşivi ayrıca yalnız regular dosyalarla,512MiB genişleme sınırıyla çıkarılır. Büyük source/binary dosyaları Git'e eklenmez. Git/path kaydı registry gibi indirilemez; kesin revision/archive/tree kanıtı olmadan PASS yoktur.

## Statik LGPL ve ayrı lisanslar

[Statik analiz](evidence/s05c/static-lgpl-analysis.json), dokuz LGPL/MPL ilgili native kayıt için source archive/file hash ve gerçek kaynak başlığından örnek içerir. Dosya örneği bütün derlenen dosyaların lisansı sayılamaz: **REQUIRES LEGAL REVIEW**. Üst paketin LGPL3 beyanı bütün alt dosyalara uygulanmaz; core LGPL2.1/later, upstream later-version seçimi, cairo MPL ve diğer lisanslar ayrı kalır.

Pinned recipe libvips C çekirdeği ve birçok kütüphaneyi libvips-cpp'ye statik bağlar. Orijinal eşleşen GLib/GObject/Pango/librsvg vb. .a/.o seti edinilip doğrulanmadı. Upstream dev paketi headers/C++ source deklarasyonu, tam statik relinking girdileri kanıtı değildir. Yeni reduced-profile libvips.a üretilebilse bile orijinal bütün statik bundle'ı kapatmaz.

## Değiştirilmiş kaynak deneyi

[Rebuild manifest'i](evidence/s05c/rebuild-manifest.json), [toolchain spec](evidence/s05c/toolchain-spec.json) ve [tekrar rehberi](LIBVIPS-REBUILD-REPRODUCTION.md) hazırlanmıştır. Başlangıç sonucu **NOT RUN/BLOCKED**; plan başarılı deney gibi sunulmaz.

Hedef exact libvips8.18.7 kaynak SHA ve pinned SONAME patch; ayrı Node24-bookworm base digest, signed Debian snapshot20261103 ve Meson1.9.1 wheel SHA ile environment. Snapshot InRelease hash'leri ayrıca pinli; apt signature/TLS kontrolü açık, yalnız tarihsel metadata expiry kontrolü kapalıdır. GCC12.2.0/Meson1.9.1/Ninja1.11.1 beklenir; gerçek linker/dpkg sürümleri artifact'ta kaydedilir. Orijinal GCC15/Rust nightly statik paketiyle aynı ortam değildir. Rust1.101.0-bookworm tag probe bulunamadı; floating nightly veya rustup shell installer kullanılmadı.

Sınırlı PNG/JPEG profilinde SVG/librsvg kapalıdır; normal uygulama imajının yerine konmaz. Aynı ortamda control ve modified kaynaklar derlenir. init.c'ye `used,retain` internal sabit marker eklenir; algoritma/API değiştirilmez ve upstream LGPL başlığı korunur. Source diff/SHA, eski/control/new binary SHA, gerçek SONAME ve nm exports, marker byte'ı, PNG dosya CRC/IHDR/zlib içeriği ve gerçek Sharp addon yükleme durumu sınanır. Yalnız LD_PRELOAD veya farklı hash yeterli değildir: yeni dosya mapped, eski dosya mapped değil, loaded-file hash actual new binary ile aynı olmalıdır. Control→modified ABI ve dağıtılan bundle→modified ABI ayrı raporlanır. Genel/read-only Compose güvenliği gevşetilmez.

## CI, retention ve açık işler

Mevcut iki zorunlu job korunur. Yeni kaynak/scope/rebuild negatif testleri zorunlu checks içindedir. Ağ/derleme deneyi ayrı **non-gating rebuild-experiment** job'ıdır; yalnız push'ta çalışır, PR'de ikinci ağır build yapılmaz. `continue-on-error` deney işini zorunlu regresyondan ayırır; başarısız step/job ve artifact BLOCKED sonucu saklanır, başarısız deney başarılı diye sayılmaz. Son HEAD push/PR checks+selfhost bitmeden DEVELOPMENT hazır denmez.

CI artifact'ları14 gün tutulur. Başarılı deneyde kaynak/patch, iki build tree, .a/.o/install girdileri, binary'ler, log ve toolchain bilgileri tar olarak; source crate cache'i ayrı hash-kontrollü tar olarak korunur. Başarısızlıkta ulaşılmış aşama/log/partial çıktılar tutulur. Bu geçici saklama, gelecekteki binary dağıtımında uzun süreli corresponding-source sağlama yükümlülüğü değildir; kalıcı mirror/offer/relink paketi hâlâ eksik.

S05-D: generated post-update Cargo.lock ve exact feature/role/link subset'ini tamamlamak; tüm static LGPL object/source girdileriyle orijinal profile uygun yeniden derleme, tam Sigstore ve uzun süreli source sunumu. Node/Debian, Prisma ve diğer genel dağıtım kapıları açık kalır. İnsan kurulumu yapılmadı. Merge/tag/release/npm/registry/deploy yoktur.
