GRANT SELECT, INSERT ON "User","Session","PasswordReset","EmailVerification","AuthAttempt","Invitation","OrganizationMembership","Membership","Organization","Site","Block","Unit","Occupancy","Person","Ownership","Charge","Payment","PaymentReversal","BulkChargeOperation","PaymentPolicyChange","FinancialCategory","FinancialEntry","FinancialEntryReversal","Announcement" TO sy_runtime;
GRANT UPDATE, DELETE ON "User","Session","PasswordReset","EmailVerification","AuthAttempt","Invitation","OrganizationMembership","Membership" TO sy_runtime;
GRANT UPDATE ON "Site","Block","Unit","Occupancy","Ownership" TO sy_runtime;
GRANT UPDATE (id) ON "Organization","Charge","Payment","FinancialEntry" TO sy_runtime;
GRANT UPDATE (active) ON "FinancialCategory" TO sy_runtime;
GRANT INSERT ON "AuditLog" TO sy_runtime;
GRANT SELECT (id) ON "AuditLog" TO sy_runtime;
GRANT SELECT ON "_prisma_migrations" TO sy_runtime;
