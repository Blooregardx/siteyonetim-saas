# Finansal CSV ve performans — S03-D

DEVELOPMENT kanıtıdır. PUBLIC/AGPL-3.0-only korunur; ücretli servis, staging/production deploy veya yeni release yoktur. S03-C PR #13 ile main’e birleşti. Başlangıç: `f8b2ff1b6857c8a1e22dae3a04704e2c8bed15b0`. Tarihsel raporlar değiştirilmedi.

## CSV biçimi, kapsam ve güvenlik

`/raporlar/csv` aidat döneminin bugünkü net borç durumudur; organizasyon, apartman, dönem, ödeme durumu, borçlu/gecikmiş filtrelerini kullanır. Aidatsız daireleri dahil etmez. `/gelir-gider/csv` ödeme/işlem tarihine göre organizasyon, apartman, ay, tür, kategori ve yöntem filtrelerini kullanır. Charge nakit değildir; Payment, PaymentReversal, FinancialEntry ve FinancialEntryReversal birer kez okunur, tablo kopyası oluşturulmaz. Reversal kendi gerçekleşme tarihinde karşı hareket olur. Manuel DATE iş tarihine timezone uygulanmaz; timestamp’ler mevcut UTC saklama sözleşmesiyle Europe/Istanbul’a çevrilir.

İki ekrandaki CSV İndir, o anda uygulanmış filtreleri taşır; sayfa ve karşılaştırma aralığı CSV’ye uygulanmaz. Kategori aidat kaynağına atanmaz: kategori seçilirse aidat satırları kapsam dışıdır. Aynı sabit veri ve filtrelerde ekran/CSV toplamları eşleşir. Yeni kayıt/ters kayıt iki ayrı HTTP isteği arasında gerçekleşirse sonuç doğal olarak değişebilir; ekran ve daha sonraki CSV ortak bir snapshot değildir.

Tutar sütunları TL’dir. UTF-8 BOM, `;` ayraç, CRLF satır sonu, ondalık virgül ve iki kuruş hanesi, binlik ayraçsız sayılar. Excel Türkçe yerel ayarıyla uyumludur; farklı yerel ayarda içe aktarırken UTF-8/noktalı virgül/ondalık virgül seçilmelidir. Metin ve başlıklar çift tırnakla çevrilir; iç `"` iki kez yazılır. Alan içi satır sonları alıntılı hücre içinde korunur. Sütun sırası kodda sabittir; dosya adları yalnız `borc-tahsilat.csv` ve `gelir-gider.csv`’dir. Filtre/kullanıcı metni dosya adına veya header’a eklenmez.

Kullanıcı metni `=`, `+`, `-`, `@` ile başlıyorsa veya bu işaretlerden önce boşluk, tab, CR/LF, Unicode kontrol/format karakteri (BOM/zero-width dahil) varsa başa apostrof eklenir. Böylece hücre formül olmaz. Bu koruma kullanıcı metnine uygulanır; güvenli tam sayı kuruştan sunucuda üretilen sayısal sütunlara uygulanmaz. Örneğin gerçek ters kayıt `-1000,00` kalır; kullanıcı metni `-1000` apostroflu metindir. Ekran para biçimleyicisi de tam lira kısmını BigInt ile biçimler, kuruş hanesini ayrı yerleştirir; güvenli sayı sınırında CSV ile bir kuruşluk float gösterim farkı oluşmaz. Sayı üretimi BigInt bölüm/kalan ile yapılır; satır değerleri ve tüm dosyanın çalışan BigInt toplamları indirme başlamadan güvenli sınırdan geçirilir, sessiz yuvarlama yoktur.

İndirme isteğinde server session, doğrulanmış e-posta ve güncel organizasyon ADMIN/MANAGER üyeliği tekrar kontrol edilir. RESIDENT, yabancı organizasyon/site/kategori reddedilir; kategori seçili siteye ait olmalıdır. Tekrarlanan veya beklenmeyen filtre anahtarları reddedilir. İstemci userId/rolü otorite değildir. Kişi/User/telefon/e-posta/kimlik sütunu veya kişiye ilişki join’i yoktur. Açıklama/gerekçe kullanıcı tarafından yazılan finans metnidir; bu alanlara gereksiz kişisel veri yazılmamalıdır, otomatik kişisel veri redaksiyonu yapılmaz.

