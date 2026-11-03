#!/usr/bin/env python3
"""Own synthetic selfhost project only; no application behavior changes."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import uuid

D=['env','-u','DOCKER_HOST','-u','DOCKER_CONTEXT','-u','DOCKER_TLS','-u','DOCKER_TLS_VERIFY','-u','DOCKER_CERT_PATH','docker','--host=unix:///var/run/docker.sock']
C=D+['compose','-p','s04a-ci','-f','compose.selfhost.yaml']
if os.environ.get('POSTGRES_DB')!='siteyonetim_test':raise ValueError('Synthetic database required')


def run(args,data=None):
    return subprocess.run(args,input=data,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)


if sys.argv[1]=='build':
    with tempfile.TemporaryDirectory(prefix='siteyonetim-s04d-build-negative-') as temp:
        dockerfile=Path(temp)/'Dockerfile'
        dockerfile.write_text('THIS_IS_NOT_A_DOCKERFILE\n')
        assert run(D+['build','-f',str(dockerfile),temp]).returncode!=0
    print('Synthetic invalid Dockerfile rejected without fallback image')
elif sys.argv[1]=='history':
    fixture=str(uuid.uuid4())
    sql=f'''INSERT INTO "_prisma_migrations"(id,checksum,migration_name,started_at,applied_steps_count) VALUES ('{fixture}','{'0'*64}','209901010001_s04d_incomplete',NOW(),0);'''
    assert run(C+['exec','-T','db','psql','-U','postgres','-d','siteyonetim_test','-v','ON_ERROR_STOP=1','-q'],sql.encode()).returncode==0
    try:
        result=run(['timeout','30']+C+['run','--rm','--no-deps','app'])
        assert result.returncode==1
    finally:
        # Only this test's inserted row; the eleven historical entries remain intact.
        cleanup=f'''DELETE FROM "_prisma_migrations" WHERE id='{fixture}';'''
        assert run(C+['exec','-T','db','psql','-U','postgres','-d','siteyonetim_test','-v','ON_ERROR_STOP=1','-q'],cleanup.encode()).returncode==0
    print('Synthetic incomplete migration state rejected; historical entries preserved')
else:raise ValueError('Unknown synthetic negative test')
