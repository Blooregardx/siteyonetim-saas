"use client";
import { useActionState, type ReactNode } from "react";
import { save } from "@/app/panel/actions";
export function DataForm({ operation, values = {}, children }: { operation: string; values?: Record<string,string>; children: ReactNode }) {
 const [state, action, pending] = useActionState(save, { message: "" });
 return <form action={action}><input type="hidden" name="operation" value={operation}/>{Object.entries(values).map(([key,value]) => <input key={key} type="hidden" name={key} value={value}/>)}{children}<button disabled={pending}>{pending ? "Kaydediliyor…" : "Kaydet"}</button><p role="status">{state.message}</p></form>;
}
