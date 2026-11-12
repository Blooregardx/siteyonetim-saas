# S05-E — Yayın öncesi karşılık gelen kaynak doğrulama protokolü

Bu protokol DEVELOPMENT içindir; gerçek source bundle/binary/release yayımlamaz.
S05-D [tasarımının](CORRESPONDING-SOURCE-DISTRIBUTION-PLAN.md) süre/yöntem ve
hukuki inceleme gereklilikleri devam eder. DURABLE SOURCE PROVISION: PARTIAL.
BINARY DISTRIBUTION READINESS: BLOCKED.

1. Bakımcı, gelecekteki runtime ve migration imajları için ayrı immutable OCI
   manifest/config digest'ini ve gözden geçirilmiş source-index SHA-256'sını
   güvenilir, bağımsız bir yayın kaydına bağlar. Paketin içindeki hash listesi
   kendi başına kimlik doğrulama değildir. Mevcut Alpha.2 değiştirilmez.
2. Offline `s05e_source_protocol.py verify ROOT INDEX_SHA` önce fiziksel
   source-index dosyasını doğrular; OCI index/manifest/config/layer bytes'ını
   hash ve descriptor size ile kontrol eder. Linux amd64 ve rootfs diff_ids
   eşleşmelidir. Layer'lar sırayla taranır; whiteout/opaque silme uygulanır.
   Binary doğru regular path'te bulunmalı ve ELF/hash eşleşmelidir.
3. Gerçek filesystem Syft SBOM'u imageID ile eşleşmelidir. package-lock veya
   directory taraması gerçek imaj SBOM'u olarak kabul edilmez. PREPUBLICATION_CANDIDATE
   için boş artifact listesi reddedilir; sentetik boş fixture etiketi değiştirilerek
   gerçek paket gibi geçirilemez. Mevcut okuyucu
   yalnız uncompressed OCI layer kabul eder; compressed/alias path veya
   desteklenmeyen durum fail-closed reddedilir, tahminle geçmez.
4. Source, patch, özgün notice, build script, toolchain source, exact Cargo.lock,
   compile log, linker map, static archive, object ve relinking talimatı
   ayrı fiziksel/hash'li roller taşır. Kaynak arşivlerinde traversal, link,
   duplicate, special file ve limit aşımı reddedilir. Bu source-package
   protokolündeki katı regular-file politikası, native kaynak açma aracının
   gözden geçirilmiş internal-link desteğinden farklıdır; gerçek bundle için
   uyumlu, içerik kaybetmeyen paketleme ayrıca doğrulanmalıdır.
5. Dosya şekli veya hash eşleşmesi, compile/link provenance veya notice'ın
   uygulanabilirliğinin tek başına kanıtı değildir. `protocolIntegrity: PASS`
   yalnız bütünlüktür; `legalApproval: false` ve genel BLOCKED daima korunur.
   Gerçek paket için tüm bileşen/license/source/kurulum kapsamını bakımcı ve
   yetkin hukuki inceleme dosya düzeyinde değerlendirir.
6. Sabit bundle/index hash'i ile iki ayrı kopya oluşturulur. Her biri diğer
   kopya/seed/cache/network fallback olmadan, boş yeni bir ortamda restore
   edilir. Restore sırasında dosya üye/hash'leri yeniden doğrulanır; bozulma,
   kayıp kopya veya yanlış imaj açık hata üretir. Hash değişikliğini onaylamak
   yerine asıl güvenilir kopyadan düzeltme ve tekrar kontrol gerekir.

## Gerçekte uygulanan sentetik prova

CI `s05e-source-seed` küçük, açıkça SYNTHETIC_PROTOCOL_TEST işaretli bir OCI ve
source inventory oluşturur. `s05e-source-copy (a/b)` ayrı GitHub runner
filesystem'lerinde doğrular ve ayrı artifact olarak korur. `s05e-source-restore
(a/b)` iki yeni runner'da yalnız kendi kopyasını indirir; restore ve kayıp/bozuk
kopya negatifleri çalışır. Summary farklı runner boot fingerprint'lerini ve
aynı harici bundle/index hash'ini denetler. Sentetik ELF/static archive bytes'ı
gerçek libvips, kaynak paketi veya ABI sonucu değildir.

Bu, farklı runner filesystem'lerinde iki kopya/restore testidir. Aynı GitHub
hesabı/artifact backend'i iki bağımsız saklama sağlayıcısı veya failure domain
değildir. 14 günlük artifact süresi açıkça geliştirme kanıtıdır. Gerçek bundle
üzerinde iki bağımsız kalıcı kopya, source sunum süresi/yöntemi, kapasite,
erişim sorumlusu ve düzenli restore henüz kanıtlanmadı. GitHub'a kalıcı saklama
garantisi atfedilmez. Süreyi otomatik araç belirlemez; uygulanabilir LGPL/MPL/
AGPL ve diğer lisanslar ile seçilen sunum yöntemi bakımcı incelemesinde kalır.

## Gerçek binary yayımlanmadan önce kalan kapılar

Tam native/Rust build ve relinking girdileri, kaynak kapsamının tamamlığı,
özgün bildirimler, image digest/SBOM eşleşmesi, source offer/erişim bilgileri,
değiştirme/kurulum hakları, hukuki inceleme ve uzun dönem kopya/erişim provasını
tamamlayın. Eksik shard, HTTP erişim kaybı, hash farkı ve yaklaşan saklama
sonlarını izleyen bounded kontrol planı işletilmelidir; bu çalışmada gerçek
yayın veya periyodik dış servis etkinleştirilmez. Node/Debian/Prisma ve yedi
Rust notice engeli bu protokolle kapanmaz. İnsan kurulum testi de yapılmış sayılmaz.
