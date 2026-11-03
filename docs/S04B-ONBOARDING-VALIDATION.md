# S04-B — İlk kurulum doğrulaması

Durum: INCOMPLETE — son HEAD CI henüz bekleniyor. Yalnız DEVELOPMENT; production-ready değildir.

Başlangıç main `dbd378f10683379223971a73a46916cf365d20dd`, temiz çalışma ağacı; dal `codex/s04-b-onboarding-wizard`.

## Akış ve güvenlik

`/kurulum` oturumsuz kullanıcıyı girişe, doğrulanmamış kullanıcıyı mevcut e-posta ekranına yönlendirir. E-posta yapılandırması kullanılamıyorsa bu ekranda bağlantı/sır açıklamayan operatör mesajı vardır. Yeni kullanıcı doğrulama sonrası yönetim türü (INDIVIDUAL/COMPANY), organizasyon adı, site adı ve isteğe bağlı adres/açıklama ile tamamlar. Başarı sayfası kendi organizasyon/site kapsamlı panel bağlantısı sunar.

İlerleme mevcut PostgreSQL kayıtlarından türetilir. Yazım transaction'ı User FOR UPDATE kilidini actor'ın SHARE kilidinden önce alır; mevcut actor doğrulaması ve organizationAccess güncel üyelik kontrolü korunur. Aynı kullanıcının ilk kurulum yazımları serileşir, kilitten sonra mevcut durum yeniden sorgulanır. İkinci gönderim mevcut organizasyon/site sonucunu kullanır; yeni audit üretmez. Management normal işlemleri User SHARE kilidiyle bu yazımlarla uyumludur. Normal panelin kasıtlı çoklu organizasyon/site oluşturması tekilleştirilmez.

Organization/Site yaratma ve audit yazımları ortak transaction yardımcılarına çıkarıldı; management'ın mevcut doğrulama/yetki/audit davranışı korundu. Site opsiyonel alanları aynı oluşturma transaction'ında yazılır. Yeni migration/setupCompleted alanı gerekmedi. Finans servislerine, tarihsel migration'lara, schema veya LICENSE'a davranış değişikliği yapılmadı.

İstemci userId/role/step/siteId kabul edilmez; strict giriş şeması ve Server Actions kullanılır. OrganizationId yalnız hedef seçimidir, yetki sağlamaz. Membership kaldırılması sonraki işlem/okumada eski kapsamı kapatır. Yeni işlem doğrulama ve canlı session callback'ini tekrar kullanır. CSRF/origin koruması Next.js Server Actions katmanındadır; yeni browser testi saldırgan origin ile tekrar gönderimi reddeder.

Mevcut ADMIN/MANAGER organizasyonla devam edebilir; RESIDENT/legacy erişimleri yükseltilmez ve panel bağlantısı gösterilir. Davetli kullanıcı yeni yönetim kurmaya zorlanmaz. Panel otomatik kurulum yönlendirmesi yapmaz. Çoklu organizasyonda önce sitesi olmayan yönetim üyeliği, sonra ID sırasındaki ilk yönetim üyeliği seçilir. Bu, geçmiş kurulum kaydı değildir; son erişilebilir durumu gösterir. Yetkisi tamamen kaldırılmış kullanıcı açıkça yeni bir yönetim başlatabilir, eski organizasyonunu geri alamaz.

## Test tasarımı

- Yeni PostgreSQL entegrasyon senaryoları: session/doğrulama, iki yönetim türü, ADMIN/audit, opsiyonel site alanları, finans üretmeme, tekrar/eşzamanlılık, normal çoklu organizasyon, yabancı kapsam, sahte alanlar, hatalı ad/uzunluklar, mevcut roller, legacy ve üyelik iptali.
- Yeni Playwright senaryoları: anonim/doğrulanmamış erişim ve döngü olmaması; iki türde 390×844 mobil tam akış, geri/devam, yenileme, çıkış/yeniden giriş, CSRF, tamamlanma/kapsamlı panel; sunucu alan hatası, sahte rol, üyelik kaldırılması; RESIDENT/legacy/davetli uyumu.
- Docker selfhost kabulüne anonim `/kurulum` isteğinin `/giris` yönlendirmesi eklendi. Bu sınırlı standalone smoke testidir; selfhost içinde tam doğrulamalı kurulum veya gerçek SMTP kanıtı değildir.

## Yerel ilk sonuçlar

ESLint, TypeScript ve 25 birim başarılı; PostgreSQL 17 siteyonetim_test üzerinde 36 entegrasyon başarılı. İlk yeni E2E koşusu 4/5; tek hata Next route announcer ile alan alert'inin geniş seçicisi çakışmasıydı. Test seçicisi forma daraltıldı; düzeltilmiş yeni E2E koşusu 5/5 başarılı. Son HEAD tam regresyon ve CI sonuçları ayrıca kaydedilecektir. Production build başarılı. Büyük Docker build yerel VFS ortamında tekrarlanmaz; selfhost CI'da doğrulanır.

## Açık sınırlar

Gerçek SMTP/HTTPS teslimi, bağımsız insan kurulumu, yük/çoklu instance kabulü ve STAGING/PRODUCTION yoktur. User kilidi kullanıcı başına kurulum yazımlarını serileştirir; dış SQL yazıcıları aynı kilit sözleşmesine uymalıdır. Runtime DB sırrı uygulama yetki sınırının parçasıdır; RLS iddiası yoktur. Ortak hesap paylaşımları aynı kullanıcı ilerlemesini paylaşır. Normal panelden sonradan oluşturulan kayıtlar da ilerlemeye dahildir; silinmiş üyeliğin tarihçesi tutulmaz.

PUBLIC, ücretsiz yazılım, AGPL-3.0-only ve Supabase kullanmama kararı korunur. Ücretli servis, global superadmin, gerçek veri/e-posta, registry push, deploy, release/tag veya merge yoktur. S04-A tarihsel kanıtları değiştirilmez; S04-C yedek işletimi ayrı kapsamdır.
