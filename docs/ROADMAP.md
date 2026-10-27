# Yol haritası

S00–S01 kapanışı: SMTP kurulum ve teslim testi; hesap sahipliği doğrulaması; daha kapsamlı limit tarayıcı regresyonları; güvenlik incelemesi; eksik temel düzenleme ve denetim gereksinimleri.

Ardından: davet/rol yönetimi, kişi ve mülkiyet ayrımı, toplu aidat, audit log ve ters kayıt, gelir/gider ve raporlar, yedekleme/geri yükleme ve izleme.

Sonraki aşamalar: banka/kart, SMS/WhatsApp, mobil istemci, yapay zekâ ve otomatik gecikme faizi. Bu görevde geliştirilmedi. Canlı dağıtım yapılmaz.

## S01-C sonrası güncelleme

E-posta sahipliği, davet/üyelik rolleri, audit ve süre aşımı temizliği kod düzeyinde uygulanmıştır. Öncelikli kalanlar: gerçek bulut DB/SMTP/HTTPS kurulumu, runtime/migration/bakım rollerinin sağlayıcıda uygulanıp test edilmesi, edge saldırı koruması, geri yükleme provası ve izleme. Ters kayıt tasarımı PAYMENT-REVERSALS.md içindedir; servis ve güvenlik testleri ayrı görevdir. S00–S01 kapanışı bu operasyonel doğrulamalar ve kalan temel yönetim ihtiyaçları değerlendirilmeden verilmez.

## S01-D sonrası

Tam ters kayıt, merkezi net bakiye ve izole runtime/migration rol testleri uygulandı. Gerçek sağlayıcıdaki DB rol ayrımı/TLS/bağlantı, SMTP teslimi, edge koruma, yedek/PITR, geri yükleme provası, bakım zamanlayıcısı ve izleme açık kalır. Hatalı ters kaydın telafisi/kısmi ters kayıt ayrı finans tasarımıdır; eski kayıtları değiştirme veya silme çözüm değildir. S00–S01 operasyonel kapanışı henüz verilmez.
