#!/usr/bin/env python3
"""Host-only SiteYonetim operations. No shell, credentials in argv, or web endpoint."""
import argparse
import contextlib
import datetime as dt
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import stat
import subprocess
import sys
import uuid

UTC = dt.timezone.utc
STAMP = '%Y%m%dT%H%M%SZ'
NAME = re.compile(r'backup-(\d{8}T\d{6}Z)-[a-f0-9]{32}\Z')
DOCKER = ['env', '-u', 'DOCKER_HOST', '-u', 'DOCKER_CONTEXT', '-u', 'DOCKER_TLS', '-u', 'DOCKER_TLS_VERIFY', '-u', 'DOCKER_CERT_PATH', 'docker', '--host=unix:///var/run/docker.sock']
ROOT = Path(__file__).resolve().parents[1]
CATALOG = """SELECT json_build_object(
'indexes',(SELECT json_agg(indexdef ORDER BY indexdef) FROM pg_indexes WHERE schemaname='public'),
'constraints',(SELECT json_agg(x ORDER BY x) FROM (SELECT conname||':'||pg_get_constraintdef(oid) x FROM pg_constraint WHERE connamespace='public'::regnamespace)s),
'owners',(SELECT json_agg(x ORDER BY x) FROM (SELECT relname||':'||pg_get_userbyid(relowner) x FROM pg_class WHERE relnamespace='public'::regnamespace AND relkind IN ('r','S','v','m'))s),
'tableAcl',(SELECT json_agg(x ORDER BY x) FROM (SELECT c.relname||':'||pg_get_userbyid(a.grantor)||':'||CASE WHEN a.grantee=0 THEN 'PUBLIC' ELSE pg_get_userbyid(a.grantee) END||':'||a.privilege_type||':'||a.is_grantable::text x FROM pg_class c CROSS JOIN LATERAL aclexplode(coalesce(c.relacl,acldefault(CASE WHEN c.relkind='S' THEN 'S'::"char" ELSE 'r'::"char" END,c.relowner)))a WHERE c.relnamespace='public'::regnamespace AND c.relkind IN ('r','S'))s),
'columnAcl',(SELECT json_agg(x ORDER BY x) FROM (SELECT c.relname||':'||a.attname||':'||pg_get_userbyid(g.grantor)||':'||CASE WHEN g.grantee=0 THEN 'PUBLIC' ELSE pg_get_userbyid(g.grantee) END||':'||g.privilege_type||':'||g.is_grantable::text x FROM pg_attribute a JOIN pg_class c ON c.oid=a.attrelid CROSS JOIN LATERAL aclexplode(a.attacl)g WHERE c.relnamespace='public'::regnamespace)s),
'defaultAcl',(SELECT json_agg(x ORDER BY x) FROM (SELECT d.defaclrole::regrole::text||':'||d.defaclnamespace::regnamespace::text||':'||d.defaclobjtype::text||':'||a.grantee::regrole::text||':'||a.privilege_type x FROM pg_default_acl d CROSS JOIN LATERAL aclexplode(d.defaclacl)a)s),
'schema',(SELECT nspowner::regrole::text||':'||nspacl::text FROM pg_namespace WHERE nspname='public'),
'functions',(SELECT json_agg(x ORDER BY x) FROM (SELECT pg_get_functiondef(oid) x FROM pg_proc WHERE pronamespace='public'::regnamespace)s),
'triggers',(SELECT json_agg(x ORDER BY x) FROM (SELECT pg_get_triggerdef(oid)x FROM pg_trigger WHERE NOT tgisinternal AND tgrelid IN(SELECT oid FROM pg_class WHERE relnamespace='public'::regnamespace))s));"""

class Refused(Exception):
    pass


def require(ok):
    if not ok:
        raise Refused('Operation refused: identity, policy or validation check failed')


def private(path, directory=False):
    path = Path(path)
    require(path.is_absolute() and str(path) == os.path.normpath(str(path)))
    for parent in [*path.parents, path]:
        require(not parent.is_symlink())
    info = path.lstat()
    require((stat.S_ISDIR(info.st_mode) if directory else stat.S_ISREG(info.st_mode)))
    require(info.st_uid == os.getuid() and info.st_mode & 0o077 == 0)
    if not directory:
        require(info.st_nlink == 1)
    return path


