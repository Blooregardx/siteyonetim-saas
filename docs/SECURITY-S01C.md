# S01-C güvenlik ve bulut işletim planı

## Kimlik ve e-posta

Mevcut hesaplar emailVerifiedAt=NULL kalır; otomatik doğrulama yoktur. Yeni kayıtta oturum açılır ama yönetim paneli doğrulamaya yönlendirir. Servisler her istekte User.emailVerifiedAt kontrol eder; eski üyelik satırları doğrulanmadan erişim vermez. 256 bit rastgele e-posta tokenının yalnızca SHA-256 özeti saklanır. Token bir saat, davet 48 saat geçerlidir. E-posta doğrulama oturumdaki aynı kullanıcıyı gerektirir ve GET ile işlem yapmaz. POST, kullanıcı satırı kilidi ve transaction ile tek kullanım sağlanır. Yeniden gönderim önceki doğrulama tokenını iptal eder.

Adres değişiminde mevcut parola yeniden istenir. Yeni adres doğrulanana kadar eski adres ve doğrulaması korunur; değişiklik yalnızca yeni adresin sahipliği kanıtlanınca uygulanır. Değişimde tüm oturumlar ve reset tokenları iptal edilir; yeniden giriş gerekir. Böylece son doğrulanmış admin geçici olarak doğrulanmamış hâle getirilmez. Uygulamanın mevcut parola ve doğrulama akışları dışında doğrudan User.email yazan uç yoktur.

## Yetkiler ve eşzamanlılık

ADMIN tüm üç rolü davet edebilir; MANAGER yalnız RESIDENT davet edebilir. Yalnız ADMIN rol değiştirir ve üye çıkarır. MANAGER yalnız kendi RESIDENT davetini iptal eder; ADMIN organizasyondaki tüm bekleyen davetleri iptal edebilir. Kabulde hem hedefin doğrulanmış e-postası hem davetçinin güncel yetkisi yeniden kontrol edilir. Var olan üyelik davet kabulüyle yükseltilmez; açık rol değişimi gerekir.

Organizasyon satır kilidi üyelik değişimi, kabul ve yönetim/finans işlemlerini sıraya koyar. Doğrulanmış son ADMIN düşürülemez veya silinemez; paralel düşürmeler de kilitle denetlenir. Üye kaldırılınca aynı organizasyon sitelerindeki doğrudan eski yetkiler ve o üyenin bekleyen davetleri iptal edilir. Rol değişiminde de eski doğrudan site yetkileri kaldırılır; böylece RESIDENT'e düşürülen kişi eski ADMIN atamasından erişemez. Açık oturum, üyelik bilgisi önbelleği taşımaz. Veritabanı yetkisi her işlemde yeniden okunur.

## Audit

AuditLog id işlem/audit kimliğidir. actorId, organizationId, siteId (uygunsa), action, entityId ve createdAt saklanır. Parola, token, e-posta, kişi adı ve talep gövdesi tutulmaz. Kimlik alanları kalıcı olay referanslarıdır; geçmişin kullanıcı/organizasyon silinmesiyle bozulmaması için audit üzerinde silmeye bağlı FK yoktur. Audit değişiklik/silme/TRUNCATE DB trigger ile reddedilir. Uygulamada değiştirme/silme ucu yoktur. DBA veya tablo sahibi trigger'ı devre dışı bırakabilir; ayrı roller ve dışa aktarılmış değişmez arşiv operasyonel güvenlik katmanıdır.

Organizasyon, davet, üyelik, apartman, blok, daire, malik/kiracı, aidat ve tahsilat yazımları audit ile aynı transaction içindedir. Audit başarısızsa işlem geri alınır. Başarılı tahsilatın idempotent tekrarı ek audit üretmez. Audit SELECT erişimi yalnız yetkili raporlama/operatör servisine verilmeli; halka açık listeleme ucu açılmadı.

## Veritabanı rolleri

Aşağıdaki rol ayrımı sağlayıcı yetkilerine uyarlanarak DBA tarafından yapılmalıdır; bu görevde üretime uygulanmadı.

- Migration sahibi: DDL, migration tablosu, fonksiyon/trigger yönetimi; yalnız CI/onaylı operatörde, uygulamada bulunmaz. Uygulama rolü bu role üye olmaz.
- Runtime: NOSUPERUSER, NOCREATEDB, NOCREATEROLE, NOREPLICATION; şema CREATE veya tablo sahipliği yok. DATABASE CONNECT ve public USAGE verilir.
- Runtime: User/Session/PasswordReset/EmailVerification/AuthAttempt/Invitation/OrganizationMembership/Membership için gerekli SELECT/INSERT/UPDATE/DELETE; Organization/Site/Block/Unit/Occupancy için yalnız uygulanan işlemlerin SELECT/INSERT yetkileri.
- Charge ve Payment: yalnız SELECT/INSERT. UPDATE/DELETE/TRUNCATE verilmez. AuditLog: yalnız INSERT (okuma gerekiyorsa denetim servisine SELECT); UPDATE/DELETE/TRUNCATE yok.
- Bakım rolü: sadece Session/PasswordReset/EmailVerification/AuthAttempt SELECT/DELETE. Audit, finans, üyelik veya kullanıcı tablosunda silme yetkisi yok.
- PUBLIC şema CREATE ve tablo ayrıcalıkları gözden geçirilmeli; yeni tablolara körlemesine ALL default privilege verilmemeli. Her migration sonrası izin farkı kontrol edilmeli.

