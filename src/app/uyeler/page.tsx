import Link from "next/link";
import { redirect,notFound } from "next/navigation";
import { requireSession,verifySession } from "@/lib/session";
import { db } from "@/lib/db";
import { management } from "@/lib/management";
import { MemberForm } from "@/components/member-form";
export default async function Page({searchParams}:{searchParams:Promise<{org?:string}>}) {
 const session=await requireSession();
 const user=await db.user.findUniqueOrThrow({where:{id:session.userId}});
 if(!user.emailVerifiedAt) redirect("/eposta-dogrula");
 const choices=await db.organizationMembership.findMany({where:{userId:user.id,role:{in:["ADMIN","MANAGER"]}},include:{organization:true}});
 const {org}=await searchParams; const selected=choices.find(m=>m.organizationId===(org??choices[0]?.organizationId));
 if(org&&!selected) notFound();
 if(!selected) return <div className="auth panel"><p>Yetkili organizasyon bulunamadı.</p><Link href="/panel">Panele dön</Link></div>;
 await management(db,verifySession).portfolio(selected.organizationId);
 const members=await db.organizationMembership.findMany({where:{organizationId:selected.organizationId},include:{user:{select:{name:true}}}});
 const invitations=await db.invitation.findMany({where:{organizationId:selected.organizationId,acceptedAt:null,revokedAt:null,expiresAt:{gt:new Date()}},select:{id:true,role:true}});
 return <div className="auth panel"><Link href="/panel">Panele dön</Link><h1>Çalışanlar ve davetler</h1><nav>{choices.map(c=><Link key={c.organizationId} href={`/uyeler?org=${c.organizationId}`}>{c.organization.name}</Link>)}</nav><h2>Yeni davet</h2><MemberForm values={{operation:"invite",organizationId:selected.organizationId}}><label>E-posta<input name="email" type="email" required/></label><Roles admin={selected.role==="ADMIN"}/></MemberForm><h2>Üyeler</h2>{members.map(m=><article key={m.userId}><p>{m.user.name} · {m.role}</p>{selected.role==="ADMIN"&&<><MemberForm values={{operation:"role",organizationId:selected.organizationId,userId:m.userId}}><Roles admin/></MemberForm><MemberForm values={{operation:"remove",organizationId:selected.organizationId,userId:m.userId}}>Üyeliği kaldır</MemberForm></>}</article>)}<h2>Bekleyen davetler</h2>{invitations.map(i=><MemberForm key={i.id} values={{operation:"cancel",organizationId:selected.organizationId,invitationId:i.id}}>Davet iptali · {i.role}</MemberForm>)}</div>;
}
function Roles({admin}:{admin:boolean}) {return <label>Rol<select name="role" aria-label="Rol">{admin&&<><option value="MANAGER">Yönetici</option><option value="ADMIN">Organizasyon sahibi / admin</option></>}<option value="RESIDENT">Sakin</option></select></label>;}
