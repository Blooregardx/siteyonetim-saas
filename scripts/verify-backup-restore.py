"""Synthetic PostgreSQL 17 drill on two distinct local Docker containers only.

Requires OSS_TEST_SOURCE_CONTAINER and OSS_TEST_RESTORE_CONTAINER; both must
contain siteyonetim_test owned by the synthetic siteyonetim test administrator.
Never points at a host database. Refuses a nonempty restore target. No drop/reset.
"""
import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path

DOCKER = ["env", "-u", "DOCKER_HOST", "-u", "DOCKER_CONTEXT", "-u", "DOCKER_TLS", "-u", "DOCKER_TLS_VERIFY", "-u", "DOCKER_CERT_PATH", "docker", "--host=unix:///var/run/docker.sock"]
SOURCE = os.environ["OSS_TEST_SOURCE_CONTAINER"]
TARGET = os.environ["OSS_TEST_RESTORE_CONTAINER"]


def query(container, statement):
    return subprocess.check_output(
        DOCKER + ["exec", "-i", container, "psql", "-v", "ON_ERROR_STOP=1", "-t", "-A",
                  "-U", "siteyonetim", "-d", "siteyonetim_test"],
        input=statement, text=True,
    ).strip()


def tables(container):
    return query(container, "SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename").splitlines()


def snapshot(container, names):
    result = {}
    for name in names:
        quoted = '"' + name.replace('"', '""') + '"'
        raw = query(container, f"SELECT coalesce(jsonb_agg(to_jsonb(t) ORDER BY to_jsonb(t)::text),'[]'::jsonb)::text FROM public.{quoted} t")
        result[name] = {"rows": len(json.loads(raw)), "sha256": hashlib.sha256(raw.encode()).hexdigest()}
    return result


def main():
    identities = [subprocess.check_output(DOCKER + ["inspect", "--format={{.Id}}", c], text=True).strip() for c in [SOURCE, TARGET]]
    if identities[0] == identities[1]:
        raise RuntimeError("Source and target must be different containers")
    for container in [SOURCE, TARGET]:
        if query(container, "SELECT current_database()") != "siteyonetim_test":
            raise RuntimeError("Synthetic database required")
        if not query(container, "SHOW server_version").startswith("17."):
            raise RuntimeError("PostgreSQL 17 required")
    if tables(TARGET):
        raise RuntimeError("Restore target must have an empty public schema")
    names = tables(SOURCE)
    if not {"User", "Organization", "Payment", "PaymentReversal", "AuditLog", "_prisma_migrations", "FinancialCategory", "FinancialEntry", "FinancialEntryReversal"}.issubset(names):
        raise RuntimeError("Source fixture/migrations missing")
    # Quiesce writers before invoking this drill; the independent pg_dump snapshot
    # is consistent, but before/after hashes intentionally detect concurrent writes.
    before = snapshot(SOURCE, names)
    catalog_sql = """SELECT json_build_object(
      'indexes',(SELECT json_agg(indexdef ORDER BY indexdef) FROM pg_indexes WHERE schemaname='public'),
      'constraints',(SELECT json_agg(x ORDER BY x) FROM (SELECT conname||':'||pg_get_constraintdef(oid) x FROM pg_constraint WHERE connamespace='public'::regnamespace)s),
      'triggers',(SELECT json_agg(x ORDER BY x) FROM (SELECT pg_get_triggerdef(oid) x FROM pg_trigger WHERE NOT tgisinternal AND tgrelid IN (SELECT oid FROM pg_class WHERE relnamespace='public'::regnamespace))s));"""
    catalog = json.loads(query(SOURCE, catalog_sql))
    with tempfile.TemporaryDirectory(prefix="siteyonetim-recovery-", dir=os.environ.get("RUNNER_TEMP")) as temp:
        dump = Path(temp) / "synthetic.dump"
        with dump.open("wb") as stream:
            dump.chmod(0o600)
            subprocess.run(DOCKER + ["exec", SOURCE, "pg_dump", "-U", "siteyonetim", "-d", "siteyonetim_test", "--format=custom"], stdout=stream, check=True)
        digest = hashlib.sha256(dump.read_bytes()).hexdigest()
        with dump.open("rb") as stream:
            subprocess.run(DOCKER + ["exec", "-i", TARGET, "pg_restore", "-U", "siteyonetim", "-d", "siteyonetim_test", "--exit-on-error", "--single-transaction"], stdin=stream, check=True)
        if names != tables(TARGET) or before != snapshot(TARGET, names):
            raise RuntimeError("Restored table names, rows or hashes differ")
        if before != snapshot(SOURCE, names):
            raise RuntimeError("Source changed during the drill; quiesce writers")
        if catalog != json.loads(query(TARGET, catalog_sql)):
            raise RuntimeError("Restored indexes/constraints/triggers differ")
    print(json.dumps({"verified": True, "tables": before, "totalRows": sum(v["rows"] for v in before.values()), "dumpSha256": digest, "catalogEqual": True}, indent=2))


if __name__ == "__main__":
    main()
