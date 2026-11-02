# S03-F — Güvenlik denetimi ve tam regresyon

## Kapsam ve başlangıç

2 Kasım 2026; yalnız DEVELOPMENT, yerel ve izole PostgreSQL 17 `siteyonetim_test`, sentetik hesap/veri ve yerel SMTP. Bu çalışma bağımsız penetrasyon testi, hukuki görüş veya production güvenlik onayı değildir.

Başlangıç main: `afd7ea7bcfe693f06daeea9d48b38b8e1fe27fcc`. PUBLIC, varsayılan main; PR #11, #12, #13, #14 ve #15 birleşmiş. PR #15’in birleşme commit’i bu başlangıç SHA’sıdır; PR içindeki son geliştirme commit’i `39cde6b1a2d6740e38d34a45aee1a28641d17ea5` ile karıştırılmamalıdır. Main-protection aktif: PR, silme/force-push engeli ve GitHub Actions (`integration_id=15368`) kaynaklı `checks` zorunlu. Strict güncellik ve dış onay sayısı zorunlu değil; bypass listesi boş. Kurallar değiştirilmedi.

Dal `codex/s03-f-security-alpha-readiness` güncel main’den oluşturuldu. Yerel Git kimliği doğrulanmış Blooregardx noreply; `.mailmap`, eski commit SHA’ları ve on tarihsel migration korunur. Başlangıç çalışma ağacı temizdi. Node 24, Next.js 16, strict TypeScript, Prisma 6 ve AGPL-3.0-only korunur. Paket/lock sürümü `0.1.0-alpha.1`; mevcut etiket `497c21cf701bf1690f135bb9b0502a7ee203a56e` noktasındadır, değiştirilmedi.

Başlangıç envanteri: 24 birim, 25 entegrasyon, 11 E2E testi; bunlar tarihsel test sayılarıdır, bu çalışmanın başarı kanıtı değildir. Yeni sayılar aşağıda ayrı raporlanır. README, yol haritası, özellikler, veritabanı, yayın/ertelenmiş işletim, S03-A–E belgeleri; schema/manifest/lock/Actions; lib/app/components/tests/scripts incelendi.

## Tehdit modeli ve güven sınırları

| Aktör | Beklenen erişim / savunma |
|---|---|
| Oturumsuz | Demo/giriş/kayıt; yönetim ekranı girişe yönlenir, CSV 401; yazım reddedilir |
| E-postası doğrulanmamış | Doğrulama/kurtarma; finans/yönetim servisleri `EMAIL_UNVERIFIED`, CSV 403 |
| RESIDENT | Mevcut organizasyonun yönetim/finans işlemlerine erişim vermez; doğrulanmış kullanıcı kendi yeni organizasyonunu oluşturabilir, ayrı resident ürün modülü yok |
| MANAGER | Kendi yetkili kapsamındaki yapı/kişi/aidat/tahsilat/manuel kayıt ve rapor; tam ters kayıt/politika/admin rol yükseltmesi yok |
| ADMIN | Kendi organizasyonunda yukarıdakiler ve yetkili tam ters kayıt, politika/üyelik işlemleri; son admin koruması |
| Başka organizasyon ADMIN’i | Kendi rolü diğer organizasyon/site/kategori/kişi/finans ID’si için yetki sağlamaz |
| Üyeliği kaldırılmış / rolü düşürülmüş eski yönetici | Sonraki istekte DB üyeliği tekrar okunur; kaldırmada organizasyona ait doğrudan site grant’leri/davetler de temizlenir |
| İptal edilmiş / süresi geçmiş oturum | DB token özeti yoksa/süresi dolduysa 401/giriş; eski cookie yeniden kullanılamaz |

Kimlik yalnız sunucu `verifySession`; istemci userId/rol/organizationId/siteId bağımsız otorite değildir. `security.actor`, `organizationAccess` ve management/okuma servisleri DB kullanıcı/doğrulama/üyeliği kontrol eder. ID kapsamı uygulama transaction’larında ve bileşik FK’lerde korunur. Bu uygulama DB RLS kullanmaz; runtime sırrı veya migration/DBA yetkisi ele geçirilmesi farklı güven sınırıdır. Yetkilendirilmiş, başlamış bir okuma/CSV snapshot’ı eşzamanlı üyelik iptalinden önceki görünümle bitebilir; ağda gönderilmiş veri geri alınmaz. Sonraki istekler yeni yetkiye tabidir.

