"""Bounded offline full-native experiment. Missing input => no native build.

Uses only an already-prepared local toolchain config digest; never pulls or
publishes an image. Acquisition is a separate online review step.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
import tomllib
import tarfile

from s05e_native_recipe import render, LOCK_SHA
from s05e_source_protocol import file_sha
from verify_s05d_evidence import safe_members

ROOT=Path(__file__).resolve().parents[1]
NATIVE_MANIFEST_SHA='64920706748151a2d562a9de657424095d78c7bd8a0785571c77d4e673dbcabe'
BASE='sha256:ae0813ccb1bb83f4e0220acdd1539f52831517de334368e960824db7e37ee210'
RUST={'rustc':'a658e87aa721f0044e36adcf5b5fba0645bedd14bc5045ea11bf475d803da64a',
      'cargo':'931952aaee9b6afb144a3e2bf74467e1cd407b7d0baa7c0cd3bf9e98abf94b2a',
      'rust-std':'536dcdcf52d81508587f4411156f20c94800e26fc13b6ef9603bfdc4af9c4407'}


def run_log(args,path,timeout=120):
    with path.open('wb') as f:
        return subprocess.run(args,stdout=f,stderr=subprocess.STDOUT,timeout=timeout,check=False).returncode


def preflight(inputs,image):
    checks=[]
    def check(label,fn):
        try:
            detail=fn();checks.append({'name':label,'decision':'PASS','detail':detail})
        except (OSError,ValueError,KeyError,subprocess.SubprocessError) as e:
            checks.append({'name':label,'decision':'BLOCKED','failureType':type(e).__name__,'reason':str(e)[:150]})
    b=ROOT/'docs/evidence/s05b'
    if file_sha(b/'libvips-source-manifest.json')!=NATIVE_MANIFEST_SHA:
        raise ValueError('HISTORICAL_NATIVE_MANIFEST_CHANGED')
    manifest=json.loads((b/'libvips-source-manifest.json').read_text())
    def hashed(path,expected):
        if file_sha(path)!=expected:raise ValueError('HASH_MISMATCH '+path.name)
        return expected
    check('controlled-lock',lambda:hashed(inputs/'generated-Cargo.lock',LOCK_SHA))
    for s in manifest['dependencies']:
        def native(s=s):
            p=inputs/'sources'/(s['name']+'.tar');hashed(p,s['sha256']);safe_members(p,allow_internal_links=True)
            return {'sha256':s['sha256'],'version':s['version']}
        check('native-source:'+s['name'],native)
    for i,s in enumerate(manifest['patches']):
        check('patch:'+str(i),lambda i=i,s=s:hashed(inputs/'patches'/(str(i)+'.patch'),s['sha256']))
    for name,h in RUST.items():
        check('rust-component:'+name,lambda name=name,h=h:hashed(inputs/'rust'/(name+'.tar.xz'),h))
    def expanded(archive,destination,drop,allowed=None):
        count=0
        with tarfile.open(archive) as t:
            for e in t:
                parts=Path(e.name).parts[drop:]
                if not e.isfile() or not parts or allowed and parts[0] not in allowed:continue
                p=destination.joinpath(*parts)
                raw=t.extractfile(e).read()
                if p.is_symlink() or file_sha(p)!=hashlib.sha256(raw).hexdigest():
                    raise ValueError('EXPANDED_SOURCE_HASH '+str(p.name))
                count+=1
        if not count:raise ValueError('EMPTY_EXPANSION')
        return count
    for name in RUST:
        check('installed-rust-bytes:'+name,lambda name=name:expanded(inputs/'rust'/(name+'.tar.xz'),inputs/'rust/toolchain',2,{'bin','lib','libexec','share','etc'}))
    def cargo_source():
        p=inputs/'rust/cargo-c-0.10.25+cargo-0.99.0.crate'
        hashed(p,'6b2ddde58a8a773ccce4b6384acacd3ce01373f52717dd2424633ed46755c627')
        return expanded(p,inputs/'rust/cargo-c-source',1)
    check('cargo-c-expanded-source',cargo_source)
    def crates(lock):
        count=0
        for r in tomllib.loads(lock.read_text())['package']:
            if not r.get('source'):continue
            if not r['source'].startswith('registry+'):
                raise ValueError('UNVERIFIED_NONREGISTRY_SOURCE')
            p=inputs/'cargo-cache/registry/cache/index.crates.io-1949cf8c6b5b557f'/(r['name']+'-'+r['version']+'.crate')
            hashed(p,r['checksum']);safe_members(p,allow_internal_links=True);count+=1
            expanded(p,inputs/'cargo-cache/registry/src/index.crates.io-1949cf8c6b5b557f'/(r['name']+'-'+r['version']),1)
        return count
    check('librsvg-registry-inputs',lambda:crates(inputs/'generated-Cargo.lock'))
    check('cargo-c-registry-inputs',lambda:crates(inputs/'rust/cargo-c-source/Cargo.lock'))
    def rpms():
        r=json.loads((ROOT/'docs/evidence/s05e/historical-rpm-files.json').read_text())
        if len(r['records'])!=241:raise ValueError('INCOMPLETE_HISTORICAL_TRANSACTION')
        for f in r['records']:hashed(inputs/f['file'],f['sha256'])
        # The offline Dockerfile additionally verifies publisher RPM signatures
        # and exact NEVRA before installation; text inventory alone cannot pass.
        return len(r['records'])
    check('historical-rpm-bytes',rpms)
    def toolchain():
        if not image.startswith('sha256:') or len(image)!=71:raise ValueError('IMMUTABLE_CONFIG_REQUIRED')
        spec=json.loads((ROOT/'docs/evidence/s05e/toolchain.json').read_text())
        if spec['preparedConfigDigest']!=image or spec['baseManifestDigest']!=BASE:
            raise ValueError('FOREIGN_TOOLCHAIN_IMAGE')
        # Exact local config ID, no registry access. Re-exec measured tools in it.
        got=json.loads(subprocess.check_output(['docker','image','inspect',image],timeout=30))[0]
        if got['Id']!=image:raise ValueError('CONFIG_ID')
        base=json.loads(subprocess.check_output(['docker','image','inspect','rockylinux/rockylinux@'+BASE],timeout=30))[0]
        layers=base['RootFS']['Layers']
        if got['RootFS']['Layers'][:len(layers)]!=layers:raise ValueError('FOREIGN_BASE_LAYERS')
        return image
    check('immutable-toolchain',toolchain)
    def bootstrap():
        spec=json.loads((ROOT/'docs/evidence/s05e/toolchain.json').read_text())
        if spec['cargoCBootstrap']['exitCode']!=0:raise ValueError('CARGO_C_BOOTSTRAP_FAILED_OR_UNFINISHED')
        for f in spec['cargoCBootstrap']['executables']:
            hashed(inputs/f['file'],f['sha256'])
        return spec['cargoCBootstrap']['version']
    check('cargo-c-bootstrap',bootstrap)
    return {'schemaVersion':1,'checks':checks,'decision':'PASS' if all(c['decision']=='PASS' for c in checks) else 'BLOCKED',
            'binaryDistributionReadiness':'BLOCKED','legalApproval':False}


def prepare(inputs,out):
    config=out/'config';config.mkdir()
    platform=ROOT/'docs/evidence/s05b/upstream/platforms/linux-x64'
    for n in ['Toolchain.cmake','meson.ini','x86_64-linux-gnu-pkgconf']:shutil.copy(platform/n,config/n)
    (config/'x86_64-linux-gnu-pkgconf').chmod(0o755)
    # Writable experiment-only install directories; no changes to application
    # Dockerfile/Compose. Preserve original file and explicit derived config.
    p=config/'meson.ini';p.write_text(p.read_text().replace("'/usr/share'","'/target/share'").replace("'/usr/share/locale'","'/target/share/locale'").replace("'/etc'","'/target/etc'").replace("'/var'","'/target/var'"))
    for n in ['s05e_extract.py']:shutil.copy(ROOT/'scripts'/n,config/n)
    recipe=render()
    (config/'control.sh').write_text(recipe)
    head=recipe.split('# Download and build dependencies from source')[0]
    head=head.replace('mkdir ${DEPS}','').replace('mkdir ${TARGET}','')
    body=recipe[recipe.index('mkdir ${DEPS}/vips'):]
    insertion='''python3.12 - <<'PYCODE'
from pathlib import Path
import hashlib,json,difflib
p=Path('/deps/vips/libvips/iofuncs/init.c')
old=p.read_bytes()
new=old+b'\\n/* S05-E: private retained marker, no public API or image algorithm change. */\\nstatic const char s05e_native_rebuild_marker[] __attribute__((used, retain)) = "S05E_MODIFIED_SOURCE_EVIDENCE";\\n'
p.write_bytes(new)
Path('/evidence/source-change.diff').write_text(''.join(difflib.unified_diff(old.decode().splitlines(True),new.decode().splitlines(True),fromfile='control/init.c',tofile='modified/init.c')))
Path('/evidence/source-change.json').write_text(json.dumps({'file':'libvips/iofuncs/init.c','beforeSha256':hashlib.sha256(old).hexdigest(),'afterSha256':hashlib.sha256(new).hexdigest()}))
PYCODE
'''
    body=body.replace('# Use version number in SONAME',insertion+'\n# Use version number in SONAME')
    (config/'modified.sh').write_text(head+body)
    for n in ['control.sh','modified.sh']:
        p=config/n
        p.write_text(p.read_text().replace('-Wl,-Bsymbolic-functions','-Wl,-Map=/evidence/'+n+'.link-map,-cref -Wl,-Bsymbolic-functions'))
    (config/'versions.properties').write_bytes((ROOT/'docs/evidence/s05b/upstream/versions.properties').read_bytes())
    # Actual compiler commands are captured by verbose Make/Ninja output.
    # Cargo JSON output is retained by librsvg's upstream cargo wrapper.
    return config


def execute(inputs,out,image,minutes,resume=None,resume_webp=False):
    report=preflight(inputs,image)
    (out/'preflight.json').write_text(json.dumps(report,indent=2)+'\n')
    result={'schemaVersion':1,'status':'BLOCKED','executed':False,'controlSha256':None,'modifiedSha256':None,
            'abiComparison':None,'sharpTests':'NOT_RUN','stage':'prerequisites','binaryDistributionReadiness':'BLOCKED',
            'recipeCommit':'ebb95f8add54eee8bed840e3fb587e4cbec857d7','sourceLockSha256':LOCK_SHA,
            'target':'x86_64-unknown-linux-gnu','profile':'CONTROLLED_FULL_NATIVE_WITH_S05D_LOCK'}
    if report['decision']!='PASS':
        (out/'full-rebuild.json').write_text(json.dumps(result,indent=2)+'\n');return 1
    config=prepare(inputs,out)
    for n in ['deps','target','control','modified','home']:
        if resume and n in {'deps','target'}:
            shutil.copytree(resume/n,out/n,symlinks=True)
        else:(out/n).mkdir()
    name='s05e-full-native-resume-webp' if resume_webp else 's05e-full-native-resume' if resume else 's05e-full-native'
    if resume:
        previous=(resume/'control.log').read_text()
        expected="aclocal-1.17" if resume_webp else "unable to copy file 'libjpeg.a'"
        if expected not in previous or not (resume/'deps/jpeg/CMakeFiles/jpeg-static.dir/link.txt').is_file():
            raise ValueError('UNREVIEWED_RESUME_CHECKPOINT')
        migration=json.loads((inputs/'inventory/scratch-migration.json').read_text())
        if migration.get('allHashesMatched') is not True:raise ValueError('UNVERIFIED_SCRATCH_MIGRATION')
        original=(config/'control.sh').read_text()
        header=original.split('# Download and build dependencies from source')[0]
        header=header.replace('mkdir ${DEPS}','mkdir -p ${DEPS}').replace('mkdir ${TARGET}','mkdir -p ${TARGET}')
        if resume_webp:
            # Restore metadata only for byte-identical original source files;
            # do not retimestamp generated/modified configure outputs.
            restored=0
            with tarfile.open(inputs/'sources/webp.tar') as t:
                for e in t:
                    parts=Path(e.name).parts[1:]
                    if not e.isfile() or not parts:continue
                    p=out/'deps/webp'/Path(*parts)
                    if p.is_file() and not p.is_symlink() and file_sha(p)==hashlib.sha256(t.extractfile(e).read()).hexdigest():
                        os.utime(p,(e.mtime,e.mtime),follow_symlinks=False);restored+=1
            remaining=original[original.index('mkdir ${DEPS}/tiff'):]
            checkpoint='\ncd /deps/webp\nmake install-strip bin_PROGRAMS= noinst_PROGRAMS= man_MANS=\n'
            result['restoredSourceMtimes']=restored
        else:
            remaining=original[original.index('mkdir ${DEPS}/png'):]
            checkpoint='\ncd /deps/jpeg\nif [ -f libjpeg.a ]; then mv libjpeg.a /evidence/failed-enospc-libjpeg.a; fi\nmake install/strip\n'
        (config/'control.sh').write_text(header+checkpoint+remaining)
        shutil.copy(resume/'control.log',out/'previous-control-failure.log')
        result['resume']={'checkpoint':'libwebp after source mtime preservation fix' if resume_webp else 'mozjpeg static archive after tmpfs ENOSPC','priorExitCode':2,'priorLog':'previous-control-failure.log','reuse':'unchanged native dependency/object inputs; same /deps and /target container paths'}
    command=['docker','run','--detach','--name',name,'--network=none','--read-only','--cap-drop=ALL',
             '--security-opt=no-new-privileges','--user',str(os.getuid())+':'+str(os.getgid()),'--memory=6g','--cpus=2','--pids-limit=512',
             '--tmpfs','/tmp:rw,nosuid,nodev,size=1g',
             '-v',str(inputs)+':/inputs:ro','-v',str(config)+':/config:ro','-v',str(config)+':/packaging:ro',
             '-v',str(out/'deps')+':/deps:rw','-v',str(out/'target')+':/target:rw','-v',str(out)+':/evidence:rw',
             '-v',str(inputs/'cargo-cache')+':/cargo:rw',
             '-e','PATH=/inputs/cargo-c-historical-install/bin:/inputs/rust/toolchain/bin:/opt/rh/gcc-toolset-15/root/usr/bin:/opt/s05e/bin:/usr/local/bin:/usr/bin:/bin:/config',
             '-e','CARGO_HOME=/cargo','-e','CARGO_NET_OFFLINE=true','-e','CARGO_BUILD_JOBS=2','-e','HOME=/evidence/home',
             '-e','PLATFORM=linux-x64','-e','FLAGS=-march=nehalem','-e','RUSTFLAGS=-Zlocation-detail=none -Zfmt-debug=none',
             '-e','PKG_CONFIG=x86_64-linux-gnu-pkgconf --static','-e','MESON=--cross-file=/config/meson.ini',image,
             'timeout','--signal=TERM','--kill-after=10s',str(minutes*60),
             'bash','-xc',
             'bash -x /config/control.sh > /evidence/control.log 2>&1 && '
             'cp -a /deps/vips /evidence/control/vips && '
             'cp -L /target/lib/libvips-cpp.so.8.18.7 /evidence/control/libvips-cpp.so.8.18.7 && '
             'rm -rf /deps/vips && '
             'bash -x /config/modified.sh > /evidence/modified.log 2>&1 && '
             'cp -a /deps/vips /evidence/modified/vips && '
             'cp -L /target/lib/libvips-cpp.so.8.18.7 /evidence/modified/libvips-cpp.so.8.18.7']
    # Make only the two mount-root mkdir operations idempotent.
    for n in ['control.sh','modified.sh']:
        p=config/n;p.write_text(p.read_text().replace('mkdir ${DEPS}\n','mkdir -p ${DEPS}\n').replace('mkdir ${TARGET}\n','mkdir -p ${TARGET}\n'))
    (out/'invocation.json').write_text(json.dumps({'command':command,'timeoutSeconds':minutes*60,'profile':'CONTROLLED_FULL_NATIVE_WITH_S05D_LOCK','legalApproval':False},indent=2)+'\n')
    result.update(executed=True,stage='control-and-modified',startedAt=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()))
    (out/'full-rebuild.json').write_text(json.dumps(result,indent=2)+'\n')
    try:
        code=run_log(command,out/'executor.log',120)
        if code==0:
            wait=subprocess.run(['docker','wait',name],stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=minutes*60+30,check=False)
            code=int(wait.stdout.strip()) if wait.returncode==0 else wait.returncode
    except subprocess.TimeoutExpired:
        subprocess.run(['docker','stop','-t','10',name],stdout=subprocess.DEVNULL,check=False,timeout=30);code=124
    result['exitCode']=code
    result['binaryFiles']={phase:phase+'/libvips-cpp.so.8.18.7' for phase in ['control','modified']}
    for phase in ['control','modified']:
        p=out/phase/'libvips-cpp.so.8.18.7'
        if p.is_file():result[phase+'Sha256']=file_sha(p)
    if code==0 and result['controlSha256'] and result['modifiedSha256'] and result['controlSha256']!=result['modifiedSha256']:
        result.update(status='PARTIAL',stage='awaiting-abi-sharp-and-static-input-validation')
    (out/'full-rebuild.json').write_text(json.dumps(result,indent=2)+'\n')
    return code


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--inputs',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--image',required=True);p.add_argument('--minutes',type=int,default=75)
    p.add_argument('--resume-mozjpeg',type=Path)
    p.add_argument('--resume-webp',type=Path)
    a=p.parse_args()
    if not 1<=a.minutes<=90:raise SystemExit('Bounded experiment requires 1..90 minutes')
    a.out.mkdir(parents=True,exist_ok=False)
    if a.resume_mozjpeg and a.resume_webp:raise SystemExit('Choose one reviewed checkpoint')
    raise SystemExit(execute(a.inputs.resolve(),a.out.resolve(),a.image,a.minutes,a.resume_webp or a.resume_mozjpeg,bool(a.resume_webp)))
