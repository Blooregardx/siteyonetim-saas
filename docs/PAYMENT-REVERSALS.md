# Tahsilat ters kayıt tasarımı — sonraki görev

Bu görevde ters kayıt servisi veya migration uygulanmadı; mevcut Payment/Charge değiştirilmez ve silinmez. Canlı tahsilat düzeltme ucu yoktur. Kapsam, doğrulama/davet/audit güvenliğini tamamlamakla sınırlandı.

Önerilen eklemeli PaymentReversal modeli: id, siteId, paymentId, amountKurus, reasonCode, actorId, createdAt, idempotencyKey. (siteId,paymentId) Payment bileşik yabancı anahtarı; paymentId UNIQUE ilk sürümde yalnız tam ters kayıt sağlar. (siteId,idempotencyKey) UNIQUE; pozitif amountKurus CHECK. Tutar, özgün ödeme tutarıyla sunucuda eşleştirilir. Serbest kişisel veri içerebilen açıklama yerine kontrollü reasonCode kullanılır.

ADMIN yetkisi ve doğrulanmış oturum gerekir. Organizasyon → Charge → Payment kilit sırası korunur. Ters kayıt, audit ve gerekli ilişki kontrolleri tek transaction içindedir. Net tahsilat=Payment toplamı−PaymentReversal toplamı; dashboard ve fazla ödeme kontrolü aynı net hesabı kullanacak şekilde birlikte değiştirilmelidir. Aynı anahtar aynı içerikte aynı sonucu, farklı içerikte conflict verir. İkinci ters kayıt reddedilir. Yanlış ters kaydın telafisi eski satırı silerek yapılmaz; yeni ve açıkça ilişkilendirilmiş düzeltme olayı ayrı tasarlanır.

Uygulamadan önce zorunlu test planı:

1. Oturumsuz, doğrulanmamış, MANAGER/RESIDENT ve başka organizasyon ADMIN reddi.
2. Başka site ödeme referansının bileşik FK ile reddi.
3. Tam ters kayıtta net tahsilat ve kalan borç; orijinal Payment'ın byte/tutar ve kimliğinin korunması.
4. Aynı isteğin seri/paralel tekrarında tek reversal ve tek audit; farklı içerikle aynı anahtar reddi.
5. Aynı ödeme için farklı anahtarlarla paralel ters kayıtta yalnız bir başarı.
6. Tahsilat ile ters kaydın yarışında bakiye tutarlılığı ve fazla ödeme reddi.
7. Audit yazımı arızasında reversal rollback; Payment ve audit immutable kısıtları.
8. Gerçek runtime rolünde Payment UPDATE/DELETE ve Audit UPDATE/DELETE/TRUNCATE reddi.

Bu testler henüz uygulanmış/başarılı sayılmaz. Tasarım devreye girene kadar hatalı tahsilat düzeltmeleri desteklenmiyor.
