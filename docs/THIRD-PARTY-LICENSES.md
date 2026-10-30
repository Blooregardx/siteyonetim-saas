# Üçüncü taraf lisans incelemesi — OSS-02

Projenin AGPL-3.0-only lisansı bağımlılıkları yeniden lisanslamaz. [Envanter](DEPENDENCY-LICENSES.csv), package-lock.json packages alanından yol/sürüm/lisans/dev/optional bilgileriyle üretildi. Aynı paketin farklı sürümleri ve platform paketleri ayrı satırdır; sayı kurulu runtime paket sayısı değildir.

Doğrudan runtime: Prisma Client Apache-2.0; Next.js, React/React DOM ve Zod MIT; Nodemailer MIT-0. Doğrudan geliştirme araçları MIT, MIT-0 veya Apache-2.0 bildirir. Bu lisanslarda AGPL-3.0-only ile kullanım için engel tespit edilmedi. Yükümlülükler ve özgün bildirimler korunur.

İnceleme yöntemi: kilitte tüm paketlerin lisans alanı tarandı; ana bağımlılıklar ile Sharp, axe-core, caniuse-lite, argparse ve BlueOak lisanslı minimatch'in kurulu LICENSE/NOTICE dosyaları incelendi. Next.js/TypeScript/Playwright içindeki üçüncü taraf bildirimleri de korunmalıdır. Kaynak ağaçta ayrı vendored kod/telif bildirimi bulunduğuna ilişkin kanıt çıkmadı. Bu kontrol kapsamlı kaynak kökeni ispatı veya bütün platformların binary denetimi değildir.

| Grup | Yükümlülük / değerlendirme |
|---|---|
| MIT, MIT-0, ISC, BSD, 0BSD, BlueOak-1.0.0 | Lisansa göre telif/izin bildirimlerini koru; izin verici bileşenler |
| Apache-2.0 | Lisans, değişiklik ve uygulanabilir NOTICE/patent hükümlerini koru |
| Sharp/libvips LGPL-3.0-or-later ve birleşik lisanslar | Bileşenleri kendi lisansında tut; dağıtılan binary için ilgili kaynak, değiştirme/yeniden bağlama ve kurulum bilgisi yükümlülüklerini değerlendir; libvips bağımlılık bildirimlerini topla |
| axe-core MPL-2.0 | Kapsanan dosya değişiklikleri ve kaynak/bildirim koşullarını koru; ayrı lint/aracın varlığı bütün projeyi MPL yapmaz |
| caniuse-lite CC-BY-4.0 | Veri kaynağının atıf, lisans ve değişiklik bildirimini koru |
| argparse Python-2.0 | Birlikte gelen tarihsel lisans/telif metinlerini koru |
| language-subtag-registry CC0-1.0 | Kamusal veri feragat metnini/kaynağını kaydet |

Registry tarball kontrolünde libvips Linux x64 ve language-subtag-registry paketlerinde LICENSE adlı dosya bulunmadı; bunların lisans beyanı registry/kilit metaverisinden gelir. Bu, uyumsuzluk kanıtı değildir; binary/konteyner yayımlamadan önce ilgili upstream sürümün tam kaynak ve bildirim dosyaları ayrıca toplanmalıdır. Diğer platformlardaki isteğe bağlı binaryler çalıştırılmadı. Bu PR binary/konteyner dağıtmaz; paket sürümlerini değiştirmez.

Gelecek release kontrolü: dağıtımın gerçek bileşen listesini çıkarın, özgün LICENSE/NOTICE dosyalarını pakete dahil edin, LGPL/MPL kaynak yükümlülüklerini doğrulayın ve yayımlanan sürüme karşılık gelen kaynak arşivini sağlayın. Genel upstream deposuna bağlantı yerel değişiklikler için tek başına yeterli değildir. Önemli yeni köken/uyumluluk belirsizliği çıkarsa dağıtımı durdurun.

Kaynaklar: [GNU LGPL v3](https://www.gnu.org/licenses/lgpl-3.0.html), [Mozilla MPL 2.0](https://www.mozilla.org/en-US/MPL/2.0/), [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), [libvips](https://github.com/libvips/libvips).

## Kilit metaverisi özeti

- 0BSD: 1 kayıt
- Apache-2.0: 45 kayıt
- Apache-2.0 AND LGPL-3.0-or-later: 3 kayıt
- Apache-2.0 AND LGPL-3.0-or-later AND MIT: 1 kayıt
- BSD-2-Clause: 8 kayıt
- BSD-3-Clause: 3 kayıt
- BlueOak-1.0.0: 1 kayıt
- CC-BY-4.0: 1 kayıt
- CC0-1.0: 1 kayıt
- ISC: 18 kayıt
- LGPL-3.0-or-later: 10 kayıt
- MIT: 383 kayıt
- MIT-0: 2 kayıt
- MPL-2.0: 1 kayıt
- Python-2.0: 1 kayıt
