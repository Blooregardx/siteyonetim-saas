-- CreateEnum
CREATE TYPE "FinancialEntryType" AS ENUM ('INCOME', 'EXPENSE');

-- CreateTable
CREATE TABLE "FinancialCategory" (
    "id" TEXT NOT NULL,
    "organizationId" TEXT NOT NULL,
    "siteId" TEXT NOT NULL,
    "type" "FinancialEntryType" NOT NULL,
    "name" TEXT NOT NULL,
    "nameKey" TEXT NOT NULL,
    "active" BOOLEAN NOT NULL DEFAULT true,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "FinancialCategory_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "FinancialEntry" (
    "id" TEXT NOT NULL,
    "organizationId" TEXT NOT NULL,
    "siteId" TEXT NOT NULL,
    "type" "FinancialEntryType" NOT NULL,
    "categoryId" TEXT NOT NULL,
    "description" TEXT NOT NULL,
    "amountKurus" INTEGER NOT NULL,
    "businessDate" DATE NOT NULL,
    "method" TEXT NOT NULL,
    "reference" TEXT NOT NULL,
    "actorId" TEXT NOT NULL,
    "idempotencyKey" TEXT NOT NULL,
    "requestHash" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "FinancialEntry_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "FinancialEntryReversal" (
    "id" TEXT NOT NULL,
    "organizationId" TEXT NOT NULL,
    "siteId" TEXT NOT NULL,
    "entryId" TEXT NOT NULL,
    "amountKurus" INTEGER NOT NULL,
    "reason" TEXT NOT NULL,
    "actorId" TEXT NOT NULL,
    "idempotencyKey" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "FinancialEntryReversal_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "FinancialCategory_organizationId_siteId_type_id_key" ON "FinancialCategory"("organizationId", "siteId", "type", "id");

-- CreateIndex
CREATE UNIQUE INDEX "FinancialCategory_siteId_type_nameKey_key" ON "FinancialCategory"("siteId", "type", "nameKey");

-- CreateIndex
CREATE INDEX "FinancialEntry_siteId_businessDate_idx" ON "FinancialEntry"("siteId", "businessDate");

-- CreateIndex
CREATE INDEX "FinancialEntry_organizationId_businessDate_idx" ON "FinancialEntry"("organizationId", "businessDate");

-- CreateIndex
CREATE UNIQUE INDEX "FinancialEntry_siteId_idempotencyKey_key" ON "FinancialEntry"("siteId", "idempotencyKey");

-- CreateIndex
CREATE UNIQUE INDEX "FinancialEntry_organizationId_siteId_id_amountKurus_key" ON "FinancialEntry"("organizationId", "siteId", "id", "amountKurus");

-- CreateIndex
CREATE UNIQUE INDEX "FinancialEntryReversal_entryId_key" ON "FinancialEntryReversal"("entryId");

-- CreateIndex
CREATE INDEX "FinancialEntryReversal_siteId_createdAt_idx" ON "FinancialEntryReversal"("siteId", "createdAt");

-- CreateIndex
CREATE UNIQUE INDEX "FinancialEntryReversal_siteId_idempotencyKey_key" ON "FinancialEntryReversal"("siteId", "idempotencyKey");

-- CreateIndex
CREATE UNIQUE INDEX "FinancialEntryReversal_organizationId_siteId_entryId_amount_key" ON "FinancialEntryReversal"("organizationId", "siteId", "entryId", "amountKurus");

-- AddForeignKey
ALTER TABLE "FinancialCategory" ADD CONSTRAINT "FinancialCategory_organizationId_siteId_fkey" FOREIGN KEY ("organizationId", "siteId") REFERENCES "Site"("organizationId", "id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "FinancialEntry" ADD CONSTRAINT "FinancialEntry_organizationId_siteId_fkey" FOREIGN KEY ("organizationId", "siteId") REFERENCES "Site"("organizationId", "id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "FinancialEntry" ADD CONSTRAINT "FinancialEntry_organizationId_siteId_type_categoryId_fkey" FOREIGN KEY ("organizationId", "siteId", "type", "categoryId") REFERENCES "FinancialCategory"("organizationId", "siteId", "type", "id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "FinancialEntryReversal" ADD CONSTRAINT "FinancialEntryReversal_organizationId_siteId_entryId_amoun_fkey" FOREIGN KEY ("organizationId", "siteId", "entryId", "amountKurus") REFERENCES "FinancialEntry"("organizationId", "siteId", "id", "amountKurus") ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE "FinancialEntry" ADD CONSTRAINT "FinancialEntry_validation" CHECK ("amountKurus">0 AND method IN ('CASH','TRANSFER') AND length(trim(description)) BETWEEN 3 AND 1000 AND "idempotencyKey" ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$');
ALTER TABLE "FinancialEntryReversal" ADD CONSTRAINT "FinancialEntryReversal_validation" CHECK ("amountKurus">0 AND length(trim(reason)) BETWEEN 3 AND 1000 AND "idempotencyKey" ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$');
ALTER TABLE "FinancialCategory" ADD CONSTRAINT "FinancialCategory_name" CHECK (length(trim(name)) >= 2 AND length(trim(name)) <= 100 AND length("nameKey")>0);
CREATE FUNCTION manual_finance_immutable() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN RAISE EXCEPTION 'manual financial history is append only'; END $$;
CREATE TRIGGER financial_entry_immutable BEFORE UPDATE OR DELETE OR TRUNCATE ON "FinancialEntry" FOR EACH STATEMENT EXECUTE FUNCTION manual_finance_immutable();
CREATE TRIGGER financial_reversal_immutable BEFORE UPDATE OR DELETE OR TRUNCATE ON "FinancialEntryReversal" FOR EACH STATEMENT EXECUTE FUNCTION manual_finance_immutable();
CREATE FUNCTION financial_category_identity() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN IF (to_jsonb(NEW)-'active') IS DISTINCT FROM (to_jsonb(OLD)-'active') THEN RAISE EXCEPTION 'category identity is immutable'; END IF; RETURN NEW; END $$;
CREATE TRIGGER financial_category_identity BEFORE UPDATE ON "FinancialCategory" FOR EACH ROW EXECUTE FUNCTION financial_category_identity();
CREATE TRIGGER financial_category_preserve BEFORE DELETE OR TRUNCATE ON "FinancialCategory" FOR EACH STATEMENT EXECUTE FUNCTION manual_finance_immutable();
CREATE INDEX "Payment_siteId_istanbul_day_idx" ON "Payment" ("siteId", (("paidAt" AT TIME ZONE 'UTC' AT TIME ZONE 'Europe/Istanbul')::date));
CREATE INDEX "PaymentReversal_siteId_istanbul_day_idx" ON "PaymentReversal" ("siteId", (("createdAt" AT TIME ZONE 'UTC' AT TIME ZONE 'Europe/Istanbul')::date));
