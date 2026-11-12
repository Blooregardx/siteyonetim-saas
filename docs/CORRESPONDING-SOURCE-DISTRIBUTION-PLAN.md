# Karşılık gelen kaynak sunumu — DEVELOPMENT tasarımı

DURABLE SOURCE PROVISION: DESIGN READY yalnız offline tasarım testleri ve bakımcı incelemesi bağlamında değerlendirilir. Henüz gerçek kaynak paketi veya binary yayımlanmadı; kalıcı erişim ve hukuki uyum sağlandı kararı verilmez. BINARY DISTRIBUTION READINESS: BLOCKED.

## Dağıtım birimi ve kanıt zinciri

Her gelecekteki Linux x86-64 runtime ve migration imajı için ayrı, immutable OCI manifest digest + config digest kaydı gerekir. Registry tag'i kimlik değildir. Export edilmiş aynı imajın config hash'ine bağlanan gerçek filesystem SBOM'u (CycloneDX/SPDX ve ham araç çıktısı), target, native binary yol/hash'leri, release source commit'i ve bütün kaynak bundle hash'leri aynı indeks içinde olmalıdır. SOURCE-ONLY Alpha.2 bu tasarımla yeniden yayımlanmaz/değiştirilmez.

İndeks zorunlu girdileri: schemaVersion, platform/feature profili, imageManifestDigest, imageConfigDigest, SBOM path/SHA-256, uygulama ve üçüncü taraf source URL/commit/archive SHA-256, Cargo.lock önce/sonra hash ve dosya, Cargo metadata/derleme/link kanıtları, kaynak değişiklikleri ve patch hash'leri, özgün LICENSE/COPYING/NOTICE ve telif metinleri, build script'leri ve komut sırası, toolchain binary/source sürümleri ve bütünlük kayıtları, static archive/object üyeleri/hash'leri ve relinking/kurulum talimatları.

Kaynaklar yalnız bağımlılık sürüm listesi olamaz: kullanılan kaynakların tamamını, derlemeyi/kurulumu kontrol eden script'leri, uygulanmış değişiklikleri ve ilgili lisansın istediği yeniden bağlama girdilerini kapsamalıdır. Registry crate checksum'u, gerçekten edinilmiş arşiv hash'inden ayrı kaydedilir. Source package, binary ile ilişkisi kurulmamış URL listesiyle tamamlanmış sayılmaz. LGPL girdileri için yalnız yeni S05-C reduced-profile libvips.a yeterli değildir.

## Paket hazırlama ve doğrulama

1. Yayın adayı imajı mevcut güvenli build akışında yalnız yerel/izole üretin; otomatik registry push yoktur.
2. Bütün kaynakları exact commit/version ve doğrulanmış hash ile edinip güvenli arşiv incelemesi yapın. Path traversal, symlink/hardlink, özel dosya ve aşırı boyut reddedilir.
3. Binary ile aynı kaynak/build/feature/toolchain kayıtlarını eşleyin. Full native/Rust compile-link kapsamındaki UNKNOWN kayıtlar ve eksik kaynak/bildirimler manuel incelemeye gider.
4. Özgün telif/lisans metinlerini ve kullanılmış lisans seçimini dosya/bileşen düzeyinde koruyun. Üst npm paketinin lisansı alt bileşenlere uygulanmaz.
5. CONTROL/MODIFIED deneyleri, .a/.o girdileri, linker komutları ve Sharp yükleme/proc maps kanıtlarını ekleyin. Eşit symbol adı tek başına ABI veya hukuki uyum ispatı değildir.
6. Manifestteki her dosyanın SHA-256 değerini ve arşiv güvenliğini offline yeniden okuyun. Bilinmeyen/boş alan veya eksik object dosyası VERIFIED olmaz.
7. Ayrı boş ortamda operatörün elde edeceği dosyalarla kaynak edinimi, build, relinking ve kurulum provasını yapın. CI artifact yolu, operatöre erişilebilir kaynak adresi yerine geçmez.
8. Operatörün değiştirilmiş uyumlu kütüphaneyi kullanma talimatını, dağıtım lisanslarındaki değiştirme/tersine mühendislik haklarını ve uygulanıyorsa Installation Information gereksinimini belgeleyin. Bunlar manuel hukuki inceleme gerektirir.

