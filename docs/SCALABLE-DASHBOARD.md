# S03-E — Ölçeklenebilir yönetim paneli

Yalnız DEVELOPMENT; sentetik PostgreSQL 17 `siteyonetim_test`. STAGING/PRODUCTION dağıtımı, yeni release ve finans geçmişi dönüşümü yoktur. Başlangıç main: `33169af14ea0a2fd898838839cc8eb7772a31e09` (S03-D, PR #14).

## Eski darboğaz ve yeni okuma modelleri

Eski panel, portföydeki her apartman için `dashboard()` çağırıyor; tüm blok, daire, kişi ilişkisi, aidat, tahsilat ve ters kayıtları Prisma nesneleri olarak yüklüyordu. Toplamlar ve filtreler JavaScript belleğinde hesaplanıyordu. S03-D’nin tarihsel başarısızlıkları korunur: 1.000 daire/6.000 aidatta 5 saniyelik transaction süresi, 10.000/60.000’de PostgreSQL stack sınırı aşılıyordu.

Yeni `dashboard-reads.ts`, mevcut management API’sine eklenen ayrı okuma modelleridir:

- `portfolioSummary`: yalnız organizasyon bilgisi, apartman/daire sayısı ve tam finansal toplamlar.
- `sitesPage`: aramalı, 25 apartman; sadece blok/daire sayıları.
- `siteOverview`: seçili apartman bilgileri, politika ve daire sayısı.
- `siteUnitsPage`: blok, numara araması, kat, tür, kullanım durumu; 25 daire. Yalnız görünen dairelerin borçları SQL ile hesaplanır.
- `siteChargesPage`: dönem, blok, daire, ödeme durumu ve borç filtresi; 25 aidat ve SQL bakiyeleri.
- `chargeDetails`: tek aidatın bütün geçmişten hesaplanan bakiyesi ve 25 tahsilat; sonraki sayfalarla tüm tahsilat/ters kayıt geçmişi.
- `blocksPage`, `personsPage`, `siteRelationsPage`: ayrı sınırlı arama/sayfalar. İlişki geçmişi yalnız seçili daire için yüklenir.
- `bulkSelection`, `selectedUnitsPage`: sınırlı seçim kimlikleri ve seçimin sayfalı doğrulanması.

`/panel` hiçbir `dashboard()`/`propertyDetails()` çağrısı yapmaz. `/kayitlar` da sınırsız `propertyDetails()` kullanmaz. Eski yardımcı API’ler, küçük fixture’lara dayalı önceki entegrasyon testleri ve geriye uyumluluk için korunmuştur; büyük portföyler için kullanılmamalıdır. Yeni canlı akışlarda malik/kiracı ilişkileri, kullanıcı bilgileri ve ödeme geçmişi daire/aidat listelerine gömülmez.

Sorgu sayısı apartman veya satır başına artan N+1 değildir. Panelde sabit sayıda bağımsız servis çağrısı vardır; aynı kullanıcı/site doğrulaması bu servislerde tekrar edilir. Bu ek sorgular bir sonraki optimizasyon adayıdır. Bütün organizasyon için bir dashboard çağrısı ve apartman başına geniş ilişki sorgusu yoktur.

## Tam aidat özeti

Kartlar seçili **organizasyonun bütün apartmanlarını ve tüm aidat geçmişini** kapsar; seçili apartmanın listeleriyle karıştırılmaz. Dairesi olup aidatı olmayan kayıtlar da daire sayısına dahildir.

PostgreSQL’de ayrı alt toplamlar kullanılır: Charge tahakkuku, Payment brüt tahsilatı, PaymentReversal tam ters kayıt toplamı. Ayrı kaynak toplamları join çoğalmasını önler. Net = brüt − ters kayıt; kalan = tahakkuk − net. Her servis çağrısının özetleri BIGINT üzerinden gelir; mevcut `reportTotals`/`chargeBalance` sözleşmesiyle güvenli tam sayıya dönüştürülür. Güvenli aralık aşılırsa hata oluşur; yuvarlama yoktur. Sayfa satırlarının toplamı genel kartları belirlemez.

Örnek kapasite fixture’ı: 10.000 daire, altışar 200 TL tahakkuk ve 100 TL kısmi tahsilat, tahsilatların %10’u tam ters kayıt. Tahakkuk 12.000.000 TL; brüt 6.000.000 TL; ters kayıt 600.000 TL; net 5.400.000 TL; kalan 6.600.000 TL. Tahakkuk nakit değildir. Manuel gelir/giderler bu aidat kartlarına eklenmez. Sabit veride S03-B borç raporu ve S03-D CSV ile tutarlılık entegrasyonda doğrulanır.

## Sayfalama ve kullanım

Tüm listelerde boyut 25’tir. Sayfa numarası 1..1.000.000 aralığında doğrulanır; deterministik sıralama benzersiz `id` ile tamamlanır. Daire/apartman/blok/kişi listelerinde `id`; aidatlarda dönem DESC + id; tahsilatlarda id; ilişkilerde başlangıç DESC + tür + id kullanılır. Kayıt tarihi sırası gerektiğinde ekranda görülen tarihle karşılaştırılabilir; id sırası kronolojik sıra garantisi değildir.

Mevcut URL filtreleri ve önceki/sonraki gezinme korunarak LIMIT/OFFSET seçilmiştir. İlk/son/boş ve 25/26, 50/51 sınırları test edilir; derin sayfa ayrıca ölçülür. Cursor API’si eklenmediği için geçerli bir cursor parametresi veya başka tenant cursor’ı kabul eden bir yol yoktur. Site/blok/daire kimlikleri server scope içinde doğrulanır. Filtre formları kendi sayfasını sıfırlar. Bağlantılar diğer aktif filtreleri korur.

OFFSET canlı listesinde ayrı HTTP istekleri arasında yeni kayıt eklenirse satır kayması olabilir; snapshot/keyset garantisi verilmez. Kayıtlar kaybolmaz, silinmez veya değişmez; arama, ilk sayfa ve detay bağlantılarıyla erişilebilir. Çok daha yüksek hacim ve eşzamanlı ekleme oranında cursor tasarımı sonraki aşamadır.

Apartman, blok ve kişi aramalarının ayrı sayfaları vardır. Blok dropdown’ları görünen blok sayfasını içerir; diğer bloklar kayıt yönetiminin blok araması/sayfalarıyla bulunur. Daire aramasının aktif sayfası tekil aidat ve hızlı kişi kaydı seçeneklerini belirler. Kayıt yönetiminde kişi araması organizasyon kapsamındadır; kişi kısa referansı kimliğini ayırır. İsim eşitliğiyle birleştirme yapılmaz.

## Tahsilat ve ters kayıt

Panelden apartman → daire araması/aidatlar → **Aidat detayı ve tahsilat** bağlantısı. Detayda güncel tam bakiye, CollectionForm, 25’lik ödeme geçmişi ve tam ters kayıtlar bulunur. MANAGER tahsilat yapar; yalnız organizasyon ADMIN’i ters kayıt butonu görür. Ödeme politikası panelde görünür; yalnız organizasyon ADMIN’i değiştirebilir.

Finans yazma kodu değiştirilmez: güncel bakiye/politika, tam bakiye seçimindeki değişiklik reddi, fazla ödeme koruması, kilit sırası, kalıcı idempotency ve audit aynı transaction içinde kalır. Güncellemelerde `/panel` layout’u revalidate edilir; detay ve kartlar yenilenir. Ters kayıt gerekçe/onay ister ve gerçek para iadesi değildir. Ödenmiş aidat, sayfa değiştirerek yeniden tahsil edilebilir hale gelmez.

## Toplu aidat seçimi

5.000 sınırı korunur. En fazla 5.000 daireli apartmanda varsayılan bütün daire kimlikleri seçilidir; yalnız aranan 25 checkbox DOM’da gösterilir. Daha büyük apartmanda seçim boş başlar ve açık sınır mesajı görünür. Arama, önceki/sonraki sayfa ve **Seçilen daireleri incele** ile seçimin tamamı doğrulanabilir. Seçimler formun açık olduğu süre boyunca sayfalar arasında korunur; tarayıcı yenilemesi veya apartman değişiminde yeni başlangıç seçimi yapılır. En fazla 5.000 kimlik istemci state’inde tutulur; 10.000 checkbox üretilmez.

Önizleme sunucuda seçimin tamamını doğrular. Tablo 25’lik gösterilir; sayı, toplam, çakışma ve hash bütün seçime aittir. Önizleme hash’i, idempotency, bayat bilgi/tek çakışmada tüm işlem reddi ve atomiklik değişmedi. Büyük seçimlerde önizleme yanıtı halen en fazla 5.000 satır metadata’sı içerir; DOM sınırlandırılmıştır. 5.000 yazımlı commit’in mevcut 60 saniye sınırı değiştirilmedi; tam 5.000’lik yazım için ayrı yük/çoklu kullanıcı provası gerekir.

## Yetki ve tutarlı okuma

Sunucu `verifySession` → mevcut `actor` ile geçerli oturum ve doğrulanmış e-posta; ardından organizasyon üyeliği ve ADMIN/MANAGER rolü. Site okumaları mevcut doğrudan ADMIN/MANAGER üyeliğini de korur. Organizasyonsuz apartmanlar portföye otomatik taşınmaz. Doğrudan site yetkisi organizasyon kişi rehberini açmaz; kontrollü organizasyon eşlemesi gerekir. RESIDENT ve yabancı site/charge/unit/block kimlikleri reddedilir; istemci rol/userId bilgisi kullanılmaz.

Her okuma servisi kısa REPEATABLE READ transaction kullanır; actor’ın mevcut User paylaşım kilidi korunur. Organizasyon FOR UPDATE veya Site/Charge yazma kilidi alınmaz. Servis içindeki liste, sayım, bakiye ve üyelik aynı görünümü paylaşır. Ayrı servisler veya ayrı HTTP istekleri aynı snapshot’ı paylaşmaz. Eşzamanlı yazım olabilir; kesin finansal işlemde mevcut yazma servisleri yeniden yetki ve bakiye kontrolü yapar. Yeni indeks/migration, runtime rolüne yeni izin ve limit artırımı yoktur.

## Ölçüm ve doğrulama

Yeniden üretim: eşleşen izole DATABASE_URL/TEST_DATABASE_URL ile `npx tsx scripts/measure-scalable-dashboard.ts`. Script yalnız loopback `siteyonetim_test` kabul eder, sentetik fixture ekler; reset veya tarihsel güncelleme yapmaz. `--skip-legacy`, önceki başarısızlık kanıtlarını koruyup yeni servisleri ayrı Node sürecinde tekrar ölçer. `--http`, aynı test DB’sine bağlı production build’in loopback TEST_BASE_URL adresinde Playwright ile gerçek paneli açar; servis/HTTP/tarayıcı süreleri ayrıdır.

[Ham ölçümler](performance/s03e-measurements.json), [EXPLAIN ANALYZE BUFFERS](performance/s03e-explain.json). Sıcak üç örneğin medyanı; gerçek soğuk önbellek iddiası yoktur. Ortam 2 CPU, PostgreSQL 17, varsayılan 128 MiB shared_buffers/4 MiB work_mem. RSS tüm Node sürecidir; 10 ms örnekleme kısa tepeleri kaçırabilir. Paralel testler, GC ve ortak cloud kaynağı sonuçları etkiler; üretim SLA’sı değildir.

| Daire / aidat | Eski dashboard | Yeni panel servisleri | Organizasyon özeti | İlk daire sayfası | İlk aidat sayfası | Son aidat sayfası | Aidat detayı |
|---|---:|---:|---:|---:|---:|---:|---:|
| 100 / 600 | 63.49 ms | 66.11 ms | 9.52 ms | 11.85 ms | 14.41 ms | 16.17 ms | 22.74 ms |
| 1.000 / 6.000 | 5.000 ms transaction sınırı: başarısız | 114.71 ms | 6.67 ms | 9.25 ms | 77.22 ms | 86.64 ms | 10.00 ms |
| 10.000 / 60.000 | 54001 stack depth: başarısız | 762.59 ms | 32.17 ms | 17.52 ms | 606.35 ms | 809.05 ms | 10.46 ms |

Eski sütun tek `dashboard()` çağrısıdır; yeni panel sütunu yedi sınırlı servisin sıralı toplamıdır. Aynı iş kapsamı olmadığından yüzdelik hızlanma iddiası yoktur. 100 dairede küçük sabit maliyet farkları vardır. 10.000 dairede **762,59 ms servis medyanı**, 3 saniyelik hedefin altındadır. Eski başarısız çağrıların HTTP/tarayıcı süreleri ayrıca ölçülmedi; servis hataları ham JSON’da korunur.

| Daire | HTTP başlık/TTFB | Tablo ve başlık hazır | networkidle dahil | Yanıt boyutu | Next Node RSS önce → sonra / örnek tepe |
|---|---:|---:|---:|---:|---:|
| 100 | 29.87 ms | 482.38 ms | 1028.19 ms | 111,586 bayt | 134.48 → 139.93 / 139.93 MiB |
| 1000 | 27.17 ms | 469.49 ms | 1023.60 ms | 153,937 bayt | 139.93 → 145.75 / 147.71 MiB |
| 10000 | 19.63 ms | 947.42 ms | 1407.07 ms | 106,940 bayt | 145.75 → 147.78 / 147.78 MiB |

Next streaming yanıtında ilk başlık tüm içeriğin hazır olması değildir. Tarayıcı hazır ölçümü gerçek tablo/başlığı bekler; networkidle değeri ayrıca en az 500 ms sessizlik içerir. HTTP her ölçek için tek navigasyon, aynı önceden yüklenmiş local production build, 100→1.000→10.000 sırasıdır. Son servis ve HTTP provaları sırasında kasıtlı başka test/restore çalıştırılmadı. [İlk keşif örnekleri](performance/s03e-exploratory.json) korunur; o HTTP turu ayrı test konteynerindeki restore ile çakıştı. Cloud CPU/I/O/GC oynaklığı ve önbellek etkisi nedeniyle sonuçlar SLA değildir.

Servis ölçümünde BEGIN/SET/COMMIT dahil sorgu sayısı organizasyon özeti 8, ilk daire 12, ilk aidat 9; panel toplamı 100/1.000’de 66, 10.000’de 65 (otomatik toplu seçim kimlik sorgusu yapılmaz). Bunlar test verifier callback’iyle servis sayımlarıdır; HTTP oturum doğrulamaları ve route üyelik sorguları ayrıca eklenir, HTTP sorgu sayısı ayrıca ölçülmedi. Liste başına veya apartman başına dashboard N+1 yoktur.

Ayrı servis Node sürecinde panel örnek tepe RSS 100 dairede 196,30 MiB, 1.000’de 197,05 MiB, 10.000’de 197,30 MiB; örnekler tüm süreç havuz/çalışma zamanı belleğini içerir. 10.000 ilk panelde 25 aidat ve 25 daire döner; 60.000 Prisma aidat nesnesi üretilmez. Bu tek oturumlu kanıt eşzamanlı çoklu kullanıcı kapasitesi garantisi değildir.

Son yerel doğrulamalar: ESLint, TypeScript, 24 birim, 25 PostgreSQL entegrasyon, 11 Playwright, production build, Prisma validate/generate ve temiz on migration sonrası şema karşılaştırması başarılı. Son yedek provasında 26 tablo / 477.484 satır ve indeks/constraint/trigger tanımları eşleşti; restore probe yeni panel servislerinde 10.000 kuruş tahakkuk, 6.500 brüt, 4.000 ters, 2.500 net, 7.500 kalan doğruladı. Ayrı GitHub CI sonucu PR’de kaydedilir. [Sentetik restore özeti](performance/s03e-recovery.json).

Birim, entegrasyon, mobil Playwright ve restore probe; oturum/tenant izolasyonu, finansal özet/CSV eşitliği, sayfa sınırları, kimlik ilişkileri, tüm finans/audit satırlarının değişmez hash’leri ve eski A/B/C/D yazma güvenliği kapsanır. Restore kontrolü yeni panel özet, liste ve aidat detayını da okur. Geçici geliştirme testi başarısızlıkları (bağlantı başlangıç sorgusunun sayılması, test çerezi kurulum biçimi ve başarı mesajının form remount ile kaybolması) düzeltildikten sonra testler yeniden çalıştırılır; nihai sonuçlar PR’de belirtilir.

## Kalan kapasite borçları

- Sabit sayıda servis de kullanıcı/site doğrulamasını tekrarlar; tek yetkilendirilmiş, sınırlı panel read model’i ileride sorgu sayısını azaltabilir.
- Aidat durum filtresi ve tam sayım, tüm site aidatlarının SQL bakiyelerini hesaplar. 60.000 ölçümü başarılı olsa da çok daha büyük hacim/çoklu kullanıcı için plan ve kilit bekleme profili gerekir.
- OFFSET derinliği, contains araması ve çok büyük üyelik menüleri daha yüksek hacimde ayrıca ölçülmelidir. Yeni indeks kazancı kanıtlanmadan eklenmedi.
- Eski `dashboard()`/`propertyDetails()` yardımcı API’leri geriye uyumluluk içindir; yeni çağrı noktaları bunları kullanmamalı. Sonraki temizlikte API kaldırma ayrı karardır.
- Toplu seçim state’i yenilemede kalıcı değildir; 5.000 metadata önizleme yanıtı, 5.000 transaction yazımı ve eşzamanlı büyük toplu işlem yükü ayrıca ölçülmelidir.
- Finansal raporların S03-D CSV limitleri, geçici dosya ve ihracat kilidi/disk kapasitesi sınırları aynen geçerlidir.

## PR #15 — İlk CI ve sonraki düzeltme

Yukarıdaki ilk S03-E commit’inin yerel sonuçları tarihsel olarak korunur. `45a0ca1` için push ve PR CI’ı, 10.000 dairede ikinci sayfa metninin beş saniyede değişmemesi nedeniyle başarısız oldu; CI restore adımı atlandı. Yeni düzeltme otomatik Link prefetch yükünü kaldırır ve HTTP/URL/render/farklı aidat kimliklerini ayrı doğrular. İlk/ikinci mobil panel süreleri ve yeniden çalıştırılan tam regresyon [S03E-CI-FIX](S03E-CI-FIX.md) belgesinde ayrı tutulur. Assertion veya veritabanı limitleri artırılmaz.
