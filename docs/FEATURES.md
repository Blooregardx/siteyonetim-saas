# Özellik durumu

Çalışan: kayıt/giriş/çıkış, PostgreSQL oturumları, korumalı panel, bireysel/şirket organizasyonu oluşturma ve seçim, organizasyon üyeliğiyle veri ayrımı, apartman/blok/daire oluşturma-listeleme, malik/kiracı kaydı, aidat oluşturma ve listeleme, nakit/havale kısmi tahsilat ve ödeme geçmişi. Sayaçlar ve finans özeti PostgreSQL sorgularından gelir. Yeni organizasyon oluşturma sahibine ADMIN üyeliği verir; bir kullanıcı birden çok organizasyon oluşturabilir.

Demo: `/demo` ve `/demo?view=company`, eski panel tasarımı ve açıkça etiketli örnek veriler.

Yapılandırma bekleyen: gerçek SMTP ile parola kurtarma teslimi.

Eksik: davet/üyelik ve rol düzenleme ekranı, mevcut kayıt güncelleme/silme, kat alanı, oturum bitiş düzenleme, kişi tekilleştirme, toplu borçlandırma, audit ve ters kayıt. Gelir/gider, rapor, personel ve diğer gelişmiş modüller geliştirme aşamasındadır. Fazla ödeme bilinçli olarak reddedilir.