scripts/verify_s05d_evidence.py içindeki offline source-package protokolü yalnız fiziksel inventory/hash ve yanlış imaj/SBOM eşleşmesini test eder. Küçük sentetik testler gerçek source/relink paketinin tamamlandığını veya hukuki PASS'ı göstermez.

## Süre ve sağlama yöntemi

Tek ve evrensel bir saklama süresi atanmaz. Uygulama AGPL-3.0-only koşulları, LGPL-2.x/3.x seçimi, MPL-2.0 ve diğer gerçek bileşen koşulları birlikte incelenir. LGPL 2.1 §6, LGPL 3'ün GPL 3'e bağlanan koşulları ve seçilen GPL 3 §6 yöntemi için source/relinking/object ve varsa kurulum bilgisi gereksinimleri ayrı matrise yazılır. Bazı yazılı teklif yollarındaki en az üç yıl şartı, bütün lisanslar için evrensel süre değildir; GPL 3 §6(b) destek/yedek parça süresine ilişkin ek koşullar da içerir. MPL 2.0 §3.1/3.2 için Source Code Form erişimi, alıcıya nasıl edinileceğinin bildirilmesi ve bildirimlerin korunması ayrıca değerlendirilir. MIT/BSD/Apache telif/NOTICE yükümlülükleri kaynağın URL'si verilerek ortadan kalkmaz.

Öneri, bakımcı/hukuk incelemesinin uygun gördüğü doğrudan eşleşen kaynak sunumu yöntemini binary edinimiyle birlikte seçmek; yazılı teklif yöntemini kendiliğinden seçmemektir. Matris yöntemi, gerekçeyi, süre başlangıcını/bitişini, sorumluyu, maliyet koşulunu ve kullanıcıya verilen bildirimi içermelidir. Otomatik araç hukuki süre/yöntem onayı vermez.

## Ücretsiz mevcut GitHub seçenekleri ve sınırları

- Git deposu: küçük manifest, patch, notice ve build script'leri için uygundur. Büyük arşivleri otomatik commit etmeyin. Deponun silinmesi, hesabın kaybı ve history değişikliği mümkündür.
- Gelecekte ayrı bakımcı onayıyla GitHub Release asset'ları: immutable hash indeksli kaynak shard'ları ve tek indirme sayfası sağlayabilir; bu çalışma release/asset oluşturmaz. Asset boyutu/kota, silinme ve hizmet erişimi riskleri sürer; GitHub kalıcı saklama garantisi vermez.
- Actions artifacts: geliştirme kanıtı/cache içindir. 14 günlük artifact hiçbir uzun süreli source offer'ın yerine geçmez.
- GitHub Pages veya dosya indeksi yalnız navigasyon olabilir; orijinal kaynakların tek kopyası/kalıcı erişim garantisi sayılmaz.

Gelecekte binary yayımlamadan önce lisans süresine uygun kapasite ve erişim sorumluluğu doğrulanmalı; en az iki bağımsız doğrulanmış kopya, düzenli hash/restore kontrolü ve kaybolan sunumu yeniden sağlama prosedürü kurulmalıdır. Ücretsiz GitHub altyapısının bu gereksinimi tek başına garanti edemediği açıkça belirtilir. Ücretli servis eklenmez; uygun saklama imkânı yoksa binary dağıtımı BLOCKED kalır.

## Erişim kaybını algılama ve yayın kapısı

Tasarım: periyodik GitHub Actions işi kaynak indeksini immutable commit'ten okuyacak; güvenilir izinli hostlardan bounded indirme yapacak, hash'leri ve manifest/SBOM/binary eşleşmesini yeniden kontrol edecek; 404/410, erişim reddi, boyut/hash bozulması, eksik shard ve yaklaşan kaynak-sunumu sürelerini açık hata olarak kaydedecektir. Cache hit'leri hash kontrolünü atlayamaz. İş başarısızlığı bakımcı tarafından izlenir; SMTP veya üçüncü kişilere otomatik ileti gönderilmez. Bu görevde böyle bir yayın/monitor işi devreye alınmaz.

Yayın öncesi iki ayrı manuel karar gereklidir: teknik bakımcı source/binary/relinking bütünlüğünü; yetkin hukuki inceleme uygulanabilir lisans, notice, source sunumu ve kullanıcı değiştirme haklarını değerlendirir. Dolu JSON alanı, yeşil CI veya platformun URL sağlaması bunların yerine geçmez. Node/Debian, Prisma ve diğer genel kapılar kapanmadan BINARY DISTRIBUTION READINESS: BLOCKED kalır.
