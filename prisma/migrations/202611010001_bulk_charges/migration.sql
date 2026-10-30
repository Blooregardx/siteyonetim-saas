CREATE TABLE "BulkChargeOperation" (
 "id" TEXT NOT NULL PRIMARY KEY,
 "siteId" TEXT NOT NULL REFERENCES "Site"("id") ON DELETE RESTRICT ON UPDATE CASCADE,
 "idempotencyKey" TEXT NOT NULL,
 "requestHash" TEXT NOT NULL,
 "createdCount" INTEGER NOT NULL CHECK ("createdCount" > 0),
 "totalKurus" BIGINT NOT NULL CHECK ("totalKurus" > 0),
 "period" TEXT NOT NULL,
 "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE UNIQUE INDEX "BulkChargeOperation_siteId_idempotencyKey_key" ON "BulkChargeOperation"("siteId", "idempotencyKey");