def read_json(path):
    private(path)
    require(Path(path).stat().st_size < 128 * 1024)
    return json.loads(Path(path).read_text())


def run(args, data=None):
    result = subprocess.run(args, input=data, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=False)
    require(result.returncode == 0)
    return result.stdout.decode().strip()


def sql(binding, statement):
    return run(DOCKER + ['exec', '-i', binding['container_id'], 'psql', '-X', '-q', '-A', '-t', '-v', 'ON_ERROR_STOP=1', '-U', 'postgres', '-d', binding['database']], statement.encode())


def identify(container, database):
    require(re.fullmatch(r'[a-zA-Z0-9_.-]+', container) and re.fullmatch(r'[a-z][a-z0-9_]{0,62}', database))
    cid = run(DOCKER + ['inspect', '--format={{.Id}}', container])
    require(re.fullmatch('[a-f0-9]{64}', cid))
    binding = {'container_id':cid, 'database':database}
    require(sql(binding, 'SELECT current_database()') == database)
    require(170000 <= int(sql(binding, 'SHOW server_version_num')) < 180000)
    binding['system_identifier'] = sql(binding, 'SELECT system_identifier FROM pg_control_system()')
    return binding


def bound(binding):
    require(set(binding) == {'container_id', 'database', 'system_identifier'})
    actual = identify(binding['container_id'], binding['database'])
    require(actual == binding)
    return binding


def config(path):
    c = read_json(path)
    require(set(c) == {'source', 'backup_directory', 'recipients_file', 'retention_days', 'revision'})
    require(set(c['source']) == {'container_id','database','system_identifier'})
    require(re.fullmatch('[a-f0-9]{64}', c['source']['container_id']))
    require(re.fullmatch(r'[a-z][a-z0-9_]{0,62}', c['source']['database']))
    require(re.fullmatch(r'[0-9]+', c['source']['system_identifier']))
    require(re.fullmatch('[a-f0-9]{40}', c['revision']))
    require(type(c['retention_days']) is int and 1 <= c['retention_days'] <= 3650)
    private(c['recipients_file'])
    return c


def initialize(path):
    path = Path(path)
    require(path.is_absolute() and len(path.parts) >= 4)
    if not path.exists():
        path.mkdir(mode=0o700)
    private(path, True)
    require(not list(path.iterdir()))
    (path / '.siteyonetim-backups').write_text('siteyonetim-backups-v1\n')
    (path / '.siteyonetim-backups').chmod(0o600)


@contextlib.contextmanager
def locked(path):
    root = private(path, True)
    require(len(root.parts) >= 4)
    private(root / '.siteyonetim-backups')
    require((root / '.siteyonetim-backups').read_text() == 'siteyonetim-backups-v1\n')
    fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    lock = os.open('.lock', os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600, dir_fd=fd)
    try:
        require(os.fstat(lock).st_nlink == 1 and os.fstat(lock).st_uid == os.getuid())
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise Refused('Another backup operation is active') from None
        yield root
    finally:
        os.close(lock)
        os.close(fd)


def hash_file(path):
    private(path)
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        while block := stream.read(65536):
            digest.update(block)
    return digest.hexdigest()


def metadata(binding):
    rows = json.loads(sql(binding, '''SELECT coalesce(json_agg(json_build_object('name',migration_name,'checksum',checksum,'finished',finished_at IS NOT NULL,'rolled_back',rolled_back_at IS NOT NULL) ORDER BY migration_name),'[]'::json) FROM "_prisma_migrations"'''))
    expected = sorted((ROOT / 'prisma/migrations').glob('*/migration.sql'))
    require(0 < len(rows) <= len(expected))
    for row, migration in zip(rows, expected):
        require(row == {'name':migration.parent.name, 'checksum':hashlib.sha256(migration.read_bytes()).hexdigest(), 'finished':True, 'rolled_back':False})
    catalog = hashlib.sha256(sql(binding, CATALOG).encode()).hexdigest()
    return {'migrations':rows, 'catalog_sha256':catalog}


