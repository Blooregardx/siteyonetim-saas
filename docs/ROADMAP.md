# Güncel yol haritası

## S04-D güncel durum — kaynak dağıtımı adayı

GitHub denetiminde [PR #20](https://github.com/Blooregardx/siteyonetim-saas/pull/20) (S03-F), [#21](https://github.com/Blooregardx/siteyonetim-saas/pull/21) (S04-A), [#22](https://github.com/Blooregardx/siteyonetim-saas/pull/22) (S04-B) ve [#23](https://github.com/Blooregardx/siteyonetim-saas/pull/23) main'e **birleşmiş** durumdadır (3 Kasım 2026). Aşağıdaki önceki taslak/açık ifadeleri yalnız tarihsel kontrol noktalarıdır; güncel PR durumu değildir.

Güncel giriş [adım adım kurulum](COMMUNITY-INSTALLATION.md); source archive/temiz otomatik prova [S04-D doğrulamasında](S04D-DISTRIBUTION-VALIDATION.md). Bağımsız üçüncü taraf insan kurulumu yapılmadı. Alpha.2 yalnız aday; yayımlanmış tek sürüm v0.1.0-alpha.1, package/lock 0.1.0-alpha.1 kalır. Sürüm/tag/registry/deploy oluşturulmaz. **SOURCE RELEASE READINESS:** son HEAD testleri ve bakımcı incelemesi kapısı. **BINARY DISTRIBUTION READINESS: BLOCKED FOR BINARY DISTRIBUTION**; LGPL/MPL/temel imaj kaynak ve bildirim kanıtı eksik.

## Önceki geliştirme kayıtları — tarihsel bağlam

## S04-C — Şifreli mantıksal yedek ve korumalı güncelleme

Host operatörüne yönelik pg_dump → age akışı, atomik encrypted backup/manifest, lock, durum ve açık etkinleştirilen systemd timer/retention altyapısı eklendi. Ayrı boş/portsuz siteyonetim_test restore provası ve hata sonrası yazıcıları durduran güncelleme aracı vardır. Web kullanıcısına ham yedek veya Docker socket yetkisi verilmez. [İşletim ve anahtar rehberi](BACKUP-OPERATIONS.md), [güncelleme](SAFE-UPGRADE.md), [DEVELOPMENT doğrulaması](S04C-BACKUP-VALIDATION.md).

Bu günlük mantıksal backup kapsamıdır; WAL/PITR, anlık kurtarma ve production RPO/RTO ayrıca tasarlanıp sınanmalıdır. Anahtar kaybı yedeği açmayı engeller; fiziksel disk kaybına karşı ayrı depoda kopya gerekir. Ücretli sağlayıcı/Supabase zorunluluğu yoktur. Zamanlayıcı/silme varsayılan etkin değildir; gerçek deploy/güncelleme yapılmadı. Aşağıdaki tarihsel kanıtlar korunur.

## S04-B — Uygulama içi ilk kurulum (bakımcı incelemesine hazır)

`/kurulum`, giriş yapmış ve e-postasını doğrulamış kullanıcı için Türkçe, mobil uyumlu başlangıç akışıdır: yönetim türü → organizasyon → ilk apartman/site → kapsamlı panel bağlantısı. Kayıt ve doğrulama mevcut ekranlardadır; SMTP olmadan doğrulama tamamlanmış sayılmaz. Panelde “İlk kuruluma başla / devam et”, doğrulama ekranında “İlk kuruluma devam et” bağlantısı vardır.

İlerleme PostgreSQL üyelik/organizasyon/site kayıtlarından türetilir; tarayıcı saklaması veya yeni setupCompleted alanı yoktur. Yenileme/yeniden giriş mevcut adımdan devam eder. Kurulum yazımlarında kullanıcı kilidi ve güncel yetki kontrolü tekrar gönderimleri tekilleştirir; normal panelin çoklu organizasyon/site oluşturması korunur. Mevcut RESIDENT ve legacy üyelikler yükseltilmez; davetliler veya mevcut kullanıcılar kuruluma zorla yönlendirilmez. Birden fazla yönetim organizasyonunda önce sitesi olmayan, sonra ID sırasındaki ilk organizasyon gösterilir; panelden kapsam seçimi ve normal işlemler korunur.

Bu akış Docker/PostgreSQL/HTTPS/SMTP kurmaz, secret göstermez veya değiştirmez. Sunucu altyapısı operatör sorumluluğundadır. Finansal kayıt veya global admin oluşturmaz. Yalnız DEVELOPMENT; [test kapsamı ve sınırlar](S04B-ONBOARDING-VALIDATION.md). S04-C güvenilir yedek işletimi ayrı aşamadır. Tarihsel kayıtlar aşağıda korunur.

## S04-A güncel karar

Supabase kullanılmayacak. Ücretsiz, PUBLIC, AGPL-3.0-only ve kendi sunucusunda kurulum önceliği korunur; ücretli servis zorunlu değildir. Sunucu/alan adı/e-posta maliyeti işletmeciye bağlıdır. Ayrı `compose.selfhost.yaml` ve [Docker kurulum rehberi](SELF-HOSTING-DOCKER.md) eklendi; `compose.yaml` geliştirme içindir. DEVELOPMENT doğrulaması üretim onayı değildir. S04-B web kurulum sihirbazı, S04-C yedek işletimi ayrı aşamalardır. Aşağıdaki eski durum raporları tarihsel bağlamıyla korunur. S04-A sonuçları S04A-VALIDATION belgesindedir.

## Güncel karar — READY FOR MAINTAINER REVIEW

Korunan `e9ed54a786ba3d33e382b6b1208241464b9c5653` commit'i normal fast-forward push ile aynı dala gönderildi; author/committer Blooregardx ve onaylı noreply adresi, eski SHA'lar değişmedi. [Push CI](https://github.com/Blooregardx/siteyonetim-saas/actions/runs/41564379171) ve [PR CI](https://github.com/Blooregardx/siteyonetim-saas/actions/runs/41564385740) tam başarılı: 25/25 birim, 29/29 entegrasyon, 14/14 E2E, build, Prisma generate/validate, temiz 11 migration/schema diff, iki query-plan modu (yalnız Charge kapsamı, 25 ödeme döngüsü), Python 3/3 ve 26 tablo/258.298 satır sentetik restore/ACL/runtime probu. 10.000 daire mobil ilk/ikinci panel push'ta 420/920 ms, PR'da 395/406 ms; üretim SLA'sı değildir.

F-10 için BLOCKED engeli bu DEVELOPMENT kontrol noktasıyla kaldırıldı. Yeni dokümantasyon HEAD'inin hem push hem PR CI'ı da başarılı olmadan bu karar merge/yayımlama için kullanılamaz; son sonuçlar PR açıklamasında doğrulanır. Bu kontrol noktasında PR #20 taslak/açıktı; yukarıdaki S04-D denetiminde birleşmiş olduğu doğrulandı. Alpha.2 tag/release veya staging/production deploy yapılmadı; kullanıcı kararı gerekir. Önceki BLOCKED/READY kayıtları aşağıda tarihsel kanıttır. [Ayrıntılı kanıt](F10-INVESTIGATION.md).

## Tarihsel yeniden açılış — 91dbba7 / BLOCKED

91dbba7 push CI 13/14 E2E ile başarısız oldu; önceki READY kontrol noktası yeniden açıldı. Charge-only kapsam ve sayfa sonrası metadata join düzeltmesi yerelde 25/29/14 ve üç bağımsız 4/4 kabul koşusunu geçti. Yeni commit’in iki CI sonucu beklenir. Aşağıdaki önceki kapanış/READY ifadeleri tarihsel kontrol noktasıdır. [Başarısızlık ve yeni kanıtlar](F10-INVESTIGATION.md). PR taslak kalır; yayın/merge yoktur.


Ücretsiz, AGPL-3.0-only, PUBLIC ve topluluk katkılı kendi sunucusunda barındırma hedefi korunur. Ticari abonelik/ücretli lisans modeli yoktur. Next.js, strict TypeScript, PostgreSQL 17 ve Prisma 6 değişmez. Üretime hazır değildir.

## Güncel durum — S03-F / 2 Kasım 2026

- [PR #10 (OSS-04)](https://github.com/Blooregardx/siteyonetim-saas/pull/10) main'e birleştirildi.
- [v0.1.0-alpha.1](https://github.com/Blooregardx/siteyonetim-saas/releases/tag/v0.1.0-alpha.1) GitHub Pre-release olarak yayımlandı; üretime hazır sürüm değildir.
- OpenAI Codex for Open Source başvurusu kullanıcı tarafından gönderildi; kabul sonucu bekleniyor. Başvuru, kabul veya destek kazanıldığı anlamına gelmez.
- S03-A toplu aidat özelliği [PR #11](https://github.com/Blooregardx/siteyonetim-saas/pull/11) ile main’e alındı (`bcab0726dde148bdc0bd166b4a50ff6a1493df87`). Mevcut v0.1.0-alpha.1 ön sürümünün parçası değildir.
- S03-B, [PR #12](https://github.com/Blooregardx/siteyonetim-saas/pull/12) ile main’e birleşti (`6798df1518e15212dd0da2bcfc6cf6f5e183b890`); Europe/Istanbul vade günü düzeltmesi dahildir.
- S03-C, [PR #13](https://github.com/Blooregardx/siteyonetim-saas/pull/13) ile main’e birleşti (`f8b2ff1b6857c8a1e22dae3a04704e2c8bed15b0`).
- S03-D, [PR #14](https://github.com/Blooregardx/siteyonetim-saas/pull/14) ile main’e birleşti (`33169af14ea0a2fd898838839cc8eb7772a31e09`): güvenli CSV, aylık karşılaştırma ve sentetik rapor ölçümleri.
- S03-E [PR #15](https://github.com/Blooregardx/siteyonetim-saas/pull/15) ile main’e birleşti (`afd7ea7bcfe693f06daeea9d48b38b8e1fe27fcc`): tam organizasyon özeti ve sınırlı/sayfalı panel, kayıt ve aidat detayları. [Mimari, kapasite ve sınırlar](SCALABLE-DASHBOARD.md).

F-10, sayfalama öncesi gereksiz tüm-kapsam ödeme toplamı işine ayrılıp sınırlı aday sorgusuyla düzeltildi; ace4983 push ve PR CI başarılı. Alpha.2 kaynak kod hazırlığı [READY FOR MAINTAINER REVIEW](ALPHA2-READINESS.md); son HEAD’in iki CI sonucu ve bakımcı incelemesi hâlâ kapıdır. [Kök neden/kanıt](F10-INVESTIGATION.md). PR #20 o aşamada taslaktı; yeni release/tag yoktur.

Güncel sonraki adım [S03-F güvenlik/regresyon kanıtı](S03F-SECURITY-REGRESSION.md) ve [alpha.2 hazırlık kararının](ALPHA2-READINESS.md) bakımcı incelemesidir. Yeni tag/release için ayrı kullanıcı onayı gerekir. Bağımsız kurulum geri bildirimi, üretim güvenliği/işletim doğrulamaları ve kapasite ölçümü açık kalır. Yeni başvuru gönderimi veya yeni release oluşturma bu belge düzeltmesinin kapsamında değildir.

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

S03-B aidat dönemi borç raporudur. S03-C ödeme/işlem tarihine göre aylık hareket raporunu ekler. S03-D CSV ve ilk sentetik rapor ölçümlerini ekler; sonraki işler daha geniş/çoklu kullanıcı yükü ve derin sayfalama tasarımıdır. S03-D aşamasındaki panelin tüm aidat geçmişini yüklemesi S03-E’nin ayrı kapsamıdır. Kısmi ters kayıt ve üretim dağıtımı kapsam dışıdır.

Tarihsel S03-D kapasite bulgusu: o aşamadaki panelin tüm geçmişi yükleyen dashboard() akışı sentetik 1.000/10.000 daire provalarında başarısız oldu; limitleri yükseltmek veya geçmişi sessiz kesmek çözüm olarak uygulanmadı. S03-E bu bulguya karşı ayrı, tam özetli ve geçmiş erişimini koruyan sayfalı panel geliştirir; yeni ölçümler [ayrı belgede](SCALABLE-DASHBOARD.md) tutulur. [Ölçüm ve sınırlar](FINANCIAL-EXPORT-PERFORMANCE.md).

## S05-A geliştirme denetimi

SOURCE RELEASE STATUS: ALPHA.2 PUBLISHED — UNCHANGED. Hazır imaj dağıtımı BLOCKED; bağımsız insan kurulumu PENDING HUMAN VALIDATION. Bu geliştirme çalışmasının son HEAD test kararı [S05-A raporunda](S05A-DISTRIBUTION-COMPLIANCE-VALIDATION.md), [binary kapıları](BINARY-DISTRIBUTION-GATES.md) ve [insan kurulum formunda](INDEPENDENT-INSTALLATION-CHECKLIST.md) izlenir. Önceki hazırlık kararları tarihsel kayıttır.

## S05-B kaynak/build incelemesi

[Kaynak doğrulaması](S05B-LIBVIPS-SOURCE-VALIDATION.md): 28 native kaynak girdisi ve 357 Rust transitif kayıt ayrı tutulur; binary provenance ve değiştirilmiş static-LGPL rebuild tamamlanmadı. LIBVIPS SOURCE EVIDENCE: PARTIAL; genel BINARY DISTRIBUTION READINESS: BLOCKED. S05-A tarihsel kanıtları değişmedi. Yeni imaj ELF/hash ve alternatif yükleme provası CI artifact'ındadır; dolu evidence metni native pakete PASS veremez. Node/Debian kaynak işleri ve bağımsız insan kurulumu açık kalır.

## S05-C kaynak ve rebuild kontrolü

[Doğrulama](S05C-REBUILD-VALIDATION.md) ve [tekrar tarifi](LIBVIPS-REBUILD-REPRODUCTION.md):357 dış Cargo.lock kaydından162'si upstream librsvg compile log'unda gözlendi;195 UNKNOWN,0 NOT SELECTED. Toolchain cargo-c build satırları ayrı tutulur. Yeni kaynak/ABI/load doğrulayıcı fiziksel dosya/hash ister; modified-source reduced-profile deneyi orijinal static bundle'a eşdeğer sayılmaz. Genel BINARY DISTRIBUTION: BLOCKED; Node/Debian/Prisma ve kalıcı source sunumu açık. Son HEAD deney sonucu ve iki mandatory CI PR kanıt kaydındadır; hazırlanmış/başarısız deney VERIFIED sayılamaz.
