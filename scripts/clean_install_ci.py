#!/usr/bin/env python3
"""Fresh public GitHub clone/archive + single Docker build in an ephemeral CI host."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

REPOSITORY='https://github.com/Blooregardx/siteyonetim-saas.git'
D=['env','-u','DOCKER_HOST','-u','DOCKER_CONTEXT','-u','DOCKER_TLS','-u','DOCKER_TLS_VERIFY','-u','DOCKER_CERT_PATH','docker','--host=unix:///var/run/docker.sock']


def execute(args,cwd=None,capture=False):
    r=subprocess.run(args,cwd=cwd,stdout=subprocess.PIPE if capture else None,stderr=subprocess.DEVNULL if capture else None,check=True)
    return r.stdout.decode().strip() if capture else None


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--revision',required=True);a=parser.parse_args()
    if os.environ.get('GITHUB_ACTIONS')!='true' or os.environ.get('POSTGRES_DB')!='siteyonetim_test' or not re.fullmatch('[a-f0-9]{40}',a.revision):raise ValueError('Ephemeral synthetic CI only')
    # Never adopt/stop/delete pre-existing app resources or reuse a prepared app image.
    for kind in ['container','volume']:
        if execute(D+[kind,'ls',('-aq' if kind=='container' else '-q'),'--filter','label=com.docker.compose.project=s04a-ci'],capture=True):raise ValueError('Existing project resources refused')
    for tag in ['s04a-ci-app','s04a-ci-migrate']:
        if subprocess.run(D+['image','inspect',tag],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0:raise ValueError('Existing app image refused')
    with tempfile.TemporaryDirectory(prefix='siteyonetim-s04d-clean-') as scratch:
        root=Path(scratch)/'source'
        execute(['git','init','-q',str(root)])
        execute(['git','-C',str(root),'fetch','--depth=1',REPOSITORY,a.revision])
        execute(['git','-C',str(root),'checkout','--detach','-q','FETCH_HEAD'])
        if execute(['git','-C',str(root),'rev-parse','HEAD'],capture=True)!=a.revision:raise ValueError('Checkout SHA mismatch')
        if any((root/p).exists() for p in ['node_modules','.next','.env','secrets']):raise ValueError('Prepared data refused')
        archive=Path(scratch)/'github-source.tar.gz'
        execute(['curl','--fail','--location','--silent','--show-error','--max-time','120','--output',str(archive),f'https://codeload.github.com/Blooregardx/siteyonetim-saas/tar.gz/{a.revision}'])
        execute(['python3','scripts/verify_distribution.py','--revision',a.revision,'--archive',str(archive)],root)
        print(json.dumps({'clean_checkout':a.revision,'environment':'fresh temporary Git clone on GitHub Linux runner; host Docker/Git/curl/Python/age reused; no prior app images or dependencies','human_independent_install':False}),flush=True)
        compose=D+['compose','-p','s04a-ci','-f',str(root/'compose.selfhost.yaml')]
        try:
            execute(['sh','scripts/test-selfhost.sh'],root)
            for image in ['app', 'migrate']:
                execute(['sh', 'scripts/collect_distribution.sh', 's04a-ci-'+image, str(Path(os.environ['RUNNER_TEMP'])/'s05a-evidence'/image)], root)
            execute(['python3','scripts/test_backup_ops.py'],root)
            execute(['python3','scripts/test_recovery.py'],root)
        finally:
            # Only this newly-created, synthetic CI project. Never a general cleanup tool.
            subprocess.run(compose+['down'],cwd=root,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            volume='s04a-ci_selfhost_data'
            label=subprocess.run(D+['volume','inspect','--format={{index .Labels "com.docker.compose.project"}}',volume],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
            if label.returncode==0 and label.stdout.strip()==b's04a-ci':
                subprocess.run(D+['volume','rm',volume],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True)


if __name__=='__main__':main()
