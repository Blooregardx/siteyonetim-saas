# S03-E / PR #15 — Çift CI başarısızlığı düzeltmesi

İlk commit `45a0ca1621ad69aa48f64687eae21c4b19354e31` için hem [push](https://github.com/Blooregardx/siteyonetim-saas/actions/runs/41091910449) hem [pull_request](https://github.com/Blooregardx/siteyonetim-saas/actions/runs/41092060997) koşusu aynı noktada başarısız oldu: 10.000 daire / 60.000 aidat E2E’si “Sayfa 2” beklerken beş saniye sonunda “Sayfa 1 / 2400” görüyordu. Her ikisinde 10 E2E başarılıydı; önceki adımlar başarılı, restore adımı E2E yüzünden atlanmıştı. İlk commit’in yerel başarılı sonuçları GitHub CI başarısı anlamına gelmiyordu.

## Neden ve kanıt sınırı

`Pager` bağlantısı `chargesPage=2`, doğru organizasyon ve site parametrelerini üretir. `dashboardPage` bunu 2 olarak doğrular; SQL OFFSET 25’tir. Yerel eski uygulama izlemesinde URL gerçekten 2’ye geçti; ikinci sayfa bağlantısı/filtre ayrıştırmasında hata bulunmadı.

Sorun asenkron gezinme ve arka plan yükü sınırındaydı: ilk test `click()` sonrasında yalnız eski DOM etiketinin beş saniyede değişmesini bekliyordu. Gerçek navigasyon yanıtı, yanıt durumu, URL commit’i ve farklı aidat kimlikleri ayrı ayrı doğrulanmıyordu. Next Link varsayılan ön yüklemesi ise ekran kaydırılırken rapor/panel/kayıt bağlantıları için talep edilmemiş RSC istekleri çalıştırıyordu. Üç yerel 10.000 daire örneğinde tek kullanıcı gezinmesine ek **10, 19 ve 13** otomatik prefetch isteği ölçüldü; bu gereksiz sorgu ve bağlantı havuzu yüküdür.

Eski CI logları URL veya ağ zaman çizelgesi kaydetmediğinden, eski koşuda URL’nin hangi milisaniyede commit edildiği ya da her prefetch’in katkısı geriye dönük kanıtlanamaz. Logların kesin kanıtladığı nokta eski DOM’un beş saniyelik pencere içinde kalmasıdır. Ölçülmeyen CI ağ zamanları uydurulmaz. Yeni test ve ölçüm bu belirsizliği ayrı HTTP, URL, render ve veri kontrolleriyle giderir. [İlk hata ve yerel ağ kanıtı](performance/s03e-navigation.json).

## Düzeltme

Panel, kayıt, aidat detayı ve Pager bağlantıları `prefetch={false}` kullanır. Yetkili veri yalnız kullanıcı ilgili bağlantıya gittiğinde yüklenir. Sayfa/filtre anlamı ve SQL değiştirilmez. Alternatif SQL gruplaması denendi; kanıtlanmış kazanç sağlamadığı için değişiklikte tutulmadı.

Mobil (390×844) E2E, 100/1.000/10.000 daire için sırayla şunları doğrular:

1. İlk panel HTTP 200, doğru tam daire/borç özeti, 25 benzersiz aidat.
2. Sonraki href’inde doğru org/site ve chargesPage=2.
3. Prefetch olmayan gerçek GET yanıtı HTTP 200 ve geçerli RSC/HTML içerik türü (client geçişi veya doğal anchor navigasyonu). RSC stream EOF’u beklenmez; Next’in stream’i açık kalabilir, sayfa URL/DOM/veri koşullarıyla doğrulanır.
4. Tarayıcı URL’sinin 2’ye commit edilmesi ve panelin yeniden render edilmesi.
5. İkinci sayfada ilk sayfayla kesişmeyen 25 benzersiz aidat; aynı tam finansal kartlar.
6. Otomatik prefetch isteği sayısı sıfır.
7. İkinci sayfadan doğru aidat detayına geçiş; CollectionForm ve ADMIN tam ters kayıt butonuna erişim.
8. Geçersiz sayfa/filtre/tekrarlı parametre ve yabancı apartman için not-found ekranı; finans tablosu/kartı sızmaması.

Next’in stream edilmiş not-found yanıtı taşıma katmanında 200 olabildiğinden, yetkisiz/bozuk filtre kontrolü yalnız HTTP durumuna dayanmaz; gerçek reddetme ekranı ve veri yokluğu denetlenir. Başarılı ikinci sayfa için hem HTTP hem URL hem içerik şarttır.

Düzeltme geliştirilirken RSC response.finished() beklemesinin açık kalan stream nedeniyle gereksiz beklediği görüldü; bu taşıma sonu beklemesi kaldırıldı, HTTP başlıkları ve işlenmiş URL/veri doğrulanır. Beş saniyelik içerik assertion’ı, mevcut 120 saniyelik toplam büyük-fixture test bütçesi, Prisma transaction sınırı ve PostgreSQL stack sınırı artırılmadı. Skip/fixme/retry ile gizleme yoktur. Mevcut finansal yazma, tahsilat, tam ters kayıt, kısmi ödeme politikası, idempotency, audit, şema ve migration dosyaları değişmez.

## Ölçümler ve tam regresyon

`TEST_DATABASE_URL` ve `DATABASE_URL` yalnız loopback PostgreSQL 17 `siteyonetim_test` olmalıdır. Sentetik aynı fixture’lar, sıfırlama veya finans geçmişini yeniden yazma yoktur.

- `npx tsx scripts/measure-scalable-dashboard.ts --ci-fix --skip-legacy`: ilk ve ikinci panelin yedi servis çağrısını ayrı ölçer; ikinci aidat sayfasını da kaydeder.
- Aynı DB’ye bağlı local production build için `TEST_BASE_URL` ve isteğe bağlı `TEST_SERVER_PID` ile `... --ci-fix --http`: mobil ilk render/HTTP, ikinci sayfa süresi, prefetch sayısı ve Node RSS. Servis medyanı HTTP/tarayıcı süresinden ayrıdır.
- [Yeni ölçümler](performance/s03e-ci-fix-measurements.json); ilk commit’in [ölçümleri](performance/s03e-measurements.json) ve [S03-D tarihsel sonuçları](FINANCIAL-EXPORT-PERFORMANCE.md) değiştirilmez.

Son tek geçişli temiz kaynaktaki mobil tam E2E turu **11/11**; PostgreSQL entegrasyon **25/25**, birim **24/24**. Skip/retry/fixme eklenmedi.

| Daire / aidat | İlk panel servis medyanı | İkinci panel servis medyanı | Mobil tam E2E ilk panel | Mobil tam E2E ikinci sayfa |
|---|---:|---:|---:|---:|
| 100 / 600 | 52.48 ms | 48.23 ms | 407.50 ms | 141.86 ms |
| 1000 / 6000 | 92.23 ms | 93.24 ms | 409.25 ms | 192.92 ms |
| 10000 / 60000 | 563.92 ms | 560.49 ms | 866.76 ms | 767.46 ms |

Servisler üç sıcak örneğin medyanıdır; son servis ölçümü aynı sentetik fixture’ları içeren **geri yüklenmiş** PostgreSQL üzerinde yapılır ve tam özetleri yeniden doğrular. 10.000 dairede ilk ve ikinci panel servis hedefi 3 saniyenin altındadır. Eski ve yeni veri tabanlarının global fixture sayısı/önbelleği farklıdır; SQL değişmedi, yüzdelik sorgu hızlanması iddia edilmez.

| Daire | Ayrı mobil HTTP: başlık TTFB | Başlık + tablo hazır | İkinci sayfa hazır | Otomatik prefetch |
|---|---:|---:|---:|---:|
| 100 | 150.12 ms | 572.17 ms | 241.36 ms | 0 |
| 1000 | 24.82 ms | 443.33 ms | 250.05 ms | 0 |
| 10000 | 27.09 ms | 1454.29 ms | 854.12 ms | 0 |

Bu ikinci HTTP provası da geri yüklenmiş veritabanında, ayrı local production server ve yeni browser context’lerinde mobil 390×844’tür; tek gezinti/ölçek, 100→1.000→10.000 sırası, rota önbelleği giderek ısınır. 10.000’de networkidle dahil 1.685,91 ms; bu değer zorunlu sessizlik aralığını içerir. Next server örnek tepe RSS 161,41 MiB; 10 ms örnekleme kısa tepeleri kaçırabilir. Tam regresyon içindeki mobil sürelerle bu ayrı provalar farklı ölçümlerdir; ikisi de saklanır. [Mobil E2E ham sonuçları](performance/s03e-ci-fix-e2e.json).

Synthetic restore: **26 tablo / 258.067 satır**, bütün satır hash’leri ve indeks/constraint/trigger tanımları eşleşti. Restore probe tenant izolasyonu, değişmez finans/audit geçmişi ve yeni panel özet/liste/detayını doğruladı. Son kapasite ölçümü ayrıca 100/1.000/10.000 geri yüklenmiş portföylerin tam toplamlarını doğrular. [Restore kanıtı](performance/s03e-ci-fix-recovery.json).

Önceki, birçok test turuyla biriken sentetik kaynakta mevcut backup doğrulayıcısının jsonb_agg dizisi 268.435.455 bayt sınırına takıldı. Finans kayıtlarını silmek veya sınırı yükseltmek yerine yeni boş PG17 kaynağa mevcut migration’lar uygulanıp tam testler bir kez çalıştırıldı ve ayrı boş hedefe restore edildi. Eski kaynaklar korunur. Çok büyük birikmiş test/operasyonel yedekleri doğrulamak için bu aracın streaming hash tasarımı ayrı kapasite borcudur.

ESLint, TypeScript, Next production build, Prisma validate/generate ve schema diff zorunlu kontrollerdir; final sonuçlar PR’de kaydedilir. İlk iki kırmızı CI koşusu geçmişte kalır; yeni commit için push ve PR CI’ının ikisi ayrı doğrulanır.

Finansal geçmişe veya audit’e geriye dönük düzeltme yapılmaz. PUBLIC, AGPL-3.0-only ve v0.1.0-alpha.1 etiketi korunur. Yalnız DEVELOPMENT: local production build doğrulama içindir; STAGING/PRODUCTION deploy veya release yoktur. PR #15 açık kalır.

Kalan sınırlar: tek oturumlu sıcak örnekler üretim SLA’sı değildir; ortak cloud CPU/I/O ve GC oynaktır. OFFSET istekleri ortak snapshot paylaşmaz. Büyük portföyde tam SQL sayımının maliyeti ve tekrarlanan sabit yetki sorguları devam eder. Otomatik prefetch kapandığından kullanıcı tıklamasında gerçek sunucu cevabı beklenir; gecikme gizlenmez.
