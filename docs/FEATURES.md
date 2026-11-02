# Güncel özellik durumu

Bu belge S03-E geliştirme dalının kapsamını anlatır; S03-E henüz main’e birleşmiş sayılmaz. S03-D PR #14 ile main’e alındı. S03-C PR #13 ile main’e alındı. S03-B PR #12 ile main’e alındı. S03-A PR #11 ile main’e alındı. PR #9 main geçişini tamamladı; bu üretim hazırlığı anlamına gelmez. Önceki raporlar tarihsel kayıttır.

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
