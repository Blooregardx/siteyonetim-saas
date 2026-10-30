"use client";
export default function ErrorPage({ reset }: { reset: () => void }) {
 return <div className="auth panel"><h1>Panel yüklenemedi</h1><p>Veritabanı bağlantısını kontrol edin veya daha sonra yeniden deneyin.</p><button onClick={reset}>Yeniden dene</button></div>;
}
