# GitHub ayarları — güncel durum ve bakımcı kontrol listesi

## Tarihsel başlangıç — OSS-01

30 Ekim 2026 OSS-01 başlangıç kontrolü: depo PUBLIC, Private Vulnerability Reporting kapalı; main protected=false, repository rulesets boştu. Bu denetim kanıtı korunur; aşağıdaki OSS-01B kontrolü güncel durumu belirtir. PR yalnız dosyaları değiştirir; GitHub ayarları kullanıcı tarafından uygulanmıştır.

## Güncel durum — OSS-01B, 30 Ekim 2026

GitHub API üzerinden yeniden doğrulandı:

| Ayar | Durum |
|---|---|
| Depo görünürlüğü | PUBLIC; böyle kalacak |
| Private Vulnerability Reporting | Etkin (`enabled=true`) |
| main-protection | Etkin (`enforcement=active`), ruleset 26175642 |
| Hedef | Varsayılan dal (`~DEFAULT_BRANCH`); şu anda main |
| Dal silme | Engelli (`deletion`) |
| Force push | Engelli (`non_fast_forward`) |
| Pull request | Zorunlu (`pull_request`) |
| Zorunlu CI | **Henüz ayarlanmadı**; required_status_checks kuralı yok |
| Bağımsız onay | Zorunlu onay sayısı 0 |
| Konuşma çözümü / eski onayın iptali | Zorunlu değil / kapalı |
| Bypass aktörleri | Liste boş |

Kanıt: [main-protection](https://github.com/Blooregardx/siteyonetim-saas/rules/26175642), [özel güvenlik bildirimi](https://github.com/Blooregardx/siteyonetim-saas/security/advisories/new). Durum anlık görüntüdür; ayar değişikliklerinde tekrar doğrulanmalıdır. Özel kanalın etkin olması, rapor gönderimi/yanıt süresinin test edildiği anlamına gelmez.

## Öncelikli kalan: zorunlu CI

Settings → Rules → Rulesets → main-protection içinde required status checks eklenmeli. OSS-01 PR kontrollerinin GitHub API check adı **`checks`** olarak doğrulandı; arayüz bunu `CI / checks` olarak gösterebilir. Son başarılı çalışmadan gerçek kontrolü ve GitHub Actions kaynağını seçin; yalnız görüntü adını tahmin ederek kural eklemeyin.

Base değişince güncel kontrolleri istemek önerilir. CI başarısı şu anda gözlemlenebilir, fakat ruleset tarafından zorunlu tutulmaz. Bu eksik bu PR tarafından otomatik giderilmez.

PR #7'nin hedefi `codex/s00-s01-foundation` dalıdır. main-protection yalnız varsayılan dalı kapsar; #7'nin hedef dalına koruma sağlamaz. Geliştirme dalında da PR/CI koruması ayrıca değerlendirilmeli. main'e özellik geçişi ayrı PR/karardır; bu PR main'e alınmaz.

## İnceleme ve bildirim işletimi

- İkinci bağımsız bakımcı varsa en az bir onay, yeni committe eski onayı geçersiz kılma, son gönderinin başka kişi tarafından onayı ve konuşma çözümü önerilir. Bunlar şu an etkinmiş gibi değerlendirilmemeli. Tek bakımcı kendi PR'sini onaylayamaz.
- Bypass istisnalarını minimum tutun; korumayı kapatmayı olağan iş akışı yapmayın.
- Security → Advisories özel bildirim kanalını kullanın; bakımcı Security alerts bildirimlerini açıp takip etmelidir. Alternatif özel adres varsa yalnız doğrulanmış adresi yayımlayın.
- PUBLIC görünürlüğünü koruyun; varsayılan dal değişirse ruleset hedefinin de değiştiğini kontrol edin.

## Diğer kontroller

Workflow içindeki token yetkisi `contents: read` düzeyindedir; hesap genelindeki Actions varsayılan yetkileri ayrıca kontrol edilmelidir. Gereksiz workflow PR oluşturma/onaylama yetkilerini kapatın. Dependabot uyarıları ve ücretsiz kullanılabilir secret scanning/push protection ayarlarını inceleyin; ücretli ürün etkinleştirmeyin. Fork workflow onay kontrollerini koruyun. Bunların hesap genelinde tamamlandığı iddia edilmez.

Kaynak: [GitHub özel bildirim](https://docs.github.com/en/code-security/how-tos/report-and-fix-vulnerabilities/configure-vulnerability-reporting/configure-for-a-repository), [korumalı dallar](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches).
