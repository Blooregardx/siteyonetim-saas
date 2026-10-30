"use client";
import Link from "next/link";
export default function ErrorPage({ reset }: { reset: () => void }) {
 return <div className="auth panel"><h1>Panel yüklenemedi</h1><p>Veritabanı bağlantısını kontrol edin veya daha sonra yeniden deneyin.</p><p>Yönetim raporlarına doğrudan erişebilirsiniz.</p><div className="view-switch"><Link href="/raporlar">Borç ve Tahsilat Raporları</Link><Link href="/gelir-gider">Gelir ve Gider Yönetimi</Link></div><button onClick={reset}>Yeniden dene</button></div>;
}