Yanıt: `text/csv; charset=utf-8`, attachment Content-Disposition, gerçek Content-Length, `Cache-Control: private, no-store`, nosniff ve sayısal X-Export-Rows. Hata yanıtları no-store Türkçe düz metindir; oturumsuz 401, yetkisiz 403, geçersiz filtre 400, sınır aşımı 413. DB hata metni döndürülmez. Boş CSV yalnız başlık içerir; ekranda boş sonuç mesajı vardır.

## Sınır, partiler ve tutarlı okuma

En fazla **50.000 kayıt ve 128 MiB**. **1.000 satırlık FETCH partileri**. Bu seçim, aşağıdaki 21.500 hareket ölçümü ve 50.000 sınır testiyle ilk alpha için doğrulandı; production kapasite garantisi değildir. 50.001 veya byte sınırı aşılırsa dosya gönderilmez, filtre daraltma istenir.

READ COMMITTED transaction’da mevcut actor/organizationAccess (User → Organization kilit sırası) ile yetkilendirme yapılır. `DECLARE ... NO SCROLL CURSOR FOR SELECT ... COUNT(*) OVER() ... ORDER BY id` tek PostgreSQL query snapshot’ını sabitler. İlk FETCH aynı görünümdeki toplamı verir; sınır kontrolü indirme başlamadan yapılır. Sonraki FETCH’ler arada doğrudan SQL ile INSERT olsa bile aynı cursor snapshot’ını okur; atlama/tekrar yaratacak OFFSET yoktur. Borç/hareket için ayrı cursor adları Prisma prepared FETCH metadata önbelleğinin şema çakışmasını önler. PostgreSQL’in cursor/sort/materialization çalışma belleği ve gerekirse geçici diski kullanılır; bütün geçmiş JS dizisine alınmaz.

Dosya önce sunucunun özel geçici dizininde (0700), 0600 dosya izniyle tamamlanır. Herhangi bir query/yazım/sınır hatası transaction ve dosyayı temizler; HTTP başarı başlıkları ancak dosya tamamlandıktan sonra gönderilir. Commit başarısızlığında da dosya kaldırılır. İndirme yerel dosyadan backpressure ile akar; kapanma/iptalde dosya kaldırılır. Kalıcı URL, harici depolama, worker, kuyruk veya finans/audit yazımı yoktur. Ağ aktarımı kesilirse Content-Length eksikliği istemci tarafından fark edilebilir; ağ hatasını başarı garantisi olarak sunmayız.

Org kilidi dosya hazırlanırken uygulama rol/finans yazımlarını bekletebilir; ağdaki yavaş istemci süresince kilit tutulmaz. Hazırlama transaction sınırı 180 saniye, havuz beklemesi 10 saniyedir. İstemci hazırlık sırasında koparsa hesaplama hemen kesilmeyebilir; dosya hazır olduğunda abort kontrolü temizler. Süreç sert kapanırsa özel tmp artıkları işletim sistemi/operatör temizliği gerektirebilir. Bunlar herkese açık dosyalar değildir. Eşzamanlı çok sayıda export disk/havuz/kilit kapasitesini tüketebilir; daha büyük ölçek ve kota politikası sonraki aşamadır.

## Karşılaştırma ve sayfalama

Seçili ay dahil son 3/6/12 takvim ayı (varsayılan 6); bir SQL’de ay bazında gruplanır. İlk gösterilen ayın farkı için önceki ay da okunur: en fazla 13 aylık pencere. Organizasyon/apartman/tür/kategori/yöntem ana raporla aynıdır. Boş aylar sıfır, yalnız reversal ayları ve negatif gider/net hareket geçerlidir. Net = net aidat + net diğer gelir − net gider. TL farkı önceki takvim ayına göre BigInt’ten güvenli kuruşa doğrulanır; sıfır/negatif bazda yanıltıcı yüzde üretilmez.

Aylık özet + karşılaştırma aynı yetkilendirilmiş transaction/org kilidinde okunur; uygulama yazımları araya giremez. Ekran sayfaları 25 satır ve benzersiz son id ile deterministik LIMIT/OFFSET kullanmayı sürdürür. Filtre değişince sayfa sıfırlanır; geri/ileri filtreleri ve aralığı korur. Ayrı sayfa istekleri ortak snapshot değildir: araya eklenen kayıt sıralamayı kaydırabilir. İndirme bu nedenle ekran sayfalarını dolaşmaz, sabit cursor kullanır. Ölçülen derin sayfalar alpha için yeterli bulundu; sınırsız derin OFFSET performansı iddia edilmez. Büyük ölçek için ekran keyset tasarımı açık iştir.

