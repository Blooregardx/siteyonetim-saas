# S01-D — tam tahsilat ters kaydı

## Uygulanan model

PaymentReversal ayrı ve eklemeli finansal kayıttır: id, siteId, paymentId, amountKurus, reasonCode, actorId, createdAt, idempotencyKey. İlk sürüm yalnız tam ters kaydı destekler; kısmi tahsilatın kaydedilmiş tutarının tamamı da ters kaydedilebilir. Payment satırı değiştirilmez/silinmez. Bu işlem gerçek banka/nakit iadesi yapmaz.

- paymentId UNIQUE: bir ödeme için tek ters kayıt.
- (siteId,idempotencyKey) UNIQUE: site kapsamında idempotency.
- (siteId,paymentId,amountKurus) FK → Payment(siteId,id,amountKurus): aynı apartman ve özgün tutarla eşitlik DB'de zorunlu.
- actorId FK → User; amountKurus > 0 CHECK; enum gerekçe ve UUID CHECK.
- Gerekçeler: DUPLICATE_ENTRY, WRONG_AMOUNT, WRONG_CHARGE, ENTRY_ERROR.
- Payment ve PaymentReversal UPDATE/DELETE/TRUNCATE işlemleri trigger ile reddedilir. Audit koruması devam eder. DBA/sahip trigger'ı kaldırabilir; runtime tablo sahibi değildir.

## Servis ve işlem sırası

`management.reversePayment` doğrulanmış kullanıcıyı okur, organizasyon satırını kilitler ve ilgili organizasyonda ADMIN üyeliği ister. Doğrudan apartman ADMIN ataması tek başına yeterli değildir; organizasyonsuz eski site için otomatik istisna yoktur. Ardından aynı siteye ait Payment okunur, Charge → Payment FOR UPDATE kilitlenir. Aynı borçta collect de organizasyon → Charge sırasını kullanır.

Önce idempotency kontrolü yapılır: aynı ödeme/gerekçe/anahtar önceki sonucu döndürür; farklı ödeme veya gerekçe aynı anahtarla conflict olur. Başka anahtarla ikinci ters kayıt ALREADY_REVERSED verir. Tutar istemciden alınmaz, özgün ödemeden kopyalanır. Reversal ve PAYMENT_REVERSE audit aynı transaction'dadır; audit arızası işlemi geri alır. Başarılı tekrar ikinci audit üretmez.

## Merkezi hesap

`paymentTotals`, `chargeBalance`, `financialSummary` kuruş cinsinden güvenli tam sayı hesabı yapar:

- Brüt tahsilat = Payment toplamı
- Ters kayıt = PaymentReversal toplamı
- Net tahsilat = brüt − ters kayıt
- Kalan borç = tahakkuk − net tahsilat

Kısmi ters kayıt veya güvenli tam sayı sınırını aşan toplam reddedilir. Dashboard, aidat, daire borcu, ödeme geçmişi ve yeni ödeme kabul kontrolü bu fonksiyonları kullanır. Bakiye için ikinci, değişebilir alan tutulmaz. Tam ters kayıttan sonra yeniden ödeme alınabilir; eski ödemenin idempotent tekrarı yeni tahsilat oluşturmaz.

Yarışta önce collect kilidi alırsa o anda yeterli bakiye yoksa OVERPAYMENT alır; ters kayıt kilidi önce alırsa yeni ödeme açılan bakiyeye uygulanabilir. Her durumda borç aşılmaz. Başarısız tahsilat ters kayıttan sonra yeni talep olarak yeniden denenebilir.

## Arayüz

/panel mevcut tasarımında brüt/net/ters kayıt/kalan borcu gösterir. Her tahsilat için ADMIN gerekçe seçer, tutar ve iade yapılmadığı açıklamasını içeren ayrı onay adımından geçer. Vazgeçme yazım yapmaz. Diğer roller kontrolü görmez; eski açık form veya sahte istemci rolü sunucuda yetki sağlamaz. Geçmişte orijinal ödeme, gerekçe, ters kayıt tutarı, tarih ve kullanıcı adı görünür.

## Sekiz zorunlu senaryonun uygulanması

`tests/reversals.integration.ts` sekiz isimli test içerir:

1. Oturumsuz, doğrulanmamış, MANAGER/RESIDENT, sahte kullanıcı ve başka organizasyon ADMIN reddi.
2. Başka site, farklı tutar, sıfır tutar, geçersiz enum/UUID, mükerrer ödeme ve DB immutable kısıtları.
3. Kısmi tahsilatın tam tersi; orijinal Payment birebir korunumu; dashboard/daire bakiyesi; yeni ödeme ve fazla ödeme reddi.
4. Seri/paralel aynı anahtar, farklı içerik conflict, tek audit.
5. Farklı anahtarlarla paralel ters kayıtta tek başarı.
6. Tahsilat/ters kayıt yarışı ve net bakiyenin korunması.
7. Gerçek DB audit arıza enjeksiyonunda rollback, Payment/Audit değişmezliği.
8. Ayrı LOGIN runtime/migration rolleri; migration rolüyle izole şemada tüm migration'ların uygulanması; runtime ile başarılı collect/reverse ve yasak UPDATE/DELETE/TRUNCATE/DDL denemeleri.

Playwright ayrıca onay/vazgeçme, rol düşürülmüş açık formdan sahte ADMIN girişimi, ters kayıt geçmişi/net bakiye ve yeniden ödemeyi doğrular. Önceki kimlik/SMTP/üyelik testleri korunur. Kesin çalıştırma sonuçları S00-S01-REPORT.md içindedir.

## Sınırlar

Ters kaydı geri almak veya düzeltmek için mevcut reversal silinmez; yanlış ters kaydın telafisi ayrı iş kuralı gerektirir ve bu sürümde yoktur. Banka/kart, gerçek iade, alacak/fazla ödeme ve gider muhasebesi kapsam dışıdır. Gerçek bulut rol/TLS/edge/yedek/izleme kurulumu operasyonel kapanışta açık kalır.
