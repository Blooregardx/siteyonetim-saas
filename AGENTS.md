# Geliştirme kuralları

- Next.js App Router, strict TypeScript, Prisma 6 ve PostgreSQL mimarisini koru.
- Tüm yönetim işlemlerinde sunucudaki `verifySession` ve `management` yetkilendirmesini kullan. İstemci userId değerlerini kimlik kabul etme.
- Tutarlar tam sayı kuruştur. Tahsilat satır kilidi, transaction, idempotency ve fazla ödeme reddini koru.
- Migration'lar veri kaybetmemeli. Üretimde reset, seed veya otomatik deploy çalıştırma.
- Testler yalnızca izole `siteyonetim_test` veritabanında çalışır.
- Demo veriyi `/panel` içine ekleme; örnekler `/demo` içinde açıkça işaretli kalsın.
- Secret, gerçek kişi verisi ve SMTP tokenlarını loglama/commit etme.
- Değişikliklerde lint, typecheck, birim, ilgili entegrasyon, build ve Playwright kontrollerini çalıştır; çalışmayanları raporla.

## Bütçesiz geliştirme kararı

- DEVELOPMENT, STAGING ve PRODUCTION durumlarını ayrı raporla. Staging/production bütçe nedeniyle ertelendi; harici servisleri kod/özellik tamamlanma koşulu yapma.
- Yalnız Codex Cloud ve mevcut GitHub altyapısıyla çalış. PostgreSQL 17 ve SMTP yalnız izole sentetik test ortamıdır; gerçek e-posta gönderme.
- Ücretli hesap, alan adı, servis veya dağıtım oluşturma; kullanıcı bilgisayarında kurulum isteme.
- Ertelenmiş operasyonları docs/DEFERRED-CLOUD-OPERATIONS.md içinde takip et.
- Kişileri ad eşitliğiyle otomatik birleştirme. Person kimliği, malik Ownership ilişkisi, kiracı Occupancy dönemi ve User hesabı ayrı kavramlardır.
- Eski Occupancy kayıtlarını ve finans geçmişini koru; yeni/güncelleme yazımlarını audit ile aynı transaction'da yap.
