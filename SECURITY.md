# Güvenlik politikası

## Bildirim

Parola, token, kişisel veri veya çalışır saldırı ayrıntılarını public issue/PR içine koymayın. Güvenlik açıklarını [GitHub özel güvenlik bildirimi](https://github.com/Blooregardx/siteyonetim-saas/security/advisories/new) üzerinden iletin. **30 Ekim 2026 OSS-01B kontrolünde Private Vulnerability Reporting etkin olarak doğrulandı.** Kullanıcı bu özelliği etkinleştirmiştir; bu PR hesap ayarı değiştirmez.

Tarihsel kayıt: OSS-01 başlangıç denetiminde kanal kapalıydı. Bu önceki bulgu güncel durum değildir; [ayar geçmişi ve kalanlar](docs/GITHUB-SETTINGS.md) ayrı tutulur.

Özel kanal erişilemiyorsa hassas ayrıntıları public alana taşımayın. Yalnız ayrıntı içermeyen özel iletişim kanalı talebi açıp bakımcının yönlendirmesini bekleyin. Doğrulanmış alternatif özel e-posta adresi henüz yayımlanmadı.

Özel raporda etkilenen commit/sürüm, etki ve yalnız sentetik veriyle tekrar adımlarını paylaşın. Erişim bilgilerini maskeleyin; gerçek sistemlere izinsiz test yapmayın. Bakımcı raporu değerlendirir, düzeltme ve güvenli açıklama zamanını bildirenle koordine eder. Yanıt süresi garantisi verilmez.

## Destek kapsamı

Henüz kararlı sürüm veya uzun süreli destek taahhüdü yoktur. Öncelik geliştirme dalındaki güncel koddur; main aynı özellikleri içermeyebilir. Güvenlik düzeltmeleri incelemeli PR ve testlerle ele alınır. Bu sürüm canlı kullanım onayı değildir.

## Uygulanan korumalar ve sınırlar

Sunucu oturumu, e-posta doğrulaması, organizasyon/rol denetimi, özetlenmiş tokenlar, scrypt parolalar, transaction içi audit, finans satır kilitleri ve idempotency uygulanmıştır. Demo ayrı tutulur. [Teknik güvenlik özeti](docs/SECURITY.md).

Hesap bazlı limiter tek başına internet ölçeğinde saldırı koruması değildir. Runtime DB sırrı uygulama yetkilerini atlamaya imkân verebilir; minimum DB izinleri, TLS, güvenli ağ, HTTPS, yedek ve geri yükleme gerekir. MFA ve oturum yönetim ekranı uygulanmadı. Gerçek sağlayıcı SMTP/DB ve üretim işletimi doğrulanmadı.

`.env`/SMTP/DB sırlarını commit etmeyin. Compose ve CI parolaları yalnız izole geliştirme/test içindir. Sır sızarsa önce iptal/rotasyon yapın; geçmiş temizliğini ayrıca planlayın. Finans ve audit geçmişini silmeyin. [Kendi sunucusunda işletim](docs/SELF-HOSTING.md).
