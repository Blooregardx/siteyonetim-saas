# Borç raporları ve kısmi ödeme politikası — S03-B

Panelde Borç ve Tahsilat Raporları bağlantısını açın. Organizasyon seçin; apartman filtresi boşsa o organizasyonun yetkili tüm apartmanları kapsanır. Başka organizasyona geçerken apartman seçimini temizleyin. Dönem, ödeme durumu, borç ve vade filtreleri birlikte uygulanır. Özetler filtrelerin tamamına aittir; sayfa 25 satırdır. Aidatsız daireler borç oluşturmaz; borçlu daire sayısı aynı daireyi bir kez sayar. Rapor kişi adı veya iletişim bilgisi içermez.

Dönem, aidatın dönemidir: bugün bilinen tahsilat/ters kayıtlar hesaba katılır. Bu ekran ödeme tarihiyle muhasebe/nakit akışı veya geçmiş tarihli bakiye raporu değildir. Vade UTC takvim gününe göre hesaplanır; vade gününde gecikmiş sayılmaz. Kısmi ödenmiş bir aidat ayrıca gecikmiş olabilir.

Örnek: 2.000 TL aidat ve 750 TL tahsilatta net 750 TL, kalan 1.250 TL. 750 TL tahsilatın tamamı ters kaydedilirse net 0 TL, kalan 2.000 TL. Kısmi ters kayıt desteklenmez.

Tahsilat Ayarları yalnız doğrulanmış organizasyon ADMIN’i tarafından değiştirilebilir. MANAGER görüntüler ve tahsilat yapabilir; RESIDENT yapamaz. Organizasyonsuz legacy apartmanlarda ayar değişikliği için önce kontrollü organizasyon eşlemesi gerekir; doğrudan apartman ADMIN üyeliği bu yetkiyi genişletmez.

Kısmi Ödeme Kabulü başlangıçta açıktır. Kapalıyken yeni tahsilat tam kalan tutar olmalıdır: 1.500 TL aidata 500 veya 1.000 TL reddedilir; 1.500 TL kabul edilir. Önceden 500 TL ödenmişse kalan 1.000 TL'nin tamamı kabul edilir. Önceki ödeme ve ters kayıtlar değiştirilmez. Fazla ödeme ve ödenmiş aidata ikinci tahsilat her durumda reddedilir.

Kalan Borcun Tamamını Tahsil Et düğmesi tutarı doldurur; Kaydet kesinleştirir. Bakiye bu arada değişmişse sunucu işlemi durdurur; sayfayı yenileyip yeni tutarı kontrol edin. Kısmi ödeme kapalıyken tutar salt okunurdur; istemciyi değiştirmek sunucu politikasını aşamaz. Başarılı işlem rapor ve panel önbelleğini yeniler.

## İşletim ve sınırlar

Yeni migration uygulandıktan sonra kısıtlı runtime rolünün Site satır kilidi için UPDATE ayrıcalığı gerekir; yalnız UPDATE(partialPaymentsAllowed) verilebilir. Politika işlemi için PaymentPolicyChange SELECT/INSERT, AuditLog INSERT + SELECT(id) gerekir; bu tablolarda UPDATE/DELETE/TRUNCATE verilmez. Rapor için Charge, Payment, PaymentReversal, Site, Unit ve Block SELECT gerekir. Mevcut User/Organization/Charge/Payment kilit izinleri korunur. DB sırrı uygulama yetki sınırının parçasıdır; DB yetkisi uygulama ADMIN kontrolünün yerini tutmaz. Bu görev üretim rolü veya deploy oluşturmaz.

Rapor tablo satırları sunucuda sayfalanır; tüm ödeme geçmişi istemciye yüklenmez. Toplam sorgusu filtre kapsamının tamamını işler; büyük portföy yük ölçümü ve derin OFFSET iyileştirmesi sonraki aşamadır. Mevcut panelin genel geçmiş görünümü için ayrıca kapasite çalışması gerekir. CSV dışa aktarım, ödeme tarihine göre rapor, banka/kart, kısmi ters kayıt ve finans silme eklenmedi. DEVELOPMENT kapsamında; STAGING/PRODUCTION ertelendi. v0.1.0-alpha.1 etiketi değiştirilmez, yeni release yayımlanmaz.
