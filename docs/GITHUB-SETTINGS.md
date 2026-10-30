# GitHub ayarları — bakımcı kontrol listesi

OSS-01 ayarları değiştirmez; ayrı PR yalnız dosya değişikliklerini içerir. 30 Ekim 2026 başlangıç kontrolü: depo PUBLIC, Private Vulnerability Reporting kapalı; main protected=false, repository rulesets boş. Son durum GitHub'da tekrar doğrulanmalıdır.

## Öncelik 1: özel güvenlik bildirimi

Settings → Security and quality / Advanced Security → Private vulnerability reporting → Enable. Menü adı GitHub arayüzüne göre değişebilir. Security → Advisories bölümünde “Report a vulnerability” kanalının açıldığını doğrulayın. Bakımcı Security alerts bildirimlerini açmalı. Kanal etkinleşince SECURITY.md içindeki başlangıç durumunu güncelleyin. Alternatif özel adres varsa yalnız doğrulanmış adresi yayımlayın.

## Öncelik 2: main koruması

Settings → Rules → Rulesets bölümünde main hedefli etkin branch ruleset (veya Branches → branch protection) oluşturun:

- Pull request zorunlu; force push ve dal silme engelli.
- `CI / checks` görüntülenen işini gerçek son check adıyla doğrulayıp zorunlu kılın. GitHub API context'i `checks` olabilir; adı tahmin ederek kilitlemeyin.
- Base değişince güncel kontroller isteyin; konuşmalar çözülmeli. Başarısız kontrolleri bypass ederek merge etmeyin.
- İkinci bağımsız bakımcı varsa en az bir onay, yeni committe eski onayı geçersiz kılma ve son gönderinin başka kişi tarafından onayı. Tek bakımcı kendi PR'sini onaylayamaz; zorunlu onay sayısını etkinleştirmeden sürdürülebilir inceleme düzeni kurun.
- Yönetici/bypass istisnalarını minimum tutup belgeleyin. Koruma ayarını kapatmayı olağan iş akışı yapmayın.

PUBLIC görünürlüğü koruyun. Bu PR'nin hedefi geliştirme dalıdır; main'e özellik geçişi ayrı PR/karardır. Geliştirme dalına da aynı kontroller önerilir. Önce çalışan CI adını doğrulayın; aksi hâlde birleştirme kilitlenebilir.

## Diğer kontroller

Actions genel token yetkisi read-only; workflow'ların PR oluşturma/onaylama yetkisi gereksizse kapalı. Dependabot uyarıları ve ücretsiz kullanılabilir secret scanning/push protection ayarlarını inceleyin; ücretli ürün etkinleştirmeyin. Fork workflow çalıştırmalarında GitHub'ın onay kontrollerini koruyun. Depoyu private yapmayın.

Kaynak: [GitHub özel bildirim](https://docs.github.com/en/code-security/how-tos/report-and-fix-vulnerabilities/configure-vulnerability-reporting/configure-for-a-repository), [korumalı dallar](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches).