def backup_role_safe(binding):
    return sql(binding, """SELECT (NOT rolcanlogin AND NOT rolsuper AND NOT rolcreatedb AND NOT rolcreaterole AND NOT rolreplication
AND NOT has_schema_privilege(oid,'public','CREATE') AND NOT has_database_privilege(oid,current_database(),'CREATE')
AND NOT EXISTS(SELECT FROM pg_auth_members WHERE member=r.oid)
AND NOT EXISTS(SELECT FROM pg_class WHERE relowner=r.oid)
AND NOT EXISTS(SELECT FROM pg_namespace WHERE nspowner=r.oid)
AND NOT EXISTS(SELECT FROM pg_class c WHERE c.relnamespace='public'::regnamespace AND c.relkind='r' AND has_table_privilege(r.oid,c.oid,'INSERT,UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER'))
)::text FROM pg_roles r WHERE rolname='sy_backup'""") == 'true'


def provision(binding):
    # Explicit host-operator action; never executed by app/init/migrate automatically.
    existing = sql(binding, "SELECT count(*) FROM pg_roles WHERE rolname='sy_backup'")
    if existing == '0':
        sql(binding, 'CREATE ROLE sy_backup NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION CONNECTION LIMIT 2')
    require(backup_role_safe(binding))
    sql(binding, f'''GRANT CONNECT ON DATABASE "{binding['database']}" TO sy_backup;
GRANT USAGE ON SCHEMA public TO sy_backup;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO sy_backup;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO sy_backup;
ALTER DEFAULT PRIVILEGES FOR ROLE sy_migrator IN SCHEMA public GRANT SELECT ON TABLES TO sy_backup;
ALTER DEFAULT PRIVILEGES FOR ROLE sy_migrator IN SCHEMA public GRANT SELECT ON SEQUENCES TO sy_backup;''')


def stop_process(p):
    if p and p.poll() is None:
        with contextlib.suppress(ProcessLookupError):
            os.killpg(p.pid, signal.SIGTERM)
        try:
            p.wait(timeout=10)
        except subprocess.TimeoutExpired:
            with contextlib.suppress(ProcessLookupError):
                os.killpg(p.pid, signal.SIGKILL)
            p.wait()


def pipeline(producer, consumer, output=None, drain=False):
    a = b = None
    try:
        a = subprocess.Popen(producer, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, start_new_session=True)
        b = subprocess.Popen(consumer, stdin=a.stdout, stdout=output or subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        if not drain:
            a.stdout.close()
        result = b.wait()
        if drain:
            # pg_restore --list may finish after the TOC. Always authenticate ALL age bytes.
            while a.stdout.read(65536):
                pass
            a.stdout.close()
        require(result == 0 and a.wait() == 0)
    finally:
        stop_process(b)
        stop_process(a)


def write_json(path, value):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'w') as out:
        json.dump(value, out, sort_keys=True)
        out.flush()
        os.fsync(out.fileno())


def backup(c):
    source = bound(c['source'])
    before = metadata(source)
    require(backup_role_safe(source))
    require(sql(source, "SELECT count(*) FROM pg_roles WHERE rolname='sy_backup' AND NOT rolcanlogin AND NOT rolsuper AND NOT rolcreatedb AND NOT rolcreaterole") == '1')
    root = private(c['backup_directory'], True)
    require(shutil.disk_usage(root).free >= 64 * 1024 * 1024)
    stamp = dt.datetime.now(UTC).strftime(STAMP)
    token = uuid.uuid4().hex
    partial = root / ('.partial-' + token)
    partial.mkdir(mode=0o700)
    try:
        cipher = partial / 'database.age'
        with cipher.open('xb') as output:
            cipher.chmod(0o600)
            pipeline(DOCKER + ['exec', source['container_id'], 'pg_dump', '-U', 'postgres', '--role=sy_backup', '-d', source['database'], '-Fc'], ['age', '-R', c['recipients_file']], output)
            output.flush()
            os.fsync(output.fileno())
        require(before == metadata(source))
        manifest = {'format':1, 'created':stamp, 'source':source, 'revision':c['revision'], 'sha256':hash_file(cipher), 'roles':['sy_migrator','sy_runtime','sy_backup'], **before}
        write_json(partial / 'manifest.json', manifest)
        final = root / f'backup-{stamp}-{token}'
        fd = os.open(partial, os.O_RDONLY | os.O_DIRECTORY)
        os.fsync(fd)
        os.close(fd)
        os.rename(partial, final)
        fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY)
        os.fsync(fd)
        os.close(fd)
        return final.name
    finally:
        # Only this invocation's known encrypted files; never recursive deletion.
        if partial.exists():
            for name in ['database.age', 'manifest.json']:
                with contextlib.suppress(FileNotFoundError):
                    (partial / name).unlink()
            partial.rmdir()


