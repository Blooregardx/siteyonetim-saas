# Gelir ve Gider Yönetimi — S03-C

Bu modül manuel kayıt esaslıdır; gerçek banka/kasa hesabıyla doğrulanmış hareket, banka bakiyesi veya mevzuata uygun resmî muhasebe defteri değildir. DEVELOPMENT kapsamındadır. STAGING ve PRODUCTION dağıtılmadı. v0.1.0-alpha.1 değiştirilmez; yeni release yayımlanmaz.

## Kullanım

Panelden **Gelir ve Gider Yönetimi** bağlantısını açın. Organizasyon ve apartman seçin; yeni kayıt bölümündeki apartman adını kontrol edin. Tüm apartmanlar raporunda giriş için ilk yetkili apartman açıkça gösterilir. Organizasyon değiştirirken önce apartman/kategori filtresini temizleyin.

**Kategoriler** altında başlangıç kategorilerini açık bir Kaydet işlemiyle ekleyebilirsiniz. Tekrar eklemek çoğaltmaz, pasifleri açmaz. Giderler: Elektrik, Su, Temizlik, Asansör bakım, Genel bakım ve onarım, Personel, Bahçe ve çevre düzenlemesi, Yönetim ve ofis giderleri, Diğer giderler. Diğer gelirler: Ortak alan kullanım geliri, Reklam geliri, Faiz geliri, Diğer gelirler. Apartmana özel yeni kategori eklenebilir. Aynı tür ve normalize ad tekrar kullanılamaz; pasif ad da tarihsel kimlik olarak ayrılır. Kategori adı/türü sonradan değiştirilmez; pasifleştirme geçmişi korur ve yeni kayıtlarda kullanımı durdurur.

**Diğer gelir ekle / Gider ekle** bölümünde türüne uygun kategori, YYYY-MM-DD işlem tarihi, TL tutarı, açıklama, CASH/Nakit veya TRANSFER/Havale-EFT ve isteğe bağlı referans girin. Örnek gider: Asansör bakım, 10 Kasım 2026, 3.500 TL, “Kasım ayı asansör periyodik bakımı”. Ekran türleri karıştırmaz; sunucu ve bileşik FK de aynı apartman/organizasyon/tür kategorisini doğrular.

Manuel gelir girişini aidat tahsilatı için kullanmayın. Aidat, teminat ve depozito adları manuel gelir kategorisi olarak reddedilir. Geri ödeme yükümlülüğü doğuran teminat/depozito kapsam dışıdır; açıklama değiştirerek bunları gelir saymak doğru değildir. Aidat tahsilatı yalnız mevcut tahsilat akışından girilir. Bu modül Payment satırlarını manuel tabloya kopyalamaz.

## Düzeltme ve denetim

Kaydedilmiş tutar/tür/kategori/tarih/açıklama güncellenmez; silme yoktur. Organizasyon ADMIN’i işlem geçmişinden **Manuel işlemi ters kaydet** seçer, gerekçe girer, onay kutusunu işaretler ve Kaydet der. Orijinal kayıt korunur; tek tam ters kayıt oluşturulur. Gerçek banka havalesi, nakit veya kart iadesi yapılmaz. Gerekiyorsa doğru bilgilerle ayrı yeni kayıt oluşturun. MANAGER giriş/kategori yönetimi yapabilir; ters kayıt yapamaz. RESIDENT erişemez; eski organizasyonsuz sitelerde kontrollü organizasyon eşlemesi gerekir.

Finans kayıtları oluşturulma zamanı, actorId, referans ve idempotency anahtarını saklar. Ters kayıt gerekçe/actor/zaman saklar. Her oluşturma, kategori pasifleştirme ve ters kayıt, entityId ile ilişkilendirilebilen AuditLog kaydıyla aynı transaction içindedir. Audit yazılamazsa finans kaydı da kalmaz. Tekrar gönderim aynı içeriğe aynı sonucu verir; aynı anahtar/farklı içerik reddedilir. DB unique ve immutable trigger’lar son savunmadır. Kategori anlamını değiştirmek ve finans/audit geçmişini silmek desteklenmez.

## Aylık finansal hareket raporu

Organizasyon/apartman, ay/yıl, tür, kategori ve yöntem filtrelerini kullanın. Kategori seçenekleri kayıt için seçilen apartmana aittir. Kategori seçildiğinde yalnız o manuel kategori kapsamda kalır; aidat kaynağı veya başka tür filtresiyle kesişim boş olabilir. Sayfa 25 satırdır; özetler bütün filtre kapsamını gösterir. İşlem sayıları ay içindeki orijinal manuel kayıtlardır; ters kayıtlar ayrı karşı hareket satırlarında görünür. Tablodaki negatif tutar tam ters kaydın etkisidir. Orijinalin “ters kaydedilmiş” etiketi güncel durumdur; orijinal tutar kendi ayından çıkarılmaz.

