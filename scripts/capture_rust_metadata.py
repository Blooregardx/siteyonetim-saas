"""Controlled resolution only; Cargo metadata/tree are not compilation evidence."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
from run_libvips_rebuild import extract
from prepare_libvips_rebuild import fetch

ROOT=Path(__file__).resolve().parents[1]


if __name__=='__main__':
    base=Path(os.environ['RUNNER_TEMP'])/'s05c-rust-metadata';base.mkdir(parents=True,exist_ok=True)
    spec=json.load(open(ROOT/'docs/evidence/s05c/toolchain-spec.json'));old=json.load(open(ROOT/'docs/evidence/s05b/libvips-source-manifest.json'));record=next(r for r in old['dependencies'] if r['name']=='rsvg')
    archive=base/'librsvg.tar';fetch(record['url'],archive,record['sha256'])
    source=base/'source';source.mkdir();extract(archive,source)
    lock=source/'Cargo.lock';before=hashlib.sha256(lock.read_bytes()).hexdigest()
    for name in ['rsvg/Cargo.toml','librsvg-c/Cargo.toml']:
        path=source/name;lines=path.read_text().splitlines(True)
        path.write_text(''.join(l.replace(', "gif", "webp"','') if 'image = ' in l else l.replace(', "pdf", "ps"','') if 'cairo-rs = ' in l else l for l in lines))
    image=spec['rustMetadataImage192'];container='s05c-cargo-'+os.environ['GITHUB_RUN_ID']
    common=['docker','run','--rm','--name',container,'--read-only','--cpus=2','--memory=3g','--user',str(os.getuid())+':'+str(os.getgid()),'--tmpfs','/tmp:size=160m,mode=1777','--cap-drop=ALL','--security-opt=no-new-privileges:true','--mount','type=bind,src='+str(base)+',dst=/work','-e','HOME=/work/home','-e','CARGO_HOME=/work/cargo','-w','/work/source',image]
    result={'image':image,'target':'x86_64-unknown-linux-gnu','inputLockSha256':before,'sourceArchiveSha256':record['sha256'],'scope':'controlled patched source manifests, original exact lock; not upstream generated post-update lock','compilation':'NOT_RUN'}
    for label,args in [('rustc',['rustc','-vV']),('metadata',['cargo','metadata','--locked','--format-version','1','--filter-platform','x86_64-unknown-linux-gnu']),('tree',['cargo','tree','--locked','--offline','--target','x86_64-unknown-linux-gnu','-p','librsvg-c','--edges','normal,build','--format','{p}|{f}'])]:
        try:
            with (base/(label+'.stdout')).open('w') as out,(base/(label+'.stderr')).open('w') as err:
                r=subprocess.run(common+args,stdout=out,stderr=err,timeout=240)
            result[label+'ExitCode']=r.returncode
        except subprocess.TimeoutExpired:
            subprocess.run(['docker','rm','--force',container],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            result[label+'ExitCode']='TIMEOUT'
        if result[label+'ExitCode']!=0:break
    result['outputLockSha256']=hashlib.sha256(lock.read_bytes()).hexdigest()
    result['decision']='RESOLVED — NOT PROVEN COMPILED' if result.get('metadataExitCode')==0 and before==result['outputLockSha256'] else 'BLOCKED'
    (base/'resolution-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
