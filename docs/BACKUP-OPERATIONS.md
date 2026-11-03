# Şifreli mantıksal yedek işletimi — S04-C

Yalnız DEVELOPMENT kanıtı vardır. Araç host operatörüne yöneliktir; web kullanıcısına yedek indirme ucu veya Docker socket yetkisi vermez. Ücretsiz, açık kaynak age ve PostgreSQL 17 kullanır; ücretli servis/Supabase gerekmez. Sunucu, depolama ve ayrı kopya maliyeti işletmeciye aittir. Günlük mantıksal dump, WAL/PITR veya anlık kurtarma değildir; RPO/RTO garantisi yoktur.

## Yetki modeli ve önkoşullar

Host'ta Python 3, Docker Engine/Compose, age/age-keygen ve yerelde hazır `postgres:17-bookworm` aracı gerekir. age işletim sisteminin güvenilir paket yöneticisiyle kurulabilir; sürüm/güvenlik güncellemelerini takip edin. age recipient açık anahtar şifrelemesi (X25519) kullanılır; parola argv'ye yazılmaz. Kimlik dosyası yalnız host'ta özel izinle okunur; imaja, Git'e veya CI artefaktına eklenmez.

Docker socket erişimi pratikte host root yetkisidir. Araç konteyner içindeki yerel `postgres` operatör oturumunu kimlik/katalog ve kontrollü rol hazırlığı için kullanır. **Dump `--role=sy_backup` ile NOLOGIN, NOSUPERUSER, NOCREATEDB, NOCREATEROLE, NOREPLICATION rolü altında çalışır.** Public şemadaki tüm uygulama tabloları (AuditLog, parola/token özetleri dahil) ve sequence'ler için SELECT/USAGE gerekir. Gelecek sy_migrator tabloları/sequence'leri için yalnız SELECT default privilege verilir. INSERT/UPDATE/DELETE/TRUNCATE/DDL/rol üyeliği verilmez; beklenmeyen yazma/sahiplik yetkisi varsa araç reddeder. Başka şemada/başka sahipte yeni tablo varsa dump güvenle hata verebilir; izin kapsamını ayrıca inceleyin, tabloyu hariç tutarak başarı üretmeyin.

`sy_runtime` ve `sy_migrator` yetkileri yedek için artırılmaz. Normal app/migrate başlangıcı backup rolü veya age gerektirmez. Sy_backup bütün hassas veriyi okuyabilir: minimum yazma yetkisi, düşük veri hassasiyeti anlamına gelmez. Docker/DBA oturumunu ele geçiren kişi SET ROLE dışına çıkabilir; bu araç host operatörünü yetkisiz web kullanıcısına dönüştürmez. Alternatif, ayrı host üzerinde TLS/PGPASSFILE ile kısıtlı SELECT backup LOGIN rolü ve güvenlik duvarıdır; mevcut CLI bu uzak bağlantı modunu uygulamaz.

## Anahtar ve yapılandırma

Aşağıdaki işlemler rehberdir; servis/timer otomatik etkinleştirilmez. Güvenilir, erişimi kısıtlı host'ta örnek:

```sh
umask 077
install -d -m 700 /etc/siteyonetim /var/lib/siteyonetim/backups
# Gizli kimliği tercihen ayrı, şifreli/offline medyada oluşturun.
age-keygen -o /GUVENLI_AYRI_MEDYA/siteyonetim.agekey
age-keygen -y /GUVENLI_AYRI_MEDYA/siteyonetim.agekey > /etc/siteyonetim/backup-recipients.txt
chmod 600 /etc/siteyonetim/backup-recipients.txt
python3 scripts/backup_ops.py init --directory /var/lib/siteyonetim/backups
```

