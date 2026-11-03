"""Verify downloaded npm tarball SRI, registry signature and provenance claims.
Does not assert full Sigstore certificate/Rekor trust or reproducible builds.
"""
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import tarfile
import tempfile

ROOT=Path(__file__).resolve().parents[1]/'docs/evidence/s05b'
COMMIT='ebb95f8add54eee8bed840e3fb587e4cbec857d7'
KEY='SHA256:DhQ8wR5APBvFHLF/+Tc+AYvPOdTpcIDqOhxsBHRwC7U'


def check(meta, attestations, keys, archive):
    data=archive.read_bytes();algo,value=meta['dist']['integrity'].split('-',1)
    if algo!='sha512' or hashlib.sha512(data).digest()!=base64.b64decode(value):raise ValueError('NPM_SRI')
    if meta['gitHead']!=COMMIT:raise ValueError('NPM_GIT_HEAD')
    with tempfile.TemporaryDirectory(prefix='s05b-signature-') as tmp:
        root=Path(tmp);key=next(k for k in keys['keys'] if k['keyid']==KEY)
        (root/'key.der').write_bytes(base64.b64decode(key['key']))
        subprocess.run(['openssl','pkey','-pubin','-inform','DER','-in',str(root/'key.der'),'-out',str(root/'key.pem')],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        (root/'message').write_text(meta['name']+'@'+meta['version']+':'+meta['dist']['integrity'])
        valid=False
        for sig in meta['dist']['signatures']:
            if sig['keyid']!=KEY:continue
            (root/'signature').write_bytes(base64.b64decode(sig['sig']))
            r=subprocess.run(['openssl','dgst','-sha256','-verify',str(root/'key.pem'),'-signature',str(root/'signature'),str(root/'message')],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            valid=valid or r.returncode==0
        if not valid:raise ValueError('NPM_REGISTRY_SIGNATURE')
    claims=[]
    for a in attestations['attestations']:
        if a['predicateType']!='https://slsa.dev/provenance/v1':continue
        statement=json.loads(base64.b64decode(a['bundle']['dsseEnvelope']['payload']))
        if statement['subject'][0]['digest']['sha512']!=hashlib.sha512(data).hexdigest():raise ValueError('ATTESTATION_SUBJECT')
        definition=statement['predicate']['buildDefinition']
        if definition['resolvedDependencies'][0]['digest']['gitCommit']!=COMMIT:raise ValueError('ATTESTATION_COMMIT')
        claims.append(statement)
    if not claims:raise ValueError('PROVENANCE_MISSING')
    binaries=[]
    with tarfile.open(archive) as t:
        for member in t:
            if member.isfile() and member.name.endswith('.so.8.18.7'):
                binary=t.extractfile(member).read();binaries.append({'path':member.name,'sha256':hashlib.sha256(binary).hexdigest(),'elfMachine':int.from_bytes(binary[18:20],'little')})
    return {'name':meta['name'],'version':meta['version'],'gitHead':COMMIT,'tarball':meta['dist']['tarball'],'sha256':hashlib.sha256(data).hexdigest(),'integrity':meta['dist']['integrity'],'registrySignatureVerified':True,'registryKeyId':KEY,'provenanceClaims':claims,'sigstoreTrustVerified':False,'binaries':binaries,'decision':'PARTIAL'}


if __name__=='__main__':
    records=[]
    for platform in ['glibc','musl']:
        meta=json.load(open('/tmp/s05b-npm-'+platform+'.json'));att=json.load(open('/tmp/s05b-att-'+platform+'.json'));keys=json.load(open('/tmp/s05b-npm-keys.json'))
        archive=Path('/tmp/s05b-upstream')/(platform+'.tgz')
        subprocess.run(['curl','--proto','=https','-fLsS','--max-time','90',meta['dist']['tarball'],'-o',str(archive)],check=True)
        result=check(meta,att,keys,archive);records.append(result)
        path=ROOT/'npm'/platform;path.mkdir(parents=True,exist_ok=True)
        (path/'metadata.json').write_text(json.dumps(meta,indent=2)+'\n')
        # Omit access-signature URLs; preserve public signed bundles.
        (path/'attestations.json').write_text(json.dumps({'attestations':[{'predicateType':a['predicateType'],'bundle':a['bundle']} for a in att['attestations']]},indent=2)+'\n')
    (ROOT/'npm/keys.json').write_text(json.dumps(keys,indent=2)+'\n')
    (ROOT/'npm-verification.json').write_text(json.dumps(records,indent=2)+'\n')
    print(json.dumps([{'name':r['name'],'binaries':r['binaries'],'signature':r['registrySignatureVerified']} for r in records]))
