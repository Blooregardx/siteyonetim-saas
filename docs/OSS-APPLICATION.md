# Codex for Open Source — başvuru durumu ve tarihsel hazırlık

## Güncel durum — 30 Ekim 2026

OpenAI Codex for Open Source başvurusu **kullanıcı tarafından gönderildi; kabul sonucu bekleniyor**. Bu durum kullanıcı beyanına dayanır; kabul, kredi veya program desteği kazanıldığı iddia edilmez. Bu görevde başvuru gönderilmez veya yinelenmez.

[PR #10](https://github.com/Blooregardx/siteyonetim-saas/pull/10) main'e birleştirildi; [v0.1.0-alpha.1](https://github.com/Blooregardx/siteyonetim-saas/releases/tag/v0.1.0-alpha.1) GitHub Pre-release olarak yayımlandı. S03-A [PR #11](https://github.com/Blooregardx/siteyonetim-saas/pull/11) üzerinde geliştirildi; henüz main'e birleştirilmedi ve yayımlanmış ön sürüme dahil değildir.

## Tarihsel başvuru hazırlık kaydı

Aşağıdaki “Gönderilmedi”, “release taslak” ifadeleri, ölçümler, form kontrolleri, TR/EN metinleri ve son gönderim kontrolü başvuru öncesi hazırlık aşamasının kaydıdır. Güncel durum beyanı veya gönderilen formun birebir kopyası değildir. Taslaklar ve karakter sayıları tarihsel bütünlük için değiştirilmedi; yeniden başvuru talimatı olarak okunmamalıdır.

**Gönderilmedi.** Bakımcı/kullanıcı adı **Blooregardx**. Proje yeni ve erken alpha aşamasında; yaygın benimsenme iddiası yok. 30 Ekim 2026 kontrolü: PUBLIC depo, AGPL-3.0-only main üzerinde; 0 yıldız, 0 fork. İndirme, aktif kullanıcı, üretim müşterisi veya bağımsız dış katkıcı ölçümü doğrulanmadı. Son sayıları gönderimden önce tekrar okuyun; commitlerdeki eski hesap aynı kişinin kimliğidir, ikinci dış katkıcı diye sayılmaz.

## Resmî form ve koşullar

[Başvuru formu](https://openai.com/form/codex-for-oss/), [program](https://developers.openai.com/community/codex-for-oss), [koşullar](https://learn.chatgpt.com/docs/codex-for-oss-terms) 30 Ekim 2026'da kontrol edildi. Proje önemi, API kullanım planı ve ek açıklama alanları **en çok 500 karakter** gösteriyor. Rol alanı Primary/Core maintainer seçimi; aşağıdaki sorumluluk ve Codex metinleri yardımcı taslaktır, formda iki ayrı ek metin alanı varmış gibi sunulmaz. Bütün taslaklar yine 500 karakter altında tutuldu; form değişirse tekrar kontrol edin.

Koşullar doğru/eksiksiz bilgi ve geçerli ChatGPT hesabı gerektirir; kullanım/ekosistem önemi ve aktif bakım değerlendirilir. Seçim, kredi veya güvenlik erişimi garanti değildir; ek doğrulama istenebilir. Faydalar kişiseldir/devredilmez, krediler ve Codex Security ayrı inceleme/koşullara tabi olabilir. Başvuruya sır veya gizli bilgi koymayın. Metin hazırlamak başvurmak veya koşulları kullanıcı adına kabul etmek değildir.

## Kullanıcının dolduracağı alanlar

Ad/soyad, ChatGPT hesabına bağlı e-posta, hesap/profil görünürlüğü, isteniyorsa OpenAI Organization ID, destek seçenekleri ve koşulları kabul: **kullanıcı tarafından** doldurulur. Bu dosyada değer uydurulmadı. GitHub kullanıcı adı Blooregardx, depo bağlantısı https://github.com/Blooregardx/siteyonetim-saas . Rol için birincil bakımcı seçimi fiili depo kontrolüyle uyumlu; son beyan kullanıcıya aittir. Kredileri kullanmak için bu görev API çağrısı/harcama başlatmaz.

## Kanıtlar

- [PUBLIC depo](https://github.com/Blooregardx/siteyonetim-saas), [LICENSE](../LICENSE), [katkı rehberi](../CONTRIBUTING.md), [güvenlik politikası](../SECURITY.md).
- Birleşmiş [PR #7](https://github.com/Blooregardx/siteyonetim-saas/pull/7), [PR #8](https://github.com/Blooregardx/siteyonetim-saas/pull/8), [main geçişi #9](https://github.com/Blooregardx/siteyonetim-saas/pull/9).
- [OSS-03 hedef birleşme CI](https://github.com/Blooregardx/siteyonetim-saas/actions/runs/40996143750), [bakım geçmişi](OSS-EVIDENCE.md), [OSS-04 kurulum/kurtarma kanıtı](OSS04-VALIDATION.md).
- Sürüm yalnız [taslak](RELEASE-NOTES-v0.1.0-alpha.1.md); yayımlanmış release veya dış kullanıcı kanıtı değildir. OSS-04 son PR/CI bağlantıları PR üzerinde doğrulanmalı.

## Kopyalanabilir taslaklar

Her dil alternatifidir; TR ve EN metinleri aynı alana birlikte yapıştırmayın. Sayılar yalnız kod bloğu içindeki metni kapsar.

### Projenin önemi / Why does this repository qualify?

Türkçe — 363/500 karakter:

```text
SiteYönetim, apartman ve siteler için AGPL-3.0-only lisanslı, Türkçe ve kendi sunucusunda çalıştırılabilen ücretsiz bir yönetim projesidir. Aidat, tahsilat ve kişi ilişkilerinde tenant ayrımı ve denetlenebilir geçmiş hedefler. Yeni ve erken alpha aşamasındadır; yaygın kullanım iddiamız yoktur. PR, CI, migration ve kurtarma testleriyle bakım kanıtları sunuyoruz.
```

English — 349/500 characters:

```text
SiteYonetim is a free, Turkish-language, self-hostable apartment management project under AGPL-3.0-only. It focuses on tenant isolation and auditable dues, receipts and resident relationships. It is new and in early alpha; we do not claim broad adoption. Merged PRs, CI, migration checks and synthetic recovery tests provide evidence of maintenance.
```

### Bakımcı sorumlulukları / Maintainer responsibilities

Türkçe — 263/500 karakter:

```text
Blooregardx olarak birincil bakımcıyım. Kapsamı ve yol haritasını yönetiyor; değişiklikleri, yetki sınırlarını, finans geçmişini ve migration güvenliğini inceliyorum. Sentetik testleri, güvenlik bildirimlerini, katkı rehberini ve sürüm hazırlığını takip ediyorum.
```

English — 252/500 characters:

```text
As Blooregardx, I am the primary maintainer. I manage scope and the roadmap, review changes, authorization boundaries, financial history and migration safety, and maintain synthetic tests, security reporting, contributor guidance and release readiness.
```

### Codex bakım işleri / Codex maintenance workflows

Türkçe — 278/500 karakter:

```text
Codex’i PR incelemesi, güvenlik regresyonları, tenant izolasyonu ve finans transaction testleri, migration/yükseltme kontrolü, kurulum ve kurtarma provası, belge tutarlılığı ve issue sınıflandırmada kullanacağım. Finans ve yetki değişikliklerinde insan incelemesini koruyacağım.
```

English — 286/500 characters:

```text
I will use Codex for PR review, security regressions, tenant isolation and financial transaction tests, migration and upgrade checks, installation and recovery drills, documentation consistency and issue triage. Human review will remain required for financial and authorization changes.
```

### API kredileri / How will you use API credits?

Türkçe — 317/500 karakter:

```text
Uygun görülürse API kredilerini yalnız bu açık kaynak deponun PR incelemesi, sentetik güvenlik/migration regresyonları, test hatası sınıflandırma ve sürüm notu taslaklarında kullanacağım. Gerçek müşteri verisi veya sır göndermeyeceğim; çıktıları bakımcı inceleyecek. Bütçe sınırları kullanıcı tarafından belirlenecek.
```

English — 297/500 characters:

```text
If awarded, API credits would support this OSS repository’s PR review, synthetic security and migration regressions, test failure triage and release-note drafts. No real customer data or secrets would be submitted. A maintainer would review outputs and set usage limits before enabling automation.
```

### Ek açıklama / Anything else we should know?

Türkçe — 318/500 karakter:

```text
Proje üretime hazır değildir. Temiz konteyner kurulumu ve ayrı PostgreSQL hedefe sentetik yedekten dönüş doğrulandı; bağımsız insan kurulumu, gerçek SMTP teslimi ve üretim güvenliği/yük testleri açık kalır. Release adayı hazırlanıyor, henüz yayımlanmadı. İndirme/aktif kullanıcı veya dış benimsenme kanıtı sunamıyoruz.
```

English — 353/500 characters:

```text
The project is not production ready. Clean-container installation and synthetic recovery to a separate PostgreSQL target passed; independent human installation, real SMTP delivery and production security/load testing remain open. An alpha release is being prepared, not published. We have no verified download, active-user or external-adoption evidence.
```

## Son gönderim kontrolü

Kişisel alanlar doğru mu, son PR/CI kanıtı güncel mi, release hâlâ taslak mı, metinler form sınırında mı ve hiçbir kullanım/benimsenme sayısı uydurulmuş mu kontrol edin. Gerekirse metni kullanıcı düzenler. Başvuruyu yalnız kullanıcı gönderir; OpenAI onayı/desteği alınmış gibi tanıtılmaz.
