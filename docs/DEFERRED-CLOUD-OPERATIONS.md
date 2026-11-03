# Bütçe kararı ve ertelenmiş bulut operasyonları

## S04-C — Şifreli mantıksal yedek ve korumalı güncelleme

Host operatörüne yönelik pg_dump → age akışı, atomik encrypted backup/manifest, lock, durum ve açık etkinleştirilen systemd timer/retention altyapısı eklendi. Ayrı boş/portsuz siteyonetim_test restore provası ve hata sonrası yazıcıları durduran güncelleme aracı vardır. Web kullanıcısına ham yedek veya Docker socket yetkisi verilmez. [İşletim ve anahtar rehberi](BACKUP-OPERATIONS.md), [güncelleme](SAFE-UPGRADE.md), [DEVELOPMENT doğrulaması](S04C-BACKUP-VALIDATION.md).

Bu günlük mantıksal backup kapsamıdır; WAL/PITR, anlık kurtarma ve production RPO/RTO ayrıca tasarlanıp sınanmalıdır. Anahtar kaybı yedeği açmayı engeller; fiziksel disk kaybına karşı ayrı depoda kopya gerekir. Ücretli sağlayıcı/Supabase zorunluluğu yoktur. Zamanlayıcı/silme varsayılan etkin değildir; gerçek deploy/güncelleme yapılmadı. Aşağıdaki tarihsel kanıtlar korunur.

## S04-A güncel karar

Supabase kullanılmayacak. Ücretsiz, PUBLIC, AGPL-3.0-only ve kendi sunucusunda kurulum önceliği korunur; ücretli servis zorunlu değildir. Sunucu/alan adı/e-posta maliyeti işletmeciye bağlıdır. Ayrı `compose.selfhost.yaml` ve [Docker kurulum rehberi](SELF-HOSTING-DOCKER.md) eklendi; `compose.yaml` geliştirme içindir. DEVELOPMENT doğrulaması üretim onayı değildir. S04-B web kurulum sihirbazı, S04-C yedek işletimi ayrı aşamalardır. Aşağıdaki eski durum raporları tarihsel bağlamıyla korunur. S04-A sonuçları S04A-VALIDATION belgesindedir.

## Üç bağımsız durum

- DEVELOPMENT: GPT Codex Cloud + mevcut GitHub; kod/migration ve sentetik, izole PostgreSQL 17/SMTP/Chromium testleriyle doğrulanan geliştirme. Harici servis bütçesi gerektirmez.
- STAGING: Gerçek bulut test entegrasyonları. Bütçe kararıyla ERTELENDİ; DEVELOPMENT tamamlanmasının koşulu değildir.
- PRODUCTION: Canlı müşteriye açılma. Bütçe kararıyla ERTELENDİ; kod/test başarısı canlıya hazır olma anlamına gelmez.

Önceki raporlardaki operasyonel kapanış bekleyen ifadeler tarihsel kayıttır. Bundan sonra geliştirme kanıtları ayrı değerlendirilir; aşağıdaki işler özellik geliştirmeyi bloke etmez. Ücretli hesap açılmaz, gerçek posta gönderilmez, gerçek müşteri verisi/testi kullanılmaz. Üretim migration/reset/deploy yapılmaz. Demo panel gerçek panelden ayrıdır.

## Ertelenmiş STAGING / PRODUCTION kontrol listesi

| Gereksinim | Üretim öncesi doğrulama | Maliyet bağımlılığı |
|---|---|---|
| Uygulama barındırma (Vercel veya alternatif) | HTTPS, secret, region, log ve rollback | Sağlayıcı/plan seçimi ertelendi |
| Yönetimli PostgreSQL (Neon veya alternatif) | TLS/pool, bağlantı limitleri, migration/runtime/bakım rol ayrımı | Depolama/işlem/bağlantı maliyeti |
| E-posta sağlayıcısı | SPF/DKIM/DMARC, teslim/bounce, token sızıntısı önleme | Sağlayıcı ve gönderim kotası |
| Alan adı ve sertifika | DNS/sahiplik/HTTPS APP_URL | Alan adı maliyeti; sertifika seçeneği |
| Yedek/PITR | RPO/RTO, şifreleme/saklama, izole geri yükleme provası | Depolama/PITR/operasyon maliyeti |
| İzleme/alarmlar | DB kilit/havuz, audit hatası, posta, bakım backlog, kapasite | Ücretsiz/ücretli seçenekler daha sonra değerlendirilecek |
| Edge/IP/bot koruması | Güvenilir proxy zinciri, hedefli hesap kilitleme ve yük saldırısı testleri | Sağlayıcı/kota seçimine bağlı |
| Bakım zamanlayıcısı | Yetkisi sınırlı token temizliği; audit/finans korunumu | Zamanlayıcı/operasyon altyapısı |
| Güvenlik/KVKK işletimi | Yetki incelemesi, secret rotasyonu, saklama/erişim politikası, olay müdahalesi | Operasyon ve gerekirse bağımsız inceleme |

Bunlar kaldırılmış güvenlik gereksinimleri değildir; staging/üretime geçiş öncesi yerine getirilecek işlerdir. Gerçek bağlantı bilgisi uydurulmaz. İzole testteki rol/SMTP başarısı gerçek sağlayıcı kurulmuş gibi raporlanmaz. Fiyat, abonelik veya ücretsiz plan garantisi verilmez.
