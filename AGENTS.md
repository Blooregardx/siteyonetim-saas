# Geliştirme kuralları

- Next.js App Router, strict TypeScript, Prisma 6 ve PostgreSQL mimarisini koru.
- Tüm yönetim işlemlerinde sunucudaki `verifySession` ve `management` yetkilendirmesini kullan. İstemci userId değerlerini kimlik kabul etme.
- Tutarlar tam sayı kuruştur. Tahsilat satır kilidi, transaction, idempotency ve fazla ödeme reddini koru.
- Migration'lar veri kaybetmemeli. Üretimde reset, seed veya otomatik deploy çalıştırma.
- Testler yalnızca izole `siteyonetim_test` veritabanında çalışır.
- Demo veriyi `/panel` içine ekleme; örnekler `/demo` içinde açıkça işaretli kalsın.
- Secret, gerçek kişi verisi ve SMTP tokenlarını loglama/commit etme.
- Değişikliklerde lint, typecheck, birim, ilgili entegrasyon, build ve Playwright kontrollerini çalıştır; çalışmayanları raporla.
