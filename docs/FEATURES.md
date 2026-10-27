# Özellik durumu

Çalışan: kayıt/giriş/çıkış, PostgreSQL oturumları, korumalı panel, bireysel/şirket organizasyonu oluşturma ve seçim, organizasyon üyeliğiyle veri ayrımı, apartman/blok/daire oluşturma-listeleme, malik/kiracı kaydı, aidat oluşturma ve listeleme, nakit/havale kısmi tahsilat ve ödeme geçmişi. Sayaçlar ve finans özeti PostgreSQL sorgularından gelir. Yeni organizasyon oluşturma sahibine ADMIN üyeliği verir; bir kullanıcı birden çok organizasyon oluşturabilir.

Demo: `/demo` ve `/demo?view=company`, eski panel tasarımı ve açıkça etiketli örnek veriler.

Yapılandırma bekleyen: gerçek SMTP ile parola kurtarma teslimi.

Eksik: davet/üyelik ve rol düzenleme ekranı, mevcut kayıt güncelleme/silme, kat alanı, oturum bitiş düzenleme, kişi tekilleştirme, toplu borçlandırma, audit ve ters kayıt. Gelir/gider, rapor, personel ve diğer gelişmiş modüller geliştirme aşamasındadır. Fazla ödeme bilinçli olarak reddedilir.

## S01-C ile güncellenen durum

Önceki eksik listesindeki e-posta doğrulama, davet/üyelik/rol ekranları, audit log ve token temizliği uygulanmıştır. ADMIN/MANAGER/RESIDENT modeli korunur. Yeni ekranlar `/eposta-dogrula`, `/uyeler`, `/davet`. Eski doğrulanmamış hesapların yetkisi aktivasyona kadar engellenir. Finansal ters kayıt hâlâ yalnız belgeli tasarımdır; canlı düzeltme işlevi yoktur.

## S01-D

Tam ters kayıt servisi ve panel onay/gerekçe/geçmiş arayüzü artık çalışır. Net tahsilat, ters kayıt sonrası borç ve yeniden ödeme bütün canlı finans görünümlerine bağlandı. Gerçek para iadesi, kısmi ters kayıt ve ters kaydın kendisini düzeltme işlevleri yoktur.

## Güncel DEVELOPMENT — S02-A

İzole testlerle doğrulanan uygulama kapsamı: apartman adı/adres/açıklama düzenleme; blok adı/açıklama; daire numarası/kat/tür/kullanım durumu; numara/blok/kat/tür/durum filtreleri; organizasyon kapsamlı Person; çoklu daire ve çoklu malik ilişkisi; ayrı Ownership/Occupancy; giriş/çıkış ve korunmuş dönem geçmişi; legacy görünümü; server yetki ve transaction içi audit.

STAGING ve PRODUCTION bütçeyle ertelendi; DEVELOPMENT tamamlanmasının koşulu değildir. Önceki özellik listeleri tarihsel kapsamı anlatır; uygulanmış yeni güncellemeler artık eksik sayılmaz. Silme, blok taşıma, ortaklık payı, kişi birleştirme, kişi adı düzenleme ve eski OWNER kaydını normalize etme bu sürümde uygulanmadı.