def entry(root, name):
    match = NAME.fullmatch(name)
    require(match)
    directory = private(root / name, True)
    require({p.name for p in directory.iterdir()} <= {'database.age','manifest.json','verified.json'})
    m = read_json(directory / 'manifest.json')
    require(set(m) == {'format','created','source','revision','sha256','roles','migrations','catalog_sha256'})
    require(m['format'] == 1 and m['created'] == match[1] and m['roles'] == ['sy_migrator','sy_runtime','sy_backup'])
    require(hash_file(directory / 'database.age') == m['sha256'])
    dt.datetime.strptime(m['created'], STAMP)
    return directory, m


def verify(root, name, identity):
    identity = private(identity)
    require(root not in identity.parents)
    directory, m = entry(root, name)
    pipeline(['age', '-d', '-i', str(identity), str(directory / 'database.age')], DOCKER + ['run','--rm','--pull=never','-i','--network=none','--read-only','--user=65534:65534','--cap-drop=ALL','--security-opt=no-new-privileges:true','--entrypoint=pg_restore','postgres:17-bookworm','--list'], drain=True)
    receipt = directory / 'verified.json'
    if receipt.exists():
        require(read_json(receipt)['sha256'] == m['sha256'])
    else:
        write_json(receipt, {'sha256':m['sha256'], 'verified_at':dt.datetime.now(UTC).isoformat()})
    return m


def restore(root, name, identity, target):
    # The target binding must be provisioned by the operator, never inferred from source.
    require(set(target) == {'purpose','binding'} and target['purpose'] == 'isolated-recovery-drill')
    binding = bound(target['binding'])
    require(binding['database'] == 'siteyonetim_test')
    require(json.loads(run(DOCKER + ['inspect','--format={{json .HostConfig.PortBindings}}',binding['container_id']])) == {})
    m = verify(root, name, identity)
    require(binding['system_identifier'] != m['source']['system_identifier'])
    # Check all user namespaces, not just public tables.
    require(sql(binding, """SELECT count(*) FROM (
SELECT oid FROM pg_class WHERE relnamespace IN(SELECT oid FROM pg_namespace WHERE nspname NOT LIKE 'pg_%' AND nspname<>'information_schema')
UNION ALL SELECT oid FROM pg_proc WHERE pronamespace IN(SELECT oid FROM pg_namespace WHERE nspname NOT LIKE 'pg_%' AND nspname<>'information_schema')
UNION ALL SELECT oid FROM pg_type WHERE typnamespace IN(SELECT oid FROM pg_namespace WHERE nspname NOT LIKE 'pg_%' AND nspname<>'information_schema')
UNION ALL SELECT oid FROM pg_namespace WHERE nspname NOT LIKE 'pg_%' AND nspname NOT IN('public','information_schema')
UNION ALL SELECT oid FROM pg_extension WHERE extname<>'plpgsql')x""") == '0')
    # No global role dumps/password hashes. Only the fixed app roles are recreated.
    for role in m['roles']:
        if sql(binding, f"SELECT count(*) FROM pg_roles WHERE rolname='{role}'") == '0':
            sql(binding, f'CREATE ROLE {role} NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION CONNECTION LIMIT {dict(sy_migrator=5,sy_runtime=10,sy_backup=2)[role]}')
        require(sql(binding, f"SELECT (NOT rolsuper AND NOT rolcreatedb AND NOT rolcreaterole AND NOT rolreplication)::text FROM pg_roles WHERE rolname='{role}'") == 'true')
        require(sql(binding, f"SELECT count(*) FROM pg_auth_members WHERE member=(SELECT oid FROM pg_roles WHERE rolname='{role}')") == '0')
    pipeline(['age','-d','-i',str(private(identity)),str(root / name / 'database.age')], DOCKER + ['exec','-i',binding['container_id'],'pg_restore','-U','postgres','-d',binding['database'],'--exit-on-error','--single-transaction'])
    sql(binding, 'REVOKE ALL ON DATABASE siteyonetim_test FROM PUBLIC; GRANT CONNECT ON DATABASE siteyonetim_test TO sy_runtime; GRANT CONNECT,CREATE ON DATABASE siteyonetim_test TO sy_migrator;')
    actual = metadata(binding)
    require(actual == {key:m[key] for key in ['migrations','catalog_sha256']})
    return {'restored':True, 'migrations':len(actual['migrations']), 'catalog_equal':True}


