#!/usr/bin/env python3
"""Real encrypted PG17 recovery and failed-upgrade drill; own resources only."""
import contextlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import shutil
import tempfile
import time
import uuid
import backup_ops as ops
import safe_upgrade

D = ops.DOCKER
IMAGE = 'postgres:17-bookworm'
MIGRATE = 's04a-ci-migrate'
APP = 's04a-ci-app'
resources = []
networks = []


def ready(cid):
    for _ in range(60):
        r = subprocess.run(D+['exec',cid,'pg_isready','-h','127.0.0.1','-U','postgres','-d','siteyonetim_test'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        if r.returncode == 0:
            return
        time.sleep(.5)
    raise ops.Refused('Synthetic PostgreSQL did not become ready')


def cluster():
    name = 's04c-'+uuid.uuid4().hex
    network = name+'-net'
    ops.run(D+['network','create','--internal',network])
    networks.append(network)
    cid = ops.run(D+['run','-d','--name',name,'--network',network,'--network-alias','db','-e','POSTGRES_HOST_AUTH_METHOD=trust','-e','POSTGRES_DB=siteyonetim_test',IMAGE])
    resources.append(cid)
    ready(cid)
    return ops.identify(cid,'siteyonetim_test'),network


def image(binding, args, fixture=None, check=True):
    env = dict(os.environ)
    env['DATABASE_URL']='postgresql://sy_migrator@127.0.0.1:5432/siteyonetim_test'
    env['TEST_DATABASE_URL']=env['DATABASE_URL']
    command = D+['run','--rm','--network','container:'+binding['container_id'],'--user',f'{os.getuid()}:{os.getgid()}','-e','DATABASE_URL','-e','TEST_DATABASE_URL']
    if fixture:
        command += ['-v',str(fixture.parent)+':/fixtures']
    r = subprocess.run(command+[MIGRATE,'node']+args,env=env,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
    if check:
        ops.require(r.returncode == 0)
    return r


def reject(operation):
    try:
        operation()
    except (ops.Refused,OSError,ValueError):
        return
    raise AssertionError('Expected refusal')


def run():
    with tempfile.TemporaryDirectory(prefix='siteyonetim-s04c-recovery-') as temp:
        base = Path(temp)
        root = base/'backups'
        ops.initialize(root)
        key = base/'identity.agekey'
        ops.run(['age-keygen','-o',str(key)])
        key.chmod(0o600)
        recipients = base/'recipients'
        recipients.write_text(ops.run(['age-keygen','-y',str(key)])+'\n')
        recipients.chmod(0o600)
        print('recovery stage: isolated source',flush=True)
        source,network = cluster()
        ops.sql(source, '''CREATE ROLE sy_migrator LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION CONNECTION LIMIT 5;
CREATE ROLE sy_runtime LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION CONNECTION LIMIT 10;
REVOKE ALL ON DATABASE siteyonetim_test FROM PUBLIC;
GRANT CONNECT,CREATE ON DATABASE siteyonetim_test TO sy_migrator;
GRANT CONNECT ON DATABASE siteyonetim_test TO sy_runtime;
ALTER SCHEMA public OWNER TO sy_migrator;
REVOKE ALL ON SCHEMA public FROM PUBLIC;
GRANT USAGE ON SCHEMA public TO sy_runtime;''')
        image(source,['node_modules/prisma/build/index.js','migrate','deploy'])
        ops.sql(source,'SET ROLE sy_migrator;'+(ops.ROOT/'docker/grants.sql').read_text())
        fixture_dir=base/'fixtures'
        fixture_dir.mkdir(mode=0o700)
        fixture = fixture_dir/'fixture.json'
        image(source,['node_modules/tsx/dist/cli.mjs','scripts/recovery-probe.ts','create','/fixtures/fixture.json'],fixture)
        # >30 MiB of synthetic table text, no arbitrary real personal data.
        ops.sql(source, '''INSERT INTO "AuthAttempt"(key,count,"expiresAt") SELECT 's04c-'||g::text||repeat(md5(g::text),10),1,'2099-01-01'::timestamp FROM generate_series(1,100000)g''')
        profile_sql = '''SELECT json_build_object('audit_all',has_table_privilege('sy_runtime','"AuditLog"','SELECT'),'audit_id',has_column_privilege('sy_runtime','"AuditLog"','id','SELECT'),'runtime_ddl',has_schema_privilege('sy_runtime','public','CREATE'),'migrator_ddl',has_schema_privilege('sy_migrator','public','CREATE'))'''
        print('recovery stage: restricted backup role',flush=True)
        prior = ops.sql(source,profile_sql)
        ops.provision(source)
        ops.require(ops.sql(source,profile_sql) == prior)
        ops.require(ops.backup_role_safe(source))
        ops.sql(source,'SET ROLE sy_backup; SELECT count(*) FROM "AuditLog";')
        for statement in ['CREATE TABLE public.forbidden(id int)','UPDATE "AuthAttempt" SET count=count','DELETE FROM "AuthAttempt"','TRUNCATE "AuthAttempt"']:
            reject(lambda statement=statement:ops.sql(source,'SET ROLE sy_backup;'+statement))
        failed = subprocess.run(D+['exec',source['container_id'],'pg_dump','-U','postgres','--role=sy_runtime','-d','siteyonetim_test','-Fc'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        ops.require(failed.returncode != 0)
        c = {'source':source,'backup_directory':str(root),'recipients_file':str(recipients),'retention_days':7,'revision':ops.run(['git','rev-parse','HEAD'])}
        config_file = base/'backup.json'
        ops.write_json(config_file,c)
        target,target_network = cluster()
        target_config = {'purpose':'isolated-recovery-drill','binding':target}
        # Reuse bounded row hashing from the historical proof without rewriting it.
        os.environ['OSS_TEST_SOURCE_CONTAINER']=source['container_id']
        os.environ['OSS_TEST_RESTORE_CONTAINER']=target['container_id']
        spec = importlib.util.spec_from_file_location('historical_recovery',ops.ROOT/'scripts/verify-backup-restore.py')
        historical = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(historical)
        names = historical.tables(source['container_id'])
        before = historical.snapshot(source['container_id'],names)
        print('recovery stage: encrypted backup and negative validation',flush=True)
        with ops.locked(root):
            name = ops.backup(c)
            ops.verify(root,name,key)
            # The role-only dump is a complete readable archive, not a runtime-role shortcut.
            wrong = base/'wrong.agekey'
            ops.run(['age-keygen','-o',str(wrong)])
            wrong.chmod(0o600)
            reject(lambda:ops.verify(root,name,wrong))
            reject(lambda:ops.verify(root,name,base/'missing.agekey'))
            # A modified ciphertext is rejected both by SHA and by age authentication.
            badname = 'backup-'+name.split('-')[1]+'-'+uuid.uuid4().hex
            bad = root/badname
            bad.mkdir(mode=0o700)
            shutil.copyfile(root/name/'database.age',bad/'database.age')
            with (bad/'database.age').open('r+b') as cipher:
                cipher.seek((bad/'database.age').stat().st_size//2)
                old=cipher.read(1)
                cipher.seek(-1,1)
                cipher.write(bytes([old[0]^1]))
            (bad/'database.age').chmod(0o600)
            manifest = ops.read_json(root/name/'manifest.json')
            ops.write_json(bad/'manifest.json',manifest)
            reject(lambda:ops.verify(root,badname,key))
            (bad/'manifest.json').unlink()
            manifest['sha256']=ops.hash_file(bad/'database.age')
            ops.write_json(bad/'manifest.json',manifest)
            reject(lambda:ops.verify(root,badname,key))
            reject(lambda:ops.restore(root,name,key,{'purpose':'isolated-recovery-drill','binding':source}))
            reject(lambda:ops.restore(root,name,key,{'purpose':'production','binding':target}))
            occupied,_ = cluster()
            ops.sql(occupied,'CREATE TABLE already_present(id integer)')
            reject(lambda:ops.restore(root,name,key,{'purpose':'isolated-recovery-drill','binding':occupied}))
            print('recovery stage: isolated empty restore',flush=True)
            result = ops.restore(root,name,key,target_config)
        ops.require(result['catalog_equal'] and result['migrations'] == 11)
        ops.require(before == historical.snapshot(target['container_id'],names))
        ops.require(before == historical.snapshot(source['container_id'],names))
        # Recreated roles have no copied passwords and are initially NOLOGIN.
        ops.sql(target,'ALTER ROLE sy_migrator LOGIN; ALTER ROLE sy_runtime LOGIN;')
        image(target,['node_modules/tsx/dist/cli.mjs','scripts/recovery-probe.ts','verify','/fixtures/fixture.json'],fixture)
        reject(lambda:ops.sql(target,'SET ROLE sy_runtime; CREATE TABLE public.forbidden(id int)'))
        reject(lambda:ops.sql(target,'SET ROLE sy_runtime; SELECT * FROM "AuditLog"'))
        reject(lambda:ops.sql(target,'SET ROLE sy_runtime; UPDATE "Payment" SET id=id'))
        runtime_password = base/'runtime_password'
        runtime_password.write_text(uuid.uuid4().hex+uuid.uuid4().hex)
        runtime_password.chmod(0o600)
        smtp = base/'smtp_url'
        smtp.touch(mode=0o600)
        app = ops.run(D+['run','-d','--read-only','--tmpfs','/tmp:size=160m,mode=1777','--cap-drop=ALL','--security-opt=no-new-privileges:true','--user',f'{os.getuid()}:{os.getgid()}','--network',target_network,'-e','POSTGRES_DB=siteyonetim_test','-e','APP_URL=https://example.invalid','-v',str(runtime_password)+':/run/secrets/runtime_password:ro','-v',str(smtp)+':/run/secrets/smtp_url:ro',APP])
        resources.append(app)
        def health():
            for _ in range(30):
                r = subprocess.run(D+['exec',app,'node','docker/health.mjs'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
                if r.returncode == 0:
                    return
                time.sleep(.5)
            raise ops.Refused('Restored app did not become healthy')
        print('recovery stage: restored standalone health',flush=True)
        health()
        ops.run(D+['restart',target['container_id']])
        ready(target['container_id'])
        health()
        ops.require(before == historical.snapshot(target['container_id'],names))
        # Exercise actual orchestration with real backup verification and a real failed
        # Prisma migration, in a disposable candidate schema copy, never historical SQL.
        candidate_js = """const fs=require('fs'),cp=require('child_process');fs.cpSync('prisma','/tmp/prisma',{recursive:true});fs.mkdirSync('/tmp/prisma/migrations/209901010001_failure');fs.writeFileSync('/tmp/prisma/migrations/209901010001_failure/migration.sql','SELECT 1/0;');process.exit(cp.spawnSync('node',['node_modules/prisma/build/index.js','migrate','deploy','--schema','/tmp/prisma/schema.prisma'],{stdio:'ignore',env:process.env}).status??1);"""
        events = []
        class Driver:
            def stop(self):
                events.append('stop')
                ops.run(D+['stop',app])
                ops.require(ops.run(D+['inspect','--format={{.State.Running}}',app]) == 'false')
            def build(self): events.append('build-reviewed-candidate')
            def migrate(self):
                events.append('migrate')
                ops.require(image(target,['-e',candidate_js],check=False).returncode == 0)
            def schema(self): events.append('schema')
            def start(self): events.append('start')
        print('recovery stage: failed real candidate migration',flush=True)
        updated = {**c,'source':target}
        with ops.locked(root):
            try:
                safe_upgrade.sequence(Driver(),lambda:ops.backup(updated),lambda n:ops.verify(root,n,key),lambda n:None)
                raise AssertionError('Expected real failed migration')
            except ops.Refused as error:
                ops.require('FAILED_WRITERS_STOPPED; stage=migrate' in str(error))
        ops.require(events == ['stop','build-reviewed-candidate','migrate','stop'])
        for table in names:
            if table != '_prisma_migrations':
                ops.require(before[table] == historical.snapshot(target['container_id'],[table])[table])
        ops.require(sql_failed_migration(target))
        # CLI failure exit, not a log-only failure; wrong target config remains private.
        target_file = base/'wrong-target.json'
        ops.write_json(target_file,{'purpose':'production','binding':target})
        cli = subprocess.run([sys.executable,str(ops.ROOT/'scripts/backup_ops.py'),'restore-drill','--config',str(config_file),'--backup',name,'--identity',str(key),'--target',str(target_file)],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        ops.require(cli.returncode == 1 and b'Operation failed or refused' in cli.stderr)
        # Basic log/manifest leak checks: fixed metadata only, no fixture identities/rows/key.
        for value in ['Sentetik',fixture.read_text(),key.read_text()]:
            ops.require(value not in (root/name/'manifest.json').read_text())
        print(json.dumps({'encrypted_recovery':True,'tables':len(names),'rows':sum(r['rows'] for r in before.values()),'migrations':11,'catalog_acl_equal':True,'backup_role_write_ddl_denied':True,'runtime_ddl_denied':True,'financial_tenant_probe':True,'restored_standalone_health':True,'restart_persistence':True,'failed_real_migration_writers_stopped':True}))


def sql_failed_migration(binding):
    return ops.sql(binding, 'SELECT count(*) FROM "_prisma_migrations" WHERE finished_at IS NULL AND rolled_back_at IS NULL') == '1'


if __name__ == '__main__':
    import sys
    try:
        run()
    finally:
        for cid in reversed(resources):
            subprocess.run(D+['rm','-f','-v',cid],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        for network in reversed(networks):
            subprocess.run(D+['network','rm',network],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
