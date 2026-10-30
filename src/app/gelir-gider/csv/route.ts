import { csvDownload } from '@/lib/export-http';
export const runtime='nodejs';
export const dynamic='force-dynamic';
export async function GET(request:Request){return csvDownload(request,'movement');}
