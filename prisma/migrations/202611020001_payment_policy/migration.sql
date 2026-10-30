ALTER TABLE "Site" ADD COLUMN "partialPaymentsAllowed" BOOLEAN NOT NULL DEFAULT true;
ALTER TABLE "Payment" ADD COLUMN "fullBalance" BOOLEAN NOT NULL DEFAULT false;
CREATE TABLE "PaymentPolicyChange" (
 "id" TEXT NOT NULL PRIMARY KEY,
 "siteId" TEXT NOT NULL,
 "organizationId" TEXT NOT NULL,
 "actorId" TEXT NOT NULL,
 "oldValue" BOOLEAN NOT NULL,
 "newValue" BOOLEAN NOT NULL,
 "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
 CONSTRAINT "PaymentPolicyChange_organizationId_siteId_fkey" FOREIGN KEY ("organizationId","siteId") REFERENCES "Site"("organizationId","id") ON DELETE RESTRICT ON UPDATE CASCADE
);
CREATE INDEX "PaymentPolicyChange_siteId_createdAt_idx" ON "PaymentPolicyChange"("siteId","createdAt");
CREATE INDEX "Charge_siteId_period_idx" ON "Charge"("siteId","period");
CREATE FUNCTION payment_policy_append_only() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN RAISE EXCEPTION 'payment policy history is append only'; END $$;
CREATE TRIGGER payment_policy_immutable BEFORE UPDATE OR DELETE OR TRUNCATE ON "PaymentPolicyChange" FOR EACH STATEMENT EXECUTE FUNCTION payment_policy_append_only();
