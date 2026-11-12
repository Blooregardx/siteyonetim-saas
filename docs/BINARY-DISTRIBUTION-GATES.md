# Hazır imaj dağıtım kapıları

## S05-E güncel DEVELOPMENT çalışması

[Full native doğrulama](S05E-NATIVE-REBUILD-VALIDATION.md),
[tekrar üretim](S05E-NATIVE-REBUILD-REPRODUCTION.md) ve
[kaynak sunumu protokolü](S05E-SOURCE-PROVISION-PROTOCOL.md) eklendi.
Özgün Rocky base digest ve 241 tarihsel RPM işlemi geri kazanıldı; 28 native
kaynak yeniden doğrulandı. r-efi exact AUTHORS kanıtlarıyla dokuz açık Rust
kaydından ikisi kaynak/bildirim edinimi bakımından PASS, yedisi BLOCKED.
Native deney ve son HEAD CI sonuçları ayrıca değerlendirilir. İki runner
kopyası/restore provası sentetiktir; kalıcı kaynak sunumu veya hukuki onay değildir.
BINARY DISTRIBUTION READINESS: BLOCKED. Alpha.2 PUBLISHED — UNCHANGED.
INDEPENDENT INSTALLATION: PENDING HUMAN VALIDATION. Tarihsel S05-A/B/C/D
kanıtları aşağıda/depolarında korunur; bunlar yeni deneyin sonucu olarak kullanılmaz.


BINARY DISTRIBUTION READINESS: BLOCKED

Runtime ve migrate ayrı ürün envanterleridir. `scripts/collect_distribution.sh IMAGE OUTPUT` yerel Docker ID'sini sabitler; SHA-256 ile doğrulanmış açık kaynak Apache-2.0 Syft 1.18.1 ile squashed gerçek imajı tarar. Syft JSON kimlik kontrolü içindir; CycloneDX JSON paylaşılabilir SBOM'dur. Lock envanteri bu SBOM yerine kullanılamaz. Syft taraması da tüm statik/bundled native bileşenleri ve hukuki yükümlülükleri eksiksiz kanıtlamaz.

1. Sabit yerel Docker ID ile image save arşivi oluşturulur; arşiv config içeriğinin SHA-256 değeri ve SBOM `source.metadata.imageID` eşleşmeli; boş/dizin SBOM reddedilir. Sabit base digest ve build provenance ayrıca kaydedilmeli.
2. Her SBOM artifact ID için kesin isim/sürüm/imaj, SPDX, upstream ve binary-source eşleşmesi incelenmeli.
3. `evidence.json` kayıtlarında `name`, `version`, `imageID`, `upstream`, `binarySourceMatch`, `noticeEvidence`, `sourceProvision`, `relinking`, `reviewer`, `decision` bulunmalı. Kaynak/notice alanları doğrulanabilir dosya/hash/URL ve açıklama içermeli; uygulanmayan yükümlülük gerekçelendirilmeli.
4. LGPL native/static alt bağımlılıklar, MPL kapsanan dosyalar, Apache NOTICE ve MIT/BSD telif metinleri ayrıca incelenmeli. Otomatik kapı metin alanlarının hukuki doğruluğunu kanıtlayamaz; bakımcı manuel kanıt incelemesi zorunludur.
5. Uyumlu sürüme ait kaynak sunumu ve yeniden bağlama/kurulum provası olmadan native LGPL PASS verilemez. Debian copyright varlığı kaynak sağlama kanıtı değildir.
6. Kapı çıkış kodları: 0 bütün kayıtlar PASS; 1 dağıtım BLOCKED/UNKNOWN; 2 bozuk/eksik girdi. Kolektör boş kanıtla 1 bekler; CI başarısı dağıtım izni değildir. Dağıtım kararı için kapı doğrudan çalıştırılmalı ve manuel inceleme tamamlanmalıdır.

Kolektör uygulamayı başlatmaz; ağsız, salt okunur, capability'siz ve imajın kendi kullanıcısıyla dosya incelemesi yapar. Docker socket yalnız host araçlarına aittir. Ham inspect/env/log/secret toplanmaz. SBOM dosya yolları içerir; yayımlamadan önce inceleyin. Bilinmeyen/çözülemeyen lisanslar istisnayla gizlenmez.

Docker containerd store index ID / config ID ayrımı: özgün inspect ID `docker-inspect-id.txt`, aynı ID ile export edilmiş arşivin config SHA-256 değeri `image-id.txt` içinde tutulur. Syft aynı arşivi tarar; tag yeniden çözülmez. Config hash kimlik eşleşmesidir; publisher imzası değildir.

## S05-B kaynak/build incelemesi

[Kaynak doğrulaması](S05B-LIBVIPS-SOURCE-VALIDATION.md): 28 native kaynak girdisi ve 357 Rust transitif kayıt ayrı tutulur; binary provenance ve değiştirilmiş static-LGPL rebuild tamamlanmadı. LIBVIPS SOURCE EVIDENCE: PARTIAL; genel BINARY DISTRIBUTION READINESS: BLOCKED. S05-A tarihsel kanıtları değişmedi. Yeni imaj ELF/hash ve alternatif yükleme provası CI artifact'ındadır; dolu evidence metni native pakete PASS veremez. Node/Debian kaynak işleri ve bağımsız insan kurulumu açık kalır.

## S05-C kaynak ve rebuild kontrolü

357 dış Cargo kaydından 162 COMPILED, 195 UNKNOWN; kaynak edinimi 344 PASS/13 BLOCKED. Değiştirilmiş PNG/JPEG profili gerçek Sharp PNG yolunda başarılıdır; özgün bundle ABI ve statik girdiler eksiktir. Gate her durumda BLOCKED kalır; S05-C receipt hash'i yalnız izleme bağıdır, hukuki onay değildir. [Kanıt ve sınırlar](S05C-REBUILD-VALIDATION.md); [tekrar tarifi](LIBVIPS-REBUILD-REPRODUCTION.md).

## S05-D denetimi

Generated lock iki kontrollü çözümlemede aynı hash'i verdi; tarihsel upstream lock olarak onaylanmadı. Metadata, compiler-artifact ve LINKED kararları ayrıdır. 13 eski notice kaydında 4 PASS/9 BLOCKED yalnız kaynak/bildirim edinimidir. Native kayıtlardaki s05dFullBundleManifestSha256 salt kanıt izidir; genel dağıtımı açmaz. [Gerçek sonuç ve sınırlar](S05D-FULL-BUNDLE-VALIDATION.md); [kalıcı kaynak planı](CORRESPONDING-SOURCE-DISTRIBUTION-PLAN.md).
