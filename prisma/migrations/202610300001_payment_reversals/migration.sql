CREATE TYPE "ReversalReason" AS ENUM ('DUPLICATE_ENTRY','WRONG_AMOUNT','WRONG_CHARGE','ENTRY_ERROR');
CREATE UNIQUE INDEX "Payment_siteId_id_key" ON "Payment"("siteId","id");
CREATE UNIQUE INDEX "Payment_siteId_id_amountKurus_key" ON "Payment"("siteId","id","amountKurus");
CREATE TABLE "PaymentReversal" (
 "id" TEXT PRIMARY KEY, "siteId" TEXT NOT NULL, "paymentId" TEXT NOT NULL, "amountKurus" INTEGER NOT NULL CHECK ("amountKurus" > 0),
 "reasonCode" "ReversalReason" NOT NULL, "actorId" TEXT NOT NULL, "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
 "idempotencyKey" TEXT NOT NULL CHECK ("idempotencyKey" ~* '^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'),
 CONSTRAINT "PaymentReversal_payment_fkey" FOREIGN KEY ("siteId","paymentId","amountKurus") REFERENCES "Payment"("siteId","id","amountKurus") ON DELETE RESTRICT ON UPDATE CASCADE,
 CONSTRAINT "PaymentReversal_actorId_fkey" FOREIGN KEY ("actorId") REFERENCES "User"("id") ON DELETE RESTRICT ON UPDATE CASCADE);
CREATE UNIQUE INDEX "PaymentReversal_paymentId_key" ON "PaymentReversal"("paymentId");
CREATE UNIQUE INDEX "PaymentReversal_siteId_idempotencyKey_key" ON "PaymentReversal"("siteId","idempotencyKey");
CREATE INDEX "PaymentReversal_siteId_createdAt_idx" ON "PaymentReversal"("siteId","createdAt");
CREATE FUNCTION reject_financial_mutation() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN RAISE EXCEPTION 'Financial records are append only'; END $$;
CREATE TRIGGER payment_immutable BEFORE UPDATE OR DELETE OR TRUNCATE ON "Payment" FOR EACH STATEMENT EXECUTE FUNCTION reject_financial_mutation();
CREATE TRIGGER reversal_immutable BEFORE UPDATE OR DELETE OR TRUNCATE ON "PaymentReversal" FOR EACH STATEMENT EXECUTE FUNCTION reject_financial_mutation();