def prune(c, root, dry_run=True, now=None):
    now = now or dt.datetime.now(UTC)
    completed = []
    verified = []
    for p in root.iterdir():
        if not NAME.fullmatch(p.name):
            continue
        try:
            directory, m = entry(root, p.name)
        except (Refused, OSError, ValueError):
            continue  # corrupt/incomplete is never counted as a good copy or auto-deleted
        created = dt.datetime.strptime(m['created'], STAMP).replace(tzinfo=UTC)
        completed.append((created,p.name))
        if (directory / 'verified.json').exists() and read_json(directory / 'verified.json').get('sha256') == m['sha256']:
            verified.append((created,p.name))
    protected = {max(completed)[1]} if completed else set()
    if verified:
        protected.add(max(verified)[1])
    selected = [name for created,name in completed if name not in protected and created < now-dt.timedelta(days=c['retention_days'])]
    if not dry_run:
        for name in selected:
            directory, _ = entry(root, name)
            for item in ['verified.json','database.age','manifest.json']:
                with contextlib.suppress(FileNotFoundError):
                    private(directory / item).unlink()
            directory.rmdir()
    return {'dry_run':dry_run, 'eligible_count':len(selected), 'protected_count':len(protected)}


def status(root):
    completed = []
    for p in root.iterdir():
        if NAME.fullmatch(p.name):
            try:
                _, m = entry(root, p.name)
                completed.append(m['created'])
            except (Refused, ValueError, OSError):
                pass
    return {'last_successful_backup':max(completed) if completed else None, 'valid_copies':len(completed)}


def main():
    os.umask(0o077)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=['init','identify','provision','backup','verify','restore-drill','prune','status'])
    parser.add_argument('--config')
    parser.add_argument('--directory')
    parser.add_argument('--container')
    parser.add_argument('--database')
    parser.add_argument('--backup')
    parser.add_argument('--identity')
    parser.add_argument('--target')
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--max-age-hours',type=int)
    args = parser.parse_args()
    if args.operation == 'init':
        initialize(args.directory)
        result = {'initialized':True}
    elif args.operation == 'identify':
        result = identify(args.container,args.database)
    else:
        c = config(args.config)
        if args.operation == 'provision':
            provision(bound(c['source']))
            result = {'backup_role_ready':True}
        else:
            with locked(c['backup_directory']) as root:
                if args.operation == 'backup':
                    result = {'backup':backup(c), 'completed':True}
                elif args.operation == 'verify':
                    verify(root,args.backup,args.identity)
                    result = {'authenticated_decryption_and_archive_list':True}
                elif args.operation == 'restore-drill':
                    result = restore(root,args.backup,args.identity,read_json(args.target))
                elif args.operation == 'prune':
                    result = prune(c,root,not args.apply)
                else:
                    result = status(root)
    if args.max_age_hours is not None:
        require(args.operation == 'status' and 1 <= args.max_age_hours <= 87600)
        stamp=result['last_successful_backup']
        result['healthy']=bool(stamp and dt.datetime.now(UTC)-dt.datetime.strptime(stamp,STAMP).replace(tzinfo=UTC) <= dt.timedelta(hours=args.max_age_hours))
    print(json.dumps(result))
    if result.get('healthy') is False:
        sys.exit(2)


def interrupted(_signal, _frame):
    raise KeyboardInterrupt


if __name__ == '__main__':
    signal.signal(signal.SIGTERM, interrupted)
    try:
        main()
    except KeyboardInterrupt:
        print('Operation interrupted; no incomplete backup is valid', file=sys.stderr)
        sys.exit(130)
    except Exception:
        # No SQL diagnostics, identities, row contents or credentials in public logs.
        print('Operation failed or refused; inspect the selected private configuration and operation state', file=sys.stderr)
        sys.exit(1)