## Sorgu değişikliği ve şema

Rapor toplamları ve görünen sayfa, tek SQL’de aynı `filtered AS MATERIALIZED` sonucunu paylaşır; önceki iki ayrı sorgunun tekrarlı agregasyonu kaldırıldı. Hareketlerde tarih/site/tür/kategori/yöntem kaynak dallarına erken uygulanır, uyumsuz aidat/manuel dalları sabit koşulla elenir. Karşılaştırma ay başına ayrı rapor çağırmak yerine PostgreSQL GROUP BY kullanır. JSON’a çevrilmiş finans sayısı veya float hesap yoktur.

Yeni indeks/migration/şema yoktur. Mevcut Charge(siteId,period), Payment/PaymentReversal site+İstanbul gün, FinancialEntry org+iş tarihi ve ilişkili FK/unique indeksleri planlarda kullanıldı. Ölçülmüş gereği olmayan indeks eklenmedi. Finans, politika ve audit tablolarının geçmişi değiştirilmez; S03-A/B/C regresyonları korunur.

## Ölçümler

[Ham süre/RSS örnekleri](performance/s03d-measurements.json), [EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)](performance/s03d-explain.json). Script: `scripts/measure-financial-reporting.ts`; yalnız localhost/127.0.0.1 PostgreSQL `siteyonetim_test`, sentetik eklemeler. Kaynak baseline doğrudan başlangıç commit’inden geçici olarak okunur; dosyalar silinir. Her yeniden çalıştırma yeni izole sentetik organizasyonlar ekler; var olan finans kayıtlarını silmez/düzeltmez. `--dashboard-only` son ölçüm portföylerinin panel servisini, `--csv-only` CSV’lerini yeni fixture eklemeden ayrıca ölçer. Baseline commit’in git nesnesi yerelde bulunmalıdır; sığ checkout’ta önce ilgili geçmiş alınmalıdır.

Ortam: Node 24.19.0, PostgreSQL 17.11 Alpine, 2 kullanılabilir CPU, shared_buffers 128 MB, work_mem 4 MB, aynı bulut çalışma alanındaki yerel Docker. Her portföyde 6 aylık aidat/tahsilat/manuel hareket, %10 ödeme ters kaydı ve %5 manuel ters kayıt; 100/1.000/10.000 daire, büyük portföyde 60.000 aidat, 60.000 tahsilat, 60.000 manuel kayıt ve ay başına 21.500 hareket. Diğer sentetik tenantlar da aynı DB’dedir.

Aşağıdakiler 3 sıcak örneğin medyan **servis wall time** değerleridir (ms); yetkilendirme/DB/Prisma dahil, HTTP/ağ/Excel hariç. Ham dosyada örnekler ve ilk çağrı da vardır. Gerçek soğuk cache ölçülmedi: fixture INSERT ve ANALYZE önbelleği ısıtır. GC/DB planner/CPU oynaklığı vardır; ayrı EXPLAIN süreleri API medyanlarıyla birebir aynı değildir. Tek sorgu planını seçip genel hız artışı iddia etmiyoruz.

| Daire | Borç ilk önce/sonra | Borç derin önce/sonra | Hareket ilk önce/sonra | Hareket derin önce/sonra | 6 ay sıralı baseline / gruplanmış |
|---|---:|---:|---:|---:|---:|
| 100 | 11,22 / 9,53 | 11,55 / 9,08 | 19,96 / 13,23 | 19,05 / 15,10 | 126,44 / 21,33 |
| 1000 | 21,26 / 14,36 | 21,09 / 14,20 | 33,46 / 19,73 | 28,74 / 22,45 | 178,18 / 75,40 |
| 10000 | 210,27 / 102,67 | 198,52 / 106,71 | 148,83 / 134,72 | 191,37 / 160,04 | 900,52 / 668,90 |

