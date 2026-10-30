# Veritabanı ve geçiş

Main üzerinde toplam **yedi migration** vardır: ilk şema ve altı eklemeli geçiş. `202610280001_sessions` User.passwordHash (nullable), Session, PasswordReset, AuthAttempt ve Payment.method ekler; son `202610310001_property_people` kişi/daire modelini genişletir. Eski kullanıcılarda parola otomatik üretilmez; doğrulanmış posta kurtarma kanalı veya kontrollü hesap sahipliği doğrulaması gerekir. Geçerli parola olmadan eski hesabın girişine izin verilmez. Nakit/havale yöntemi saklanır; eski ödemeler CASH varsayımı taşır, bu geçmiş verinin gerçek ödeme yönteminin kanıtı değildir.

Session ve PasswordReset ham token yerine SHA-256 özetini saklar. Session 7 gün, reset 30 dakika geçerlidir. Süresi dolmuş oturumlar doğrulanmaz. Eski token/limit satırları için periyodik temizlik operasyonu kurulmalıdır.

## Eski Site.organizationId geçişi

Alan nullable korunmuştur; yetim kayıtlar silinmez veya tahmine dayalı şirkete atanmaz. Yeni siteler üyeliği doğrulanmış organizasyonda açılır. Geçiş için önce yedek alınmalı, site ADMIN üyeliği ve yönetim sözleşmesi doğrulanmalı, site→organizasyon eşlemesi onaylı operatör listesiyle hazırlanmalıdır. Transaction içinde yalnızca organizationId NULL olan beklenen satırlar güncellenmeli; satır sayısı denetlenmeli, üyelikler ve borç/ödeme kimlikleri korunmalıdır. Tüm siteler doğrulanmadan NOT NULL uygulanmamalıdır. Eski doğrudan üyelik servis düzeyinde korunur; yeni organizasyon panelinde otomatik gösterilmez.

## Tarihsel kişi tasarımı — S01 (güncel uygulama S02-A bölümünde)

Mevcut Occupancy isim kopyası ve OWNER/TENANT ilişkisi taşır; otomatik kullanıcı hesabı veya erişim hakkı oluşturmaz. Gelecek eklemeli model: organizasyon kapsamlı Person, isteğe bağlı doğrulanmış User bağı, tarihli Ownership ve Occupancy.personId. Bir Person birden çok daireyle ilişkilenebilir. İsim eşitliği kişi birleştirmek için yeterli değildir. Önce nullable personId eklenmeli; operatör doğrulamalı eşleme ve tarih kontrolleri sonrası eski isim alanı kaldırılması ayrı migration olmalıdır. Mülkiyet ve fiili ikamet dönemleri ayrı tutulmalıdır. Bu aşamada kişi birleştirme veya veri kaybettiren dönüşüm uygulanmadı.

## S01-C eklemeli migration

`202610290001_security_audit`: User.emailVerifiedAt nullable (eski kullanıcılar doğrulanmaz), EmailVerification, organizasyon/rol kapsamlı Invitation ve append-only AuditLog ekler. Mevcut finans tabloları veya satırları değiştirilmez. Tokenlar yalnız özetle saklanır. AuditLog üzerindeki UPDATE/DELETE/TRUNCATE trigger'ı DDL yetkisi olmayan uygulama rollerinin geçmişi değiştirmesini engeller; actor/tenant/site/entity alanları geçmiş kimlik referansları olarak kalır. Migration sahibi ve uygulama rolü ayrımı SECURITY-S01C.md içindedir. Migration geri almak için tabloları veya audit geçmişini düşürmek yerine ileri düzeltme hazırlanmalıdır.

## S01-D tam ters kayıt

`202610300001_payment_reversals`: ReversalReason enum, Payment üzerindeki bileşik unique indeksler, PaymentReversal ve immutable Payment/Reversal trigger'ları. `202610300002_reversal_relation_key`: Prisma'nın bire bir bileşik ilişki doğrulaması için reversal tarafında bileşik unique indeks. İlk migration'ın uygulanmış SQL'i değiştirilmeden ikinci eklemeli migration kullanıldı. Eski finans verileri korunur; ters kayıt geriye dönük üretilmez.

