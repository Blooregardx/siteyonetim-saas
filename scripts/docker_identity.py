"""Bind Docker engine references to actual exported image configuration bytes.

Docker's containerd store can report a manifest-list digest in inspect.Id;
that value must never be silently relabelled as a configuration digest.
Reads a local docker-save stream without extracting or retaining image layers.
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import tarfile


def saved_config(stream):
    candidates={};manifest=None;seen=set();total=0
    with tarfile.open(fileobj=stream,mode='r|') as t:
        for i,e in enumerate(t):
            p=PurePosixPath(e.name)
            if p.is_absolute() or '..' in p.parts or '\\' in e.name or e.name in seen:
                raise ValueError('UNSAFE_DOCKER_SAVE_MEMBER')
            seen.add(e.name);total+=e.size
            if i>=100000 or total>12*1024**3 or e.size<0:raise ValueError('DOCKER_SAVE_LIMIT')
            if e.isdir():continue
            if not e.isfile():raise ValueError('DOCKER_SAVE_SPECIAL_OR_LINK')
            if e.name=='manifest.json':
                if e.size>4*1024**2:raise ValueError('MANIFEST_SIZE')
                manifest=json.loads(t.extractfile(e).read())
            elif e.size<=4*1024**2 and re.fullmatch(r'[a-f0-9]{64}(?:\.json)?',p.name):
                raw=t.extractfile(e).read()
                try:data=json.loads(raw)
                except (ValueError,UnicodeDecodeError):continue
                if isinstance(data,dict) and 'rootfs' in data and 'architecture' in data:
                    encoded=p.name.removesuffix('.json')
                    if hashlib.sha256(raw).hexdigest()!=encoded:raise ValueError('CONFIG_FILENAME_HASH')
                    candidates[e.name]=(encoded,data)
    if not isinstance(manifest,list):raise ValueError('DOCKER_SAVE_MANIFEST_REQUIRED')
    chosen=[]
    for entry in manifest:
        key=entry['Config']
        if key not in candidates:raise ValueError('CONFIG_BLOB_MISSING')
        digest,data=candidates[key]
        if data.get('architecture')=='amd64' and data.get('os')=='linux':chosen.append((digest,data))
    if len(chosen)!=1:raise ValueError('AMBIGUOUS_OR_WRONG_PLATFORM')
    return chosen[0]


def identity(reference):
    if reference.startswith('-'):raise ValueError('IMAGE_REFERENCE')
    info=json.loads(subprocess.check_output(['docker','image','inspect',reference],timeout=30))[0]
    engine=info['Id']
    if not re.fullmatch('sha256:[a-f0-9]{64}',engine):raise ValueError('ENGINE_IMAGE_ID')
    child=subprocess.Popen(['docker','image','save','--platform=linux/amd64',engine],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    try:
        digest,config=saved_config(child.stdout)
        while child.stdout.read(1024*1024):pass
        child.stdout.close();stderr=child.stderr.read();code=child.wait(timeout=120)
        if code:raise ValueError('LOCAL_IMAGE_EXPORT_FAILED')
    except BaseException:
        child.kill();child.wait();raise
    expected=config['rootfs']['diff_ids']
    if expected!=info['RootFS']['Layers'] or config['architecture']!=info['Architecture'] or config['os']!=info['Os']:
        raise ValueError('EXPORTED_CONFIG_ROOTFS_OR_PLATFORM_MISMATCH')
    return {'engineImageID':engine,'configDigest':'sha256:'+digest,'architecture':'amd64','os':'linux',
            'rootfsDiffIDs':expected,'engineDescriptor':info.get('Descriptor'),
            'scope':'Local engine reference bound to hashed docker-save config bytes; no registry push'}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--image',required=True);p.add_argument('--expected-config');p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();r=identity(a.image)
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps(r))
    if a.expected_config and r['configDigest']!=a.expected_config:raise SystemExit('BLOCKED: canonical configuration digest mismatch')