## İncelenen alanlar ve kanıt eşlemesi

- **Kimlik/oturum:** `auth-actions.ts`, `accounts.ts`, `session.ts`, `password.ts`, mail yapılandırması. Salt+scrypt/timing-safe doğrulama; rastgele tokenların SHA-256 özeti; 7 günlük DB oturumu; production `__Host-`, Secure/HttpOnly/SameSite=Lax cookie. Girişte yeni token, çıkışta DB silme; reset tek kullanım ve bütün oturumları iptal; adres değişimi mevcut parola ve yeni adres kanıtıyla tamamlanır, oturumları/resetleri iptal eder. Mevcut akış E2E’si yanlış parola, doğrulama, reset ve adres değişimini; yeni `security-session.spec.ts` sahte/expired/revoked cookie ve güncel üyelik etkisini; ek logout replay kontrolü eski cookie’yi sınar. Sabit dahili yönlendirmeler; Server Actions Origin/forwarded Host uyumsuzluğunun gerçek POST ile reddi `flows.spec.ts` içinde. Yönetim GET’leri yazım yapmaz. Log incelemesinde uygulama yolunda ham parola/token loglama bulunmadı; bu her işletim proxy/log ayarı için garanti değildir.
- **Tenant:** Organization/Site/Block/Unit/Person/Ownership/Occupancy/Charge/Payment/PaymentReversal/BulkChargeOperation/PaymentPolicyChange/FinancialCategory/FinancialEntry/FinancialEntryReversal/AuditLog kapsamı. `management`, `property`, `security`, `reversals`, `reports-policy`, `income-expenses`, `dashboard`, `financial-export` entegrasyonları yabancı referansları ve rollerini sınar. Gerçek GET/CSV ve Server Actions negatifleri E2E’de; her model/route için ayrı fuzz testi yapıldığı iddia edilmez. Legacy organizasyonsuz sitelerin mevcut doğrudan yetkisi genişletilmedi.
- **Finans:** Int kuruş, SQL toplamlarında BIGINT ve güvenli JS sayı kontrolü. User→Organization→Site→Charge/Payment kilitleri; güncel bakiye/politika; idempotency ve farklı içerikte çatışma; fazla tahsilat reddi ve eşzamanlı yarışlar. Ters kayıt org ADMIN, tek tam ters; audit aynı transaction’da, arızada rollback. Payment/Reversal/Audit/politika/manuel geçmişin UPDATE/DELETE/TRUNCATE korumaları ve ayrı LOGIN runtime rolü entegrasyonda. DBA’nın DDL ile trigger kaldırabilmesi uygulama tarafından önlenemez.
- **Rapor:** Charge nakit sayılmaz; Payment/Reversal ve manuel Entry/Reversal ayrı kaynaklardan bir kez okunur. Ters kayıt kendi döneminde; İstanbul tarih sözleşmesi, sayfalama öncesi toplamlar, rapor/CSV eşitliği testlerde korunur. Resmî muhasebe/banka bakiyesi iddiası yok.
- **Toplu aidat:** 5.000 seçim sınırı, sunucu seçim kontrolü, hash snapshot, idempotency, çatışmada tüm ret, transaction/audit rollback. Mevcut test daire değişimi/aidat çatışmasını; yeni test blok değişimi ve seçili dairenin silinmesini sınar. E2E sayfalar arasında seçimi ve onay sonucunu sınar. 5.000 yazımın üretim yük garantisi verilmez.
- **CSV:** İki route için session/rol/org/site/kategori, allowlist/tekrarlanan filtre reddi, sabit dosya adı, UTF-8/Türkçe/CRLF ve formula kaçışları. 50.000 kayıt, 128 MiB, özel temp dizin ve 0600 dosya; tamamı hazır olmadan HTTP başarı başlığı yok. Cursor snapshot’ında eşzamanlı eklemeye rağmen atlama/tekrar yok. Yeni sınır testi çok baytlı UTF-8 ile tam sınır ve taşmayı 128 MiB dosya üretmeden doğrular. Açıklama/gerekçe kişisel veri içerebilir; otomatik redaksiyon yoktur, indiren yetkili de dosyayı korumalıdır.
- **Panel:** Mobil 390×844, 100/1.000/10.000 daire, 6× aidat; ilk/ikinci sayfada ayrık 25 kayıt, tam ve sabit özet, URL, çalışan istemci araması; detay/tahsilat/admin ters kayıt, kayıt/ilişki ve toplu seçim. Mevcut büyük fixture tekrar kullanılır. Bu tek kullanıcılı sentetik regresyondur; production/çoklu kullanıcı benchmark’ı değildir.

