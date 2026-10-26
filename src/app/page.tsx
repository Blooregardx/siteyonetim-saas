import Link from "next/link";
import { demoCharges } from "@/lib/demo";
import { formatMoney, outstanding, summarize } from "@/lib/finance";
export default function Home() {
  const totals = summarize(demoCharges, "2026-10-26");
  const rate = Math.round(totals.collectedKurus / totals.totalKurus * 100);
  return <div className="shell">
    <a className="skip" href="#main">İçeriğe geç</a>
    <aside><Link className="brand" href="/">▦ SiteYönetim<span>YÖNETİM PLATFORMU</span></Link>
      <div className="site">Örnek Yaşam Sitesi<small>2 blok · 4 daire</small></div>
      <nav aria-label="Ana menü"><a href="#main">◈ Genel bakış</a><a href="#dues">▤ Aidat ve tahsilat</a><a href="#units">▦ Daireler</a><a href="#announcements">◉ Duyurular</a></nav>
      <p className="aside-note">Daha düzenli bir site,<br/>daha kolay bir yönetim.</p>
    </aside>
    <main id="main"><header><span>Yönetim / Genel bakış</span><span className="badge">Örnek veri</span></header>
      <section className="heading"><div><p className="eyebrow">SİTENİZ BİR BAKIŞTA</p><h1>Genel bakış</h1><p>Aidatları ve tahsilatları tek yerden takip edin.</p></div><span className="period">Ekim 2026</span></section>
      <div className="notice">Bu panel bir başlangıç demosudur. Veriler örnektir; giriş ve gerçek veri kaydı henüz bağlı değildir.</div>
      <section className="stats" aria-label="Finansal özet">{[
        ["Toplam aidat", totals.totalKurus, "4 daire için tahakkuk"], ["Tahsil edilen", totals.collectedKurus, `%${rate} tahsilat oranı`],
        ["Bekleyen ödeme", totals.outstandingKurus, "Kalan aidat bakiyesi"], ["Gecikmiş ödeme", totals.overdueKurus, "26 Ekim 2026 itibarıyla"],
      ].map(([label, value, note]) => <article key={label}><p>{label}</p><strong>{formatMoney(Number(value))}</strong><small>{note}</small></article>)}</section>
      <section id="dues" className="panel"><div className="panel-title"><div><h2>Aidat ve tahsilat</h2><p>Ekim ayı ödeme durumu</p></div><span className="badge">{demoCharges.length} kayıt</span></div>
        <div className="table-wrap"><table><caption className="sr-only">Ekim 2026 örnek aidat kayıtları</caption><thead><tr><th scope="col">Daire / Sakin</th><th scope="col">Aidat</th><th scope="col">Ödenen</th><th scope="col">Kalan</th><th scope="col">Durum</th></tr></thead><tbody>{demoCharges.map(c => <tr key={c.id}><td><b>{c.unit}</b><small>{c.resident}</small></td><td>{formatMoney(c.amountKurus)}</td><td>{formatMoney(c.paidKurus)}</td><td>{formatMoney(outstanding(c))}</td><td><span className={`status ${outstanding(c) === 0 ? "paid" : "pending"}`}>{outstanding(c) === 0 ? "Ödendi" : c.paidKurus > 0 ? "Kısmi ödeme" : "Gecikmiş"}</span></td></tr>)}</tbody></table></div>
      </section>
      <div className="bottom"><section id="units" className="panel"><h2>Daire özeti</h2><p>Örnek sitenin blok dağılımı</p><div className="block"><b>A Blok</b><span>2 daire</span></div><div className="block"><b>B Blok</b><span>2 daire</span></div></section>
      <section id="announcements" className="panel"><h2>Yönetim notları</h2><p>Örnek duyuru</p><div className="announcement"><span>10 EKİM</span><h3>Ekim ayı aidatları</h3><p>Örnek aidat tutarı daire başına 2.500 TL olarak belirlenmiştir.</p></div></section></div>
      <footer>SiteYönetim · Başlangıç sürümü · Örnek veriler, Ekim 2026</footer>
    </main></div>;
}
