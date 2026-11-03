#!/usr/bin/env python3
"""Explicit host operation; failures leave app writers stopped. No rollback/reset."""
import argparse
import json
import re
import signal
import subprocess
import sys
import uuid
from pathlib import Path
import backup_ops as ops


def sequence(driver, take_backup, verify_backup, restore_drill):
    """Shared real orchestration, also exercised with an injected failing migration."""
    stage = 'stop-writers'
    try:
        driver.stop()
        stage = 'backup'
        name = take_backup()
        stage = 'verify-backup'
        verify_backup(name)
        stage = 'restore-drill'
        restore_drill(name)
        stage = 'build'
        driver.build()
        stage = 'migrate'
        driver.migrate()
        stage = 'schema-check'
        driver.schema()
        stage = 'start-health'
        driver.start()
        return {'state':'SUCCESS', 'backup':name}
    except BaseException:
        try:
            driver.stop()
            state = 'FAILED_WRITERS_STOPPED'
        except BaseException:
            state = 'FAILED_WRITERS_STATE_UNKNOWN'
        raise ops.Refused(f'{state}; stage={stage}; operator recovery required') from None


class Compose:
    def __init__(self, repo, env_file, project, source):
        self.command = ops.DOCKER + ['compose','--env-file',str(env_file),'-p',project,'-f',str(repo / 'compose.selfhost.yaml')]
        self.source = source
        self.repo = repo

    def call(self, args):
        # Do not expose compose expanded env, URLs or raw tool errors.
        return ops.run(self.command + args)

    def stop(self):
        self.call(['stop','app'])
        ids = self.call(['ps','-a','-q','app']).splitlines()
        ops.require(len(ids) == 1)
        ops.require(ops.run(ops.DOCKER + ['inspect','--format={{.State.Running}}',ids[0]]) == 'false')

    def build(self):
        self.call(['--profile','tools','build'])

    def migrate(self):
        self.call(['run','--rm','migrate'])

    def schema(self):
        meta = ops.metadata(self.source)
        ops.require(len(meta['migrations']) == len(list((self.repo / 'prisma/migrations').glob('*/migration.sql'))))

    def start(self):
        self.call(['up','-d','--wait','app'])
        self.call(['exec','-T','app','node','docker/health.mjs'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',required=True)
    parser.add_argument('--repo',required=True)
    parser.add_argument('--env-file',required=True)
    parser.add_argument('--project',required=True)
    parser.add_argument('--target-revision',required=True)
    parser.add_argument('--expected-current-image',required=True)
    parser.add_argument('--identity',required=True)
    parser.add_argument('--restore-target')
    parser.add_argument('--skip-restore-drill',action='store_true')
    parser.add_argument('--reviewed-upgrade',action='store_true')
    parser.add_argument('--other-writers-quiesced',action='store_true')
    a = parser.parse_args()
    ops.require(a.reviewed_upgrade and a.other_writers_quiesced)
    ops.require(bool(a.restore_target) != a.skip_restore_drill)
    ops.require(re.fullmatch('[a-f0-9]{40}',a.target_revision) and re.fullmatch('sha256:[a-f0-9]{64}',a.expected_current_image))
    ops.require(re.fullmatch('[a-z][a-z0-9-]{0,40}',a.project))
    repo = Path(a.repo)
    ops.require(repo.is_absolute() and repo.resolve() == ops.ROOT)
    ops.private(a.env_file)
    ops.private(a.identity)
    ops.require(ops.run(['git','-C',str(repo),'rev-parse','HEAD']) == a.target_revision)
    ops.require(not ops.run(['git','-C',str(repo),'status','--porcelain']))
    c = ops.config(a.config)
    ops.bound(c['source'])
    ops.metadata(c['source'])  # unchanged migration prefix is required before stopping app
    driver = Compose(repo,Path(a.env_file),a.project,c['source'])
    ids = driver.call(['ps','-a','-q','db']).splitlines()
    ops.require(ids == [c['source']['container_id']])
    apps = driver.call(['ps','-a','-q','app']).splitlines()
    ops.require(len(apps) == 1)
    ops.require(ops.run(ops.DOCKER + ['inspect','--format={{.Image}}',apps[0]]) == a.expected_current_image)
    with ops.locked(c['backup_directory']) as root:
        record = {'target_revision':a.target_revision,'previous_image':a.expected_current_image,'source':c['source'],'restore_drill_requested':bool(a.restore_target)}
        try:
            result = sequence(driver,lambda:ops.backup(c),lambda name:ops.verify(root,name,a.identity),lambda name:ops.restore(root,name,a.identity,ops.read_json(a.restore_target)) if a.restore_target else None)
            record.update(result)
        except ops.Refused as error:
            record.update({'state':str(error)})
            raise
        finally:
            ops.write_json(root / ('upgrade-'+uuid.uuid4().hex+'.json'),record)
    print(json.dumps({'state':result['state'],'backup':result['backup']}))


if __name__ == '__main__':
    signal.signal(signal.SIGTERM,ops.interrupted)
    try:
        main()
    except KeyboardInterrupt:
        print('Upgrade interrupted before orchestration; inspect writer state',file=sys.stderr)
        sys.exit(130)
    except Exception as error:
        # Only our fixed state labels are safe for an operator log.
        text = str(error) if isinstance(error,ops.Refused) else 'Upgrade refused; inspect private configuration'
        print(text,file=sys.stderr)
        sys.exit(1)