## Bulgular

Doğrulanmış P0/P1 saptanmadı. Bu sonuç taranan kod ve test kapsamıyla sınırlıdır; bütün olası açıkların yokluğu iddia edilmez.

| Kimlik / seviye | Dosya, etki ve yeniden üretim kanıtı | Öneri / uygulama / test / kalan risk |
|---|---|---|
| F-01 / P2 — yedek doğrulama ölçeği | `scripts/verify-backup-restore.py`: önce `jsonb_agg` ile bütün tablo tek JSON; dump `read_bytes` ile tek seferde belleğe. S03-E’de bildirilmiş büyük aggregate sınırı ve eski kod bunu doğrular; bu çalışmada tekrar 1 GiB JSON üretmeye çalışılmadı. Veriyi bozmaz ama kurtarma kanıtını engelleyebilir. | Akış hash’i uygulandı: COPY text, 64 KiB istemci parçaları; dump da akış hash’i. Üç Python testi ve gerçek restore eşitliği. PostgreSQL sort/temp disk ve tek satır sınırları sürer; writers durdurulmalı. Eski/yeni hash formatı aynı değildir. |
| F-02 / P2 — dev bağımlılık uyarısı | `package-lock.json`: minimatch 3.1.5 ve 10.2.6; [GHSA-g3hv-75wg-m249](https://github.com/advisories/GHSA-g3hv-75wg-m249), advisory aralığı `<11.0.1`. Audit 16 moderate paket düğümü, tek kök advisory; 0 high/critical. Açıklama özellikle 10.2.6 `optimizationLevel>=2` ve saldırgan glob deseni büyümesini tarif eder. Eski sürümün aynı fonksiyonu taşımaması advisory metaverisiyle karıştırılmamalı. | ESLint/import/React/TypeScript-ESLint geliştirme ağacı; HTTP isteklerinden erişilebilir kullanım bulunmadı. Güvenilmeyen katkı globlarıyla CI kaynak tüketimi olasılığı; untrusted PR zaten secret’sız/read-only CI’da işlenir. Kör major/override veya audit fix yapılmadı. Ayrı uyumluluk testiyle güncel desteklenen lint bağımlılıklarına geçiş açık. |
| F-03 / P2 — auth trafik koruma sınırı | `src/app/auth-actions.ts` limit anahtarı e-posta/kullanıcı bazlı; `:global` limiti için çağrı yok. Çok sayıda farklı hedef aynı genel kotaya bağlanmaz; hedef adres limitini tüketme mümkün olabilir. Bu kod kontrolü eksikliğidir; canlı DoS/hesap ele geçirme deneyi yapılmadı. | Güvenilir proxy/IP/global bütçe, bot/posta ve hedefli kilitlenme tasarımı ayrı iş. Mevcut atomik DB limiti korunur; üretim kapısı açık. Bu görev edge servisi kurmadı. |
| F-04 / P2 — OFFSET ve istekler arası tutarlılık | `dashboard-reads.ts`, rapor okuma modelleri: OFFSET; ayrı istekler ortak snapshot taşımaz. Eşzamanlı eklemede sayfa kayması olabilir. Önceki S03-E’nin açık teknik borcu; bu çalışmada finans kaybı veya CSV cursor atlaması bulunmadı. | Büyük sayfalama yeniden tasarlanmadı. Tam toplam ve sayfa regresyonları korundu. Standart tam navigasyon gönderilmemiş ana formu yeniler; toplu seçim kendi sayfalarında korunur. |
| F-05 / P3 — kurtarma izinleri kanıtı | Eski `verify-backup-restore.py` index/constraint/trigger karşılaştırıyor, ACL’leri karşılaştırmıyordu. Tek başına bu eksiklik runtime izni kaybı kanıtı değildi. | Tablo/sütun/şema ACL karşılaştırması eklendi. Sentetik NOLOGIN rolüyle anlamlı grant taşıma provası ve ayrı LOGIN runtime entegrasyonu. Global rol/parolalar pg_dump kapsamı değildir; gerçek işletim rol politikası ayrıca doğrulanmalı. |
| F-07 / P2 — aidat/toplu işlem DB değişmezliği | `Charge` ve `BulkChargeOperation` tablolarında diğer finans tablolarındaki immutable trigger yoktu. İzole eski şemada NOLOGIN, yalnız SELECT/UPDATE(id) rolüyle `UPDATE "Charge" SET id=id` başarılı oldu; transaction rollback edildi. Bu rol satır kilidi için gereken izni taşıyordu. Charge tutarı bu rol tarafından güncellenemez; eksiklik uygulamadan yetkisiz finans yazımı kanıtı değildir. Daha geniş DB izinleriyle tahakkuk/idempotency geçmişi yanlış değiştirilebilir. | Veri yazmayan ek `202611040001_financial_immutability`: mevcut reject fonksiyonuyla iki tabloya UPDATE/DELETE/TRUNCATE statement trigger’ı. Eski on migration korunur, yeni zincir 11. Yeni entegrasyon tutar/id, delete/truncate, değişmeyen satırlar, tahsilat ve başarılı toplu tekrarını; mevcut LOGIN runtime testi Charge id UPDATE reddini sınar. DBA/DDL sınırı sürer. |
| F-08 / P2 — yerel E2E/süre hassasiyeti | `tests/e2e/flows.spec.ts`, `reports-policy.spec.ts`; uzun tek senaryoda toplam test timeout’u, bir panel okumasında P2028 ve politika sonrası boş geçici status görüldü. Politika DB değeri doğruydu; finans yazımı kaybı saptanmadı. | Uzun test üç bağımsız senaryoya ayrıldı; kontroller korundu. Politika testi güncel UI ve DB durumunu doğrular. Tam 14/14 E2E geçti. Timeout artışı/skip yok. P2028’in alt nedeni giderilmiş sayılmaz; kaynak tüketimi, transaction süreleri ve üretim yükü ayrı takip edilmeli. |
| F-06 / P3 — belge/test eksikleri | README/ROADMAP/FEATURES/RELEASE-CHECKLIST güncel olmayan “alpha.1 yayımlanmadı / S03-E birleşmedi” ifadeleri; CSV byte limitinde odaklı sınır testi eksikliği. | Güncel durum düzeltildi; tarihsel raporlar/sayılar korunur. Byte limit hesabı aynı davranışı koruyan küçük fonksiyona ayrıldı ve sınır testi eklendi. Yeni oturum/yetki/snapshot regresyonları eklendi. |

## Yeni çalıştırma sonuçları

| Kontrol | Sonuç / kanıt |
|---|---|
| ESLint / TypeScript | Başarılı; ayrıştırılmış E2E kodu için yeniden çalıştırıldı |
| Birim | 25/25; 0 atlanan / 0 başarısız |
| PostgreSQL entegrasyon | Temiz 11 migration’lı ortamda 28/28; 0 atlanan / 0 başarısız |
| Playwright | Ayrıştırma sonrası tam 14/14; 0 atlanan / 0 başarısız |
| Production build | Başarılı; bu yalnız build, deploy değildir |
| Prisma generate / validate | Başarılı; Prisma 6.19.3 |
| Temiz migration / şema diff | Ayrı yeni PG17 test DB’sinde 11/11; fark yok |
| Alpha.1 yükseltme | 7→10→11; legacy kullanıcı/site/üyelik/aidat/ödeme/audit sentinelleri korundu; fark yok |
| Güncel main yükseltme | 10→11; tam finans, yetki ve audit regresyonları başarılı |
| Streaming Python regresyonları | 3/3 başarılı; sınırlı okuma/parça sınırı/Unicode/binary hash |
| Sentetik backup/restore | Başarılı: 26 tablo / 308.493 satır; hash, katalog/ACL ve runtime izin sınırı eşit; kaynak/hedef uygulama probu başarılı |
| Lisans/SPDX | Resmî tam AGPL hash’i, manifest/lock, yeni kod tanımları; bağımlılıklar/şema/mailmap ve eski migration’lar korunur |
| Markdown | 37 Markdown dosyası / 130 yerel dosya bağlantısı başarılı; uzak URL/anchor sağlığı iddia edilmez |
| npm audit | Tüm ağaç 16 moderate paket / tek advisory; high/critical 0; production 0 |
| Secret / hassas dosya | Uzak dallar dahil erişilebilir 39 commit/362 blob; yüksek güvenli desen/izlenen hassas dosya eşleşmesi yok; 170 izlenen dosya ayrıca tarandı; yüksek güvenli sır veya fixture’da örnek-dışı e-posta adayı yok |

Çalıştırma: `npm run db:generate`, `npm run db:validate`, `npm run db:deploy`, `npm run check`, `npm run test:integration`, `npm run build`, `npm run test:e2e`; `npx prisma migrate status`, `npx prisma migrate diff --from-url "$DATABASE_URL" --to-schema-datamodel prisma/schema.prisma --exit-code`; `PYTHONDONTWRITEBYTECODE=1 python3 scripts/test_backup_stream.py`, `python3 scripts/verify-source-readiness.py`; `npm audit --json` ve `npm audit --omit=dev --json`. Test URL’leri yalnız loopback `siteyonetim_test` içindir; gerçek sır kullanılmaz. CI kaynak kontrollerini ve schema diff’i de tekrarlar; audit tam ağacında yalnız high/critical başarısızlık eşiği, production ağacında sıfır uyarı kontrolü kullanır. Yeşil CI, tüm ağacın uyarısız olduğu anlamına gelmez.

Son commit push/PR CI bağlantıları ve gerçek sonuçları PR açıklamasında ve nihai raporda yer alır; iki koşu tamamlanmadan PR hazır kabul edilmez.

Son 14/14 yerel koşudaki mobil 390×844 tarayıcı gözlemleri (tek örnek; servis medyanı değildir):

| Daire / aidat | İlk panel | İkinci sayfa |
|---|---:|---:|
| 100 / 600 | 522 ms | 629 ms |
| 1.000 / 6.000 | 658 ms | 543 ms |
| 10.000 / 60.000 | 3.169 ms | 1.914 ms |

Her ölçekte 25 ayrık kayıt, doğru URL, tam özet ve çalışan arama/detay/finans erişimi doğrulandı. 10.000 ölçekte ilk tarayıcı gözlemi 3 saniyenin üzerindedir; önceki S03-E servis medyanı/hedefi farklı metriktir ve yeniden ölçülmüş sayılmaz. Kapasite fixture’ları aynı test kaynağında tekrar kullanıldı; temiz nihai ortamda bir kez yeniden üretildi. Değişken süreler ve P2028 alt nedeni P2 performans/güvenilirlik takibidir. Bu bir production SLA’sı değildir.

## İlk denemeler ve açık test kararlılığı sınırı

Başlangıçtaki yeni test kodunda Session için yanlış `id` alanı kullanımı typecheck ile; yeni block snapshot testinde eksik `description` girdisi entegrasyon ile yakalandı. Bunlar test verisi/kodu hatalarıydı; tokenHash ve tam girişle düzeltildi. İlk tam entegrasyon 26/27, düzeltmeden sonraki koşu 27/27 idi; ek değişmezlik testiyle güncel kapsam 28 oldu.

İlk E2E 10/12: CSV sınır yanıtı ve adres değişimi akışı toplam 30 saniyelik test bütçesini aştı. O sırada bağımsız yerel kontroller de çalışıyordu; bu durum kesin kök neden olarak sunulmaz. Sıralı tekrarı 12/12 geçti. Ek migration sonrasındaki ilk E2E 11/12: ana akışta Payment count okuması Prisma P2028/5 saniyelik transaction kapanmasıyla kesildi. Sonraki E2E 11/12: politika testinin geçici başarı mesajı boş kaldı; DB kontrolünde politika kapalıydı. Politika testi, güncel ekrandaki Kapalı durumu ve DB değerini birlikte doğrulayacak şekilde düzeltildi; gerçek iş kuralı kontrolü güçlendirildi. Timeout yükseltilmedi, test atlanmadı. Temiz 11 migration’lı ortamda entegrasyon 28/28, E2E ilk koşu 11/12 (ana akışın toplam test süresi) oldu. Eski tek ana E2E, bütün kontrolleri korunarak bağımsız kayıt/güvenlik, finans ve kayıt-düzenleme senaryolarına ayrıldı. Her biri bağımsız sentetik fixture ve oturum kullanır; birbirinin sonucuna bağımlı veya serial-skip değildir. Orijinal kayıt/CSRF/adres değişimi ve finans UI assertion’ları korunur; kayıt düzenlemede finans satırı eşitliği ayrıca eklendi. Sonraki tam kapsam 14 E2E’dir. Bu ayrıştırma P2028’in alt nedeninin düzeltildiği iddiası değildir. Son tam sonuç yukarıda ayrı verilir; aralıklı süre/ortam hassasiyeti P2 güvenilirlik takibidir, giderilmiş kök neden iddiası yoktur.

İlk ACL karşılaştırması bütün satır hash’leri eşitken explicit sahip ACL’si ile eşdeğer implicit varsayılanı farklı saydı. Karşılaştırma `acldefault`/`aclexplode` ile semantik tablo/sütun grant’lerine düzeltildi; yeni boş hedefte bütün prova yeniden yapıldı. İlk temiz yeni DB çağrısında ayrıntısız Prisma schema-engine hatası alındı; hazır olma kontrolünden sonra aynı zincir başarılı oldu. Başarısız denemeler başarı sayılmadı. İlk npm audit beklemesi durduruldu; proxy açık ve sınırlı ağ süreli gerçek tarama tekrarlandı. Tarihsel CI sonuçları silinmedi.

## Migration ve kurtarma yöntemi

Başlangıçta temiz izole PG17’de 10 migration; yeni zincir 11 migration. Alpha.1 commit’inin yedi migration’ı üçüncü, ayrı geçici `siteyonetim_test` konteynerine uygulanıp sentetik kullanıcı/site/direct üyelik/blok/daire/10.000 kuruş aidat/2.500 kuruş ödeme/audit eklendi. Önce S03-A–C’nin üç migration’ı, ardından S03-F’nin bir ek migration’ı sonrası sentineller, unverified/null parola ve organizasyonsuz site güven sınırı korundu; şema farkı yok. Tarihsel migration değiştirilmedi; S03-F, aşağıda gerekçesi verilen `202611040001_financial_immutability` migration’ını ekler; güncel sayı 11 olur. Başlangıç main 10 migration’dır; 10→11 veri korumalı yükseltmesi ve güncel şemada no-op deploy ayrıca kontrol edilir.

Son 11 migration provası: **26 tablo / 308.493 satır**, `catalogEqual=true`, `runtimePrivilegesChecked=true`. Dump SHA-256: `716beca3eddacb48cbe03cc67230d84bcaceafc2af53bde7acd2bb910f041032`. Bu hash yayımlanmış bir yedeğin bağlantısı değildir; dump geçicidir ve araç tarafından kaldırılır. Kaynak/hedef uygulama probunda 15 ilgili audit ve 11 migration korundu. Önceki 10 migration’lı ara prova 26/365.916 idi; farklı fixture kapsamıdır, nihai sayı yerine kullanılmaz.

Restore: farklı boş hedef, pg_dump custom / pg_restore single transaction; bütün public tablolar, satır sayıları/akış hash’leri, 11 migration geçmişi, index/constraint/trigger ve tablo/sütun/şema ACL’leri karşılaştırılır. `recovery-probe.ts` brüt 6.500 / ters 4.000 / net 2.500 / borç 7.500 kuruş, tenant ve immutable audit/finans kontrolünü hedefte tekrarlar. Kaynak/hedef yazıcıları durdurulur. Global roller önceden kontrollü hazırlanır; sentetik NOLOGIN grant fixture’ı production hesabı değildir. Gerçek sır/kişisel veri veya yedek Git’e eklenmez.

## Tedarik zinciri, lisans ve hassas bilgi

Actions checkout/setup-node tam SHA’ya sabit, checkout credentials persist etmez, izin `contents: read`; pull_request_target/untrusted kodla secret kullanım yolu yok. Çift push/PR koşusu aynı tam workflow’u çalıştırır. V4 Actions runtime desteği, ESLint 9 desteği ve PostgreSQL 17-alpine digest/güncelleme politikası ayrı P3 bakım işleridir; mevcut sürümler kapsam dışı major yükseltilmedi.

Production bağımlılıkları için ayrı `npm audit --omit=dev` sonucu 0 uyarıdır. 479 kilit bağımlılık kaydının lisans metaverisi var; manifest/lock/dependency inventory ve LICENSE değişmedi. AGPL-3.0-only SPDX korunur. LGPL Sharp/libvips ve MPL/NOTICE kaynak yükümlülükleri [üçüncü taraf incelemesinde](THIRD-PARTY-LICENSES.md) açık; bu denetim binary/konteyner dağıtımı onaylamaz. Yalnız proje kaynak kodu alpha adayı; node_modules/.next/browser/dump eklenmez. Tam platform/kaynak kökeni hukuki garantisi verilmez.

Başlangıçta 10 yerel ref üzerinden 32 commit/350 blob; bütün uzak dallar getirildikten sonra 24 ref üzerinden 39 commit/362 blob yüksek güvenli token/özel anahtar desenleri ve hassas dosya adlarıyla tarandı; eşleşme yok. Geçmişte erişilemeyen GitHub PR/cache/unreachable objeler için yokluk garantisi yoktur. Mevcut çalışma ağacı ve son değişiklikler ayrıca kontrol edilir. Sentetik fixture adresleri `example.invalid`; Git kimlik eşlemesindeki bilinçli metadata kullanıcı veritabanı değildir; kişisel e-postalar rapora taşınmaz. Desen taraması bütün kişisel veriyi veya her biçimde sırrı bulma garantisi değildir. Bir gerçek sır bulunursa değer yayımlanmadan iptal/rotasyon ve kapsam incelemesi gerekir; geçmiş yeniden yazılmaz.

## İlk GitHub CI ve URL assertion düzeltmesi

`1c23b4624ed8234031c21973efaeae145cad591b` için [push CI](https://github.com/Blooregardx/siteyonetim-saas/actions/runs/41519691459) başarılıydı: 25/28/14 test, backup/restore 26 tablo/258.144 satır, katalog/izin eşitliği. Aynı commitin [PR CI](https://github.com/Blooregardx/siteyonetim-saas/actions/runs/41519852680) koşusu 13/14 E2E ile başarısız oldu; restore adımı bu koşuda çalışmadı, başarılı sayılmaz. Eski koşular silinmedi veya yeniden etiketlenmedi.

PR hatası 10.000 daire testinin ikinci sayfa URL assertion’ında: HTTP 200/commit gerçekleşmiş, hata mesajındaki URL beklenen panel/org/site/chargesPage=2 değerini taşıyor, document readyState loading idi. Kurulu Playwright 1.64.1 kodunda `toHaveURLWithPredicate` → `waitForURL` → `waitForLoadState(undefined)` yolu varsayılan **load** olayını da bekliyor. Önceki açık commit bekleyişinden sonra predicate assertion bu gizli lifecycle koşulunu tekrar getiriyordu. Bu, Next.js’in daha alt bir arızasının kanıtı değildir.

**F-09 / P3:** `tests/e2e/scalable-dashboard.spec.ts`: URL assertion’ı gerçek bağlantının tam `target.href` metniyle yapıldı. Playwright’ın metin URL matcher’ı URL değerini denetler; predicate overload’un örtülü load bekleyişini kullanmaz. Tam URL kontrolü org/site/sayfa ile birlikte bütün link filtrelerini korur. HTTP yanıtı, commit bekleyişi, 25 ayrık satır, tam özet ve çalışan istemci araması assertion’ları değişmedi. Süre artırımı, retry ekleme veya test atlama yok; uygulama navigasyonu/finans kodu değiştirilmedi. İlgili dosya lint/typecheck ve son commitin tam push/PR iş akışlarıyla doğrulanır. Gerçek veri render’ı veya etkileşim takılırsa sonraki assertion’lar yine hata verir; streaming/load alt nedeni kapatılmış sayılmaz.

Son commit CI sonucu ve bağlantıları PR açıklaması/nihai raporda kaydedilir; önceki başarılı push, yeni commit veya başarısız PR sonucu yerine kullanılmaz.

## Açık işletim kapıları

Gerçek SMTP teslimi, bağımsız insan kurulumu, TLS/proxy ve canlı güvenlik/yük testi, MFA, tüm işletim rolleri, yedek şifreleme/saklama/PITR/RPO/RTO, izleme/alarmlar ve veri koruma süreçleri tamamlanmadı. CSV açıklamaları kişisel veri içerebilir. Sentetik başarı STAGING/PRODUCTION veya felaket kurtarma garantisi değildir. [Hazırlık kararı](ALPHA2-READINESS.md); yeni release/tag yalnız ayrı kullanıcı onayıyla değerlendirilebilir.
