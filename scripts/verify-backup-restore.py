# SPDX-License-Identifier: AGPL-3.0-only
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


def digest_stream(stream):
    """Bounded client memory; COPY text escapes embedded row newlines."""
    digest = hashlib.sha256()
    rows = 0
    while chunk := stream.read(64 * 1024):
        digest.update(chunk)
        rows += chunk.count(b"\n")
    return digest.hexdigest(), rows


def snapshot(container, names):
    result = {}
    for name in names:
        quoted = '"' + name.replace('"', '""') + '"'
        # Sort can spill to PostgreSQL temporary disk instead of building one
        # jsonb array. Only one row is converted to JSON at a time.
        statement = f"""COPY (SELECT to_jsonb(t)::text FROM public.{quoted} t ORDER BY to_jsonb(t)::text COLLATE "C") TO STDOUT WITH (FORMAT text, ENCODING 'UTF8')"""
        command = DOCKER + ["exec", "-i", container, "psql", "-X", "-q", "-v", "ON_ERROR_STOP=1",
                            "-U", "siteyonetim", "-d", "siteyonetim_test", "-c", statement]
        with tempfile.TemporaryFile() as errors:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=errors)
            try:
                digest, rows = digest_stream(process.stdout)
                if process.wait() != 0:
                    # Do not expose row contents or database diagnostics in CI.
                    raise RuntimeError("Table streaming failed; inspect the isolated database privately")
            finally:
                process.stdout.close()
                if process.poll() is None:
                    process.kill()
                    process.wait()
        result[name] = {"rows": rows, "sha256": digest}
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
      'tableAcl',(SELECT json_agg(x ORDER BY x) FROM (
        SELECT c.relname||':'||pg_get_userbyid(a.grantor)||':'||CASE WHEN a.grantee=0 THEN 'PUBLIC' ELSE pg_get_userbyid(a.grantee) END||':'||a.privilege_type||':'||a.is_grantable::text x
        FROM pg_class c CROSS JOIN LATERAL aclexplode(coalesce(c.relacl,acldefault(CASE WHEN c.relkind='S' THEN 'S'::"char" ELSE 'r'::"char" END,c.relowner))) a
        WHERE c.relnamespace='public'::regnamespace AND c.relkind IN ('r','S'))s),
      'columnAcl',(SELECT json_agg(x ORDER BY x) FROM (
        SELECT c.relname||':'||a.attname||':'||pg_get_userbyid(g.grantor)||':'||CASE WHEN g.grantee=0 THEN 'PUBLIC' ELSE pg_get_userbyid(g.grantee) END||':'||g.privilege_type||':'||g.is_grantable::text x
        FROM pg_attribute a JOIN pg_class c ON c.oid=a.attrelid CROSS JOIN LATERAL aclexplode(a.attacl) g
        WHERE c.relnamespace='public'::regnamespace)s),
      'schemaAcl',(SELECT nspacl::text FROM pg_namespace WHERE nspname='public'),
      'triggers',(SELECT json_agg(x ORDER BY x) FROM (SELECT pg_get_triggerdef(oid) x FROM pg_trigger WHERE NOT tgisinternal AND tgrelid IN (SELECT oid FROM pg_class WHERE relnamespace='public'::regnamespace))s));"""
    catalog = json.loads(query(SOURCE, catalog_sql))
    with tempfile.TemporaryDirectory(prefix="siteyonetim-recovery-", dir=os.environ.get("RUNNER_TEMP")) as temp:
        dump = Path(temp) / "synthetic.dump"
        with dump.open("wb") as stream:
            dump.chmod(0o600)
            subprocess.run(DOCKER + ["exec", SOURCE, "pg_dump", "-U", "siteyonetim", "-d", "siteyonetim_test", "--format=custom"], stdout=stream, check=True)
        with dump.open("rb") as stream:
            digest, _ = digest_stream(stream)
        with dump.open("rb") as stream:
            subprocess.run(DOCKER + ["exec", "-i", TARGET, "pg_restore", "-U", "siteyonetim", "-d", "siteyonetim_test", "--exit-on-error", "--single-transaction"], stdin=stream, check=True)
        if names != tables(TARGET) or before != snapshot(TARGET, names):
            raise RuntimeError("Restored table names, rows or hashes differ")
        if before != snapshot(SOURCE, names):
            raise RuntimeError("Source changed during the drill; quiesce writers")
        if catalog != json.loads(query(TARGET, catalog_sql)):
            raise RuntimeError("Restored indexes/constraints/triggers/ACLs differ")
    # Optional synthetic ACL fixture. Global role creation is deliberately external.
    runtime_checked = False
    if query(SOURCE, "SELECT EXISTS(SELECT FROM pg_roles WHERE rolname='s03f_restore_runtime')") == "t":
        for container in [SOURCE, TARGET]:
            expected = query(container, """SELECT (NOT rolsuper AND NOT rolcanlogin AND NOT rolcreatedb AND NOT rolcreaterole
              AND has_table_privilege(rolname, '\"Payment\"', 'SELECT')
              AND has_column_privilege(rolname, '\"Payment\"', 'id', 'UPDATE')
              AND NOT has_column_privilege(rolname, '\"Payment\"', 'amountKurus', 'UPDATE')
              AND NOT has_table_privilege(rolname, '\"Payment\"', 'DELETE')
              AND NOT has_table_privilege(rolname, '\"Payment\"', 'TRUNCATE'))
              FROM pg_roles WHERE rolname='s03f_restore_runtime'""")
            if expected != "t":
                raise RuntimeError("Synthetic runtime privilege boundary differs")
            query(container, 'SET ROLE s03f_restore_runtime; SELECT count(*) FROM "Payment"; RESET ROLE;')
        runtime_checked = True
    print(json.dumps({"verified": True, "tables": before, "totalRows": sum(v["rows"] for v in before.values()), "dumpSha256": digest, "catalogEqual": True, "runtimePrivilegesChecked": runtime_checked, "hashFormat": "postgres-copy-text-jsonl-v1"}, indent=2))


if __name__ == "__main__":
    main()
