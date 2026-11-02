# F-10 — Kontrollü teşhis kaydı

Başlangıç: PR #20, `e02576f4616fcc216f7ff3aa77e4f0321ce8815a`. Bu belge S03-F tarihsel başarısızlıklarını değiştirmez. İnceleme devam ederken alpha.2 **BLOCKED**, PR taslaktır.

## Ölçüm güvenliği ve evreler

`F10_DIAGNOSTICS=1` yalnız DATABASE_URL ve TEST_DATABASE_URL aynı loopback PostgreSQL `siteyonetim_test` olduğunda sunucu ölçümünü açar. Sunucuya sentetik ölçek/nonce etiketi gönderilir; bu etiket yetki sağlamaz. SQL/parametre, cookie, token, parola, e-posta veya satır içeriği loglanmaz. Sorgular yalnız komut, şekil hash’i ve süreyle; PostgreSQL beklemeleri durum/bekleme türü ve süreyle kaydedilir. Çıktılar sınırlıdır; kesilme sayacı bulunur.

Tarayıcı navigasyon olayı → sunucu dispatch/Panel girişi → session/user/membership → ayrı okuma servisleri ve Prisma süreleri → render başlangıcı/komponent dönüşü → HTTP başlıkları/chunk/gövde tamamlanması → DOM ilk düğüm/25 satır/DOMContentLoaded/load → mevcut istemci arama kontrolleri. CDP ağ olaylarından yalnız bu metaveri alınır. Ham Playwright trace ağ başlıklarında cookie içerebileceği için kullanılmaz; redakte olay zaman çizelgesi kullanılır.

Başlıkların gelmesi HTML’in veya verinin hazır olduğu anlamına gelmez. Server Component’in JSX döndürmesi de tüm HTTP gövdesinin bittiği anlamına gelmez; ayrı olaylar kaydedilir. Proxy/ölçüm ek yükü vardır; ölçümler production SLA’sı değildir. Finans, yetki, transaction timeout, migration ve test assertion’ları değiştirilmedi.

## İlk yerel kanıtlar — henüz kök neden değil

Aynı sentetik kapasite fixture’ları tekrar kullanılarak bağımsız Next/Chromium süreçlerinde hedef dosya 4/4 ve tam E2E 14/14 geçti. İlk 10.000 daire ikinci sayfa gözlemi: başlık 16 ms, 25 satır 1.315 ms, gövde tamamlanması 1.320 ms. Tam sıra gözleminde sunucu verileri yaklaşık 1,3 saniyede hazırladı; en uzun charges sorgusu yaklaşık 1,1 saniyeydi. Gövde ve DOM bunu yakından izledi. Kalıcı DB lock veya P2028 gözlenmedi. Bu başarılı gözlemler başarısız CI’ın alt nedenini kanıtlamaz.

Sonraki teşhis aynı ölçümlerle push/PR CI üzerinde yapılır. Test skip/fixme/retry veya timeout artırımı uygulanmaz. Başarılı bir deneme tek başına F-10’u kapatmaz.