Tablo son ölçüm koşusudur: otomatik testler bittikten sonra başka test süreci çalıştırılmadan tekrarlandı. Önceki sentetik fixture’lar korunmuştur. [İlk keşif koşusunda](performance/s03d-exploratory.json) küçük portföyün hareket derin sayfası 8,39→9,06 ms ile yavaşladı; her koşuda kazanç veya aynı mutlak süre garantisi yoktur. Derin sayfa borçta yaklaşık son sayfadan bir önceki, harekette yaklaşık 20.000 satır OFFSET’tir. Karşılaştırmanın eski özelliği yoktu: baseline 6 ayrı tek-ay raporunun toplamı, yeni sorgu fark için bir ek ayı da kapsar. CSV’nin önceki uygulaması yoktu; sahte bir önce/sonra CSV kazancı belirtilmez.

| CSV | Satır | Süre ms | Boyut byte | İşlem RSS önce / gözlenen tepe MiB | Örneklenen RSS artışı MiB |
|---|---:|---:|---:|---:|---:|
| Borç (100) | 100 | 31,83 | 11935 | 105,04 / 105,54 | 0,50 |
| Hareket (100) | 215 | 32,46 | 26683 | 105,54 / 105,92 | 0,38 |
| Borç (1000) | 1000 | 91,61 | 119586 | 105,92 / 108,04 | 2,12 |
| Hareket (1000) | 2150 | 69,32 | 267648 | 108,04 / 117,42 | 9,38 |
| Borç (10000) | 10000 | 235,37 | 1214087 | 117,42 / 139,21 | 21,79 |
| Hareket (10000) | 21500 | 376,40 | 2696648 | 139,21 / 181,61 | 42,39 |

CSV, toplu taşma kontrolü dahil son kodla aynı fixture’larda `--csv-only` modunda ayrı Node sürecinde tekrar ölçüldü. RSS bütün Node sürecidir (Prisma/GC/kütüphaneler dahil), 10 ms örnekleme gerçek en yüksek anı kaçırabilir. Sunucu dosya üretim süresidir; ağ indirmesi ölçülmedi. 50.000 satır sınırı ayrı entegrasyonda tamamlandı, atlama/tekrar bitset ile denetlendi; 50.001 tüm-kapsam isteği API ve HTTP 413 düzeyinde reddedildi. 10.000 dairelik portföyün tüm 6 ayındaki 60.000 aidatı indirme isteği de EXPORT_LIMIT ile reddedildi. Ek bir bellek karşılaştırması veya production yük garantisi çıkarılmamalıdır.

### Mevcut panelin başarısız kapasite provası

Dashboard sorgusu değişmedi; geçmişi sessiz kesmek veya özetleri ilk sayfaya indirmek uygulanmadı. Panel hata ekranına bağımsız raporlara doğrudan erişim bağlantıları eklendi; bu gezinme kolaylığı sorgu kapasitesini düzeltmez. Ayrı sıcak süreçte yalnız `dashboard()` servisi ölçüldü, HTML/browser değil:

- 100 daire / 600 aidat / 600 ödeme: 62,43 ms; RSS 83,27→88,64 MiB.
- 1.000 daire / 6.000 aidat: başarısız; 5.000 ms transaction sınırı aşıldı (hata 8.845 ms bildiriyor).
- 10.000 daire / 60.000 aidat: başarısız; PostgreSQL `stack depth limit exceeded` (54001).

Bu başarısızlıklar gizlenmedi ve yapılandırma limitleri yükseltilmedi. Panel için tam finansal özetleri ayrı hesaplayan, daire/aidat/geçmişi sayfalayan ve mevcut tahsilat/ters kayıt/toplu aidat erişimini koruyan ayrı tasarım gerekir. S03-D raporlarının geçmesi panelin büyük portföye hazır olduğu anlamına gelmez.

## Sonraki aşama bağlantısı — S03-E

Yukarıdaki S03-D ölçümleri ve başarısız panel provaları tarihsel kanıttır; değerler değiştirilmedi. S03-D PR #14 ile main’e alındı. S03-E, sınırsız panel/kayıt yüklemesini ayrı okuma modelleri ve tam SQL özetleriyle ele alır. Yeni önce/sonra ölçümleri, HTTP/tarayıcı doğrulaması ve kalan sınırlar [SCALABLE-DASHBOARD](SCALABLE-DASHBOARD.md) belgesindedir. CSV, bağımsız borç/hareket raporu ve aylık karşılaştırma sorguları bu aşamada değiştirilmez.
