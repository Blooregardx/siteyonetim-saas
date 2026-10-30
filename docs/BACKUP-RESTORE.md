# Sentetik yedekleme ve geri yükleme provası

Bu bir production yedekleme servisi değildir. Yalnız iki ayrı, geçici PostgreSQL 17 konteynerindeki `siteyonetim_test` içindir. Üretim/diğer proje DB'leri, gerçek kullanıcılar veya gerçek e-posta kullanılmaz. Başarılı izole prova PITR, RPO/RTO, şifreleme, saklama veya felaket kurtarma onayı değildir.

## Önkoşullar ve güvenlik

Linux üzerinde yerel Docker socket erişimi, Python 3, Node 24, npm bağımlılıkları ve Prisma Client gerekir. Kaynak ve hedef farklı konteyner olmalı; hedefin public şeması boş olmalıdır. Migration ve test fixture'ları kaynakta hazırdır. Hedefte dump'ın referans verdiği roller önceden kontrollü oluşturulmalıdır: pg_dump tek DB verisini taşır, global rolleri/parolaları oluşturmaz. Ayrı runtime rolü varsa hedefte aynı isim/uygun izin politikası hazırlanır; gerçek sırlar kopyalanmaz.

Kaynak uygulama/yazıcıları durdurun. pg_dump tutarlı snapshot alır; ayrıca hash karşılaştırması eşzamanlı yazmayı hata sayar. Bu betikler genel amaçlı üretim araçları değildir; restore aracı hedefi silmez/resetlemez ve dolu hedefte durur.

## Tekrarlama

1. İki izole PG17 konteynerinde ayrı boş `siteyonetim_test` hazırlayın; yalnız test yöneticisi `siteyonetim` kullanın. Gerçek ortamdaki kullanıcı/URL'leri kullanmayın.
2. Kaynak için DATABASE_URL ve TEST_DATABASE_URL aynı loopback test URL'si olsun. `npm ci`, `npm run db:generate`, `npm run db:validate`, `npm run db:deploy` çalıştırın. Fixture oluşturma bir yazma işlemidir, yalnız test DB'sinde yapılır.
3. Yerel özel geçici dosyada ID manifesti oluşturun:

```sh
npx tsx scripts/recovery-probe.ts create "$RUNNER_TEMP/recovery-fixture.json"
```

4. İki Docker konteynerinin adını/ID'sini OSS_TEST_SOURCE_CONTAINER ve OSS_TEST_RESTORE_CONTAINER değişkenlerinde açıkça seçin; sonra:

```sh
python3 scripts/verify-backup-restore.py
```

5. DATABASE_URL ve TEST_DATABASE_URL değerlerini aynı loopback **hedef** test DB URL'sine değiştirip aşağıdaki kontrolü çalıştırın:

```sh
npx tsx scripts/recovery-probe.ts verify "$RUNNER_TEMP/recovery-fixture.json"
npx prisma migrate status
npx prisma migrate diff --from-url "$DATABASE_URL" --to-schema-datamodel prisma/schema.prisma --exit-code
```

Hedef başka Docker ağ alanındaysa Node kontrolünü o konteynerin ağına bağlı geçici Node ortamından çalıştırın; test korumasını aşmak için hostname/path kontrollerini kaldırmayın. RUNNER_TEMP mevcut ve yalnız test artefaktları için ayrılmış olmalıdır.

## Neler karşılaştırılır?

PG custom format yedeği pg_restore --exit-on-error --single-transaction ile boş hedefe yüklenir. Tüm public tablo adları, tüm satırların sıralanmış JSON hash'leri/sayıları ve index/constraint/trigger tanımları karşılaştırılır. `_prisma_migrations`, kullanıcı/organizasyon ilişkileri, Payment/PaymentReversal ve AuditLog dahildir. Kaynak değişirse prova başarısız olur.

Uygulama probu: doğrulanmış sentetik admin, başka tenant, apartman/blok/daire, malik/kiracı, 10000 kuruş aidat, 4000 tahsilatın yetkili tam tersi ve 2500 yeni tahsilat. Beklenen brüt 6500, ters 4000, net 2500, borç 7500 kuruş. Başka tenant erişimi/ters kaydı, aynı ödemenin tekrar ters kaydı ve finans/audit UPDATE girişimleri reddedilmeli. 7 migration ve 10 ilgili site audit kaydı korunmalı.

## Sonuç ve sınır

OSS-04 otomatik provasında **21 tablo/442 satır** eşleşti; uygulama probu kaynakta ve geri yüklenmiş hedefte başarılı. [Kanıt](OSS04-VALIDATION.md). Dump/fixture/gerçek satırlar Git'e eklenmez; özel geçici dump doğrulama bitince araç tarafından kaldırılır. Yerel ilk keşif dump'ı da görev sonunda kaldırılır. CI aynı provayı iki servisle tekrarlar; her çalışmanın veri sayısı rastgele fixture sayısına göre değişebilir.

Production yedekleri hassastır: kullanıcı, parola özeti ve oturum bilgileri içerebilir. Gelecek işletimde şifreleme, erişim/saklama, rol yedeği, uygulama sürümü eşleme ve izole geri dönüş testi ayrı tasarlanmalıdır. Eski uygulamaya dönmek şemayı geri almaz; finans/audit geçmişi silinmez.
