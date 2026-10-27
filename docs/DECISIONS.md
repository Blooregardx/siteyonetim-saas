# Kararlar

- Mevcut Next.js/Prisma ve management servisleri korundu. Yeni backend/kimlik sağlayıcısı bağımlılığı yerine PostgreSQL tabanlı opaque oturum ve Node scrypt kullanıldı.
- Server Actions ortak mutasyon katmanıdır; ek kimlik kabul eden Route Handler açılmadı.
- Seçili organizasyon URL parametresidir; sunucu her istekte üyelik denetler. URL yetki vermez.
- Mevcut ADMIN/MANAGER/RESIDENT rolleri geriye uyumlu tutuldu. Ayrıntılı sekiz rol ve davet modeli ayrı yetki tasarımı gerektirir.
- Eski organizasyonsuz siteler otomatik taşınmaz. Demo `/demo` altında ayrıldı.
- Ödeme yöntemi eklendi; kuruş, kilit ve idempotency korundu. Fazla ödeme/alacak modeli kapsam dışında.

## S01-C

- E-posta doğrulaması yalnız UI'da değil her servis transaction'ında kontrol edilir; mevcut kullanıcılar otomatik doğrulanmaz.
- E-posta değişimi önce yeni adrese kanıt gönderir, doğrulama sonrası atomik değişir ve oturumlar iptal olur; son aktif admin gereksiz yere doğrulanmamış duruma düşürülmez.
- Son aktif ADMIN ve yetki iptali yarışları organizasyon satır kilidiyle korunur. MANAGER yüksek rol davet edemez; rol değişimi yalnız ADMIN'dedir.
- Audit başarısızlığı kritik iş transaction'ını geri alır; audit operasyon kimliği ile entity kimliği ayrı tutulur. Snapshot kimlik referansları geçmişin silinmemesi için audit FK/cascade bağı değildir.
- Global giriş limiti kaldırıldı; edge koruma eksikliği açıkça belgelenir.
- Ters kayıt, net bakiye ve concurrency kuralını birlikte değiştireceği için ayrı finans güvenliği görevi olarak tasarlandı; mevcut Payment değişmez.

## S01-D

Özgün Payment korunur; tek tam ters kayıt ayrı PaymentReversal satırıdır. Tutar eşitliği uygulama kuralına ek olarak site/ödeme/tutar FK'siyle zorlanır. Satır kilitleri aynı borçtaki tahsilat ve ters kaydı sıraya koyar. Audit idempotent tekrarlarla çoğalmaz. Yeni ters kayıt anahtarı UUID'dir; eski collect anahtarları geriye uyumluluk için değiştirilmedi. Immutable trigger sebebiyle testler finans fixture'larını silmez. Prisma'nın bileşik bire bir ilişki gereksinimi ayrı eklemeli indeks migration'ıyla karşılandı.
