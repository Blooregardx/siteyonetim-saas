# Güncel özellik durumu

Bu belge S03-C geliştirme dalının kapsamını anlatır; S03-C henüz main’e birleşmiş sayılmaz. S03-B PR #12 ile main’e alındı. S03-A PR #11 ile main’e alındı. PR #9 main geçişini tamamladı; bu üretim hazırlığı anlamına gelmez. Önceki raporlar tarihsel kayıttır.

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

Panelde **Toplu Aidat Oluştur**: yetkili apartmanı seçin, YYYY-MM dönemini, TL tutarını ve son ödeme tarihini girin. Tüm daireler başlangıçta seçilidir; istenmeyenleri çıkarın. Önizlemede blok/daire, dönem, tutar, vade, mevcut aidat ve özet gösterilir. Önizleme aidat yazmaz. Bilgileri kontrol edip **Onayla ve aidatları oluştur** ile kesinleştirin; sonuç sayı, toplam ve dönemi gösterir. Tekil aidat ekranı korunur.

Mevcut aidatı olan tek daire bile tüm işlemi engeller; seçimden çıkarıp yeni önizleme gerekir. Değişen daire/blok/aidat bilgisi yeni önizleme gerektirir. Kısmi oluşturma, mevcut aidatı değiştirme, banka/kart işlemi yoktur. Bir işlem en fazla 5000 daire içerir; büyük portföylerde performans ölçümü sonraki aşamadır. DEVELOPMENT kapsamında; STAGING/PRODUCTION dağıtılmadı.

## S03-B — Borç/tahsilat raporları ve ödeme politikası

Panelde **Borç ve Tahsilat Raporları** bağlantısı; yetkili organizasyon/apartman, aidat dönemi, ödeme durumu, borç ve vade filtreleri. Ödenmedi/kısmi/tam ödeme ile vade durumu ayrı değerlendirilir. Aidatsız daireler borçlu sayılmaz. Sayfa 25 aidattır; dokuz özet kartı bütün filtre kapsamını gösterir. Kişisel bilgiler rapora alınmaz. Aidat dönemi raporu bugünkü net borcu gösterir; ödeme tarihine göre muhasebe/nakit akışı değildir.

**Tahsilat Ayarları → Kısmi Ödeme Kabulü** varsayılan açık; yalnız doğrulanmış organizasyon ADMIN’i değiştirebilir. MANAGER mevcut politikayı görür. Kapatıldığında yeni ödeme güncel kalan borcun tamamı olmalıdır; eski ödemeler/ters kayıtlar korunur. **Kalan Borcun Tamamını Tahsil Et** tutarı doldurur; bu seçimde bakiye değişmişse sunucu yeni kontrol ister. [Kullanım ve sınırlar](REPORTS-PAYMENT-POLICY.md).

## S03-C — Gelir ve Gider Yönetimi

Panel menüsünden manuel gider/aidat dışı gelir, apartmana özel tür ayrımlı kategoriler, işlem geçmişi ve aylık finans özeti. Varsayılan kategoriler açık kullanıcı işlemiyle eklenir; otomatik production seed yoktur. Kullanılan kategorilerin anlamı değiştirilemez, kategoriler pasifleştirilebilir. Manuel kayıtlar ve ters kayıtlar append-only; gerekçeli/onaylı ters kayıt yalnız organizasyon ADMIN’i, giriş ADMIN/MANAGER tarafından yapılır.

Rapor Payment ve PaymentReversal kaynaklarını okur, aidat tahsilatını manuel gelire kopyalamaz. Charge nakit sayılmaz. Ters kayıt kendi ayına karşı hareket olarak yazılır. Europe/Istanbul zaman damgası gruplaması, açık manuel iş tarihi, sunucuda 25 satır ve tam filtre toplamları. [Kullanım ve sınırlamalar](INCOME-EXPENSES.md). Banka bakiyesi, resmî muhasebe, depozito/teminat veya açılış bakiyesi modülü değildir.