Net finansal hareket = net aidat tahsilatı + net diğer gelir − net gider. Charge aidat tahakkukudur, gerçekleşmiş nakit değildir. Örnek: 75.000 TL tahakkuk, 52.500 TL net aidat tahsilatı, 2.000 TL diğer gelir, 18.000 TL gider → toplam gelir 54.500 TL, net hareket **36.500 TL**. Kalan aidat borcu **22.500 TL** S03-B borç raporunda ayrıca görünür; mevcut nakit sayılmaz.

Bu ekran S03-B aidat dönemi borç raporunu değiştirmez. Aylık hareketler ödeme/işlem tarihine göre hesaplanır. Payment ve PaymentReversal zaman damgaları açık Europe/Istanbul dönüşümüyle gruplanır; manuel hareket kendi iş tarihindedir. Ters kayıt kendi oluşturulduğu ayda karşı hareket olur. Örneğin ekim gideri 1.000 TL, kasım ters kaydı −1.000 TL: ekim gideri 1.000 TL kalır, kasım gideri −1.000 TL olabilir. Aynı kural diğer gelir ve aidat tahsilatı için geçerlidir. Ayın son günü 23.59 ekime, sonraki 00.00/00.30 kasıma aittir; sistem TZ’si sonucu değiştirmez. Mevcut timestamp alanlarının UTC saklama sözleşmesi ve veritabanı bağlantısının UTC ayarı korunmalıdır.

## Sınırlar ve minimum izinler

Tek kayıt 1..2.147.483.647 kuruştur. Toplamlar PostgreSQL BIGINT ile hesaplanır; JS güvenli tam sayı sınırını aşan sonuç sessiz yuvarlanmaz, rapor reddedilir. Açılış bakiyesi, banka mutabakatı, hesaplar arası transfer, resmî defter, fatura, kısmi ters kayıt ve banka/kart entegrasyonu yoktur. İlk rapor yük ölçümleri S03-D belgesindedir. Daha geniş/çoklu kullanıcı yükü, derin OFFSET ve mevcut panelin tüm aidat geçmişini belleğe yüklemesi ayrı performans borcudur.

Yeni runtime izinleri: FinancialCategory/FinancialEntry/FinancialEntryReversal SELECT + INSERT, FinancialCategory UPDATE(active), FinancialEntry UPDATE(id) (yalnız satır kilidi; immutable trigger yazmayı reddeder). Bu tablolara DELETE/TRUNCATE verilmez. AuditLog INSERT + SELECT(id), Site/User/Organization mevcut kilit/okuma izinleri ve aidat kaynakları SELECT gereklidir. Kategori kimliği, Entry ve Reversal UPDATE trigger ile korunur. Runtime DDL, migration, süper kullanıcı veya rol oluşturma izni taşımaz. DB sırrı ayrı güvenlik sınırıdır; DB yetkisi uygulama ADMIN kontrolünün yerini tutmaz. Üretim rolü veya deploy bu görevde oluşturulmaz.

## S03-D raporlama eklentisi

CSV İndir, uygulanmış organizasyon/apartman/ay/tür/kategori/yöntem filtrelerinin tüm hareketlerini kapsar; sayfa filtresi uygulanmaz. Negatif ters kayıt tutarları korunur. İndirme üst sınırı 50.000 satır veya 128 MiB; aşımda filtre daraltma hatası verilir. CSV biçimi ve güvenliği [ayrı belgede](FINANCIAL-EXPORT-PERFORMANCE.md).

Aylık Karşılaştırma için Son 3/6/12 ay seçilebilir (varsayılan 6); seçilen ay dahildir. Ana raporun organizasyon/apartman/tür/kategori/yöntem filtreleri aynen uygulanır. Kategori seçiliyse aidat kaynakları kapsam dışıdır. Boş aylar sıfır; net fark önceki takvim ayına göre TL olarak gösterilir. İlk ayın farkı için bir önceki ay da sorgulanır. Yüzde ve banka bakiyesi iddiası yoktur. Negatif net/gider etkisi mümkündür. Ekrandaki aylık özet ve karşılaştırma aynı yetkilendirilmiş transaction’da okunur; başka HTTP istekleri ortak snapshot garantisi taşımaz.

Mevcut dashboard() büyük portföy provalarında zaman aşımı/stack sınırına ulaştı; sayfalanmış panel yeniden tasarımı ayrıca yapılmalıdır. Rapor/CSV iyileştirmeleri panelin kapasite borcunu kapatmaz.
