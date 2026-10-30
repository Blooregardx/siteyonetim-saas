# Mimari ve geliştirme sırası

## Mevcut model

`Site` veri ayrımının köküdür. `Membership` kullanıcıyı bir siteye ADMIN, MANAGER veya RESIDENT rolüyle bağlar. Aynı kullanıcı birden fazla siteye üye olabilir. Blok, daire, aidat ve ödeme ilişkileri bileşik `siteId` anahtarları kullanır; başka sitedeki bir kayda bağlanmak veritabanında engellenir. Bu kısıtlar okuma yetkisi veya RLS sağlamaz.

Aidat tutarı ve ödemeler tam sayı kuruş olarak saklanır. Bakiye, aidattan ödemelerin toplamı çıkarılarak hesaplanmalıdır; ikinci bir bakiye alanı tutulmaz. `period` için servis katmanında YYYY-MM doğrulaması gerekir. Her daire/dönem için tek aidat vardır. Ek tahakkuklar için bu model genişletilmelidir. Ödemede siteye özgü idempotency anahtarı mükerrer kayıtları engeller. Finansal kayıtlarda kademeli silme yoktur.

Migration, pozitif aidat ve ödeme tutarlarını CHECK kısıtlarıyla korur. Toplam ödemenin borcu aşmaması servis katmanında transaction ve satır kilidiyle uygulanmalıdır. Mevcut saf hesap fonksiyonu yalnızca girdi bakiyesini doğrular; `src/lib/management.ts` artık transaction ve satır kilidiyle tahsilat yazar.

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


## S00–S01 uygulanan temel

`Organization` bireysel yönetici veya şirket türündedir. Organizasyon ADMIN/MANAGER üyeleri bağlı siteleri yönetebilir; mevcut site bazlı ADMIN/MANAGER üyelikleri de korunur. RESIDENT yönetim servisine erişemez. Tüm mevcut servis metotları sunucunun doğruladığı oturum callback'ini kullanır. Bu callback bir kimlik doğrulama sağlayıcısı değildir; güvenilir oturum entegrasyonu yapılmadan HTTP isteklerindeki kullanıcı kimliğiyle doldurulmamalıdır.

Eski siteleri bozmamak için `organizationId` nullable bırakılmıştır. Mevcut verinin organizasyonlara atanması ayrı bir geçiş işidir. Yeni `createSite` servisi organizasyon üyeliği ister. `Occupancy` malik ve kiracı bilgilerini daireye site kapsamındaki bileşik yabancı anahtarla bağlar; bu kişiler otomatik olarak kullanıcı hesabı veya erişim hakkı kazanmaz.

Tahsilat servisi borcu `FOR UPDATE` ile kilitler, bakiyeyi transaction içinde hesaplar, fazla ödemeyi reddeder ve aynı idempotency anahtarının farklı içerikle tekrarını engeller. Doğrudan SQL yazımları bu servis korumasını aşabilir; uygulama veritabanı erişimi yalnızca sunucuda tutulmalıdır. Finansal düzeltme/ters kayıt ve denetim izi henüz yoktur. Her daire/dönem tek tahakkuk sınırı sürer.

Önceki geliştirme sırasındaki organizasyon, kayıt ve tahsilat servisleri kısmen tamamlandı. Sonraki adım gerçek oturum doğrulayıcısı, CSRF korumalı form/HTTP entegrasyonu ve tarayıcı uçtan uca testleridir. Demo panel bu servise bağlı değildir.

## Güncel oturum ve arayüz entegrasyonu

Önceki bölümde ertelenmiş olan gerçek oturum ve Server Actions katmanı artık uygulanmıştır. `session.ts` PostgreSQL Session tablosundaki token özetini ve süreyi doğrular; `management(db, verifySession)` gerçek kullanıcıyı kullanır. `panel/actions.ts` Zod doğrulamalı tüm yazımları aynı yetkili servise yönlendirir. `/panel` organizasyon üyeliğiyle gerçek sayaç, liste ve bakiye üretir. `/demo` bağımsız örnek paneldir. Geçiş ve kişi tasarımı DATABASE.md içinde, güncel sınırlar SECURITY.md ve FEATURES.md içindedir.

## S01-C güvenlik sınırı

`accounts.ts` e-posta doğrulama ve davet/üyelik servisidir. `security.ts` doğrulanmış actor, organizasyon kilidi ve audit yardımcılarını içerir. `management.ts` bütün veri erişimlerinde güncel doğrulama/üyelik kontrolünü uygular. Yetki kaybı açık oturumdan bağımsız olarak sonraki işlemde geçerlidir. Kullanıcı satırı kilidi adres değişimini, organizasyon satırı kilidi yetki değişimini işlemlerle sıraya koyar; tahsilatta buna Charge FOR UPDATE kilidi eklenir. `mail.ts` gerçek ortamda HTTPS ve TLS'yi zorunlu kılar. `cleanup.ts` sabit güvenlik tablolarında sınırlı süre-aşımı temizliği sunar; audit ve finans geçmişine dokunmaz.

## S01-D finans merkezi

PaymentReversal, immutable ödeme geçmişine bağlı ayrı tam ters kayıttır. `finance.ts` içindeki paymentTotals/chargeBalance/financialSummary canlı finans hesaplarının ortak kaynağıdır. collect ve reversePayment organizasyon→Charge kilidini paylaşır; reversePayment ayrıca Payment kilidi alır. ADMIN doğrulaması ve audit yazımı reversal ile tek transaction'dadır. Dashboard, aidat, daire borcu ve yeni ödeme sınırı brütten reversal çıkarılarak hesaplanır. Ayrıntılı model, yarış davranışı ve test haritası PAYMENT-REVERSALS.md içindedir.

## S02-A ve durum ayrımı

DEVELOPMENT, STAGING ve PRODUCTION bağımsızdır; ertelenen servisler DEFERRED-CLOUD-OPERATIONS.md içinde takip edilir. Yeni `/kayitlar` ekranı mevcut session/management/action katmanını kullanır. Person organizasyon kapsamlı kimlik, Ownership tarihli mülkiyet, Occupancy tarihli kiracılık, User ise yetkili hesaptır. Eski Occupancy satırları korunur; yeni OWNER kayıtları Ownership'e yazılır. Güncellemeler ve dönem kapatmalar mevcut organizasyon kilidi/audit transaction düzenini korur. Kullanım durumu elle yönetilen ayrı operasyonel etikettir.
