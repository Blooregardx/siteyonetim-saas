# S04-C — Şifreli yedek, kurtarma ve güncelleme doğrulaması

Durum: **READY FOR MAINTAINER REVIEW — DEVELOPMENT kod kabulü.** Production-ready değildir. Son HEAD'in iki CI başarısı ayrıca bakımcı kapısıdır.

Doğrulanan kod `d1ee5404390d6a93029497ddbfdc4f57cda373e4`:

| Koşu | checks | selfhost + encrypted recovery |
|---|---|---|
| [Push 41642147018](https://github.com/Blooregardx/siteyonetim-saas/actions/runs/41642147018) | Başarılı | Başarılı |
| [PR 41642154958](https://github.com/Blooregardx/siteyonetim-saas/actions/runs/41642154958) | Başarılı | Başarılı |

Koşular completed/success; headSha eşleşir. Bu raporla birlikte son restore-hedef/DB ACL sertleştirmesi gönderilir: portsuz ve özel rollü/başka uygulama DB'si bulunmayan hedef, NOLOGIN/beklenen rol limitleri ve kontrollü DB owner/ACL zorunludur. Son HEAD push/PR sonuçları [taslak PR #23](https://github.com/Blooregardx/siteyonetim-saas/pull/23) açıklamasında ayrıca kaydedilir; tamamlanmamış koşular başarı sayılmaz.

## Tam CI kanıtı

İki koşuda mevcut Docker kabulü ve gerçek age ile **12/12 host hata testi** başarılı. Yeni şifreli recovery adımı **26 tablo / 100.048 satır**, 11 migration, source/target bounded hash eşitliği, katalog/owner/index/constraint/column/enum/function/trigger/tablo-sütun/default ACL eşitliği, backup ve runtime DDL/yazma reddi, yanlış/eksik anahtar/değiştirilmiş ciphertext/yanlış-dolu hedef reddi, finans/audit/tenant probu, restored standalone health ve restart kalıcılığını geçti. Candidate içinde gerçek başarısız Prisma migration kaydı oluştu; diğer tüm veri tabloları değişmedi ve app durmuş kaldı. Bu, gerçek sunucu upgrade kabulü değildir.

Checks iki koşuda ESLint, strict TypeScript, **25/25 birim, 36/36 PostgreSQL entegrasyon, 19/19 Playwright**, production build, Prisma validate/generate ve 11 migration/schema diff, source/license/npm audit, iki dashboard query-plan modu, Python streaming **3/3** ve tarihsel sentetik restore başarılı. Push tarihsel restore **258.385 satır** eşleştirdi. Restore probu brüt6500/ters4000/net2500/kalan7500 kuruş, 15 audit, 11 migration; tenantIsolation=true ve immutableHistory=true. Koşuya göre süreli sentetik satır sayısı değişebilir; her koşu kendi kaynak/hedef eşitliğini doğrular.

İlk `58cd4b2` CI selfhost recovery, tarihsel hash yardımcısının sabit siteyonetim test yöneticisi nedeniyle durdu. Tarihsel betik değiştirilmedi; yeni provalarda yalnız orijinal bounded digest algoritması, postgres operatörüne açık bağlanan COPY stream ile kullanıldı. Sonraki iki CI tamamıyla başarılı. Hata retry/test atlama ile gizlenmedi.

Başlangıç main `6ce422c7a83e03109222a2a9810d6fee85e885f9`, temiz çalışma ağacı; dal `codex/s04-c-backup-recovery`. 11 migration, S04-A roller/named volume ve S04-B davranışı incelendi; tarihsel migration, finans servisi, web uygulaması ve LICENSE değişmedi.

## Mimari

Host-only Python CLI: sabit Docker komutları ve container+PG system_identifier bağlamı; ayrı NOLOGIN sy_backup SELECT rolü; pg_dump -Fc → age recipient pipe; encrypted partial → fsync/SHA/manifest → atomik dizin yayımı. Private key günlük backup host'unda gerekmez ve imaja konmaz. Plaintext dump dosyası yoktur. Backup/verify/prune/restore/upgrade aynı kernel flock'u kullanır. Yerel status ve opsiyonel yaş kontrolü, açık etkinleştirilen systemd timer (03.00, host/operatör saat dilimi), 7 gün örnek retention vardır.

Restore yalnız farklı, portsuz, boş `siteyonetim_test` cluster'ına; sabit NOLOGIN rol politikası, owner/tablo-sütun/default ACL ve katalog/migration kontrolü. Parola özeti/global rol dump'ı kullanılmaz. Anahtar doğrulaması ve arşivin açılması tek başına uygulama verisi kurtarma kanıtı sayılmaz.

Upgrade CLI, kimlik/temiz checkout/migration prefix ön kontrolünden sonra app'i durdurur, şifreli backup ve verify yapar, seçili restore provası/build/migrate/schema/health sırasını uygular. Hata sonrası app durmuş olarak kalır veya durumu açıkça UNKNOWN raporlanır; otomatik down/reset/restore/eskisini başlatma yoktur. Gerçek sunucuda çalıştırılmadı.

## Test kapsamı

Host hata matrisi: 32 MiB gerçek age stream; çakışan lock; üretici/encryption hatası; SIGTERM interruption; düşük disk ve gerçek dosya boyut sınırı/ENOSPC simülasyonu; retention dry-run/süre/son tamamlanmış ve son verified kopya; bozuk kopyayı sağlam saymama; yanlış dizin, symlink/hardlink/traversal; upgrade aşama sırası ve verify hatasında ilerlememe.

Gerçek encrypted recovery CI, selfhost işindeki hazır imajları yeniden kullanır; ikinci büyük build yoktur. Kendine ait üç PG17 cluster ve internal ağlarda: migration, mevcut finans probe'u, 100.000 sentetik AuthAttempt satırı, ayrı backup okuma/DDL-yazma reddi, runtime/migrator izinlerinin değişmemesi; şifreli backup/decrypt, yanlış/eksik anahtar, değiştirilmiş ciphertext (SHA ve age authentication), yanlış/dolu hedef reddi, ayrı boş restore; bütün satırlar ve owner/index/constraint/trigger/function/tablo-sütun/default ACL eşitliği; finans/audit/tenant probu; restore sonrası standalone health ve restart kalıcılığı; gerçek hatalı candidate migration sırasında app'in durmuş kalması sınanır.

Kaynak yazıcılar bu provada quiescent'tir; before/after kaynak hash'i ayrıca eşleştirilir. pg_dump'ın kendi consistent snapshot'ı bağımsız zamanlardaki kaynak/hedef hash eşitliğiyle karıştırılmaz. Başarısız migration'ın `_prisma_migrations` hata kaydı beklenir; diğer veri tablolarının hash'leri değişmemelidir. Candidate SQL yalnız disposable container /tmp dizinindedir; tarihsel migration'lar değiştirilmez.

## İlk yerel kanıtlar

ESLint/strict TypeScript ve 25 birim geçti. Gerçek age v1.3.2 binary'si upstream yayın SHA-256 özetiyle doğrulandı; host hata matrisi 12/12 geçti. Büyük uygulama Docker build'i yerel VFS ortamında tekrarlanmadı. Küçük PG17 ön provasında encrypted backup oluştu; ayrı arşiv okuyucusu aşaması başarısız oldu. PG17 okuyucu tek başına çalıştı; sonraki çoklu konteyner provasında VFS disk %98 doldu ve hedef başlayamadı. Yerel restore başarılı sayılmadı; tam zincir CI'da doğrulanacaktır. PostgreSQL katalog sorgusunda default ACL object type için açık text cast düzeltildi; ilk prova başarısızlığı gizlenmedi.

## Sınırlar

Mantıksal günlük backup, WAL/PITR/anlık kurtarma, fiziksel disk felaketi, bağımsız insan kurulumu, gerçek SMTP/HTTPS veya production update onayı değildir. Anahtar kaybı yedeği erişilemez kılar; aynı diskteki kopya disk kaybını karşılamaz. Ayrı medya/kopya, saklama/anahtar/erişim politikası gerekir. Manifest SHA kazara bozulma kontrolüdür, imza değildir; yalnız güvenilir kendi backup'ınızı izole SQL hedefinde açın.

Docker operatörü host root ve DB yerel postgres yetkisi taşır; pg_dump SET ROLE sy_backup altında olsa da bu operatör güven sınırıdır. Web runtime'a socket/yedek yetkisi verilmez. Sy_backup hassas bütün veriyi okuyabilir. Başka şema/sahip/özel rol/extension eklenirse politika ve restore ayrıca gözden geçirilir; bilinmeyen ACL sessizce düşürülmez.

Timer/silme otomatik etkin değildir. CLI advisory lock'u bilerek atlayan aynı UID/root yazıcı güvenilir operatör sınırındadır. SIGKILL/host çökmesi cleanup garantisi değildir; partial geçerli sayılmaz. Update bakım modu ve harici yazıcıların durması operatör sorumluluğudur. Kaynak imaj/binary dağıtımı ve LGPL/MPL bildirim yükümlülükleri önceki açık kapıdır.

PUBLIC/AGPL-3.0-only korunur; Supabase/ücretli servis/abonelik yok. Gerçek veri/e-posta, gerçek sunucu, staging/production deploy, release/tag, registry push ve merge yapılmaz. Tarihsel BACKUP-RESTORE/S04-A/B kanıtları korunur.
