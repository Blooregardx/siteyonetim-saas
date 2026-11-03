# Hazır imaj dağıtım kapıları

BINARY DISTRIBUTION READINESS: BLOCKED

Runtime ve migrate ayrı ürün envanterleridir. `scripts/collect_distribution.sh IMAGE OUTPUT` yerel Docker ID'sini sabitler; SHA-256 ile doğrulanmış açık kaynak Apache-2.0 Syft 1.18.1 ile squashed gerçek imajı tarar. Syft JSON kimlik kontrolü içindir; CycloneDX JSON paylaşılabilir SBOM'dur. Lock envanteri bu SBOM yerine kullanılamaz. Syft taraması da tüm statik/bundled native bileşenleri ve hukuki yükümlülükleri eksiksiz kanıtlamaz.

1. Yerel imaj ID ve SBOM `source.metadata.imageID` eşleşmeli; boş/dizin SBOM reddedilir. Sabit base digest ve build provenance ayrıca kaydedilmeli.
2. Her SBOM artifact ID için kesin isim/sürüm/imaj, SPDX, upstream ve binary-source eşleşmesi incelenmeli.
3. `evidence.json` kayıtlarında `name`, `version`, `imageID`, `upstream`, `binarySourceMatch`, `noticeEvidence`, `sourceProvision`, `relinking`, `reviewer`, `decision` bulunmalı. Kaynak/notice alanları doğrulanabilir dosya/hash/URL ve açıklama içermeli; uygulanmayan yükümlülük gerekçelendirilmeli.
4. LGPL native/static alt bağımlılıklar, MPL kapsanan dosyalar, Apache NOTICE ve MIT/BSD telif metinleri ayrıca incelenmeli. Otomatik kapı metin alanlarının hukuki doğruluğunu kanıtlayamaz; bakımcı manuel kanıt incelemesi zorunludur.
5. Uyumlu sürüme ait kaynak sunumu ve yeniden bağlama/kurulum provası olmadan native LGPL PASS verilemez. Debian copyright varlığı kaynak sağlama kanıtı değildir.
6. Kapı çıkış kodları: 0 bütün kayıtlar PASS; 1 dağıtım BLOCKED/UNKNOWN; 2 bozuk/eksik girdi. Kolektör boş kanıtla 1 bekler; CI başarısı dağıtım izni değildir. Dağıtım kararı için kapı doğrudan çalıştırılmalı ve manuel inceleme tamamlanmalıdır.

Kolektör uygulamayı başlatmaz; ağsız, salt okunur, capability'siz ve imajın kendi kullanıcısıyla dosya incelemesi yapar. Docker socket yalnız host araçlarına aittir. Ham inspect/env/log/secret toplanmaz. SBOM dosya yolları içerir; yayımlamadan önce inceleyin. Bilinmeyen/çözülemeyen lisanslar istisnayla gizlenmez.
