// SPDX-License-Identifier: AGPL-3.0-only
import { NextRequest,NextResponse } from 'next/server';
import { panelProbeEnabled } from './lib/panel-probe';
export function proxy(request:NextRequest){
 const label=request.headers.get('x-f10-probe')??'';
 if(panelProbeEnabled()&&/^f10_(100|1000|10000)_[a-f0-9]{8}$/.test(label))console.log('[F10] '+JSON.stringify({at:Date.now(),label,page:Number(request.nextUrl.searchParams.get('chargesPage')??1),stage:'server.dispatch'}));
 return NextResponse.next();
}
export const config={matcher:'/panel'};
