# v0.1.0-alpha.2 — Draft release notes

**TASLAK — YAYIMLANMADI / DRAFT — NOT PUBLISHED**

**EARLY DEVELOPMENT / ALPHA — NOT PRODUCTION READY**

This candidate prepares merged improvements since Alpha.1 for source-only maintainer review. Package/lock are now 0.1.0-alpha.2; private: true remains. Alpha.1 is unchanged. Publication date and final release commit require a separate decision.

## Candidate scope

S03-A–F and S04-A–D are merged after alpha.1: PRs #11–15 and #20–24. A final release commit must be selected separately.

- Previewed, idempotent bulk charges with transaction/audit protection.
- Partial/full collection policy, debt and movement reports, manual income/expenses and full reversals. A reversal is not a real money refund.
- Safe CSV, full-scope summaries and bounded pages; S03-E/F dashboard/payment aggregation improvements and immutable financial triggers.
- S04-A: Node24/PG17/Prisma6 standalone non-root Docker, loopback app/unpublished DB ports, distinct migration/runtime roles and migration/health gates.
- S04-B: Turkish mobile onboarding at `/kurulum`, existing verification/membership/audit rules, resumable and duplicate-safe first organization/site setup.
- S04-C: host-only pg_dump→age encrypted streams, atomic publication, locking/retention/status, opt-in systemd examples; isolated empty-target recovery and upgrade orchestration that stops app writers on migration failure.
- S04-D: clearer community installation/troubleshooting, read-only preflight, clean public GitHub source/archive acceptance and distinct source/binary distribution gates. Automated installation is not independent human validation.

## Requirements and compatibility

Initial automated Docker acceptance covers Linux x86-64, Docker Engine with Compose v2 or a compatible plugin, Git/Python3/OpenSSL. Node24/PostgreSQL17/Prisma6 run in images; host backup additionally needs age. Operators must provide and validate HTTPS and SMTP. No paid provider, Supabase, subscription or license key is required; infrastructure may cost money.

Eleven migrations remain unchanged; S04 adds no schema migration. Older databases need reviewed forward migrations under the separate owner, checksum/schema checks and financial/audit preservation. No automatic reset/down migration. An old image is not automatically compatible with a new schema; no automatic backup overwrite of the active database. [Safe upgrade](SAFE-UPGRADE.md).

## Known limits and operational gates

Staging/production, real SMTP/HTTPS delivery, independent human installation, internet-scale load/bot protection/MFA, monitoring and operational SLAs are unverified. OFFSET and separate-page snapshot limits remain. Daily logical backups are not WAL/PITR or a physical-disk disaster guarantee. Losing the private key makes a backup inaccessible; separate protected key/backup copies are necessary. Timers/pruning are opt-in.

AGPL-3.0-only remains. Source-only and binary/container distribution are separate activities. **BLOCKED FOR BINARY DISTRIBUTION:** LGPL/MPL and base-image corresponding-source/notice obligations are not fully evidenced. No prebuilt image is published. [License review](THIRD-PARTY-LICENSES.md), [readiness](ALPHA2-READINESS.md), [installation](COMMUNITY-INSTALLATION.md), [S04-D evidence](S04D-DISTRIBUTION-VALIDATION.md).

The [previous S03-F draft](ALPHA2-RELEASE-NOTES-EN-S03F-HISTORY.md) is preserved. Publication requires final HEAD CI, exact source-archive review, maintainer review, version metadata updates and a separate user decision.


Alpha.1 → Alpha.2 requires more than a package version change: encrypted backup, recovery rehearsal into a separate empty cluster, reviewed forward migrations and controlled upgrade. [Backup operations](BACKUP-OPERATIONS.md). [Source validation / kaynak doğrulaması](ALPHA2-SOURCE-RELEASE-VALIDATION.md).
