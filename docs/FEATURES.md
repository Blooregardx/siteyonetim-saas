# Güncel özellik durumu

## S04-C — Şifreli mantıksal yedek ve korumalı güncelleme

Host operatörüne yönelik pg_dump → age akışı, atomik encrypted backup/manifest, lock, durum ve açık etkinleştirilen systemd timer/retention altyapısı eklendi. Ayrı boş/portsuz siteyonetim_test restore provası ve hata sonrası yazıcıları durduran güncelleme aracı vardır. Web kullanıcısına ham yedek veya Docker socket yetkisi verilmez. [İşletim ve anahtar rehberi](BACKUP-OPERATIONS.md), [güncelleme](SAFE-UPGRADE.md), [DEVELOPMENT doğrulaması](S04C-BACKUP-VALIDATION.md).

Bu günlük mantıksal backup kapsamıdır; WAL/PITR, anlık kurtarma ve production RPO/RTO ayrıca tasarlanıp sınanmalıdır. Anahtar kaybı yedeği açmayı engeller; fiziksel disk kaybına karşı ayrı depoda kopya gerekir. Ücretli sağlayıcı/Supabase zorunluluğu yoktur. Zamanlayıcı/silme varsayılan etkin değildir; gerçek deploy/güncelleme yapılmadı. Aşağıdaki tarihsel kanıtlar korunur.

## S04-B — Uygulama içi ilk kurulum

`/kurulum`, giriş yapmış ve e-postasını doğrulamış kullanıcı için Türkçe, mobil uyumlu başlangıç akışıdır: yönetim türü → organizasyon → ilk apartman/site → kapsamlı panel bağlantısı. Kayıt ve doğrulama mevcut ekranlardadır; SMTP olmadan doğrulama tamamlanmış sayılmaz. Panelde “İlk kuruluma başla / devam et”, doğrulama ekranında “İlk kuruluma devam et” bağlantısı vardır.

İlerleme PostgreSQL üyelik/organizasyon/site kayıtlarından türetilir; tarayıcı saklaması veya yeni setupCompleted alanı yoktur. Yenileme/yeniden giriş mevcut adımdan devam eder. Kurulum yazımlarında kullanıcı kilidi ve güncel yetki kontrolü tekrar gönderimleri tekilleştirir; normal panelin çoklu organizasyon/site oluşturması korunur. Mevcut RESIDENT ve legacy üyelikler yükseltilmez; davetliler veya mevcut kullanıcılar kuruluma zorla yönlendirilmez. Birden fazla yönetim organizasyonunda önce sitesi olmayan, sonra ID sırasındaki ilk organizasyon gösterilir; panelden kapsam seçimi ve normal işlemler korunur.

Bu akış Docker/PostgreSQL/HTTPS/SMTP kurmaz, secret göstermez veya değiştirmez. Sunucu altyapısı operatör sorumluluğundadır. Finansal kayıt veya global admin oluşturmaz. Yalnız DEVELOPMENT; [test kapsamı ve sınırlar](S04B-ONBOARDING-VALIDATION.md). S04-C güvenilir yedek işletimi ayrı aşamadır. Tarihsel kayıtlar aşağıda korunur.

## S04-A güncel karar

Supabase kullanılmayacak. Ücretsiz, PUBLIC, AGPL-3.0-only ve kendi sunucusunda kurulum önceliği korunur; ücretli servis zorunlu değildir. Sunucu/alan adı/e-posta maliyeti işletmeciye bağlıdır. Ayrı `compose.selfhost.yaml` ve [Docker kurulum rehberi](SELF-HOSTING-DOCKER.md) eklendi; `compose.yaml` geliştirme içindir. DEVELOPMENT doğrulaması üretim onayı değildir. S04-B web kurulum sihirbazı, S04-C yedek işletimi ayrı aşamalardır. Aşağıdaki eski durum raporları tarihsel bağlamıyla korunur. S04-A sonuçları S04A-VALIDATION belgesindedir.

## Güncel karar — READY FOR MAINTAINER REVIEW

