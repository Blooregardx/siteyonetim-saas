# v0.1.0-alpha.1 — sürüm notu taslağı

**EARLY DEVELOPMENT / ALPHA — NOT PRODUCTION READY**

Yayımlanmadı. Tag, GitHub Release, binary veya konteyner oluşturulmadı/yayımlanmadı. Kullanıcı onayı gerekir. Başlangıç kodu main `55a27f18ed4c014f1b3044db6e181382879d38f2`; nihai aday bu OSS-04 PR'sinin onaylanacak commitidir. Bakımcı Blooregardx; lisans AGPL-3.0-only.

## Dağıtım önerisi

İlk aday yalnız kaynak kod temelli GitHub ön sürümü olmalıdır: onaylanan commitin kaynak arşivi ve bu notlar. node_modules, .next, çalıştırılabilir dosya, Docker imajı, veritabanı yedeği, fixture, gerçek .env veya sağlayıcı bilgisi eklenmez. Başlangıç package.json sürümü 0.1.0 idi; bu PR paket ve lock kökünü 0.1.0-alpha.1 adayına eşitler. Bu bir yayın işlemi değildir. SemVer'de alpha.1, 0.1.0 kararlı sürümünden önce gelir; önceki 0.1.0 metaverisi kararlı ürün veya yayımlanmış release kanıtı değildi.

## Uygulanmış kapsam

- Kayıt/giriş/çıkış, PostgreSQL oturumları, e-posta doğrulama/adres değişimi ve parola kurtarma kodu.
- Organizasyonlar, ADMIN/MANAGER/RESIDENT modeli, davet ve üyelik/rol yönetimi.
- Apartman/blok/daire oluşturma, düzenleme ve filtreler; Person, çoklu malik ve tarihli kiracı ilişkileri.
- Aidat, nakit/havale kısmi tahsilat, idempotency/fazla ödeme reddi; tam ters kayıt, net bakiye ve korunmuş finans geçmişi. Gerçek banka iadesi değildir.
- Transaction içi audit, tenant kapsamı, finans/audit değişmezlik korumaları, ayrı örnek demo.
- Yedi eklemeli migration; birim, PostgreSQL entegrasyon ve tarayıcı testleri.

## Doğrulama ve sınırlar

[OSS-04 kanıtı](OSS04-VALIDATION.md): temiz Node/PostgreSQL konteynerleriyle aynı geliştirici tarafından otomatik kurulum provası; sentetik SMTP; runtime rolüyle E2E; ayrı boş PostgreSQL hedefinde geri yükleme ve veri hash karşılaştırması. Bu, bağımsız bir insan kullanıcının kurulum testi değildir. Production build yalnız yerel testte çalıştırıldı; canlı deploy yapılmadı.

## Açık eksikler

Gerçek SMTP teslim doğrulaması; bağımsız kullanıcı kurulumu; gerçek işletim yedeği/PITR/afet kurtarma ve hedef RPO/RTO; üretim güvenliği/yük testleri; MFA; tam işletim/izleme/alarmlar. İzole yedekten dönüş provası başarılı olsa da üretim yedeklemesi tamamlanmış sayılmaz. Oturum yönetim ekranı, toplu borçlandırma, kısmi ters kayıt ve gerçek para iadesi yoktur.

Eski hesaplar otomatik doğrulanmaz; eski siteler otomatik organizasyona atanmaz. Güncellemeden önce yedek ve izole yükseltme provası gerekir. Veriyi reset/seed ile düzeltmeyin. [Veritabanı](DATABASE.md), [kurulum](SELF-HOSTING.md), [kurtarma](BACKUP-RESTORE.md).

Üçüncü taraf lisansları korunur. Binary/konteyner dağıtımı bu adayın kapsamı değildir; ilgili kaynak/NOTICE/LGPL yükümlülükleri ayrıca tamamlanmalıdır. Ücretsiz yazılım, ücretsiz sunucu/SMTP hizmeti değildir. [Yayın kapısı](RELEASE-CHECKLIST.md).
