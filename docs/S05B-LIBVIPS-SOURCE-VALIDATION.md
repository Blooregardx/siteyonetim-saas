# S05-B Sharp/libvips kaynak doğrulaması

DEVELOPMENT: INCOMPLETE — son HEAD push ve PR CI tamamlanmalı.
LIBVIPS SOURCE EVIDENCE: PARTIAL
RELINKING EVIDENCE: BLOCKED — yeni imaj deneyi sonucu bekleniyor.
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
