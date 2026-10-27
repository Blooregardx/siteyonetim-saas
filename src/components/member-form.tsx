"use client";
import { useActionState, type ReactNode } from "react";
import { memberAction } from "@/app/uyeler/actions";
export function MemberForm({values,children}:{values:Record<string,string>;children?:ReactNode}) {
 const [state,action,pending]=useActionState(memberAction,{message:""});
 return <form action={action}>{Object.entries(values).map(([name,value])=><input type="hidden" key={name} name={name} value={value}/>)}{children}<button disabled={pending}>{pending ? "İşleniyor…" : "Uygula"}</button><p role="status">{state.message}</p></form>;
}
