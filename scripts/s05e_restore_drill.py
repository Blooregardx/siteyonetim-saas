"""Small synthetic source-package copies on separate CI runner filesystems.

Shared GitHub artifact storage is a correlated failure domain, not two durable
providers. These tests do not publish any actual corresponding-source bundle.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import tarfile

from s05e_source_protocol import fixture, file_sha, restore


def identity():
    boot=Path('/proc/sys/kernel/random/boot_id').read_bytes()
    return hashlib.sha256(boot).hexdigest()


def seed(out):
    out.mkdir(parents=True,exist_ok=False)
    root=out/'synthetic-source';index=fixture(root)
    archive=out/'synthetic-source.tar'
    with tarfile.open(archive,'w') as t:
        for p in sorted(root.rglob('*')):
            if p.is_file():
                e=t.gettarinfo(p,arcname=str(p.relative_to(root)))
                e.uid=e.gid=e.mtime=0;e.uname=e.gname=''
                with p.open('rb') as f:t.addfile(e,f)
    result={'bundleSha256':file_sha(archive),'indexSha256':index,'purpose':'SYNTHETIC_PROTOCOL_TEST'}
    shutil.rmtree(root)
    (out/'expected.json').write_text(json.dumps(result,indent=2)+'\n')
    if os.environ.get('GITHUB_OUTPUT'):
        with open(os.environ['GITHUB_OUTPUT'],'a') as f:
            f.write('bundle='+result['bundleSha256']+'\nindex='+index+'\n')
    return result


def copy_or_restore(stage,source,out,bundle,index,label):
    if label not in {'a','b'}:raise ValueError('COPY_LABEL')
    out.mkdir(parents=True,exist_ok=False)
    archive=source/'synthetic-source.tar'
    if stage=='copy':
        result=restore(archive,bundle,index,out/'verification')
        shutil.rmtree(out/'verification')
        shutil.copyfile(archive,out/archive.name)
        origin=identity()
    else:
        receipt=json.loads((source/'copy-receipt.json').read_text())
        if receipt['copyLabel']!=label or receipt['bundleSha256']!=bundle or receipt['indexSha256']!=index:
            raise ValueError('FOREIGN_COPY_RECEIPT')
        origin=receipt['copyRunnerFingerprint']
        if origin==identity():raise ValueError('RESTORE_MUST_USE_A_DIFFERENT_RUNNER')
        result=restore(archive,bundle,index,out/'restored')
        # Negative: an unavailable or corrupt own copy must not silently fall
        # back to the other copy, seed, cache or network.
        damaged=out/'corrupted.tar';damaged.write_bytes(archive.read_bytes()+b'CORRUPTION')
        try:restore(damaged,bundle,index,out/'unexpected-success')
        except ValueError:result['corruptionRejected']=True
        else:raise ValueError('CORRUPTION_ACCEPTED')
        damaged.unlink()
        try:restore(out/'missing.tar',bundle,index,out/'unexpected-missing-success')
        except ValueError:result['missingCopyRejected']=True
        else:raise ValueError('MISSING_COPY_ACCEPTED')
        shutil.rmtree(out/'restored')
    result.update(stage=stage,copyLabel=label,bundleSha256=bundle,indexSha256=index,
                  copyRunnerFingerprint=origin,runnerFingerprint=identity(),failureDomain='shared GitHub artifact backend; NOT durable independence')
    (out/(stage+'-receipt.json')).write_text(json.dumps(result,indent=2)+'\n')
    return result


def summary(root):
    rows=[json.loads(p.read_text()) for p in sorted(root.rglob('restore-receipt.json'))]
    if len(rows)!=2 or {r['copyLabel'] for r in rows}!={'a','b'}:raise ValueError('TWO_RESTORES_REQUIRED')
    if len({r['copyRunnerFingerprint'] for r in rows})!=2 or len({r['runnerFingerprint'] for r in rows})!=2:
        raise ValueError('INDEPENDENT_RUNNER_FILESYSTEMS_REQUIRED')
    if len({r['bundleSha256'] for r in rows})!=1 or len({r['indexSha256'] for r in rows})!=1:
        raise ValueError('COPY_BINDING_MISMATCH')
    if not all(r['protocolIntegrity']=='PASS' and r['corruptionRejected'] and r['missingCopyRejected'] and r['legalApproval'] is False and r['binaryDistributionReadiness']=='BLOCKED' for r in rows):
        raise ValueError('RESTORE_FAILURE_OR_CLEARANCE_CLAIM')
    result={'schemaVersion':1,'independentRunnerCopies':2,'successfulRestores':2,
            'scope':'SYNTHETIC_PROTOCOL_TEST only; one shared storage provider',
            'protocolIntegrity':'PASS','durableSourceProvision':'PARTIAL','legalApproval':False,
            'binaryDistributionReadiness':'BLOCKED','restores':rows}
    (root/'restore-summary.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('stage',choices=['seed','copy','restore','summary'])
    p.add_argument('--source',type=Path);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--bundle');p.add_argument('--index');p.add_argument('--label')
    a=p.parse_args()
    result=seed(a.out) if a.stage=='seed' else summary(a.out) if a.stage=='summary' else copy_or_restore(a.stage,a.source,a.out,a.bundle,a.index,a.label)
    print(json.dumps(result))