Kimlik dosyası 0600, anahtar dizini 0700 ve CLI kullanıcısına ait olmalı. Günlük backup host'unda **yalnız açık recipient** gerekir; private key günlük timer için gerekli değildir. Anahtarı backup dosyalarıyla aynı dizinde tutmayın; araç bunu reddeder. Başka bir host'ta/offline medyada en az bir güvenli anahtar kopyası ve denenmiş kurtarma erişimi sağlayın. **Gizli anahtar kaybolursa yedek açılamaz.** Recipient değişimi eski yedekleri yeni anahtarla açılabilir yapmaz; eski kimlikleri saklama politikasıyla koruyun.

```sh
python3 scripts/backup_ops.py identify --container SECILEN_DB_KONTEYNERI --database siteyonetim
cp ops/backup.config.example.json /etc/siteyonetim/backup.json
chmod 600 /etc/siteyonetim/backup.json
```

Identify çıktısındaki tam container_id, PostgreSQL system_identifier ve database adını özel config'e güvenilir editörle girin. `revision`, çalışan kaynak sürümün incelenmiş 40 karakter commit SHA'sıdır; imaj kimliğini ayrıca kaydedin. Config, recipient ve backup dizini aynı operatöre ait özel izinlerde olmalıdır. Symlink/hardlink kimlik ve yedek dosyaları reddedilir. Üst dizinler root/operatöre ait ve başkalarınca yazılamaz olmalıdır; root-owned sticky /tmp özel istisnadır. Root dizini veya işaret dosyası bulunmayan başka dizin kabul edilmez. DB konteyneri yeniden oluşturulduğunda container ID değişir: eski config'le iş başarısız olur; veri volume/cluster kimliğini ayrıca doğruladıktan sonra config'i kontrollü güncelleyin.

## İlk rol hazırlığı ve yedek

```sh
python3 scripts/backup_ops.py provision --config /etc/siteyonetim/backup.json
python3 scripts/backup_ops.py backup --config /etc/siteyonetim/backup.json
python3 scripts/backup_ops.py status --config /etc/siteyonetim/backup.json --max-age-hours 36
```

Provision açık operatör işlemidir; app başlangıcında çalışmaz. Backup tüm DB için `pg_dump -Fc` → age pipe kullanır. Plaintext arşiv diske yazılmaz; 64 KiB hash/verify okumalarıyla istemci belleği sınırlıdır. PostgreSQL snapshot'ı kendi içinde tutarlıdır; bağımsız zamanlardaki veri hash'leriyle aynı garanti değildir. Normal online backup sırasında yazımlar devam edebilir. Restore karşılaştırması/güncelleme öncesi prova için tüm yazıcıları durdurun; testler before/after kaynak hash eşitliğiyle değişimi ayrıca denetler. Eşzamanlı DDL/migration yapılmaz; öncesi/sonrası migration/katalog değişimi backup'ı başarısız sayar.

`.partial-*` içinde yalnız şifreli veri oluşur. Dump ve encryption çıkış kodları, fsync, şifreli SHA-256 ve metadata tamamlanınca dizin atomik `backup-UTC-uuid` adına taşınır. Manifest yalnız kaynak operasyon kimliği, sürüm, migration checksum ve katalog hash'i içerir; kullanıcı satırı/kimliği içermez. Başarısız/kesilen işlem geçerli kopya yayımlamaz. SIGKILL/host çökmesinde kalan partial dizinler geçerli sayılmaz ve otomatik silinmez. Alan/yazma hatasında nonzero exit vardır; disk rezervini izleyin. Yayımlama dizini fsync hatasında normal adı geri çekilip partial temizliği denenir. Filesystem I/O arızasında kurtarma/rename de başarısız olabilir: otomatik prune çalıştırmayın, host/disk durumunu inceleyip şüpheli kopyayı ayrı restore ile doğrulayın.

Dosyalar: `database.age`, `manifest.json`, doğrulama sonrasında `verified.json`. Bir backup birimi bütün dizindir. Yalnız bir age dosyasını başka manifest ile karıştırmayın. SHA-256 kazara bozulmayı yakalar; manifest bir imza değildir. age ciphertext bütünlüğünü doğrular, gönderen kimliğini kanıtlamaz: recipient açık anahtarına sahip herkes yeni arşiv üretebilir. Özel backup dizini ve ayrı güvenilir digest/kaynak kaydı korunmalıdır. Güvenilmeyen kaynaktan SQL arşivi restore etmeyin.