Uygulama servislerinin tüm kısıtları PostgreSQL RLS değildir. Runtime DB sırrı sızarsa uygulama yetki modelini atlama riski vardır. TLS, secret izolasyonu, ağ erişimi, bağlantı sınırı ve erişim logları gerekir. İzole test rolü migration sahibidir; gerçek runtime rolü sağlayıcıda henüz oluşturulmadı.

## Ortam değişkenleri ve SMTP

DATABASE_URL uygulamanın sağlayıcıya uygun TLS/pool bağlantısıdır. Migration komutunda DATABASE_URL ayrı migration rolü/doğrudan bağlantı URL'si olarak CI secret'ından enjekte edilir. MIGRATION_DATABASE_URL belgeli operatör secret adıdır; Prisma otomatik okumaz. Komut ortamı açıkça seçilmelidir. URL/parolalar loglanmaz. Sağlayıcı TLS doğrulaması kapatılmaz; pooler Prisma transaction ve bağlantı özellikleriyle uyumlu olmalıdır.

APP_URL HTTPS ve yalnız origin olmalı; kullanıcı/parola, yol, query veya fragment kabul edilmez. SMTP_URL smtps veya zorunlu STARTTLS kullanan smtp olmalıdır; MAIL_FROM satır sonu içeremez. TLS sertifika doğrulaması kapatılmaz. HTTP/düz SMTP yalnız DATABASE_URL=TEST_DATABASE_URL ve loopback siteyonetim_test + loopback uygulama/SMTP koşullarında kabul edilir. Gerçek sağlayıcı hesabı, SPF/DKIM/DMARC, teslim/bounce izleme ve HTTPS sertifikası ayrıca kurulmalıdır.

## Temizlik

HTTP bakım ucu açılmadı. Onaylı bakım rolü/DB secret'ı ile bulut zamanlayıcısından `npm run security:cleanup -- --apply` çağrılır. --apply olmadan yazmaz. Her tabloda en çok 1000 süresi geçmiş satır silinir; FOR UPDATE SKIP LOCKED eşzamanlı işlemlerden kaçınır. İşlem gerekirse sonraki çalışmada devam eder. Yalnız sabit dört güvenlik tablosu hedeflenir. Audit, davet geçmişi ve finans silinmez. Sonuç yalnız tablo/sayıdır; token veya kullanıcı bilgisi loglanmaz. Öneri: 5–15 dakikalık periyot; hata, süre ve backlog alarmı. Süre aşmış satırlar temizlik gecikse de doğrulanmaz.

## Giriş sınırlaması

Eski global 100/15 dakika limiti kaldırıldı; tek saldırganın tüm kullanıcıları kilitlemesi önlendi. E-posta bazında 10/15 dakika giriş/kayıt ve kurtarma limiti, oturum kullanıcısı bazında doğrulama yeniden gönderim limiti sürer. Kayıtlı hesaplara hedefli kilitleme ve rastgele e-postalarla yük saldırısı hâlâ mümkündür. Güvenilir edge IP/risk limiti, bot koruması ve alarm kurulmadan internet ölçeğinde yeterli sayılmaz. x-forwarded-for doğrudan güvenilir kimlik olarak alınmadı. Devre dışı global limit satırları süre sonunda temizlenir.

## Yedekleme, geri yükleme, izleme

Sağlayıcıda şifreli otomatik yedek + PITR seçilmeli; RPO/RTO iş hedefiyle belirlenmeli. Migration öncesi snapshot ve izole ortama geri yükleme provası yapılmalı. Erişimler ayrı operatör rolünde olmalı. Yedek saklama/KVKK süreleri kararlaştırılmalı. Audit arşivi ve erişimleri ayrı tutulmalı. Oturum/token içeren yedekler hassas sayılmalı.

DB bağlantı havuzu, kilit bekleme, transaction hatası, audit yazım hatası, doğrulama/davet teslim hatası, giriş ret oranı ve bakım backlog'u izlenmeli. Finans/audit hataları alarm üretmeli; token veya parola loglanmamalı. Gerçek bulutta yedek/geri yükleme veya alarm doğrulaması yapılmadı.
