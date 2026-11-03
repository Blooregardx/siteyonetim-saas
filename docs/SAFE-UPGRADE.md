# Korumalı self-hosting güncellemesi — S04-C

Yalnız DEVELOPMENT altyapısıdır; gerçek sunucu güncellemesi bu görevde yapılmaz. Yeni sürümü incelemek, bakım penceresini açmak ve tüm yazıcıları kontrol etmek operatörün sorumluluğudur. Otomatik sürüm indirme, production deploy, reset, down migration veya eski yedeği mevcut DB üzerine yükleme yoktur.

## Ön inceleme ve kaynak kimliği

1. Çalışan app'in tam Docker image ID'sini ve mevcut incelenmiş commit'ini kaydedin. Yalnız package sürümüne güvenmeyin; farklı commit'ler aynı alpha sürümünü taşıyabilir.
2. DB tam container/system_identifier kimliğini backup config ile eşleştirin. DB volume'unu silmeyin. `backup_ops.py provision` ayrı operatör adımıyla backup rolünü hazırlamış olmalıdır.
3. Yeni kaynak commit'ini temiz checkout'ta inceleyin; AGPL/üçüncü taraf koşullarını ve migration SQL'lerini değerlendirin. Eski migration checksum'ları yeni kaynakta aynı prefix olmalı. Bu kontrol uygulamanın bütün geri/ileri uyumluluğunu otomatik kanıtlamaz.
4. Reverse proxy'yi bakım moduna alın; yalnız güvenilir operatör sağlık trafiğine izin verin. Harici işçiler/DB yazıcılarını durdurun. Araç yalnız Compose `app` servisini durdurur; başka yazıcıları kendiliğinden bulamaz.
5. Başarısızlığı karşılayacak disk/backup ve ayrı kurtarma anahtarını hazırlayın. age kimliği gerektiği için kontrollü bakım oturumunda çevrimiçi olur; günlük timer için private key gerekmez.

## Araç sırası

`scripts/safe_upgrade.py` açık operatör komutudur. Repo aynı araç checkout'u olmalı; HEAD incelenen `--target-revision` ile aynı ve çalışma ağacı temiz olmalıdır. Compose DB ID'si backup kaynağına, çalışan app image ID'si `--expected-current-image` değerine uymalıdır. Beklenmeyen kimlikte daha yazıcı durdurmadan reddeder.

Sıra: app durdur ve durmuş olduğunu doğrula → şifreli backup → tam age/list doğrulaması → seçilmiş ayrı restore provası → yerel app/migrate build → ayrı migration işlemi → schema checksum/tam migration kontrolü → app başlat ve healthcheck. Migration wrapper ayrıca Prisma schema diff yapar. Reverse proxy'yi başarıdan sonra operatör açar; app'in kısa sağlık penceresinde dış yazım kabul etmemesi bakım moduna bağlıdır.

```sh
python3 scripts/safe_upgrade.py \
  --config /etc/siteyonetim/backup.json \
  --repo /opt/siteyonetim \
  --env-file /opt/siteyonetim/.env.selfhost \
  --project siteyonetim \
  --target-revision INCELENMIS_40_HEX_COMMIT \
  --expected-current-image sha256:CALISAN_64_HEX_IMAGE_ID \
  --identity /GUVENLI_AYRI_MEDYA/siteyonetim.agekey \
  --restore-target /etc/siteyonetim/recovery-target.json \
  --reviewed-upgrade --other-writers-quiesced
```

`--restore-target` yalnız farklı cluster'da boş/portsuz `siteyonetim_test` hedefi kabul eder. Restore provasını yapmadan ilerlemek ancak açık `--skip-restore-drill` ile mümkündür; iki seçenek aynı anda kullanılamaz. Bu seçenek bir kurtarma kanıtı değildir; yedek decrypt/list kontrolü yine zorunludur. İlk önemli güncellemede ve düzenli aralıklarla ayrı provayı atlamayın. Üretim RPO/RTO/PITR veya geri uyumluluk garantisi verilmez.

Backup config'in revision alanı yedeğin alındığı çalışan kaynak sürümünü, upgrade kaydı hedef commit ve önceki imaj ID'sini taşır. Başarı sonrası gerçekten çalışan imajı kaydedin, config sürüm bilgisini kontrollü güncelleyin. CLI config otomatik sır/rol parolası değiştirmez veya başka repo/servis seçmez.

## Hata ve kurtarma

Her orchestration hatasında app yeniden durdurulur. Çıkış durumu `FAILED_WRITERS_STOPPED` veya durdurma doğrulanamıyorsa `FAILED_WRITERS_STATE_UNKNOWN` olur; ikinci durumda hemen erişimi ve süreçleri operatör denetlemelidir. Backup dizinindeki özel `upgrade-*.json` kaydı hedef/önceki imaj, kaynak bağlamı, backup adı (başarıda) ve durumu içerir. Kayıt yazma/disk hatası durumunda komut başarısızdır; journal ve süreç durumunu da inceleyin. SIGTERM/SIGINT orchestration sırasında güvenli durma yoluna gider; SIGKILL/host çökmesinde otomatik cleanup garantisi yoktur.

- Migration hatasında eski imaj otomatik başlatılmaz; kısmen uygulanmış/yeni şema eski uygulamayla uyumlu olmayabilir.
- `prisma migrate reset`, otomatik down migration, DROP/TRUNCATE veya `compose down -v` işletim yolu yoktur.
- Başarısız update'ten sonra mevcut DB üzerine eski backup otomatik restore edilmez. Bu, yeni yazılmış tahsilat/audit geçmişini kaybettirebilir.
- Yazıcıları kapalı, reverse proxy'yi bakım modunda tutun. Yapısal durumu, `_prisma_migrations` ve DB loglarını özel oturumda inceleyin. Hassas logları issue/CI'a taşımayın.
- İleri düzeltme veya ayrı boş hedefe doğrulanmış restore planını onaylı operatör uygular. Eski imaja dönüş yalnız şema ve yeni veri uyumluluğu ayrıca kanıtlanırsa yapılır.
- Otomatik araç backup/verify sırasında hata verirse build/migrate/start aşamalarına geçmez. Başlangıç sonrası health hatasında da app durdurulur; otomatik veri geri alma yapılmaz.

CI, gerçek PG17 üzerinde ayrı geçici candidate dizinine kasıtlı başarısız bir migration ekleyip aynı orchestration'ın migration aşamasında durduğunu sınar; host'taki tarihsel migration dosyaları değişmez. Gerçek sunucu veya production güncellemesi kabulü değildir. [Yedek işletimi](BACKUP-OPERATIONS.md), [doğrulama](S04C-BACKUP-VALIDATION.md).
