# F-10 — Kök neden, düzeltme ve doğrulama

Başlangıç: PR #20, `e02576f4616fcc216f7ff3aa77e4f0321ce8815a`. S03-F güvenlik düzeltmeleri ve tarihsel başarısızlık kayıtları korunur. Düzeltme ace4983 için hem push hem PR CI başarılı; alpha.2 kaynak kod hazırlığı **READY FOR MAINTAINER REVIEW**. PR kullanıcı isteğiyle taslak kalır. Son HEAD’in iki CI kapısı korunur; merge/yayımlama onayı verilmez.

## Kanıtlanan neden

Varsayılan `ALL` / borç filtresiz aidat sorgusu, 25 satırı seçmeden önce bütün kapsamın ödeme/ters kayıt bakiyesini `filtered AS MATERIALIZED` içine hesaplıyordu. 60.000 aidatta bu 60.000 tekrarlı ödeme toplamı/index okuması demekti. Sayfa 2 de aynı işi tekrar yapıyordu. Toplam satır sayısını bulmak için varsayılan listede bu bakiye hesapları gerekmiyordu.

Teşhis commit’i `0745c6271ad3ccc894488a2b08c11ea80cc0daa5` için [push](https://github.com/Blooregardx/siteyonetim-saas/actions/runs/41525819051) ve [PR](https://github.com/Blooregardx/siteyonetim-saas/actions/runs/41525826543) CI’ları 13/14 E2E ile başarısız oldu. Her ikisinde session/üyelik ve önceki okumalar bitti; `siteChargesPage` başladıktan sonra render başlamadı. PostgreSQL’de aktif kalan sorgunun MD5’i `e9cfa5bd26b8a270b8a33865592d722b`, uygulamanın bu aidat SQL’iyle birebir eşleşti. Ham SQL parametreleri loglanmadı.

| Evre (ikinci sayfa navigasyonundan itibaren) | Push teşhisi | PR teşhisi |
|---|---:|---:|
| Tarayıcı navigasyonu | 0 ms | 0 ms |
| Sunucu dispatch | 2 ms | 1 ms |
| Panel girişi | 5 ms | 3 ms |
| HTTP 200 başlıkları | 10 ms | 8 ms |
| Aidat okuma servisi başlangıcı | 243 ms | 134 ms |
| Aynı aktif SQL’in gözlenen yaşı | en az 4.756 ms | en az 4.834 ms |
| Kalıcı lock bekleme örneği | 0 | 0 |
| Render/gövde tamamlanması/25 satır | gözlem penceresinde yok | gözlem penceresinde yok |
| İstemci araması | önceki evre engelli olduğu için ulaşılmadı | önceki evre engelli olduğu için ulaşılmadı |

Başlıklar, dinamik sayfanın verisi bitmeden gönderilen HTML başlangıcına aitti. Eksik pager/DOM bu örneklerde tamamlanmayan SQL okumasının sonucuydu; yalnız Playwright lifecycle sorunu değildi. Gözlem penceresinde P2028 kaydı yoktu; daha sonra oluşmayacağı iddia edilmez. Mevcut 5 saniyelik Prisma transaction sınırı değiştirilmedi.

`EXPLAIN ANALYZE` eski sorguda 60.000 Payment/PaymentReversal lookup ve ödeme toplamı döngüsünü doğruladı. Yerel özel/genel plan örnekleri yaklaşık 1.607/1.011 ms idi; özel planda JIT maliyeti de ölçüldü. CI’ın tam planı/JIT dağılımı yakalanmadığından “tek neden generic plan/JIT/CPU” denmez. Tek tek koşuların neden farklı süre aldığı bütünüyle açıklanmış değildir. Kanıtlanan uygulama sorunu, gösterilecek 25 satır için LIMIT öncesi yapılan gereksiz bütün-kapsam bakiye işidir.

## En küçük kalıcı düzeltme

`dashboard-reads.ts` içinde:

1. Statik tenant/site/dönem/blok/daire kapsamı bir kez belirlenir.
2. Varsayılan listede tam kayıt sayısı bu kapsamdan alınır, sıralı 25 aday seçilir; ödeme/ters kayıt toplamı yalnız bu adaylar için hesaplanır.
3. Ödeme durumu veya borç filtresi varsa filtre doğru bakiyeye bağlıdır: kapsamın bakiyeleri önce hesaplanır, filtre/count bundan sonra, sayfalama en son uygulanır. Bu yolun bütün-kapsam çalışma gereği gizlenmez.
4. Organizasyonun tam finansal özeti ayrı mevcut sorgusunda kalır. Yetki, tenant, READ REPEATABLE READ, tutar hesaplama, finansal yazma/audit, CSV ve migration kodu değişmez.

Plan doğrulamasında hem özel hem genel planda toplam **60.000**, sayfa **25**, ödeme aggregate döngüsü **25**. İlk yerel plan örnekleri yaklaşık 115/115 ms; tam regresyon sonrası örnekler 115/269 ms. `verify-dashboard-query-plan.ts` aynı mevcut fixture’ı salt okunur kullanır, parametreleri yayımlamaz, her iki plan türünde 25 döngüyü ve mevcut 3 saniyelik servis hedefinden alınan sorgu bütçesini doğrular. SET/PREPARE yalnız o test bağlantısında kalır; uygulama/DB genel ayarları değişmez.

Ölçümlü düzeltme koşusunda 10.000 daire ikinci sayfa: başlık 25 ms, sunucu JSX dönüşü 309 ms, gövde tamamlanması 338 ms, 25 satır 340 ms. Geçici üretim-sunucu proxy/Prisma/SSR teşhis kancaları bu karşılaştırmadan sonra kaldırıldı. Son uygulama yolundaki değişiklik yalnız aidat okuma sorgusudur.

## Kabul ve regresyon kanıtı

Son uygulama yolunda, teşhis kancaları kapalı, aynı kapasite fixture’ları tekrar kullanılarak üç ayrı Next/Playwright worker/Chromium süreci çalıştırıldı: **4/4, 4/4, 4/4**. Bu retry/repeat-each değildir; her sonuç ayrı saklandı. Her süreçte ölçekler 100→1.000→10.000, her testte yeni browser context; DB ve OS/DB cache yeniden kullanılır. Soğuk cache veya production SLA’sı değildir.

Her ölçekte mobil 390×844: iki sayfada ayrık 25 aidat, tam URL, değişmeyen tam özet; aidat detayı, tam tutarı dolduran tahsilat butonu, ADMIN ters kayıt onayı açma/iptal ve değişmeyen finansal kayıt sayıları; toplu aidat araması, kayıt ekranı, geçersiz parametre/yabancı tenant reddi doğrulandı.

| Daire | Üç koşuda ilk panel | Üç koşuda ikinci sayfa | İstemci araması |
|---|---:|---:|---:|
| 100 | 675–744 ms | 516–545 ms | 118–199 ms |
| 1.000 | 457–575 ms | 477–525 ms | 90–97 ms |
| 10.000 | 466–528 ms | 514–715 ms | 85–140 ms |

Yerel: lint/typecheck, 25/25 birim, **29/29 entegrasyon**, 14/14 tam E2E, build, Prisma generate/validate, 11 migration/no-op deploy ve fark olmayan schema diff; Python streaming 3/3. Yeni entegrasyon, 60 aidatta ALL/PAID/PARTIAL/UNPAID × borç filtresinin bütün sayfalarını ve finans/audit hash’lerinin değişmediğini kontrol eder; toplamları sayfa büyüklüğüne indiren yanlış optimizasyonu engeller.

Sentetik restore: **26 tablo / 371.530 satır**; hash, indeks/constraint/trigger/ACL ve runtime izin eşitliği; hedefte 11 migration, 15 audit, tenant izolasyonu ve immutable finans probu geçti. Dump geçicidir; Git’e eklenmez. Bu production felaket kurtarma garantisi değildir.

[Sayısal, hassas verisiz kanıt](performance/f10-evidence.json). Son commit push/PR CI sonuçları PR açıklamasında ve nihai raporda ayrı kaydedilir. Her ikisi başarılı olmadan BLOCKED kaldırılmaz.

## Teşhis güvenliği ve sınırlar

0745c62’de sunucu ölçümü yalnız açık F10_DIAGNOSTICS bayrağı, eşit loopback DATABASE_URL/TEST_DATABASE_URL ve siteyonetim_test ile etkinleşiyordu. Nihai uygulamadan bu geçici kancalar kaldırıldı. Testte kalan opt-in CDP/DOM zaman çizelgesi ve PostgreSQL bekleme örnekleri yalnız süre/komut şekli hash’i/durum/kayıt sayısı içerir; SQL/parametre, cookie, token, parola, e-posta veya satır içeriği içermez. Ham browser trace ağ başlıkları taşıyabileceği için kullanılmadı. Olay/bekleme sayıları sınırlıdır, kesilme sayacı vardır; teşhis kaynak tüketimi sıfır değildir.

İlk teşhis JSON’undaki test status alanı finally sırasında framework sonucu henüz güncellenmeden alınmıştı; başarı kanıtı olarak kullanılmadı. Gerçek CI sonucu 13/14 idi. Bu yanıltıcı alan kaldırıldı; sonuç Playwright/GitHub’dan alınır. Önceki başarısız loglar silinmedi. Timeout artırımı, skip/fixme, retry veya assertion kaldırılması yapılmadı.

OFFSET’in eşzamanlı eklemelerde kayması, ayrı HTTP snapshot’ları, bakiye filtresinde tam kapsam hesabı ve üretim/çok kullanıcı kapasite sınırları sürer. Gerçek SMTP, bağımsız insan kurulumu, MFA ve işletim/izleme doğrulamaları bu görevle tamamlanmaz. PR #20 taslak kalır; main merge ve release/tag ayrı kullanıcı kararıdır.

## Başarılı düzeltme CI kontrol noktası

`ace4983b96b949584d382c0bae468c2e29466bbb`: [push CI](https://github.com/Blooregardx/siteyonetim-saas/actions/runs/41555386707) ve [PR CI](https://github.com/Blooregardx/siteyonetim-saas/actions/runs/41555393666) tam başarılı. İkisinde 25/25 birim, 29/29 entegrasyon, 14/14 E2E, her iki plan modunda 25 döngü, Python 3/3, 11 migration ve 26 tablo/258.298 satır restore/izin eşitliği doğrulandı. 10.000 daire ilk/ikinci panel gözlemleri push’ta 435/884 ms, PR’da 397/444 ms; karşılık gelen istemci araması 103/71 ms. Bunlar tek CI örnekleridir, üretim SLA’sı değildir.

Bu kontrol noktası sonradan oluşan dokümantasyon commit’inin CI’ı yerine kullanılmaz. Son HEAD’in gerçek iki sonucu PR açıklamasında ve nihai raporda ayrıca kaydedilir. [Güncel hazırlık kararı](ALPHA2-READINESS.md).
