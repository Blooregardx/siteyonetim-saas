# Hazır imaj dağıtım kapıları

## S05-E güncel kapı — BINARY DISTRIBUTION READINESS: BLOCKED

[Full native kanıt](S05E-NATIVE-REBUILD-VALIDATION.md): gerçek CONTROL/MODIFIED
farklı byte/source hash'leriyle üretildi; 3500 export ve 558 versioned import
korundu. Gerçek Sharp 0.35.5 addon'u ile altı PNG/JPEG/SVG testi geçti; eski
library negatif denemesi reddedildi. Bunlar bit düzeyinde historical rebuild
veya eksiksiz type ABI kanıtı değildir. S05-D controlled lock kullanıldı.

Genel kapı açılmaz: mevcut runtime/migration imajları özgün npm bundle'ını
kullanır; yeni .so'lar o image/SBOM kimliklerine bağlanmış değildir. Node/Debian,
Prisma, per-file kaynak/notice kapsamı ve uzun dönem source sunumu açık kalır.
Kalan dokuz Rust kaydında yalnız iki exact r-efi AUTHORS edinimi PASS, yedi
kayıt BLOCKED. Static LGPL girdileri ve type ABI PARTIAL; hukuki onay yoktur.

[Kaynak protokolü](S05E-SOURCE-PROVISION-PROTOCOL.md) gerçek OCI config/layer,
binary ve SBOM bytes'ını bağlar. Engine inspect.Id, manifest-list ve config
karıştırılmaz. Source-index olmayan gerçek DEVELOPMENT relink candidate'ı
complete-source kapısından geçemez. İki runner kopyası/restore sentetiktir;
14 günlük aynı GitHub backend'i kalıcı iki sağlayıcı sayılmaz. Alpha.2 PUBLISHED
— UNCHANGED; INDEPENDENT INSTALLATION: PENDING HUMAN VALIDATION.

## S05-B kaynak/build incelemesi

[Kaynak doğrulaması](S05B-LIBVIPS-SOURCE-VALIDATION.md): 28 native kaynak girdisi ve 357 Rust transitif kayıt ayrı tutulur; binary provenance ve değiştirilmiş static-LGPL rebuild tamamlanmadı. LIBVIPS SOURCE EVIDENCE: PARTIAL; genel BINARY DISTRIBUTION READINESS: BLOCKED. S05-A tarihsel kanıtları değişmedi. Yeni imaj ELF/hash ve alternatif yükleme provası CI artifact'ındadır; dolu evidence metni native pakete PASS veremez. Node/Debian kaynak işleri ve bağımsız insan kurulumu açık kalır.

## S05-C kaynak ve rebuild kontrolü

357 dış Cargo kaydından 162 COMPILED, 195 UNKNOWN; kaynak edinimi 344 PASS/13 BLOCKED. Değiştirilmiş PNG/JPEG profili gerçek Sharp PNG yolunda başarılıdır; özgün bundle ABI ve statik girdiler eksiktir. Gate her durumda BLOCKED kalır; S05-C receipt hash'i yalnız izleme bağıdır, hukuki onay değildir. [Kanıt ve sınırlar](S05C-REBUILD-VALIDATION.md); [tekrar tarifi](LIBVIPS-REBUILD-REPRODUCTION.md).

## S05-D denetimi

Generated lock iki kontrollü çözümlemede aynı hash'i verdi; tarihsel upstream lock olarak onaylanmadı. Metadata, compiler-artifact ve LINKED kararları ayrıdır. 13 eski notice kaydında 4 PASS/9 BLOCKED yalnız kaynak/bildirim edinimidir. Native kayıtlardaki s05dFullBundleManifestSha256 salt kanıt izidir; genel dağıtımı açmaz. [Gerçek sonuç ve sınırlar](S05D-FULL-BUNDLE-VALIDATION.md); [kalıcı kaynak planı](CORRESPONDING-SOURCE-DISTRIBUTION-PLAN.md).
