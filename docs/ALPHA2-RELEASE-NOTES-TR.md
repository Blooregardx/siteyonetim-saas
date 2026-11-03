# v0.1.0-alpha.2 — Türkçe sürüm notu taslağı

**TASLAK / YAYIMLANMADI — EARLY DEVELOPMENT, NOT PRODUCTION READY.** Alpha.1 mevcut etiketinde kalır. Package ve kilit 0.1.0-alpha.1; 0.1.0-alpha.2 değişikliği yalnız ayrı yayımlama kararından sonra önerilir. Bu belge tag, GitHub Release veya registry imajı oluşturmaz.

## Aday kapsam

S03-A–F ve S04-A–D, alpha.1 sonrasındaki incelenmiş main değişikliklerini kapsayabilir. PR #11–15, #20–23 birleşmiştir; S04-D bu taslağın inceleme çalışmasıdır. Kesin release commit'i ayrıca seçilmelidir.

- Önizlemeli, idempotent ve transaction/audit korumalı toplu aidat.
- Kısmi/tam tahsilat politikası, borç/tahsilat ve aylık hareket raporları, manuel gelir/gider ve tam ters kayıt. Gerçek para iadesi değildir.
- Güvenli CSV, tam kapsam özetleri ve 25 satırlık sayfalar; S03-E/F bounded panel/ödeme hesabı düzeltmeleri ve finansal immutable trigger'lar.
- S04-A: Node 24/PG17/Prisma6, standalone non-root Docker, loopback app/portsuz DB, ayrı sy_migrator/sy_runtime ve migration/health kapıları.
- S04-B: Türkçe mobil `/kurulum`, mevcut doğrulama/üyelik/audit kuralları, devam edilebilir ve tekrar gönderimde tekilleşen ilk organizasyon/site.
- S04-C: host-only pg_dump→age şifreli akış, atomik yayımlama, lock/retention/status, açık etkinleştirilen systemd örneği; ayrı boş hedefe restore ve başarısız migration'da app'i durduran update hazırlığı.
- S04-D: sade kurulum/topluluk rehberi, salt okunur preflight, GitHub'dan temiz kaynak/archive otomatik kabulü ve dağıtım kapılarının ayrılması. Otomatik prova bağımsız insan kurulumu değildir.

## Gereksinimler ve uyumluluk

İlk otomatik Docker kabulü Linux x86-64; Docker Engine + Compose v2/uyumlu plugin, Git/Python3/OpenSSL. Node24, PostgreSQL17 ve Prisma6 imajlarda; host backup için age ayrıca gerekir. Gerçek kullanımda HTTPS ve SMTP operatör tarafından kurulup doğrulanır. Ücretli servis/Supabase/abonelik/lisans anahtarı gerekmez; altyapı işletmeciye maliyet çıkarabilir.

11 migration korunur; S04 aşamaları şema migration'ı eklemez. Alpha.1 veya eski DB'den ilerlerken incelenmiş migration zinciri ayrı rolle uygulanmalı, source checksum/schema diff ve veri/audit korunumu doğrulanmalıdır. Otomatik reset/down migration yoktur. Eski imaja dönmek yeni şemayla uyum garantisi değildir; backup mevcut DB üzerine otomatik yüklenmez. [Güncelleme](SAFE-UPGRADE.md).

## Bilinen eksikler ve işletim kapıları

Staging/production, gerçek SMTP/HTTPS teslimi, bağımsız insan kurulumu, internet yükü/bot koruması/MFA, tam alarm/işletim ve kapasite SLA'sı doğrulanmadı. OFFSET/ayrı sayfalar arası snapshot sınırları sürer. Günlük mantıksal backup, WAL/PITR veya fiziksel disk kurtarma garantisi değildir. Private key kaybı yedeği açılamaz kılar; ayrı güvenli anahtar/backup kopyası gerekir. Timer/prune varsayılan etkin değildir.

AGPL-3.0-only korunur. Kaynak-only arşiv ile binary/container dağıtımı farklıdır. **BLOCKED FOR BINARY DISTRIBUTION:** LGPL/MPL ve temel imaj karşılık gelen kaynak/bildirim yükümlülükleri tamamlanmadı; hazır imaj yayımlanmaz. [Lisans incelemesi](THIRD-PARTY-LICENSES.md), [Alpha.2 kararı](ALPHA2-READINESS.md), [kurulum](COMMUNITY-INSTALLATION.md), [S04-D kanıtı](S04D-DISTRIBUTION-VALIDATION.md).

Önceki taslak [S03-F tarihçesinde](ALPHA2-RELEASE-NOTES-TR-S03F-HISTORY.md) korunur. Yayım için son HEAD CI, kesin source arşivi, bakımcı incelemesi, sürüm metadata değişikliği ve ayrı kullanıcı kararı gerekir.
