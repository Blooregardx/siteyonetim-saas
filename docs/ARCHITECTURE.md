# Mimari ve geliştirme sırası

## Mevcut model

`Site` veri ayrımının köküdür. `Membership` kullanıcıyı bir siteye ADMIN, MANAGER veya RESIDENT rolüyle bağlar. Aynı kullanıcı birden fazla siteye üye olabilir. Blok, daire, aidat ve ödeme ilişkileri bileşik `siteId` anahtarları kullanır; başka sitedeki bir kayda bağlanmak veritabanında engellenir. Bu kısıtlar okuma yetkisi veya RLS sağlamaz.

Aidat tutarı ve ödemeler tam sayı kuruş olarak saklanır. Bakiye, aidattan ödemelerin toplamı çıkarılarak hesaplanmalıdır; ikinci bir bakiye alanı tutulmaz. `period` için servis katmanında YYYY-MM doğrulaması gerekir. Her daire/dönem için tek aidat vardır. Ek tahakkuklar için bu model genişletilmelidir. Ödemede siteye özgü idempotency anahtarı mükerrer kayıtları engeller. Finansal kayıtlarda kademeli silme yoktur.

Migration, pozitif aidat ve ödeme tutarlarını CHECK kısıtlarıyla korur. Toplam ödemenin borcu aşmaması servis katmanında transaction ve satır kilidiyle uygulanmalıdır. Mevcut saf hesap fonksiyonu yalnızca girdi bakiyesini doğrular; henüz bir ödeme yazma servisi yoktur.

## Sonraki geliştirme adımları

1. Kimlik doğrulama sağlayıcısı, davet ve oturum yönetimi; tüm sorgularda sunucu tarafında üyelik/rol kontrolü. İstemciden gelen site kimliğine güvenilmemeli.
2. Yönetici için site/blok/daire CRUD; sakin-daire eşlemesi ve kullanıcıya özel görünüm. Mevcut model sakinlerin hangi daireyi görebileceğini henüz tanımlamaz.
3. Yetkili aidat oluşturma ve ödeme kayıt servisi; transaction, fazla ödeme ve tekrar istek kontrolleri, denetim kaydı.
4. Gerçek PostgreSQL ile site ayrımı, yetkisiz erişim, eşzamanlı ödeme ve idempotency entegrasyon testleri.
5. Giderler, belgeler, duyuru CRUD, raporlar ve bildirimler.
6. Yedekleme/geri yükleme denemesi, izleme, KVKK saklama ve silme politikası. Abonelik ve ödeme sağlayıcısı daha sonra seçilmeli.

Üretime geçmeden önce kullanıcıya açık tüm okuma/yazma yolları yetkilendirilmeli; gizli bilgiler platformun secret yönetiminde tutulmalıdır. Veritabanı doğrudan tarayıcıya açılmamalıdır.

## Bağımlılık notu

Prisma 6'nın transitif `deepmerge-ts` bağımlılığı, GHSA-ggr8-5vv4-36mx nedeniyle npm `overrides` ile 8.x sürümüne yükseltilmiştir. Şema doğrulama, istemci üretimi ve PostgreSQL migration uygulaması bu sürümle doğrulanmıştır. Prisma güncellenirken override gereksinimi yeniden değerlendirilmelidir.
