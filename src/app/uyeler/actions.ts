"use server";
import { z } from "zod";
import { revalidatePath } from "next/cache";
import { db } from "@/lib/db";
import { verifySession } from "@/lib/session";
import { accounts } from "@/lib/accounts";
import { mailConfiguration, sendLink } from "@/lib/mail";
export async function memberAction(_state:{message:string},form:FormData) {
 try {
  const api=accounts(db,verifySession);
  const get=(key:string)=>z.string().min(1).max(200).parse(form.get(key));
  const operation=get("operation");
  if(operation==="accept") await api.accept(get("token"));
  else {
   const org=get("organizationId");
   if(operation==="invite") {
    mailConfiguration();
    const invitation=await api.invite(org,get("email"),z.enum(["ADMIN","MANAGER","RESIDENT"]).parse(form.get("role")));
    try { await sendLink(invitation.email,"davet",invitation.token,"SiteYönetim organizasyon daveti"); }
    catch { await api.cancel(org,invitation.id); throw new Error("DELIVERY_FAILED"); }
   } else if(operation==="cancel") await api.cancel(org,get("invitationId"));
   else if(operation==="remove") await api.changeMember(org,get("userId"),null);
   else if(operation==="role") await api.changeMember(org,get("userId"),z.enum(["ADMIN","MANAGER","RESIDENT"]).parse(form.get("role")));
   else throw new Error("INVALID_OPERATION");
  }
  revalidatePath("/uyeler");revalidatePath("/panel");
  return {message:"İşlem tamamlandı."};
 } catch(error) { return {message:error instanceof Error && error.message==="LAST_ADMIN" ? "Son aktif yönetici kaldırılamaz veya yetkisi düşürülemez." : "İşlem reddedildi. Yetki, doğrulama, davet süresi ve posta ayarlarını kontrol edin."}; }
}