## Doğrulama, durum ve zamanlama

```sh
python3 scripts/backup_ops.py verify --config /etc/siteyonetim/backup.json --backup BACKUP_DIZIN_ADI --identity /GUVENLI_AYRI_MEDYA/siteyonetim.agekey
```

Verify, age akışının **tamamını** çözer ve doğrular; pg_restore TOC/list kontrolü erken bitse bile kalan plaintext yalnız pipe üzerinden tüketilir. Liste kontrolü PG17 araç konteynerinde network=none/read-only/non-root çalışır. Backup kimliği kaynağın çevrimiçi olmasını gerektirmez; config şeması ve yerel dosyalar yine gerekir. Doğru anahtar ve dosyanın açılması tek başına veri kurtarma değildir; ayrı restore provası gerekir.

Status son başarılı dump+şifreleme zamanını (UTC) ve SHA'sı eşleşen kopya sayısını verir; bu decryption veya restore kanıtı değildir. `--max-age-hours 36` sağlıksız/eski/yok veya gelecekte zaman damgalı kopyada exit 2 döndürür; yerel izleme bu çıkış kodunu kullanabilir. Diğer hatalar exit 1, interrupt 130'dur. Araç veri/SQL/parola tanısını loglamaz; sabit hata ve güvenli sayılar verir. Ayrıntılı incelemeyi özel operatör oturumunda yapın; `set -x`, env dump veya anahtar içeriği yazdırmayın.

`ops/systemd/` servis/timer örnekleri varsayılan olarak devre dışıdır. Yolları gözden geçirip `/etc/systemd/system/` altına kurun. Örnek 03.00 host saat dilimindedir; gerekirse `OnCalendar=*-*-* 03:00:00 Europe/Istanbul` olarak düzenleyin ve `systemd-analyze calendar` ile doğrulayın. Açık etkinleştirme adımı:

```sh
systemctl daemon-reload
systemctl enable --now siteyonetim-backup.timer
systemctl list-timers siteyonetim-backup.timer
journalctl -u siteyonetim-backup.service
```

`Persistent=true` kaçırılan çalışmayı host açılışında telafi edebilir. Kernel flock aynı backup dizininde çakışmayı reddeder; hata systemd tarafından failed sayılır. Servis sandbox'ı Docker root yetkisini ortadan kaldırmaz. Anahtar kaybı/yanlış recipient riskini periyodik ayrı restore provasıyla kontrol edin. Uyarı servisi bağlamak isteğe bağlıdır; gerçek bildirim gönderimi bu kapsamda yoktur.

## Saklama ve ayrı kopya

Örnek retention 7 gün; config'te 1–3650 gün ayarlanabilir. Silme timer'da otomatik açık değildir:

```sh
python3 scripts/backup_ops.py prune --config /etc/siteyonetim/backup.json
# dry-run sayısını ve seçili dizini inceleyin; açık silme:
python3 scripts/backup_ops.py prune --config /etc/siteyonetim/backup.json --apply
```

En yeni tamamlanmış SHA-geçerli kopya ve varsa son decryption-verified kopya korunur. Eksik/bozuk kopyalar sağlam kopya sayılmaz ve otomatik silinmez. Yalnız işaretli özel dizindeki tam eşleşen backup adları ve bilinen dosyalar ele alınır; beklenmeyen adlar, partial'lar ve diğer dosyalar kapsam dışıdır. Symlink/hardlink kopyalar takip edilmez. Aynı UID/root kötü niyetli operatörü veya advisory flock'u bilerek atlayan yazıcıyı bu dosya politikası güvenlik sınırı yapmaz.

