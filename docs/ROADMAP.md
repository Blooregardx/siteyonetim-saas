# Yol haritası

Hedef ücretsiz, özgür/açık kaynak ve topluluk katkılarına açık, kendi sunucusunda barındırılabilir site/apartman yönetimidir. Depo PUBLIC kalır. Ticari abonelik veya ücretli lisans geliştirilmez. Next.js, TypeScript, PostgreSQL ve Prisma 6 korunur. Lisans henüz seçilmedi.

1. **OSS-01 — hazırlık (bu PR):** tutarlı belgeler, katkı/topluluk süreci, güvenli CI, lisans değerlendirmesi ve bakım kanıtları. PR açılması lisans/ayar işlerinin tamamlandığı anlamına gelmez.
2. **Başvuru öncesi:** bakımcı lisans kararını verir; özel güvenlik bildirimi ve main korumaları etkinleştirilir. Geliştirme dalının main'e geçişi ayrı incelemeyle yapılır; geçmiş yeniden yazılmaz.
3. **Kendi sunucusunda kurulum:** temiz kurulum ve mevcut şemadan yükseltme provası, minimum runtime/migration/bakım izinleri, HTTPS/SMTP, güvenli güncelleme ve yedekten dönüş belgelerinin izole doğrulaması. Ücretli servis şartı yoktur.
4. **Güvenlik ve bakım:** kötüye kullanım koruması, güvenilir proxy sınırları, sayfalama/kapasite, saklama ve olay müdahalesi; mevcut finans ve audit kuralları korunur.
5. **Topluluk sürümü:** bilinen eksiklerle etiketli geliştirme sürümü, sürüm notları, issue sınıflandırma ve PR inceleme kanıtları. Kullanım/adopsiyon verileri uydurulmaz.
6. **Sonraki işlevler:** ayrı tasarım ve testlerle toplu aidat önizlemesi/idempotent oluşturma; daha sonra raporlama, kişi eşleme ve ortaklık payı. Banka/kart, mesajlaşma ve mobil istemci taahhüt edilmiş teslimler değildir.

S00–S01 ve S02-A ile uygulanmış kapsam [FEATURES](FEATURES.md) içindedir. E-posta doğrulama, davet/rol, audit ve tam ters kayıt artık bekleyen özellik olarak listelenmez. Kısmi ters kayıt ve gerçek para iadesi uygulanmadı. STAGING/PRODUCTION için [operasyon listesi](DEFERRED-CLOUD-OPERATIONS.md) geçerlidir; canlı dağıtım bu görevin parçası değildir.
