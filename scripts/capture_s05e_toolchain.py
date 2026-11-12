"""Measure a local pinned sysroot and separately record bootstrap outcome."""
import argparse
import json
import os
from pathlib import Path
import subprocess

from s05e_source_protocol import file_sha
from docker_identity import identity

BASE='sha256:ae0813ccb1bb83f4e0220acdd1539f52831517de334368e960824db7e37ee210'
MEASURE=r'''
import hashlib,json,pathlib,shutil,subprocess
paths=['gcc','g++','cc','c++','ld','as','ar','ranlib','strip','cmake','make','nasm','pkgconf','python3.12','meson','ninja']
records=[]
for n in paths:
 p=pathlib.Path(shutil.which(n)).resolve()
 args=[str(p),'-v'] if n=='gcc' else [str(p),'--version']
 r=subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,check=False)
 records.append({'name':n,'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'command':args,'exitCode':r.returncode,'versionOutput':r.stdout.decode(errors='replace')})
for n in ['cc1','cc1plus','collect2']:
 p=pathlib.Path(subprocess.check_output(['gcc','-print-prog-name='+n],text=True).strip()).resolve()
 records.append({'name':n,'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
print(json.dumps(records))
'''


def capture(inputs,out,image):
    out.mkdir(parents=True,exist_ok=True)
    info=json.loads(subprocess.check_output(['docker','image','inspect',image],timeout=30))[0]
    image=info['Id']
    if not image.startswith('sha256:'):raise ValueError('IMMUTABLE_IMAGE')
    base=json.loads(subprocess.check_output(['docker','image','inspect','rockylinux/rockylinux@'+BASE],timeout=30))[0]
    base_identity=identity('rockylinux/rockylinux@'+BASE)
    image_identity=identity(image)
    if base_identity['configDigest']!='sha256:98ab72cce29f004554c86e88d6789b7f8d09fe90aee099ec56e9b71a2a7e406c':
        raise ValueError('ORIGINAL_BASE_CONFIG')
    if info['RootFS']['Layers'][:len(base['RootFS']['Layers'])]!=base['RootFS']['Layers']:
        raise ValueError('FOREIGN_BASE_IMAGE')
    cmd=['docker','run','--rm','--network=none','--read-only','--cap-drop=ALL','--security-opt=no-new-privileges',image,'python3.12','-c',MEASURE]
    tools=json.loads(subprocess.check_output(cmd,timeout=120))
    (out/'measured-tools.json').write_text(json.dumps(tools,indent=2)+'\n')
    installed=subprocess.check_output(['docker','run','--rm','--network=none','--cap-drop=ALL',image,'cat','/installed-rpms.tsv'],timeout=120)
    (out/'installed-rpms.tsv').write_bytes(installed)
    state=json.loads(subprocess.check_output(['docker','inspect','s05e-cargo-c-historical'],timeout=30))[0]['State']
    bootstrap={'exitCode':state['ExitCode'] if not state['Running'] else None,'oomKilled':state['OOMKilled'],'executables':[], 'version':None}
    if bootstrap['exitCode']==0:
        for p in sorted((inputs/'cargo-c-historical-install/bin').iterdir()):
            if p.is_file():bootstrap['executables'].append({'file':str(p.relative_to(inputs)),'sha256':file_sha(p)})
        args=['docker','run','--rm','--network=none','--read-only','--cap-drop=ALL','--security-opt=no-new-privileges',
              '--user',str(os.getuid())+':'+str(os.getgid()),
              '-v',str(inputs)+':/inputs:ro',image,'/inputs/cargo-c-historical-install/bin/cargo-cbuild','--version']
        r=subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=30,check=False)
        (out/'cargo-c-version.txt').write_bytes(r.stdout)
        bootstrap.update(version=r.stdout.decode().strip(),versionExitCode=r.returncode)
        if r.returncode or '0.10.25+cargo-0.99.0' not in bootstrap['version']:
            raise ValueError('CARGO_C_VERSION')
    result={'schemaVersion':1,'baseManifestDigest':BASE,'preparedConfigDigest':image_identity['configDigest'],
            'preparedEngineImageID':image,'baseIdentity':base_identity,'preparedIdentity':image_identity,
            'decision':'PARTIAL','historicalByteReproducibility':'NOT_PROVEN',
            'historicalUpstreamPostUpdateCargoLock':'UNKNOWN; S05-D controlled lock used for new experiment',
            'originalTransactionEvidence':'historical-transaction.json','rpmFiles':'historical-rpm-files.json',
            'measuredToolsFile':'measured-tools.json','measuredToolsSha256':file_sha(out/'measured-tools.json'),
            'installedRpmsFile':'installed-rpms.tsv','installedRpmsSha256':file_sha(out/'installed-rpms.tsv'),
            'cargoCBootstrap':bootstrap,'legalApproval':False,'binaryDistributionReadiness':'BLOCKED'}
    (out/'toolchain.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--inputs',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--image',required=True)
    a=p.parse_args();print(json.dumps(capture(a.inputs.resolve(),a.out,a.image)['cargoCBootstrap']))
