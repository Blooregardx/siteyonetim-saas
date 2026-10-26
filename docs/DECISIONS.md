# Kararlar

- Mevcut Next.js/Prisma ve management servisleri korundu. Yeni backend/kimlik sağlayıcısı bağımlılığı yerine PostgreSQL tabanlı opaque oturum ve Node scrypt kullanıldı.
- Server Actions ortak mutasyon katmanıdır; ek kimlik kabul eden Route Handler açılmadı.
- Seçili organizasyon URL parametresidir; sunucu her istekte üyelik denetler. URL yetki vermez.
- Mevcut ADMIN/MANAGER/RESIDENT rolleri geriye uyumlu tutuldu. Ayrıntılı sekiz rol ve davet modeli ayrı yetki tasarımı gerektirir.
- Eski organizasyonsuz siteler otomatik taşınmaz. Demo `/demo` altında ayrıldı.
- Ödeme yöntemi eklendi; kuruş, kilit ve idempotency korundu. Fazla ödeme/alacak modeli kapsam dışında.