Tutar eşitliği ve site kapsamı üç alanlı FK, tek ters kayıt paymentId unique, tekrar anahtarı site/key unique, gerekçe enum ve pozitif tutar/UUID CHECK ile korunur. Finans fixture'ları test bitiminde artık silinmez; yalnız izole test DB'de kalır. Tüm test DB'sinin yeniden oluşturulması ancak açıkça izole geliştirme/test işletimiyle yapılabilir; üretimde reset yoktur.

## S02-A — eklemeli kişi ve apartman modeli

`202610310001_property_people`: Site/Block açıklama, Unit.floor (nullable), sectionType=RESIDENTIAL ve usageStatus=UNKNOWN alanları; Person ve Ownership tabloları; Occupancy.organizationId/personId nullable ilişkileri. Eski Occupancy satırları ve name/kind alanları aynen korunur; otomatik backfill veya adla kişi birleştirmesi yoktur. Yeni hızlı kişi kaydı her zaman ayrı Person oluşturur; var olan kişiyi yeniden kullanmak için kayıt yönetiminde açık personId seçilir.

Person organizasyon kapsamındadır, User hesabı veya erişim yetkisi değildir. Bir kişi farklı dairelere, bir daire farklı maliklere bağlanabilir. Yeni malik ilişkileri Ownership, kiracı dönemleri Occupancy'dir. Legacy OWNER Occupancy satırları yalnız eski kayıt olarak gösterilir. Yeni ilişkilerde kişi→organizasyon, site→organizasyon ve daire→site bileşik FK'leri yanlış tenant ilişkilendirmesini engeller. Eski organizasyonsuz sitelerde yeni Person işlemi için kontrollü organizasyon eşlemesi gerekir.

Tarih aralıkları gün bazında ve uçları dahil yorumlanır; aynı kişi/daire/tür için çakışan açık/yeni dönem servis transaction'ında reddedilir. Yeni giriş önceki çıkıştan sonraki gün veya daha sonra başlar. Birden fazla farklı kiracı ortak kullanım için mümkündür. Kapanmış dönem sonradan değiştirilmez; yeni dönem ayrı satırdır. Başlangıçtan önce çıkış DB/servis tarafından reddedilir. Eski tutarsız tarih verisini migration sırasında bozmamak için Occupancy tarih CHECK'i NOT VALID eklenir: mevcut satırlar taranıp değiştirilmez, yeni INSERT/UPDATE denetlenir. Eski verinin denetlenmesi ayrı kontrollü iştir.

Kat -20..200 veya boş olabilir. Tür/durum alanları genişletilebilir string kodlarıdır; UI/servis güncel izinli kodları doğrular. Kullanım durumu operasyonel etikettir, kiracı veya mülkiyet kaydından otomatik türetilmez. Daire düzenlemesi blockId/siteId ilişkisini değiştirmez; mevcut daire numarası unique kısıtı korunur. Ortaklık payı/yüzdesi bu sürümde tutulmaz; çoklu Ownership modeli ileride pay bilgisiyle genişletilebilir.

Organizasyon genelindeki Person rehberi ve mevcut kişiyi bağlama işlemi organizasyon ADMIN/MANAGER üyeliği gerektirir. Yalnız doğrudan apartman yetkisi olan kullanıcıya organizasyonun tüm kişi listesi açılmaz; kendi apartman ilişki geçmişi ve yetkili apartman düzenlemeleri korunur. Kişi seçeneklerinde isim yanında sabit kısa referans gösterilir; aynı isimli kayıtlar otomatik birleştirilmez.

## OSS-04 kurtarma doğrulaması

Temiz PG17 ortamındaki bütün yedi migration ve şema karşılaştırması başarılı. Ayrı boş PG17 hedefe dump/restore ile tüm public tablolar, migration geçmişi, finans/audit satırları ve index/constraint/trigger tanımları eşleşti. Bu sentetik kanıttır; üretim yedek politikası/PITR/RPO/RTO değildir. [Uygulanabilir prova](BACKUP-RESTORE.md), [sonuçlar](OSS04-VALIDATION.md).
