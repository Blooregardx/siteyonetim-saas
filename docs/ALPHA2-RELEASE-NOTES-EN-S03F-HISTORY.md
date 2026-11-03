> Tarihsel S03-F taslağıdır. Güncel aday [sürüm notundadır](ALPHA2-RELEASE-NOTES-EN.md); eski PR taslak durumları güncel durum değildir.

# v0.1.0-alpha.2 — Draft release notes

## Current decision — READY FOR MAINTAINER REVIEW

The preserved commit `e9ed54a786ba3d33e382b6b1208241464b9c5653` was pushed normally without changing its author, committer or history. Both [push CI](https://github.com/Blooregardx/siteyonetim-saas/actions/runs/41564379171) and [PR CI](https://github.com/Blooregardx/siteyonetim-saas/actions/runs/41564385740) passed in full: 25 unit, 29 integration, 14 E2E tests, build, 11 clean migrations/schema comparison, both query-plan modes, 3 streaming tests and synthetic restore of 26 tables/258,298 rows including privileges. This clears the F-10 DEVELOPMENT blocker at this checkpoint. The final documentation HEAD must also pass both workflows. PR #20 remains **draft and open**; publishing or merging requires a separate user decision. No release/tag/deployment was created. Earlier decisions below are historical evidence. [Investigation](F10-INVESTIGATION.md).

## Historical reopening — 91dbba7 / BLOCKED

Push CI on 91dbba7 failed (13/14 E2E), reopening the previous READY checkpoint. The Charge-only scope and post-pagination metadata joins passed local 25/29/14 regression and three independent 4/4 acceptance runs. Both CI results on the new commit remain required. Earlier READY statements below are historical checkpoints. [Investigation](F10-INVESTIGATION.md). PR remains draft; no release or merge.


**DRAFT — NOT PUBLISHED. EARLY DEVELOPMENT / ALPHA — NOT PRODUCTION READY.** This preparation does not bump package/lock versions or modify v0.1.0-alpha.1. The final commit, tag and release date require a separate maintainer decision. [Readiness decision](ALPHA2-READINESS.md), [security/regression evidence in Turkish](S03F-SECURITY-REGRESSION.md).

**Development readiness:** F-10 was addressed by bounding charge balance aggregation to the selected page; both fix CI workflows passed. Status: READY FOR MAINTAINER REVIEW. This remains a draft requiring final-HEAD checks and separate user authorization to publish.

## Changes merged into main since alpha.1

- S03-A / PR #11: bulk dues for up to 5,000 selected units, preview/hash validation, idempotency and all-or-nothing conflict handling.
- S03-B / PR #12: debt/collection reporting and due-date/period filters; ADMIN-controlled partial-payment policy and server-side balance rechecks.
- S03-C / PR #13: site-scoped income/expense categories, immutable manual entries, justified ADMIN full reversals and monthly summaries by payment/business date. Dues assessment is not cash; collections are not copied into manual income.
- S03-D / PR #14: two authenticated CSV exports with Turkish UTF-8 formatting, formula injection defenses, 50,000-row / 128 MiB limits and cursor snapshots; 3/6/12-month comparisons.
- S03-E / PR #15: bounded dashboard reads with complete organization totals; paged dues, collections, ownership/occupancy and record history, unit/charge search and persistent bulk selections across component pages. Main merge: `afd7ea7bcfe693f06daeea9d48b38b8e1fe27fcc`.
- S03-F candidate: security/regression review, additive database immutability protection for charges/bulk history, streaming synthetic backup/restore hashes, ACL comparisons and focused session/authorization/stale-preview/CSV-boundary regressions. Inclusion requires separate review of the S03-F PR.

Existing authentication, verification/recovery, organizations/roles/invitations, property/person relationships, collection and immutable financial/audit behavior are preserved. A reversal does not issue a real refund. Reports are not certified accounting records or bank balances.

## Source distribution and installation

This is a **project source-code** alpha candidate, using Node 24, Next.js 16, PostgreSQL 17 and Prisma 6. The current chain contains eleven migrations; historical migrations remain unchanged. See [self-hosting](SELF-HOSTING.md) and [backup/restore](BACKUP-RESTORE.md). Take private backups and rehearse updates in isolation; reverting application code does not revert the database or remove financial/audit history.

AGPL-3.0-only remains in force. Operators of modified network versions must offer interacting users access to the corresponding source; distribution obligations also apply. See [licensing](LICENSING.md) and [third-party requirements](THIRD-PARTY-LICENSES.md). Free software does not mean free server, SMTP or domain hosting. No binaries, containers, node_modules, browsers or dumps are distributed by this preparation; LGPL/MPL/NOTICE obligations for those remain separate gates.

## Known limitations

- Real SMTP delivery, independent human installation, live security/load and full operations/monitoring readiness are unverified. MFA is not implemented.
- Single-user synthetic tests at 10,000 units/60,000 charges do not establish production capacity or a multi-user SLA. Production load for 5,000-charge writes remains unverified.
- OFFSET pagination and separate request snapshots may shift pages under concurrent inserts. Full navigation resets unsaved main-form fields; bulk selections persist within their component pagination.
- CSV descriptions may contain personal information; no automatic redaction is provided. Downloads and backups require careful handling.
- Development lint dependencies retain a minimatch advisory; lint/Actions runtime maintenance remains open. Production traffic protection, least-privilege operations, TLS/proxy, encrypted backups/PITR/RPO/RTO and incident response remain incomplete.
- A synthetic restore is not a disaster-recovery guarantee. Streaming client hashes still require PostgreSQL sorting and temporary disk resources.

DEVELOPMENT validation is not STAGING or PRODUCTION approval. Merging, tagging and publishing require separate user authorization; this draft performs none of them.
