# Güncel özellik durumu

Bu belge main üzerindeki güncel alpha kapsamını anlatır. PR #9 main geçişini tamamladı; bu üretim hazırlığı anlamına gelmez. Önceki raporlar tarihsel kayıttır.

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

Gelir/gider, gelişmiş raporlar, personel, banka/kart entegrasyonu ve mobil istemci tamamlanmış özellikler değildir. STAGING/PRODUCTION ertelenmiştir. Ücretsiz kendi sunucusunda barındırma hedefi, kurulumu yapanın altyapı maliyeti olmayacağı garantisi değildir.

## OSS-02 lisans durumu

Özgün proje kodu ve belgeleri AGPL-3.0-only ile lisanslanır. Kendi sunucusunda çalıştırma, değiştirme ve lisans koşullarıyla paylaşma mümkündür. Bu hukuki/dağıtım hazırlığı yeni uygulama özelliği veya üretim onayı değildir. Ücretsiz yazılım, ücretsiz barındırma hizmeti anlamına gelmez. [Haklar ve yükümlülükler](LICENSING.md).

## OSS-04 işletim kanıtı

Temiz konteyner kurulumu ve sentetik backup/restore doğrulandı; bağımsız bir insanın kurulumu doğrulanmadı. Runtime rolüyle 4 E2E testi geçti. Gerçek SMTP teslimi, üretim güvenliği/yük testleri, MFA ve tam işletim/izleme açık. [Kanıt](OSS04-VALIDATION.md).

## S03-A — Toplu aidat

Panelde **Toplu Aidat Oluştur**: yetkili apartmanı seçin, YYYY-MM dönemini, TL tutarını ve son ödeme tarihini girin. Tüm daireler başlangıçta seçilidir; istenmeyenleri çıkarın. Önizlemede blok/daire, dönem, tutar, vade, mevcut aidat ve özet gösterilir. Önizleme aidat yazmaz. Bilgileri kontrol edip **Onayla ve aidatları oluştur** ile kesinleştirin; sonuç sayı, toplam ve dönemi gösterir. Tekil aidat ekranı korunur.

Mevcut aidatı olan tek daire bile tüm işlemi engeller; seçimden çıkarıp yeni önizleme gerekir. Değişen daire/blok/aidat bilgisi yeni önizleme gerektirir. Kısmi oluşturma, mevcut aidatı değiştirme, banka/kart işlemi yoktur. Bir işlem en fazla 5000 daire içerir; büyük portföylerde performans ölçümü sonraki aşamadır. DEVELOPMENT kapsamında; STAGING/PRODUCTION dağıtılmadı.
