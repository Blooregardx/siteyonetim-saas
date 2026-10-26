ALTER TABLE "User" ADD COLUMN "passwordHash" TEXT;
ALTER TABLE "Payment" ADD COLUMN "method" TEXT NOT NULL DEFAULT 'CASH';
ALTER TABLE "Payment" ADD CONSTRAINT "Payment_method_check" CHECK ("method" IN ('CASH','TRANSFER'));
CREATE TABLE "Session" ("tokenHash" TEXT PRIMARY KEY, "userId" TEXT NOT NULL REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE, "expiresAt" TIMESTAMP(3) NOT NULL);
CREATE INDEX "Session_userId_idx" ON "Session"("userId");
CREATE TABLE "PasswordReset" ("tokenHash" TEXT PRIMARY KEY, "userId" TEXT NOT NULL REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE, "expiresAt" TIMESTAMP(3) NOT NULL);
CREATE INDEX "PasswordReset_userId_idx" ON "PasswordReset"("userId");
CREATE TABLE "AuthAttempt" ("key" TEXT PRIMARY KEY, "count" INTEGER NOT NULL, "expiresAt" TIMESTAMP(3) NOT NULL);