Korunan `e9ed54a786ba3d33e382b6b1208241464b9c5653` commit'i normal fast-forward push ile aynı dala gönderildi; author/committer Blooregardx ve onaylı noreply adresi, eski SHA'lar değişmedi. [Push CI](https://github.com/Blooregardx/siteyonetim-saas/actions/runs/41564379171) ve [PR CI](https://github.com/Blooregardx/siteyonetim-saas/actions/runs/41564385740) tam başarılı: 25/25 birim, 29/29 entegrasyon, 14/14 E2E, build, Prisma generate/validate, temiz 11 migration/schema diff, iki query-plan modu (yalnız Charge kapsamı, 25 ödeme döngüsü), Python 3/3 ve 26 tablo/258.298 satır sentetik restore/ACL/runtime probu. 10.000 daire mobil ilk/ikinci panel push'ta 420/920 ms, PR'da 395/406 ms; üretim SLA'sı değildir.

F-10 için BLOCKED engeli bu DEVELOPMENT kontrol noktasıyla kaldırıldı. Yeni dokümantasyon HEAD'inin hem push hem PR CI'ı da başarılı olmadan bu karar merge/yayımlama için kullanılamaz; son sonuçlar PR açıklamasında doğrulanır. PR #20 **taslak ve açık** kalır. Alpha.2 tag/release veya staging/production deploy yapılmadı; kullanıcı kararı gerekir. Önceki BLOCKED/READY kayıtları aşağıda tarihsel kanıttır. [Ayrıntılı kanıt](F10-INVESTIGATION.md).

## Tarihsel yeniden açılış — 91dbba7 / BLOCKED

91dbba7 push CI 13/14 E2E ile başarısız oldu; önceki READY kontrol noktası yeniden açıldı. Charge-only kapsam ve sayfa sonrası metadata join düzeltmesi yerelde 25/29/14 ve üç bağımsız 4/4 kabul koşusunu geçti. Yeni commit’in iki CI sonucu beklenir. Aşağıdaki önceki kapanış/READY ifadeleri tarihsel kontrol noktasıdır. [Başarısızlık ve yeni kanıtlar](F10-INVESTIGATION.md). PR taslak kalır; yayın/merge yoktur.


Bu belge main’e alınmış S03-A–E kapsamını anlatır. S03-E PR #15 ile `afd7ea7bcfe693f06daeea9d48b38b8e1fe27fcc` commit’inde birleşti. S03-F yeni ürün özelliği eklemez; [güvenlik/regresyon kanıtları](S03F-SECURITY-REGRESSION.md) ve [alpha.2 hazırlığı](ALPHA2-READINESS.md) ayrı belgelenir. S03-D PR #14 ile main’e alındı. S03-C PR #13 ile main’e alındı. S03-B PR #12 ile main’e alındı. S03-A PR #11 ile main’e alındı. PR #9 main geçişini tamamladı; bu üretim hazırlığı anlamına gelmez. Önceki raporlar tarihsel kayıttır.

| Alan | Uygulanmış geliştirme kapsamı | Sınır / eksik |
|---|---|---|
| Kimlik | Kayıt, giriş/çıkış, PostgreSQL oturum, e-posta doğrulama, parola kurtarma ve adres değişimi | Gerçek SMTP teslimi doğrulanmadı; MFA/oturum yönetim ekranı yok |
| Yetki | Organizasyonlar, ADMIN/MANAGER/RESIDENT, davet, rol değişimi/iptal, son admin koruması | DB sırrı uygulama yetki sınırının parçasıdır |
| Yapılar | Apartman/blok/daire oluşturma; ad/adres/açıklama ve daire kat/tür/durum düzenleme; filtreler | Silme ve blok taşıma yok |
| Kişiler | Organizasyon kapsamlı Person, ayrı Ownership ve tarihli Occupancy, çoklu daire/malik, giriş/çıkış geçmişi | Adla otomatik birleştirme, kişi adı düzenleme, ortaklık payı ve eski OWNER normalizasyonu yok |
| Finans | Tekil ve iki aşamalı toplu aidat, nakit/havale kısmi tahsilat, idempotency, fazla ödeme reddi, tam ters kayıt ve net bakiye | Gerçek para iadesi, kısmi ters kayıt, ters kaydın düzeltmesi yok |
| Audit | İşlemle aynı transaction, geçmiş koruma trigger'ları, güvenlik token temizliği | DBA yetkisi ayrı güvenlik sınırıdır; işletim arşivi/zamanlayıcı kurulmadı |
| Demo | Ayrı `/demo` sayfasında açıkça işaretli örnekler | Gerçek müşteri verisi kullanılmaz |
| Test | Birim, izole PostgreSQL entegrasyon/rol izinleri ve Playwright akışları | Başarı her commit için ayrıca kontrol edilir |

Gelişmiş muhasebe raporları, personel, banka/kart entegrasyonu ve mobil istemci tamamlanmış özellikler değildir. STAGING/PRODUCTION ertelenmiştir. Ücretsiz kendi sunucusunda barındırma hedefi, kurulumu yapanın altyapı maliyeti olmayacağı garantisi değildir.

## OSS-02 lisans durumu

Özgün proje kodu ve belgeleri AGPL-3.0-only ile lisanslanır. Kendi sunucusunda çalıştırma, değiştirme ve lisans koşullarıyla paylaşma mümkündür. Bu hukuki/dağıtım hazırlığı yeni uygulama özelliği veya üretim onayı değildir. Ücretsiz yazılım, ücretsiz barındırma hizmeti anlamına gelmez. [Haklar ve yükümlülükler](LICENSING.md).

## OSS-04 işletim kanıtı

Temiz konteyner kurulumu ve sentetik backup/restore doğrulandı; bağımsız bir insanın kurulumu doğrulanmadı. Runtime rolüyle 4 E2E testi geçti. Gerçek SMTP teslimi, üretim güvenliği/yük testleri, MFA ve tam işletim/izleme açık. [Kanıt](OSS04-VALIDATION.md).

## S03-A — Toplu aidat (main’e alındı)

Panelde **Toplu Aidat Oluştur**: yetkili apartmanı seçin, YYYY-MM dönemini, TL tutarını ve son ödeme tarihini girin. En fazla 5.000 daireli apartmanda tüm daireler başlangıçta seçilidir; daha büyük apartmanda seçim boş başlar. Arama ve sayfalarla seçim yapın; seçilenleri inceleyin. Önizlemede blok/daire, dönem, tutar, vade, mevcut aidat ve özet gösterilir. Önizleme aidat yazmaz. Bilgileri kontrol edip **Onayla ve aidatları oluştur** ile kesinleştirin; sonuç sayı, toplam ve dönemi gösterir. Tekil aidat ekranı korunur.

Mevcut aidatı olan tek daire bile tüm işlemi engeller; seçimden çıkarıp yeni önizleme gerekir. Değişen daire/blok/aidat bilgisi yeni önizleme gerektirir. Kısmi oluşturma, mevcut aidatı değiştirme, banka/kart işlemi yoktur. Bir işlem en fazla 5000 daire içerir. S03-E, checkbox ve önizleme tablosunu 25’lik gösterir; büyük yazım transaction’ının ayrı yük provası açık kalır. DEVELOPMENT kapsamında; STAGING/PRODUCTION dağıtılmadı.

## S03-B — Borç/tahsilat raporları ve ödeme politikası

Panelde **Borç ve Tahsilat Raporları** bağlantısı; yetkili organizasyon/apartman, aidat dönemi, ödeme durumu, borç ve vade filtreleri. Ödenmedi/kısmi/tam ödeme ile vade durumu ayrı değerlendirilir. Aidatsız daireler borçlu sayılmaz. Sayfa 25 aidattır; dokuz özet kartı bütün filtre kapsamını gösterir. Kişisel bilgiler rapora alınmaz. Aidat dönemi raporu bugünkü net borcu gösterir; ödeme tarihine göre muhasebe/nakit akışı değildir.

**Tahsilat Ayarları → Kısmi Ödeme Kabulü** varsayılan açık; yalnız doğrulanmış organizasyon ADMIN’i değiştirebilir. MANAGER mevcut politikayı görür. Kapatıldığında yeni ödeme güncel kalan borcun tamamı olmalıdır; eski ödemeler/ters kayıtlar korunur. **Kalan Borcun Tamamını Tahsil Et** tutarı doldurur; bu seçimde bakiye değişmişse sunucu yeni kontrol ister. [Kullanım ve sınırlar](REPORTS-PAYMENT-POLICY.md).

## S03-C — Gelir ve Gider Yönetimi

Panel menüsünden manuel gider/aidat dışı gelir, apartmana özel tür ayrımlı kategoriler, işlem geçmişi ve aylık finans özeti. Varsayılan kategoriler açık kullanıcı işlemiyle eklenir; otomatik production seed yoktur. Kullanılan kategorilerin anlamı değiştirilemez, kategoriler pasifleştirilebilir. Manuel kayıtlar ve ters kayıtlar append-only; gerekçeli/onaylı ters kayıt yalnız organizasyon ADMIN’i, giriş ADMIN/MANAGER tarafından yapılır.

Rapor Payment ve PaymentReversal kaynaklarını okur, aidat tahsilatını manuel gelire kopyalamaz. Charge nakit sayılmaz. Ters kayıt kendi ayına karşı hareket olarak yazılır. Europe/Istanbul zaman damgası gruplaması, açık manuel iş tarihi, sunucuda 25 satır ve tam filtre toplamları. [Kullanım ve sınırlamalar](INCOME-EXPENSES.md). Banka bakiyesi, resmî muhasebe, depozito/teminat veya açılış bakiyesi modülü değildir.

## S03-D — CSV, karşılaştırma ve rapor performansı

İki raporda filtre kapsamının tamamını içeren, sunucuda yeniden yetkilendirilen CSV. UTF-8 BOM, noktalı virgül, ondalık virgül; kullanıcı metninde formula injection koruması, sunucu sayılarında doğru negatif tutar. En fazla 50.000 kayıt/128 MiB, 1.000 satırlık cursor partileri, özel geçici dosya ve no-store indirme. 3/6/12 aylık karşılaştırma (varsayılan 6), boş aylar sıfır, önceki aya TL farkı; ana raporun kapsam filtreleri aynıdır. İşlem kaynakları, ters kayıt tarihi ve Istanbul sözleşmesi korunur.

Rapor toplamı ve sayfası tek SQL içinde aynı filtrelenmiş CTE’yi paylaşır; karşılaştırma PostgreSQL’de gruplanır. Şema/indeks/migration değişmedi. S03-D aşamasındaki büyük panel akışı S03-E’nin ayrı kapsamıdır; yük provalarındaki başarısızlıklar dahil [ölçümler](FINANCIAL-EXPORT-PERFORMANCE.md) belgelenmiştir. CSV ve özetler banka bakiyesi veya resmî muhasebe değildir.

## S03-E — Tam özetli, sayfalı yönetim paneli

Organizasyonun tüm apartman/daire sayısı ve aidat tahakkuk, brüt/ters/net tahsilat, kalan borcu PostgreSQL üzerinden hesaplanır. Listeler 25 kayıt; kartlar yalnız sayfa satırlarından oluşmaz. Apartman araması, daire blok/numara/kat/tür/durum filtreleri, aidat dönem/blok/daire/durum/borç filtreleri ve bütün geçmişe sayfalı erişim vardır. Tahsilat ve ADMIN tam ters kayıt aidat detayındadır; mevcut CollectionForm ve finansal yazma kuralları korunur.

Kayıt ekranında blok/daire/kişi arama ve sayfaları, seçili dairenin ilişki geçmişi vardır; bütün organizasyon ilişkileri bir defada yüklenmez. Toplu aidat seçimleri form açıkken sayfalar arasında korunur; en fazla 5.000, küçük apartmanda varsayılan tüm seçim, büyük apartmanda açık boş seçim. Sunucu önizleme/hash/idempotency/atomiklik kuralları değişmez.

Yeni read modelleri kısa tutarlı transaction kullanır; ayrı sayfalar arasında snapshot garantisi yoktur. OFFSET derinliği ölçülür; eski sınırsız yardımcılar geriye uyumluluk için korunur fakat canlı ekranlarda kullanılmaz. [Kullanım, ölçümler ve açık sınırlar](SCALABLE-DASHBOARD.md).

## F-10 — Sınırlı aidat sayfası hesabı

Varsayılan filtresiz aidat listesinde tam kapsam sayılır; ödeme/ters kayıt toplamları sayfanın 25 adayı için hesaplanır. Bakiye/durum filtresinde doğru filtre ve toplam için bütün kapsam hesabı korunur; organizasyonun tam özeti değişmez. 10.000 daire/60.000 aidat, üç bağımsız mobil kabul koşusu ve ace4983’in iki tam CI akışı başarılı. [Ölçüm ve sınırlar](F10-INVESTIGATION.md). Bu production kapasite/SLA veya yayımlama onayı değildir.
