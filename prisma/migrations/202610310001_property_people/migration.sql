ALTER TABLE "Site" ADD COLUMN description TEXT;
ALTER TABLE "Block" ADD COLUMN description TEXT;
ALTER TABLE "Unit" ADD COLUMN floor INTEGER, ADD COLUMN "sectionType" TEXT NOT NULL DEFAULT 'RESIDENTIAL', ADD COLUMN "usageStatus" TEXT NOT NULL DEFAULT 'UNKNOWN';
ALTER TABLE "Unit" ADD CONSTRAINT "Unit_floor_check" CHECK (floor BETWEEN -20 AND 200);
CREATE UNIQUE INDEX "Site_organizationId_id_key" ON "Site"("organizationId",id);
CREATE TABLE "Person" (id TEXT PRIMARY KEY,"organizationId" TEXT NOT NULL,name TEXT NOT NULL,
 CONSTRAINT "Person_organizationId_fkey" FOREIGN KEY ("organizationId") REFERENCES "Organization"(id) ON DELETE RESTRICT ON UPDATE CASCADE);
CREATE UNIQUE INDEX "Person_organizationId_id_key" ON "Person"("organizationId",id);
CREATE INDEX "Person_organizationId_name_idx" ON "Person"("organizationId",name);
CREATE TABLE "Ownership" (id TEXT PRIMARY KEY,"organizationId" TEXT NOT NULL,"siteId" TEXT NOT NULL,"unitId" TEXT NOT NULL,"personId" TEXT NOT NULL,"startedAt" DATE NOT NULL,"endedAt" DATE,
 CONSTRAINT "Ownership_dates_check" CHECK ("endedAt" IS NULL OR "endedAt">="startedAt"),
 CONSTRAINT "Ownership_organizationId_personId_fkey" FOREIGN KEY ("organizationId","personId") REFERENCES "Person"("organizationId",id) ON DELETE RESTRICT ON UPDATE CASCADE,
 CONSTRAINT "Ownership_organizationId_siteId_fkey" FOREIGN KEY ("organizationId","siteId") REFERENCES "Site"("organizationId",id) ON DELETE RESTRICT ON UPDATE CASCADE,
 CONSTRAINT "Ownership_siteId_unitId_fkey" FOREIGN KEY ("siteId","unitId") REFERENCES "Unit"("siteId",id) ON DELETE RESTRICT ON UPDATE CASCADE);
CREATE INDEX "Ownership_siteId_unitId_idx" ON "Ownership"("siteId","unitId");
CREATE INDEX "Ownership_organizationId_personId_idx" ON "Ownership"("organizationId","personId");
ALTER TABLE "Occupancy" ADD COLUMN "organizationId" TEXT, ADD COLUMN "personId" TEXT;
ALTER TABLE "Occupancy" ADD CONSTRAINT "Occupancy_person_pair_check" CHECK (("organizationId" IS NULL)=("personId" IS NULL));
ALTER TABLE "Occupancy" ADD CONSTRAINT "Occupancy_dates_check" CHECK ("endedAt" IS NULL OR "endedAt">="startedAt") NOT VALID;
ALTER TABLE "Occupancy" ADD CONSTRAINT "Occupancy_organizationId_personId_fkey" FOREIGN KEY ("organizationId","personId") REFERENCES "Person"("organizationId",id) ON DELETE RESTRICT ON UPDATE CASCADE;
ALTER TABLE "Occupancy" ADD CONSTRAINT "Occupancy_organizationId_siteId_fkey" FOREIGN KEY ("organizationId","siteId") REFERENCES "Site"("organizationId",id) ON DELETE RESTRICT ON UPDATE CASCADE;
