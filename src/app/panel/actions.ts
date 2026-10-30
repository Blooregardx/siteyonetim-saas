"use server";
import { z } from "zod";
import { revalidatePath } from "next/cache";
import { db } from "@/lib/db";
import { verifySession } from "@/lib/session";
import { management } from "@/lib/management";
const text = z.string().trim().min(1).max(200);
const money = z.string().regex(/^\d{1,8}([,.]\d{1,2})?$/).transform(v => { const [a,b=""] = v.replace(",", ".").split("."); return Number(a)*100+Number(b.padEnd(2,"0")); }).pipe(z.number().int().positive().max(2147483647));
export async function save(_state: { message: string }, form: FormData) {
  const api = management(db, verifySession);
  try {
    const get = (key: string) => text.parse(form.get(key));
    const site = () => get("siteId");
    switch (get("operation")) {
      case "financial-defaults": await api.defaultCategories(site()); break;
      case "financial-category": await api.createCategory(site(),{type:z.enum(["INCOME","EXPENSE"]).parse(form.get("type")),name:get("name")}); break;
      case "financial-category-deactivate": await api.deactivateCategory(site(),get("categoryId")); break;
      case "financial-entry": await api.createEntry(site(),{type:z.enum(["INCOME","EXPENSE"]).parse(form.get("type")),categoryId:get("categoryId"),description:form.get("description") as string,amountKurus:money.parse(form.get("amount")),businessDate:get("businessDate"),method:z.enum(["CASH","TRANSFER"]).parse(form.get("method")),reference:String(form.get("reference")??""),idempotencyKey:get("idempotencyKey")}); break;
      case "financial-reversal": z.literal("yes").parse(form.get("confirmed")); await api.reverseEntry(site(),get("entryId"),String(form.get("reason")),get("idempotencyKey")); break;
      case "payment-policy": await api.setPartialPaymentsAllowed(site(),z.enum(["true","false"]).parse(form.get("allowed"))==="true"); break;
      case "site-update": await api.updateSite(site(),{name:get("name"),address:form.get("address"),description:form.get("description")}); break;
      case "block-update": await api.updateBlock(site(),get("blockId"),{name:get("name"),description:form.get("description")}); break;
      case "unit-update": await api.updateUnit(site(),get("unitId"),{number:get("number"),floor:form.get("floor")===""?null:Number(form.get("floor")),sectionType:get("sectionType"),usageStatus:get("usageStatus")}); break;
      case "person": await api.createPerson(site(),get("name")); break;
      case "person-link": await api.linkPerson(site(),get("unitId"),get("personId"),z.enum(["OWNER","TENANT"]).parse(form.get("kind")),get("startedAt")); break;
      case "relation-end": await api.endRelation(site(),get("relationId"),z.enum(["OWNER","TENANT"]).parse(form.get("kind")),get("endedAt")); break;
      case "organization": await api.createOrganization(get("name"), z.enum(["INDIVIDUAL","COMPANY"]).parse(form.get("kind"))); break;
      case "site": await api.createSite(get("organizationId"), get("name")); break;
      case "block": await api.createBlock(site(), get("name")); break;
      case "unit": await api.createUnit(site(), get("blockId"), get("number")); break;
      case "occupant": await api.recordOccupant(site(), get("unitId"), get("name"), z.enum(["OWNER","TENANT"]).parse(form.get("kind")), z.coerce.date().parse(form.get("startedAt"))); break;
      case "charge": await api.createCharge(site(), get("unitId"), get("period"), money.parse(form.get("amount")), z.coerce.date().parse(form.get("dueDate"))); break;
      case "reversal": z.literal("yes").parse(form.get("confirmed")); await api.reversePayment(site(),get("paymentId"),z.enum(["DUPLICATE_ENTRY","WRONG_AMOUNT","WRONG_CHARGE","ENTRY_ERROR"]).parse(form.get("reasonCode")),z.string().uuid().parse(form.get("idempotencyKey"))); break;
      case "payment": await api.collect(site(), get("chargeId"), money.parse(form.get("amount")), z.string().uuid().parse(form.get("idempotencyKey")), z.enum(["CASH","TRANSFER"]).parse(form.get("method")),form.get("fullBalance")==="true"); break;
      default: throw new Error("INVALID_OPERATION");
    }
  } catch (error) {
    const message = error instanceof Error ? error.message : "";
    return { message: message === "CATEGORY_EXISTS" ? "Bu tür ve ada sahip kategori zaten var; yeni bir ad kullanın." : message === "INVALID_CATEGORY" ? "Kategori geçersiz veya pasif. Seçiminizi kontrol edin." : message === "BALANCE_CHANGED" ? "Kalan borç değişti. Sayfayı yenileyip güncel tutarı kontrol edin." : message === "PARTIAL_PAYMENTS_DISABLED" ? "Kısmi ödeme kapalı. Kalan borcun tamamını tahsil edin; güncel bakiye için sayfayı yenileyin." : message === "ALREADY_REVERSED" ? "Bu işlem daha önce ters kaydedildi." : message === "IDEMPOTENCY_CONFLICT" ? "İşlem anahtarı farklı içerikle kullanılmış. Sayfayı yenileyin." : message === "OVERPAYMENT" ? "Tutar kalan borcu aşıyor. Fazla ödeme kabul edilmez." : message === "FORBIDDEN" || message === "UNAUTHENTICATED" ? "Bu işlem için yetkiniz veya geçerli oturumunuz yok." : "Kayıt yapılamadı. Alanları ve mükerrer kayıt olasılığını kontrol edin." };
  }
  revalidatePath("/gelir-gider"); revalidatePath("/raporlar"); revalidatePath("/kayitlar"); revalidatePath("/panel"); return { message: "Kayıt başarıyla tamamlandı." };
}