Tek diskteki şifreli yedek, **aynı diskin fiziksel kaybına karşı koruma sağlamaz**. Tüm backup dizinini (manifest dahil) erişimi kısıtlı ayrı/offline depoya çoğaltın; ayrı kopyada hash ve restore provası yapın. Şifreleme anahtarını ayrı tutun. Operatör saklama/KVKK, erişim, medya ömrü, anahtar kurtarma ve silme politikasını yazılı belirlemelidir. Şifreli dosya silmek snapshot/SSD üzerindeki tüm geçmiş kopyaları güvenli silmiş sayılmaz.

## Ayrı boş hedefe restore provası

İlk restore aracı yalnız açık seçilmiş **siteyonetim_test**, farklı PG cluster system_identifier ve portsuz izole Docker hedefine izin verir. Gerçek DB üzerine restore veya otomatik reset yoktur. Ayrı boş PG17 konteynerini operatör hazırlar; yeni hedef volume'unu gerçek volume ile karıştırmayın. Hedefte app/yazıcı çalışmaz. Identify ile hedefin tam kimliğini alın, 0600 hedef JSON'u oluşturun:

```json
{"purpose":"isolated-recovery-drill","binding":{"container_id":"HEDEFIN_TAM_64_HEX_ID_DEGERI","database":"siteyonetim_test","system_identifier":"HEDEFIN_SYSTEM_IDENTIFIER_DEGERI"}}
```

```sh
python3 scripts/backup_ops.py restore-drill --config /etc/siteyonetim/backup.json --backup BACKUP_DIZIN_ADI --identity /GUVENLI_AYRI_MEDYA/siteyonetim.agekey --target /etc/siteyonetim/recovery-target.json
```

Hedef cluster yalnız postgres/siteyonetim_test ve template DB'leri ile bilinen rollerden oluşmalı; postgres DB'de de kullanıcı tablosu bulunmamalıdır. Hedef bütün kullanıcı şema nesneleri bakımından boş olmalı; farklı/yanlış/dolu hedef reddedilir. Restore önce tam decrypt/list doğrular, sonra ayrı geçişte `pg_restore --exit-on-error --single-transaction` çalıştırır. Parola özeti/global rol dump'ı taşınmaz. Yalnız sabit sy_migrator/sy_runtime/sy_backup rolleri NOSUPERUSER/NOCREATEDB/NOCREATEROLE/NOREPLICATION/NOLOGIN olarak oluşturulur; owner, tablo/sütun/default ACL ve trigger'lar arşivden gelir. Runtime/migrator/backup rol limitleri sırasıyla 10/5/2'dir. Backup NOLOGIN ve SET ROLE kullandığından dump oturumları postgres bağlantısı sayılır; backup concurrency koruması rol limiti değil, aynı dizindeki CLI flock'udur. Başka özel rol gerektiren arşiv sessizce ACL atlayarak yüklenmez; operatör incelemesi gerekir.

Başarılı decrypt/restore sonrasında 11 migration (gelecekte incelenmiş prefix), checksum ve katalog/owner/index/constraint/function/trigger/ACL hash eşitliği aranır. Hedefte login/secret rotasyonu ayrı operatör adımıdır; gerçek sırlar kopyalanmaz. Gerçek kullanıma açmadan önce schema diff, doğru runtime kimliği/DDL reddi, uygulama sağlığı ve iş verisi/tenant/audit doğrulaması ayrıca gerekir. CI bunları sentetik finans probuyla ve standalone health ile sınar; gerçek kullanıcı verisinde sentetik probe çalıştırılmaz.

Restore esnasında araç hatası/host kesintisi varsa hedefi kirlenmiş kabul edin; aynı hedefe kör tekrar yapmayın. Orijinal DB'ye otomatik kopyalama yapılmaz. Hedefi inceleyin; gerekirse **yeni ayrı boş hedef** hazırlayın. SQL arşivleri kod içerebilir; yalnız güvenilir kendi backup'ınızı izole hedefte açın. Kurtarma başarısı ve erişim onayı olmadan trafik vermeyin. Güncelleme için [SAFE-UPGRADE](SAFE-UPGRADE.md), test sınırları için [S04-C kanıtı](S04C-BACKUP-VALIDATION.md).
