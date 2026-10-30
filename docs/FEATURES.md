# Güncel özellik durumu

Bu belge geliştirme dalının güncel kod kapsamını anlatır; main'e birleştirildiği veya üretime hazır olduğu anlamına gelmez. Önceki raporlar tarihsel kayıttır.

| Alan | Uygulanmış geliştirme kapsamı | Sınır / eksik |
|---|---|---|
| Kimlik | Kayıt, giriş/çıkış, PostgreSQL oturum, e-posta doğrulama, parola kurtarma ve adres değişimi | Gerçek SMTP teslimi doğrulanmadı; MFA/oturum yönetim ekranı yok |
| Yetki | Organizasyonlar, ADMIN/MANAGER/RESIDENT, davet, rol değişimi/iptal, son admin koruması | DB sırrı uygulama yetki sınırının parçasıdır |
| Yapılar | Apartman/blok/daire oluşturma; ad/adres/açıklama ve daire kat/tür/durum düzenleme; filtreler | Silme ve blok taşıma yok |
| Kişiler | Organizasyon kapsamlı Person, ayrı Ownership ve tarihli Occupancy, çoklu daire/malik, giriş/çıkış geçmişi | Adla otomatik birleştirme, kişi adı düzenleme, ortaklık payı ve eski OWNER normalizasyonu yok |
| Finans | Aidat, nakit/havale kısmi tahsilat, idempotency, fazla ödeme reddi, tam ters kayıt ve net bakiye | Gerçek para iadesi, kısmi ters kayıt, ters kaydın düzeltmesi ve toplu borçlandırma yok |
| Audit | İşlemle aynı transaction, geçmiş koruma trigger'ları, güvenlik token temizliği | DBA yetkisi ayrı güvenlik sınırıdır; işletim arşivi/zamanlayıcı kurulmadı |
| Demo | Ayrı `/demo` sayfasında açıkça işaretli örnekler | Gerçek müşteri verisi kullanılmaz |
| Test | Birim, izole PostgreSQL entegrasyon/rol izinleri ve Playwright akışları | Başarı her commit için ayrıca kontrol edilir |

Gelir/gider, gelişmiş raporlar, personel, banka/kart entegrasyonu ve mobil istemci tamamlanmış özellikler değildir. STAGING/PRODUCTION ertelenmiştir. Ücretsiz kendi sunucusunda barındırma hedefi, kurulumu yapanın altyapı maliyeti olmayacağı garantisi değildir.
