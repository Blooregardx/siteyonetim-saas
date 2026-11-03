#!/usr/bin/env python3
"""Verify an actual GitHub source tarball against a selected clean Git tree."""
import argparse
import hashlib
import json
from pathlib import Path,PurePosixPath
import re
import subprocess
import tarfile

ROOT=Path(__file__).resolve().parents[1]
REQUIRED={'LICENSE','COPYRIGHT','README.md','Dockerfile','compose.selfhost.yaml','.env.selfhost.example','.env.example','package.json','package-lock.json','prisma/schema.prisma','docker/init.sh','docker/grants.sql','scripts/selfhost-preflight.sh','scripts/backup_ops.py','scripts/safe_upgrade.py','docs/THIRD-PARTY-LICENSES.md','docs/LICENSING.md','.dockerignore','.gitignore','docs/BACKUP-OPERATIONS.md','docs/SAFE-UPGRADE.md','scripts/selfhost_preflight.py','docs/COMMUNITY-INSTALLATION.md','docs/TROUBLESHOOTING.md','docs/S04D-DISTRIBUTION-VALIDATION.md'}
PRIVATE=re.compile(rb'AGE-SECRET-KEY-[A-Z0-9]{40,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')
LICENSE_SHA='0d96a4ff68ad6d4b6f1f30f713b18d5184912ba8dd389f86aa7710db079abcb0'


def require(ok):
    if not ok:raise ValueError('Source archive policy or Git content mismatch')


def tree(root,revision):
    require(re.fullmatch('[a-f0-9]{40}',revision))
    raw=subprocess.check_output(['git','ls-tree','-rz','--full-tree',revision],cwd=root)
    result={}
    for item in raw.split(b'\0'):
        if not item:continue
        header,name=item.split(b'\t',1);mode,kind,digest=header.decode().split()
        require(kind=='blob' and mode in ['100644','100755'])
        result[name.decode()]=(mode,digest)
    return result


def allowed(name):
    p=PurePosixPath(name)
    if p.is_absolute() or '..' in p.parts:return False
    if any(part in {'.git','node_modules','.next','coverage','test-results','playwright-report','backups','secrets','uploads','dumps','__pycache__'} for part in p.parts):return False
    if p.name.startswith('.env') and name not in {'.env.example','.env.selfhost.example'}:return False
    if name.endswith(('.age','.agekey','.key','.dump','.backup','.sql.gz','.pyc','.tsbuildinfo')):return False
    return True


def verify(root,revision,archive):
    expected=tree(root,revision)
    require(REQUIRED<=set(expected))
    require(len([n for n in expected if re.fullmatch(r'prisma/migrations/\d[^/]+/migration.sql',n)])==11)
    seen=set();top=None;total=0
    with tarfile.open(archive,'r:gz') as source:
        for member in source:
            parts=PurePosixPath(member.name).parts
            require(parts and not PurePosixPath(member.name).is_absolute() and '..' not in parts)
            top=top or parts[0];require(parts[0]==top)
            if len(parts)==1:require(member.isdir());continue
            name='/'.join(parts[1:]);require(allowed(name))
            if member.isdir():continue
            require(member.isfile() and name not in seen and name in expected and 0<=member.size<=8*1024*1024)
            total+=member.size;require(total<=128*1024*1024)
            stream=source.extractfile(member)
            digest=hashlib.sha1(f'blob {member.size}\0'.encode());sha=hashlib.sha256();carry=b''
            while chunk:=stream.read(65536):
                require(not PRIVATE.search(carry+chunk));carry=chunk[-256:]
                digest.update(chunk);sha.update(chunk)
            stream.close()
            require(digest.hexdigest()==expected[name][1])
            require(bool(member.mode&0o111)==(expected[name][0]=='100755'))
            if name=='LICENSE':require(sha.hexdigest()==LICENSE_SHA)
            seen.add(name)
    require(seen==set(expected))
    sha=hashlib.sha256()
    with Path(archive).open('rb') as stream:
        while chunk:=stream.read(65536):sha.update(chunk)
    return {'source_archive_verified':True,'commit':revision,'files':len(seen),'archive_sha256':sha.hexdigest(),'scope':'tracked source only; not binary license clearance'}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=ROOT)
    parser.add_argument('--revision',required=True)
    parser.add_argument('--archive',type=Path,required=True)
    args=parser.parse_args()
    try:print(json.dumps(verify(args.root,args.revision,args.archive)))
    except Exception:
        print('Source archive verification failed; no archive contents logged')
        raise SystemExit(1)
