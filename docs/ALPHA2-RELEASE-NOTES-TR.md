# v0.1.0-alpha.2 — Türkçe sürüm notu taslağı

**TASLAK — yayımlanmadı. EARLY DEVELOPMENT / ALPHA — NOT PRODUCTION READY.** Paket sürümü bu hazırlıkta yükseltilmez; mevcut v0.1.0-alpha.1 değişmez. Nihai commit/tag ve yayın tarihi ayrı bakımcı kararıdır. [Hazırlık kararı](ALPHA2-READINESS.md), [denetim](S03F-SECURITY-REGRESSION.md).

**Geliştirme hazırlığı:** F-10 sınırlı aidat sorgusuyla giderildi; düzeltmenin iki CI akışı başarılı. Karar READY FOR MAINTAINER REVIEW. Bu metin taslaktır; son HEAD kontrolleri ve ayrı kullanıcı yayımlama onayı gerekir.

## Alpha.1 sonrasında main’e alınan geliştirmeler

- S03-A / PR #11: en fazla 5.000 daire, önizleme/hash, idempotency ve çatışmada tam ret ile toplu aidat.
- S03-B / PR #12: borç/tahsilat raporları, vade ve dönem filtreleri; ADMIN kontrollü kısmi ödeme politikası ve sunucuda güncel bakiye kontrolü.
- S03-C / PR #13: apartman kapsamlı gelir/gider kategorileri, manuel işlem ve gerekçeli ADMIN tam ters kaydı; ödeme/işlem tarihine göre aylık finans özeti. Aidat tahakkuku nakit sayılmaz; tahsilat manuel gelire kopyalanmaz.
- S03-D / PR #14: iki güvenli CSV, Türkçe UTF-8, formula injection koruması, 50.000 satır / 128 MiB sınır, cursor snapshot’ı; 3/6/12 aylık karşılaştırmalar.
- S03-E / PR #15: tam organizasyon toplamlarıyla sınırlı panel okuma modelleri; sayfalanmış aidat, tahsilat, malik/kiracı ve kayıt geçmişi, daire/aidat araması ve sayfalar arasında toplu seçim. Main birleşmesi `afd7ea7bcfe693f06daeea9d48b38b8e1fe27fcc`.
- S03-F aday değişiklikleri: güvenlik/regresyon incelemesi, aidat/toplu işlem geçmişi için eklemeli DB değişmezlik koruması, akış tabanlı sentetik backup/restore hash doğrulaması ve ACL karşılaştırması; ek oturum/yetki/snapshot/CSV sınır testleri. Bunların sürüme dahil olması S03-F PR’sinin ayrı incelenmesine bağlıdır.

Mevcut kayıt/giriş, e-posta doğrulama/kurtarma, organizasyon/rol/davet, yapı/kişi ilişkileri, tahsilat ve immutable finans/audit davranışı korunur. Ters kayıt gerçek para iadesi değildir. Yazılım resmî muhasebe veya banka bakiyesi taahhüt etmez.

## Kurulum ve dağıtım kapsamı

Yalnız **proje kaynak kodu** alpha adayı; Node 24, Next.js 16, PostgreSQL 17, Prisma 6. Güncel şemada 11 migration vardır; tarihsel dosyalar değiştirilmez. [Kendi sunucusunda kurulum](SELF-HOSTING.md), [yedek/geri yükleme](BACKUP-RESTORE.md). Güncellemeden önce özel yedek ve izole prova gerekir; eski uygulamaya dönmek şemayı geri almaz, finans/audit kayıtları silinmez.

AGPL-3.0-only korunur: değiştirilmiş sürümü ağ üzerinden sunanlar etkileşen kullanıcılara karşılık gelen kaynak edinme olanağını sağlamalı; dağıtım koşullarını da karşılamalıdır. [Lisans](LICENSING.md) / [üçüncü taraf yükümlülükleri](THIRD-PARTY-LICENSES.md). Yazılımın ücretsiz olması sunucu/SMTP/alan adı hizmetinin ücretsiz olduğu anlamına gelmez. Binary/konteyner/node_modules/browser/dump dağıtımı bu hazırlığın parçası değildir; LGPL/MPL/NOTICE kapıları ayrıca açık.

## Bilinen sınırlamalar

- Gerçek SMTP teslimi, bağımsız insan kurulumu, canlı güvenlik/yük ve tam işletim/izleme doğrulaması yapılmadı; MFA yok.
- Tek kullanıcılı sentetik 10.000 daire/60.000 aidat regresyonu üretim kapasitesi/çok kullanıcılı SLA değildir. 5.000 aidat yazımının production yükü ayrıca doğrulanmalı.
- OFFSET ve ayrı HTTP snapshot’ları eşzamanlı eklemede sayfa kaydırabilir. Tam sayfa navigasyonu gönderilmemiş ana formu yeniler; toplu seçim kendi sayfalarında korunur.
- CSV açıklamaları kişisel bilgi içerebilir; otomatik redaksiyon yok. Sunucu/indirme dosyası ve yedekler hassastır.
- Dev lint ağacında minimatch advisory’si ve lint/Actions runtime bakım işleri açık. Üretim rate-limit/bot, minimum roller, TLS/proxy, şifreleme/PITR/RPO/RTO ve olay müdahalesi tamamlanmadı.
- Sentetik restore başarısı gerçek felaket kurtarma garantisi değildir; yeni hash yöntemi PostgreSQL sıralama/geçici disk maliyetini kaldırmaz.

DEVELOPMENT doğrulamaları STAGING veya PRODUCTION onayı değildir. Yayımlama, merge ve tag için ayrı kullanıcı kararı gerekir; bu taslak bunları gerçekleştirmez.
