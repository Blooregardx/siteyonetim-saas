# Güncel yol haritası

Ücretsiz, AGPL-3.0-only, PUBLIC ve topluluk katkılı kendi sunucusunda barındırma hedefi korunur. Ticari abonelik/ücretli lisans modeli yoktur. Next.js, strict TypeScript, PostgreSQL 17 ve Prisma 6 değişmez. Üretime hazır değildir.

## Güncel durum — 30 Ekim 2026

- [PR #10 (OSS-04)](https://github.com/Blooregardx/siteyonetim-saas/pull/10) main'e birleştirildi.
- [v0.1.0-alpha.1](https://github.com/Blooregardx/siteyonetim-saas/releases/tag/v0.1.0-alpha.1) GitHub Pre-release olarak yayımlandı; üretime hazır sürüm değildir.
- OpenAI Codex for Open Source başvurusu kullanıcı tarafından gönderildi; kabul sonucu bekleniyor. Başvuru, kabul veya destek kazanıldığı anlamına gelmez.
- S03-A toplu aidat özelliği [PR #11](https://github.com/Blooregardx/siteyonetim-saas/pull/11) ile main’e alındı (`bcab0726dde148bdc0bd166b4a50ff6a1493df87`). Mevcut v0.1.0-alpha.1 ön sürümünün parçası değildir.
- S03-B, [PR #12](https://github.com/Blooregardx/siteyonetim-saas/pull/12) ile main’e birleşti (`6798df1518e15212dd0da2bcfc6cf6f5e183b890`); Europe/Istanbul vade günü düzeltmesi dahildir.
- S03-C: gelir/gider, kategori yönetimi, immutable manuel hareket/ters kayıt ve aylık hareket raporu geliştirme dalında uygulanır; main’e birleşme ayrı inceleme gerektirir.

Güncel sonraki adım S03-C değişikliklerinin incelenmesidir. Bağımsız kurulum geri bildirimi, üretim güvenliği/işletim doğrulamaları ve kapasite ölçümü açık kalır. Yeni başvuru gönderimi veya yeni release oluşturma bu belge düzeltmesinin kapsamında değildir.

## Tarihsel OSS-04 hazırlık kaydı

Aşağıdaki tamamlanma ve öncelik listeleri OSS-04 PR'si birleşmeden, ön sürüm yayımlanmadan ve başvuru gönderilmeden önceki durumu korur. “Henüz release/tag yok”, “başvuru gerçekleşmiş sayılmaz” ve gelecekteki toplu aidat ifadeleri o aşamaya aittir; güncel bekleyen işler olarak okunmamalıdır. Main `55a27f1` referansı da tarihsel kontrol noktasıdır.

### O aşamada tamamlananlar

- OSS-01/01B: katkı/güvenlik belgeleri, CI sertleştirmesi; PR #7 birleşti.
- OSS-02: AGPL-3.0-only ve lisans envanteri; PR #8 birleşti.
- OSS-03: kaynak özelliklerin main'e geçişi; PR #9 birleşti. Main 55a27f1, zorunlu GitHub Actions checks etkin.
- OSS-04 yerel kanıtı: yeni konteynerlerde temiz kurulum, runtime rolüyle E2E ve ayrı PG17 hedefe sentetik yedekten dönüş. [Kanıt](OSS04-VALIDATION.md). Bu PR'nin henüz birleştiği varsayılmaz.

### O aşamadaki öncelik sırası

1. OSS-04 PR ve son CI'ını incele; v0.1.0-alpha.1 **kaynak kod temelli ön sürüm** adayını kullanıcı kararıyla değerlendir. Henüz release/tag yok. [Kontrol listesi](RELEASE-CHECKLIST.md).
2. Başvuru taslaklarını hesap sahibinin gerçek bilgileriyle sonlandır; kullanıcı gönderebilir. Başvuru veya kabul gerçekleşmiş sayılmaz.
3. Bağımsız kullanıcı kurulumu ve kullanılabilirlik geri bildirimi; gerçek SMTP/TLS/proxy doğrulaması. Bunlar tamamlanmadı ve ücretli sağlayıcı açma koşulu değildir.
4. Üretim güvenliği/yük/bot koruması, MFA, minimum işletim rolleri, yedek/PITR/RPO/RTO ve izleme. Sentetik restore başarısı bu işletim işlerini kapatmaz.
5. Ayrı tasarım/testlerle sayfalama ve toplu aidat önizleme/idempotency; ileride raporlama, kontrollü kişi eşleme ve ortaklık payı. Banka/kart, mobil istemci ve mesajlaşma teslim taahhüdü değildir.

Tarihsel S00/S01 raporları ve OSS-EVIDENCE aşama kayıtları korunur; güncel kapsam [FEATURES](FEATURES.md), işletim açıkları [DEFERRED-CLOUD-OPERATIONS](DEFERRED-CLOUD-OPERATIONS.md) içindedir. Finans/audit geçmişi korunur; migration kozmetik amaçla değiştirilmez.

S03-A sınırı: iki aşamalı, çakışmada tümü reddedilen toplu aidat PR #11 ile main’e birleşti. Bu çalışma mevcut alpha etiketi ve sürümü değiştirmez; yeni sürüm yayımlamaz.

S03-B aidat dönemi borç raporudur. S03-C ödeme/işlem tarihine göre aylık hareket raporunu ekler. Sonraki işler: büyük portföy kapasite ölçümü, derin sayfalama ve CSV. Mevcut panelin tüm aidat geçmişini yüklemesi ayrı performans borcudur. Kısmi ters kayıt ve üretim dağıtımı kapsam dışıdır.
