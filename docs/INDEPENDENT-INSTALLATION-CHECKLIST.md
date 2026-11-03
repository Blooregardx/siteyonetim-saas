# Bağımsız kurulum katılımcı formu

INDEPENDENT INSTALLATION: PENDING HUMAN VALIDATION

Projeyi daha önce kullanmamış bir geliştirici henüz bu formu tamamlamadı. Temiz CI kurulumu insan doğrulaması değildir. Yalnız boş, izole Linux x86-64 test ortamı ve sentetik veri kullanın; gerçek SMTP göndermeyin. Bu belge production onayı değildir.

- [ ] Linux dağıtımı/kernel, x86-64, Git/Python3/OpenSSL, host age/age-keygen sürümlerini kaydedin; kaynak ve Docker alanında en az 10 GiB boşluk kontrol edin.
- [ ] Docker Engine ve Compose v2 sürüm/daemon kontrollerini yapın; socket erişiminin root yetkisi olduğunu anlayın.
- [ ] [Kurulum rehberi](COMMUNITY-INSTALLATION.md) ile kaynak indirin; `git switch --detach c20646fddbc8a7e3dcd45cbc01aacd531c225e4a` ve HEAD doğrulayın. [Alpha.2](https://github.com/Blooregardx/siteyonetim-saas/releases/tag/v0.1.0-alpha.2) source-only'dir; hazır imaj yoktur.
- [ ] Rehberdeki umask/openssl adımlarıyla her rol için ayrı secret oluşturun; UID/GID ve izinleri doğrulayın. Değerleri rapora koymayın.
- [ ] Salt okunur preflight ve Compose config doğrulansın; yerel build yapılsın. SMTP eksikliği demo-only olarak kaydedilsin.
- [ ] PostgreSQL 17 boş named volume'da sağlıklı başlasın; DB host portu açılmasın.
- [ ] Ayrı migrate servisi 11 migration'ı uygulasın; hata varsa app başlatılmasın. Tarihsel SQL değişmesin.
- [ ] App health ve `/demo` açılsın; oturumsuz `/panel` ve `/kurulum` erişimi yönetim yetkisi vermesin.
- [ ] Sentetik hesap akışları için yalnız izole SMTP yakalayıcı kullanın; `/kurulum` adımları ve yeniden gönderimde tekilleşmeyi kaydedin. Gerçek HTTPS sertifikası/SMTP teslimi ayrı operatör kapısıdır; test başarısıyla doğrulanmış saymayın.
- [ ] DB/app restart sonrası sentetik kayıt ve migration geçmişi korunsun; `down -v` kullanmayın.
- [ ] [Yedek işletimi](BACKUP-OPERATIONS.md) ile sentetik şifreli backup ve ayrı boş cluster'a restore provası yapın. Mevcut DB üzerine restore etmeyin; health/tenant/finans/audit korunumu doğrulayın. Anahtar ve yedeği paylaşmayın.
- [ ] [Güvenli teşhis](TROUBLESHOOTING.md) ile sabit hata kodları toplayın; env/config dump, ham log, token, e-posta, kişi bilgisi ve private key paylaşmayın. Güvenlik açığını [özel kanala](../SECURITY.md) iletin.

Katılımcı sonuçları (henüz doldurulmadı): tarih / takma ad / önceki proje deneyimi / OS ve araç sürümleri / kesin SHA / süre / her adım PASS-FAIL-SKIPPED / takılınan adım / maskelenmiş hata kodu / belge önerisi / backup-restore sonucu / kalan sorunlar / genel sonuç. Atlanan adım başarılı sayılmaz. Bakımcı incelemesi ve katılımcının açık beyanı olmadan PENDING kaldırılmaz.
