# libvips değiştirme ve yeniden bağlama sınırı

S05-B deneyinin kodu `docker/libvips-evidence.mjs`; mevcut selfhost runtime ve migrate imajlarında, ağsız, non-root, read-only ve yalnız geçici `/tmp` tmpfs ile çalışır. İmaj katmanları değişmez.

Sharp addon libvips-cpp shared object'ini dinamik kullanır. Ancak pinned upstream `build/posix.sh`, libvips C çekirdeğini ve birçok alt bağımlılığı libvips-cpp içine statik bağlar; `--exclude-libs`, version-script ve `-Bsymbolic-functions` uygular. Bu nedenle bir shared object'in yüklenebilmesi, statik LGPL alt parçalarının yeniden bağlanabildiğinin kanıtı değildir.

Prova: glibc libvips-cpp dosyasını farklı geçici dizine kopyala, SHA-256 eşitliğini kaydet; ayrı Node sürecinde LD_LIBRARY_PATH ile 2×2 sentetik görseli 1×1 PNG'ye dönüştür; `/proc/self/maps` içinde alternatif dosyanın gerçekten yüklendiğini denetle. Başarılıysa yalnız aynı byte'ların alternatif yerden yüklenmesi doğrulanmıştır. Bu bir değiştirilmiş kütüphane derlemesi değildir; RELINKING EVIDENCE en fazla PARTIAL olabilir. Başarısız çıktı VERIFIED sayılmaz.

Tam kanıt için: ilgili LGPL sürümü/dosya kapsamını belirle; aynı libvips SONAME/ABI'ı sağlayan değiştirilmiş kaynağı bütün statik LGPL alt bağımlılıklarıyla derle; gerekli object/archive/link girdilerini, header'ları, araç sürümlerini, yamaları ve kurulum tarifini sağla; değiştirilmiş sürümle gerçek Sharp addon ve sentetik görsel testini çalıştır. Orijinal kaynak kod, değişiklik bildirimleri, lisans/telif metinleri ve uygulanabilir kurulum bilgisi ayrıca dağıtım paketine bağlanmalıdır. Upstream tarifindeki floating nightly Rust, paket yöneticileri ve base tag'leri kesin toolchain provenance sağlamaz.

glibc ve musl binaryleri ayrı değerlendirilir. Debian imajındaki musl dosyasının bulunması, kullanılabilir olduğu anlamına gelmez. Musl binary silinmez veya glibc deneyinin başarısıyla doğrulanmış sayılmaz. Bit düzeyinde reproducible build, source/build provenance ve kullanıcının değiştirme mekanizması ayrı kararlardır.

İlk yeni CI deneyi LD_LIBRARY_PATH ile başarısız oldu (görsel üretildi, alternatif dosya yüklenmedi). İkinci probe LD_PRELOAD'ı ayrı kaydeder ve orijinal dosyanın mapped olmadığını denetler. ELF dinamik tag'leri gözlenmeden RPATH önceliği varsayım olarak kesinleştirilmez. Her iki yöntemin sonuçları artifact'ta ayrı bulunur; yalnız alternatifin mapped olması, orijinal de mapped ise yeterli değildir.

Probe container'ın scratch tmpfs'i yalnız bu izole deneyde `exec` seçeneğiyle açılır; indirilen yabancı kod çalıştırılmaz, imajın kendi kütüphanesi kopyalanır. Normal uygulama Compose tmpfs/read-only/capability seçenekleri değiştirilmez. Default noexec scratch'te LD_PRELOAD dosyayı map edemediği için mount koşulu ayrıca kaydedilir. S05-A yerel imajındaki tanılama yeni S05-B imaj kanıtı değildir; yeni kanıt yalnız yeni CI imajından alınır.

Yeni dc50c65 runtime ve migration CI imajlarında doğrulanan sonuç: DT_RPATH nedeniyle LD_LIBRARY_PATH alternatifini kullanmadı. Ayrı LD_PRELOAD deneyi executable scratch'te aynı-byte alternatif libvips-cpp'yi map etti; özgün dosya map edilmedi ve PNG üretildi. Karar PARTIAL; native/static LGPL alt parçalarıyla değiştirilmiş kaynağı yeniden derleme ve kullanıcıya gerekli girdileri sağlama hâlâ BLOCKED.

## S05-C kaynak ve rebuild kontrolü

[Doğrulama](S05C-REBUILD-VALIDATION.md) ve [tekrar tarifi](LIBVIPS-REBUILD-REPRODUCTION.md):357 dış Cargo.lock kaydından162'si upstream librsvg compile log'unda gözlendi;195 UNKNOWN,0 NOT SELECTED. Toolchain cargo-c build satırları ayrı tutulur. Yeni kaynak/ABI/load doğrulayıcı fiziksel dosya/hash ister; modified-source reduced-profile deneyi orijinal static bundle'a eşdeğer sayılmaz. Genel BINARY DISTRIBUTION: BLOCKED; Node/Debian/Prisma ve kalıcı source sunumu açık. Son HEAD deney sonucu ve iki mandatory CI PR kanıt kaydındadır; hazırlanmış/başarısız deney VERIFIED sayılamaz.
