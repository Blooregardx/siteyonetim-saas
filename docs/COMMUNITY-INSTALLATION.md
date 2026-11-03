# SiteYönetim’i Docker ile Kur — Adım Adım

Bu rehber S04-A–D araçlarını içeren incelenmiş kaynak commit'i içindir. **EARLY DEVELOPMENT / ALPHA — production-ready değildir.** Yazılım ücretsiz, PUBLIC ve AGPL-3.0-only; Supabase, abonelik veya lisans anahtarı gerekmez. Sunucu, alan adı ve e-posta işletmeciye maliyet çıkarabilir. Bu rehberde kullanıcıya gerçek sunucu kurdurulmadı; otomatik prova insan kurulumu değildir.

## 1. Ortamı seçin

İlk kabul kapsamı Linux x86-64 ve Docker Engine + Compose v2 veya yeni uyumlu Compose plugin'idir. Ubuntu/Debian üzerinde Docker'ın resmî dağıtım yönergelerini kullanın: [Docker Engine](https://docs.docker.com/engine/install/), [Compose plugin](https://docs.docker.com/compose/install/linux/). macOS/Windows Docker Desktop, ARM ve rootless/user namespace eşlemeleri bu kabulün kanıtı değildir. Bunlar için ayrı doğrulama gerekir; ücretli ürün zorunluluğu yoktur.

Host'ta Git, Python 3 ve OpenSSL gerekir. Node.js 24 ve PostgreSQL 17 Docker imajlarından gelir; Docker kurulumu için host npm bağımlılığı hazırlamanız gerekmez. Backup işletiminde ayrıca host age/age-keygen gerekir. Docker socket erişimi host root yetkisine eşdeğerdir; bunu web uygulamasına vermeyin. Başlangıç için kaynak filesystem'inde ve erişilebiliyorsa Docker data filesystem'inde en az 10 GiB boş alan ön kontrol eşiğidir, kapasite garantisi değildir. Docker data dizini host'tan okunamıyorsa araç açık uyarı verir; operatör ayrıca denetlemelidir. VFS, eski/yeni imajlar, veri ve ayrı yedek alanı daha fazlasını gerektirir; gerçek veri boyutuna göre planlayın.

```sh
docker version
docker compose version
python3 --version
openssl version
```

## 2. GitHub’dan kaynak alın

Alpha.2 kaynak-only ön sürümü yayımlandı: `v0.1.0-alpha.2`, kesin commit `c20646fddbc8a7e3dcd45cbc01aacd531c225e4a`. Hazır Docker dağıtımı halen engellidir. Yeni kurulumda hareketli main yerine bu sabit kaynağı seçin.

```sh
git clone https://github.com/Blooregardx/siteyonetim-saas.git
cd siteyonetim-saas
git switch --detach c20646fddbc8a7e3dcd45cbc01aacd531c225e4a
git rev-parse HEAD
```

Bu PR henüz birleşmediyse main'de yeni ön kontrol bulunmayabilir; PR'nin tam SHA'sını inceleme için seçin. Kaynak arşivi kullananlar aynı commit arşivini açmalıdır. Hazır binary/container dağıtımı onaylanmış değildir; yerel kaynak build'i farklı işlemdir. [Lisans sınırları](THIRD-PARTY-LICENSES.md).

## 3. Yapılandırma ve şifreleri hazırlayın

Yeni, boş kurulum dizininde aşağıdaki adımlar uygulanır. Mevcut secret/volume'u üzerine yazarak düzeltmeyin. Gerçek secret değerlerini komut satırına, geçmişe, issue'ya veya Git'e koymayın.

```sh
umask 077
cp .env.selfhost.example .env.selfhost
mkdir -m 700 secrets
openssl rand -hex 32 > secrets/db_password
openssl rand -hex 32 > secrets/migrator_password
openssl rand -hex 32 > secrets/runtime_password
: > secrets/smtp_url
chmod 600 .env.selfhost
# Standart Debian imajları: node UID=1000, postgres GID=999.
sudo chown 1000:999 secrets/*
sudo chmod 640 secrets/*
```

`.env.selfhost` dosyasını güvenilir editörle açın: POSTGRES_DB için basit PostgreSQL adı, APP_URL için yalnız HTTPS origin, gerçek e-posta için MAIL_FROM ve istenen loopback APP_PORT (varsayılan 3000) girin. Örnek alan adı gerçek TLS kurulumu değildir.

SMTP_URL değerini `secrets/smtp_url` içine güvenilir editörle, dosya sahibine uygun kontrollü operatör yetkisiyle girin; `smtps://` veya zorunlu STARTTLS kullanan `smtp://` gerekir. Bu dosyanın boş olması yalnız demo/smoke incelemesine izin verir; kayıt/doğrulama/kurtarma tamamlanmış sayılmaz. Bu rehber SMTP sağlayıcısı açmaz veya gerçek e-posta göndermez. Secret dosyalarını herkesçe okunabilir yapmayın. Rootless veya farklı UID/GID kullanıyorsanız ayrı izin eşlemesi doğrulayın; örnek izinleri körlemesine genişletmeyin.

## 4. Ön kontrolü çalıştırın

```sh
sh scripts/selfhost-preflight.sh
# Gerçek hesap/doğrulama kullanımı öncesi eksik mail ayarını hata saymak için:
sh scripts/selfhost-preflight.sh --require-mail
```

Araç salt okunurdur; daemon/servis başlatmaz, chmod/chown veya volume düzeltmesi yapmaz. Çıktıda değerler yerine sabit hata/uyarı kodları vardır. `ok: true` TLS sertifikası veya SMTP tesliminin doğrulandığı anlamına gelmez. Port zaten çalışan app'e aitse port kontrolü başarısız olur; bu araç ilk başlangıç öncesi içindir. [Hata kodları ve güvenli teşhis](TROUBLESHOOTING.md).

## 5. Build → DB → migration → app sırası

```sh
docker compose --env-file .env.selfhost -f compose.selfhost.yaml config --quiet
docker compose --env-file .env.selfhost -f compose.selfhost.yaml --profile tools build
docker compose --env-file .env.selfhost -f compose.selfhost.yaml up -d db
docker compose --env-file .env.selfhost -f compose.selfhost.yaml run --rm migrate
docker compose --env-file .env.selfhost -f compose.selfhost.yaml up -d --wait app
docker compose --env-file .env.selfhost -f compose.selfhost.yaml ps
curl --fail --silent http://127.0.0.1:3000/demo > /dev/null
```

APP_PORT değiştiyse curl adresini o portla kullanın. PostgreSQL 17 named volume'a yazar; varsayılan DB portu yayınlanmaz. App yalnız 127.0.0.1 üzerinde erişilir. İlk boş volume init'i sy_migrator ve sy_runtime rollerini hazırlar; 11 migration ayrı migrate işleminde uygulanır. App root olmayan kullanıcıyla ve DDL yetkisi olmayan rolle çalışır; migration her restart'ta çalıştırılmaz. Eksik/başarısız migration veya runtime DDL yetkisi app başlangıcını reddeder.

`ps` app/db sağlığını gösterir. `/demo` örnek veridir. Oturumsuz `/kurulum` girişe yönlenmelidir; `/panel` App Router streaming yönlendirmesi de kullanabilir, yalnız HTTP 200 görmek yönetim erişimi kanıtı değildir. Build başarısı tek başına çalışan imaj kanıtı değildir. `down -v`, reset veya volume silme kurulum adımı değildir.

## 6. HTTPS ve ilk hesabı tamamlayın

Host ters proxy'sini loopback app portuna yönlendirin; güvenilir sertifika ve HTTPS yönlendirmesi kurun. App/DB portlarını doğrudan internete açmayın. Gerçek kullanımda HTTPS zorunludur; CI'ın localhost sentetik HTTP smoke testi bir production istisnası değildir.

SMTP TLS/STARTTLS, MAIL_FROM, SPF/DKIM/DMARC ve gerçek teslimi operatör ayrıca doğrular. Sonra HTTPS üzerinden `/kayit` ile kendi hesabınızı açın, e-postayı doğrulayın, `/kurulum` içinde yönetim türü → organizasyon → ilk apartman/site adımlarını tamamlayın. Normal panelde yeni ve sitesi eksik kullanıcı için devam bağlantısı vardır; mevcut üyeler/davetliler zorlanmaz. Global admin/demo parolası veya otomatik finans kaydı oluşturulmaz.

## 7. Backup ve güncelleme

[Yedek işletimi](BACKUP-OPERATIONS.md) ayrı host age anahtarı, şifreli pipe, özel backup dizini, isteğe bağlı systemd timer ve retention adımlarını açıklar. Timer/silme varsayılan etkin değildir. Private key kaybı yedeği erişilemez kılar; aynı fiziksel disk bozulmasına karşı ayrı kopya gerekir. Günlük dump WAL/PITR değildir.

[Güvenli güncelleme](SAFE-UPGRADE.md): incelenmiş commit/image/DB kimliği → bakım modu/yazıcı kontrolü → şifreli backup/verify ve ayrı restore → yeni build → ayrı migration → schema/health. Başarısızlıkta otomatik eski backup'ı mevcut DB üzerine yüklemeyin veya eski imajı körlemesine başlatmayın.

## 8. Sorun ve destek

Önce [TROUBLESHOOTING](TROUBLESHOOTING.md) ve [güvenlik politikası](../SECURITY.md). Commit, Linux/Docker/Compose sürümü ve sabit preflight kodları güvenle raporlanabilir. Raw env/secret/backup/age key, oturum tokenı veya gerçek kullanıcı verisi eklemeyin. App/DB logları kişisel veri içerebilir; ham log yüklemeyin. Gönüllü alpha geliştirme desteği vardır; SLA/LTS veya yanıt süresi garantisi yoktur. [Katkı rehberi](../CONTRIBUTING.md).

Teknik ayrıntılar ve tarihsel sınırlar [SELF-HOSTING-DOCKER](SELF-HOSTING-DOCKER.md); otomatik temiz kaynak kanıtı ve insan testi ayrımı [S04-D raporunda](S04D-DISTRIBUTION-VALIDATION.md).
