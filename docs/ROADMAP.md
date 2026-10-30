# Güncel yol haritası — OSS-04

Ücretsiz, AGPL-3.0-only, PUBLIC ve topluluk katkılı kendi sunucusunda barındırma hedefi korunur. Ticari abonelik/ücretli lisans modeli yoktur. Next.js, strict TypeScript, PostgreSQL 17 ve Prisma 6 değişmez. Üretime hazır değildir.

## Tamamlanan aşamalar

- OSS-01/01B: katkı/güvenlik belgeleri, CI sertleştirmesi; PR #7 birleşti.
- OSS-02: AGPL-3.0-only ve lisans envanteri; PR #8 birleşti.
- OSS-03: kaynak özelliklerin main'e geçişi; PR #9 birleşti. Main 55a27f1, zorunlu GitHub Actions checks etkin.
- OSS-04 yerel kanıtı: yeni konteynerlerde temiz kurulum, runtime rolüyle E2E ve ayrı PG17 hedefe sentetik yedekten dönüş. [Kanıt](OSS04-VALIDATION.md). Bu PR'nin henüz birleştiği varsayılmaz.

## Öncelik sırası

1. OSS-04 PR ve son CI'ını incele; v0.1.0-alpha.1 **kaynak kod temelli ön sürüm** adayını kullanıcı kararıyla değerlendir. Henüz release/tag yok. [Kontrol listesi](RELEASE-CHECKLIST.md).
2. Başvuru taslaklarını hesap sahibinin gerçek bilgileriyle sonlandır; kullanıcı gönderebilir. Başvuru veya kabul gerçekleşmiş sayılmaz.
3. Bağımsız kullanıcı kurulumu ve kullanılabilirlik geri bildirimi; gerçek SMTP/TLS/proxy doğrulaması. Bunlar tamamlanmadı ve ücretli sağlayıcı açma koşulu değildir.
4. Üretim güvenliği/yük/bot koruması, MFA, minimum işletim rolleri, yedek/PITR/RPO/RTO ve izleme. Sentetik restore başarısı bu işletim işlerini kapatmaz.
5. Ayrı tasarım/testlerle sayfalama ve toplu aidat önizleme/idempotency; ileride raporlama, kontrollü kişi eşleme ve ortaklık payı. Banka/kart, mobil istemci ve mesajlaşma teslim taahhüdü değildir.

Tarihsel S00/S01 raporları ve OSS-EVIDENCE aşama kayıtları korunur; güncel kapsam [FEATURES](FEATURES.md), işletim açıkları [DEFERRED-CLOUD-OPERATIONS](DEFERRED-CLOUD-OPERATIONS.md) içindedir. Finans/audit geçmişi korunur; migration kozmetik amaçla değiştirilmez.
