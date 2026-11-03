# Kurulumda güvenli teşhis

Bu belge veri silme/reset veya otomatik yetki genişletme önermez. Mevcut volume'daki gerçek veriyi yedeklemeden hiçbir kurtarma işlemi yapmayın. Preflight kontrol-only'dir; başarısızlığı gidermek operatörün ayrı, incelenmiş işlemidir.

| Kod/belirti | Anlam ve güvenli sonraki adım |
|---|---|
| ENV_FILE_MISSING / ENV_FILE_PERMISSIONS | .env.selfhost yok veya özel regular dosya değil. Örnekten güvenli hazırlayın; içeriğini loglamayın. |
| SECRET_FILE_MISSING / SECRET_TYPE_INVALID | Dosya yok, symlink/hardlink veya beklenmeyen tip. Sırrı ayrı güvenli operatör işlemiyle sağlayın; var olanı ezmeyin. |
| SECRET_UID_GID_INVALID / SECRET_PERMISSIONS_INVALID | Standart node1000/postgres999 okuma eşlemesi yok. Metadata'yı inceleyin; 0777/0644 ile açmayın. |
| SECRET_SIZE_INVALID | OpenSSL 32-byte hex dosyasının beklenen uzunluğu yok. Araç değeri okumaz; mjs giriş kapısı formatı ayrıca doğrular. |
| DATABASE_BINDING_INVALID | db/app/migrate aynı geçerli DB adına bakmıyor. Yeni bağlantı/rol hazırlığını kontrol edin; mevcut volume'u resetlemeyin. |
| DATABASE_PORT_PUBLISHED / APP_PORT_BINDING_INVALID | DB portu veya app public binding'i var. Mevcut tasarım portsuz DB/loopback app bekler; ağ tasarımını inceleyin. |
| POSTGRES_17_REQUIRED | Compose imajı test edilmiş PG17 değil. Eski PGDATA'yı farklı major imajla açmayın; ayrı migration/restore planı gerekir. |
| APP_PORT_UNAVAILABLE | Seçilen port dolu veya bind izni yok. Var olan süreci otomatik öldürmeyin; başka loopback portu seçin veya sahibini araştırın. |
| DISK_RESERVE_INSUFFICIENT / DOCKER_DISK_RESERVE_INSUFFICIENT / VFS_DISK_MULTIPLICATION | Build/veri/yedek alanı yetersiz olabilir. Eşik kapasite garantisi değildir; yalnız kendi tanımlı sentetik test kaynaklarınızı temizleyin. Global prune/user cache silme yok. |
| DOCKER_DATA_DISK_NOT_CHECKED | Docker data dizini host üzerinden incelenemedi; kaynak filesystem eşiği Docker disk kapasitesi garantisi değildir. Operatör ayrıca kontrol etmeli. |
| HTTPS_ORIGIN_INVALID | APP_URL yalnız HTTPS origin olmalı; user/pass/path/query/fragment yok. Sertifika varlığı ön kontrolde sınanmaz. |
| SMTP_MISSING_REGISTRATION_UNAVAILABLE / MAIL_FROM_MISSING | Demo incelemesi olabilir, gerçek kayıt/doğrulama tamamlanmaz. --require-mail bunları hata sayar. |
| SMTP_DELIVERY_NOT_VERIFIED | Nonempty dosya teslim kanıtı değildir; secret değeri okunmaz/yazdırılmaz. Operatör TLS ve gerçek teslimi ayrı doğrular. |
| DOCKER_UNAVAILABLE / COMPOSE_V2_REQUIRED | Docker erişimi/plugin yok. Docker grubunun root eşdeğerini gözden geçirin; socket'i web'e mount etmeyin. |
| COMPOSE_CONFIGURATION_INVALID | Config çözümü başarısız. Araç raw stderr/config yazdırmaz. Editörle syntax ve gerekli değişkenleri kontrol edin. |
| SELFHOST_START_FAILED | DB hazır değil, bağlantı/rol/secret/sürüm veya migration kapısı başarısız. Daha yetkili rolü app'e vererek geçmeyin. |
| SELFHOST_MIGRATION_FAILED | Ayrı migrate işi başarısız; app'i kapalı tutun. Güvenli stage/kod çıktısını inceleyin; reset/down kullanmayın. |
| Yarım/eski PG volume | Init yalnız ilk boş PGDATA'da çalışır. Rol/secret dosyasını değiştirmek var olan DB rol/parolasını değiştirmez. DBA kontrollü onarım veya ayrı boş restore gerekir. |
| Image build başarısız | Exit kodunu koruyun; app'i eski/hazır bir imajla başarılı kuruldu gibi göstermeyin. Disk, TLS/proxy ve lockfile uyumunu inceleyin. |
| Backup identity/restore key yok | Doğrulama başarısızdır; backup bozulmuş sayılması veya şifresiz fallback yapılması gerekmez. Doğru ayrı anahtarı bulun; kayıpsa yedek açılamaz. |

## Neler güvenle incelenebilir?

```sh
sh scripts/selfhost-preflight.sh
docker compose --env-file .env.selfhost -f compose.selfhost.yaml ps
```

Bunlar yine yerel altyapı bilgisi içerir; paylaşmadan önce gözden geçirin. `docker inspect` çıktısını topluca, `docker compose config` çıktısını `--quiet` olmadan veya `env`/`set -x` çıktısını paylaşmayın. Secret metadata'sı için `stat` kullanabilirsiniz; içeriği `cat` ile issue'ya taşımayın.

Gerekirse app/migrate/db loglarını yalnız özel operatör oturumunda inceleyin. Sabit stage/hata kodlarını ayırın; raw DB SQL, e-posta, token, URL veya satır içeriğini topluluk kanalına koymayın. Preflight secret içeriklerini açmaz; doğru dosya uzunluğu/parçası veya dosyanın nonempty olması password/SMTP geçerliliğini ispatlamaz.

CI negatif senaryoları yalnız sentetik siteyonetim_test'te çalışır: DB başlamadan/migration öncesi ret, yanlış ad, NOLOGIN/yarım rol, yanlış runtime CREATE ve tek sentetik unfinished migration kaydı; on bir tarihsel kayıt/SQL dosyası korunur. Bu kontroller bütün tarihsel PG volume formatlarını otomatik onarmak veya tüm sunucu sorunlarını kapsamak değildir.

Güvenlik şüphesini public issue yerine [özel kanaldan](../SECURITY.md) bildirin. Yanıt süresi ve üretim kurtarma desteği garantisi yoktur.
