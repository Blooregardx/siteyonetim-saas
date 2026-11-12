"""Isolated DEVELOPMENT acquisition; no upstream installer, native build or publication."""
import argparse
import base64
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import tarfile
import tomllib
import urllib.error
import urllib.parse
import urllib.request
from verify_s05d_evidence import LOCK_SHA, RECIPE, TARGET, RUST_MANIFEST_SHA, digest, safe_members, lock_changes, mpl_header

ROOT=Path(__file__).resolve().parents[1]
BASE='node:24-bookworm-slim@sha256:c86ecead9e55a5210ac1727de38a4ca840bf03dcaf34dc9749addbf383b1920c'
HOSTS={'static.rust-lang.org','static.crates.io','api.github.com','download.gnome.org'}
OLD=ROOT/'docs/evidence/s05b/upstream/librsvg-Cargo.lock'
PARENT=ROOT/'docs/evidence/s05b/libvips-source-manifest.json'
RECIPE_FILE=ROOT/'docs/evidence/s05b/upstream/build/posix.sh'


def fetch(url, path, expected=None, maximum=100*1024**2):
    parsed=urllib.parse.urlparse(url)
    if parsed.scheme!='https' or parsed.hostname not in HOSTS or path.is_symlink():
        raise ValueError('UNTRUSTED_DOWNLOAD')
    if expected and path.is_file() and digest(path.read_bytes())==expected:
        return path.read_bytes()
    req=urllib.request.Request(url,headers={'User-Agent':'SiteYonetim-S05D-source-audit'})
    with urllib.request.urlopen(req,timeout=45) as response:
        final=urllib.parse.urlparse(response.url)
        if final.scheme!='https' or final.hostname not in HOSTS:
            raise ValueError('REDIRECT_HOST')
        data=response.read(maximum+1)
    if len(data)>maximum or expected and digest(data)!=expected:
        raise ValueError('DOWNLOAD_SIZE_OR_HASH')
    path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
    return data


def write(path, value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2)+'\n')


def extract_regular(path, destination, drop):
    safe_members(path, max_file=768*1024**2, max_total=2*1024**3,allow_internal_links=True) if drop==2 else safe_members(path,allow_internal_links=True)
    with tarfile.open(path) as t:
        for e in t:
            if not e.isfile():continue
            parts=PurePosixPath(e.name).parts[drop:]
            if not parts:continue
            p=destination.joinpath(*parts);p.parent.mkdir(parents=True,exist_ok=True)
            p.write_bytes(t.extractfile(e).read());p.chmod(e.mode & 0o755)


def command(root, label, args, timeout=180):
    out=root/(label+'.stdout');err=root/(label+'.stderr')
    with out.open('w') as stdout,err.open('w') as stderr:
        try:r=subprocess.run(args,stdout=stdout,stderr=stderr,timeout=timeout)
        except subprocess.TimeoutExpired:
            return {'command':args,'exitCode':'TIMEOUT','stdout':out.name,'stderr':err.name}
    return {'command':args,'exitCode':r.returncode,'stdout':out.name,'stderr':err.name}


def capture_cargo(root):
    r={'schemaVersion':1,'recipeCommit':RECIPE,'target':TARGET,'inputLockSha256':LOCK_SHA,
       'status':'BLOCKED','historicalUpstreamLock':False,'generatedLockFile':None,
       'generatedLockSha256':None,'attempts':[],'toolchain':{'verified':False,'probes':[]},
       'stage':'toolchain-availability','binaryDistributionReadiness':'BLOCKED'}
    scope={'schemaVersion':1,'target':TARGET,'origin':'S05-D controlled attempt; S05-C compilation history retained separately',
           'records':[{'name':p['name'],'version':p['version'],'source':p.get('source','path'),
                       'checksum':p.get('checksum'),'packageId':None,'features':None,'dependencyRole':'UNKNOWN',
                       'status':'UNKNOWN','reason':'No S05-D compiler/linker capture'} for p in tomllib.loads(OLD.read_text())['package']]}
    try:
        if digest(OLD.read_bytes())!=LOCK_SHA:raise ValueError('ORIGINAL_LOCK')
        parent=json.loads(PARENT.read_text())
        if parent['package']['commit']!=RECIPE or digest(RECIPE_FILE.read_bytes())!=parent['buildFiles']['upstream/build/posix.sh']:
            raise ValueError('RECIPE_HASH')
        # Probe only the publication dates corresponding to the observed exact compiler.
        selected=None
        for date in ['2026-09-27','2026-09-26']:
            url='https://static.rust-lang.org/dist/'+date+'/channel-rust-nightly.toml'
            try:
                checksum=fetch(url+'.sha256',root/('rust-'+date+'.sha256'),maximum=4096).decode().split()[0]
                if not re.fullmatch('[a-f0-9]{64}',checksum):raise ValueError('MANIFEST_CHECKSUM_FORMAT')
                if date!='2026-09-27' or checksum!=RUST_MANIFEST_SHA:raise ValueError('UNREVIEWED_DIST_MANIFEST')
                data=fetch(url,root/('rust-'+date+'.toml'),checksum,5*1024**2)
                manifest=tomllib.loads(data.decode())
                version=manifest['pkg']['rustc']['version']
                if '1.101.0-nightly' not in version or '75a75c3e0' not in version:
                    r['toolchain']['probes'].append({'url':url,'result':'EXACT_VERSION_MISMATCH','observed':version})
                    continue
                selected=manifest;r['toolchain']['distributionDate']=date;r['toolchain']['manifestSha256']=checksum
                break
            except (urllib.error.URLError,ValueError,KeyError,UnicodeError) as e:
                r['toolchain']['probes'].append({'url':url,'result':type(e).__name__,'httpStatus':getattr(e,'code',None)})
        if selected is None:raise ValueError('EXACT_TOOLCHAIN_UNAVAILABLE')
        r['stage']='toolchain-download';r['toolchain']['components']=[]
        tools=root/'toolchain';tools.mkdir()
        for component in ['rustc','cargo','rust-std']:
            m=selected['pkg'][component]['target'][TARGET]
            url=m['xz_url'];expected=m['xz_hash'];p=root/(component+'.tar.xz')
            fetch(url,p,expected,180*1024**2)
            extract_regular(p,tools,2)
            r['toolchain']['components'].append({'name':component,'url':url,'sha256':expected,'file':p.name})
        container='s05d-cargo-'+os.environ['GITHUB_RUN_ID']
        common=['docker','run','--rm','--name',container,'--read-only','--cpus=2','--memory=3g',
                '--user',str(os.getuid())+':'+str(os.getgid()),'--cap-drop=ALL','--security-opt=no-new-privileges:true',
                '--tmpfs','/tmp:size=160m,mode=1777','--mount','type=bind,src='+str(root)+',dst=/work',
                '--mount','type=bind,src=/etc/ssl/certs/ca-certificates.crt,dst=/ca.pem,readonly',
                '-e','SSL_CERT_FILE=/ca.pem','-e','CARGO_HTTP_CAINFO=/ca.pem','-e','HOME=/work/home',
                '-e','CARGO_HOME=/work/cargo','-e','PATH=/work/toolchain/bin:/usr/local/bin:/usr/bin:/bin']
        for label in ['rustc','cargo']:
            a=command(root,label,common+[BASE,'/work/toolchain/bin/'+label,'-vV'])
            if a['exitCode']!=0:raise ValueError('TOOLCHAIN_EXECUTION')
            p=root/a['stdout'];r['toolchain'][label+'Log']=p.name;r['toolchain'][label+'LogSha256']=digest(p.read_bytes())
        rustc=(root/r['toolchain']['rustcLog']).read_text()
        if '1.101.0-nightly' not in rustc or '75a75c3e0' not in rustc or TARGET not in rustc:
            raise ValueError('TOOLCHAIN_IDENTITY')
        r['toolchain']['verified']=True
        r['toolchain']['binaryHashes']={str(p.relative_to(root)):digest(p.read_bytes()) for p in (tools/'bin').glob('*') if p.is_file()}
        source=next(d for d in parent['dependencies'] if d['name']=='rsvg')
        archive=root/'librsvg.tar';fetch(source['url'],archive,source['sha256'])
        r['sourceArchive']={'url':source['url'],'sha256':source['sha256']}
        for index in [1,2]:
            work=root/('resolution-'+str(index));work.mkdir();extract_regular(archive,work,1)
            if digest((work/'Cargo.lock').read_bytes())!=LOCK_SHA:raise ValueError('SOURCE_LOCK')
            changes=[]
            for name in ['rsvg/Cargo.toml','librsvg-c/Cargo.toml']:
                p=work/name;before=p.read_text();after=''.join(
                    line.replace(', "gif", "webp"','') if name=='rsvg/Cargo.toml' and 'image = ' in line
                    else line.replace(', "pdf", "ps"','') if 'cairo-rs = ' in line else line
                    for line in before.splitlines(True))
                p.write_text(after);changes.append({'file':name,'beforeSha256':digest(before.encode()),'afterSha256':digest(after.encode())})
            p=work/'meson.build';before=p.read_text();p.write_text(''.join(line.replace(", 'linux'",'') if line.startswith("if host_system in ['windows'") else line for line in before.splitlines(True)))
            c=common+['-w','/work/'+work.name,BASE,'/work/toolchain/bin/cargo','update','--workspace']
            r['stage']='cargo-update-'+str(index);a=command(root,'update-'+str(index),c,240)
            a.update(command=['cargo','update','--workspace'],beforeSha256=LOCK_SHA,
                     afterSha256=digest((work/'Cargo.lock').read_bytes()),lockFile=work.name+'/Cargo.lock',
                     changes=lock_changes(OLD.read_text(),(work/'Cargo.lock').read_text()),featureChanges=changes)
            r['attempts'].append(a)
            if a['exitCode']!=0:raise ValueError('CARGO_UPDATE_FAILED')
        if r['attempts'][0]['afterSha256']!=r['attempts'][1]['afterSha256']:raise ValueError('RESOLVER_NONDETERMINISM')
        shutil.copyfile(root/r['attempts'][0]['lockFile'],root/'generated-Cargo.lock')
        r.update(status='PARTIAL',generatedLockFile='generated-Cargo.lock',
                 generatedLockSha256=digest((root/'generated-Cargo.lock').read_bytes()),stage='metadata')
        work=root/'resolution-1'
        a=command(root,'metadata',common+['-w','/work/resolution-1',BASE,'/work/toolchain/bin/cargo','metadata','--locked','--format-version','1','--filter-platform',TARGET],240)
        r['metadata']=a
        if a['exitCode']==0:
            raw=(root/a['stdout']).read_bytes();metadata=json.loads(raw)
            nodes={n['id']:n for n in metadata['resolve']['nodes']}
            scope['metadataSha256']=digest(raw);scope['metadataFile']=a['stdout'];scope['featureMode']='workspace-default';scope['records']=[]
            lock_entries={(p['name'],p['version'],p.get('source','path')):p for p in tomllib.loads((root/'generated-Cargo.lock').read_text())['package']}
            incoming={}
            for node in metadata['resolve']['nodes']:
                for dep in node.get('deps',[]):
                    incoming.setdefault(dep['pkg'],[]).extend({'fromPackageId':node['id'],'kind':k.get('kind') or 'normal','target':k.get('target')} for k in dep.get('dep_kinds',[]))
            for package in metadata['packages']:
                node=nodes.get(package['id'])
                scope['records'].append({'name':package['name'],'version':package['version'],'source':package.get('source') or 'path',
                                        'packageId':package['id'],'features':node['features'] if node else None,
                                        'outgoingDependencyKinds':sorted({d.get('kind') or 'normal' for d in package['dependencies']}),
                                        'incomingDependencyRoles':incoming.get(package['id'],[]),
                                        'checksum':lock_entries.get((package['name'],package['version'],package.get('source') or 'path'),{}).get('checksum'),
                                        'status':'RESOLVED' if node else 'UNKNOWN',
                                        'reason':'Metadata resolution only, no compiler-artifact or linker proof'})
            r['tree']=command(root,'tree',common+['-w','/work/resolution-1',BASE,'/work/toolchain/bin/cargo','tree','--locked','--target',TARGET,'-p','librsvg-c','--edges','normal,build','--format','{p}|{f}'],180)
            covered={(p['name'],p['version'],p['source']) for p in scope['records']}
            for key,entry in lock_entries.items():
                if key not in covered:
                    scope['records'].append({'name':key[0],'version':key[1],'source':key[2],'checksum':entry.get('checksum'),
                        'packageId':None,'features':None,'incomingDependencyRoles':[],'status':'UNKNOWN',
                        'reason':'Not represented in filtered metadata; absence alone is not NOT SELECTED evidence'})
            scope['generatedLockSha256']=r['generatedLockSha256']
            # A bounded diagnostic Rust build is distinct from the unavailable full cbuild/native sysroot.
            build_common=common[:]
            for key,value in {'CARGO_BUILD_JOBS':'2','CARGO_PROFILE_RELEASE_DEBUG':'false',
                              'CARGO_PROFILE_RELEASE_CODEGEN_UNITS':'1','CARGO_PROFILE_RELEASE_INCREMENTAL':'false',
                              'CARGO_PROFILE_RELEASE_LTO':'true','CARGO_PROFILE_RELEASE_OPT_LEVEL':'z',
                              'CARGO_PROFILE_RELEASE_PANIC':'abort','RUSTFLAGS':'-Zlocation-detail=none -Zfmt-debug=none --remap-path-prefix=/work/cargo/registry/='}.items():
                build_common+=['-e',key+'='+value]
            build=command(root,'compiler',build_common+['--network=none','-w','/work/resolution-1',BASE,
                 '/work/toolchain/bin/cargo','build','--locked','--offline','--release','-p','librsvg-c','--message-format=json-render-diagnostics','-vv'],240)
            r['diagnosticRustBuild']=build
            scope['compilerCapture']={**build,'file':build['stdout'],'sha256':digest((root/build['stdout']).read_bytes()),
                                      'network':'none','profile':'release librsvg-c default; no native sysroot/cargo-c'}
            by_id={p['packageId']:p for p in scope['records'] if p['packageId']}
            retained=0
            for line in (root/build['stdout']).read_text().splitlines():
                try:message=json.loads(line)
                except json.JSONDecodeError:continue
                if message.get('reason')!='compiler-artifact' or message.get('fresh') is not False:continue
                package=by_id.get(message.get('package_id'))
                if package is None:continue
                evidence=[]
                for filename in message.get('filenames',[]):
                    path=PurePosixPath(filename)
                    if not str(path).startswith('/work/') or '..' in path.parts:continue
                    local=root.joinpath(*path.parts[2:])
                    if not local.is_file() or local.is_symlink() or not local.resolve().is_relative_to(root.resolve()):continue
                    if retained+local.stat().st_size>32*1024**2:continue
                    data=local.read_bytes()
                    if not (data.startswith(b'!<arch>\n') or data.startswith(b'\x7fELF')):continue
                    name='compiled-'+digest(data)+'.bin';(root/name).write_bytes(data);retained+=len(data)
                    evidence.append({'file':name,'sha256':digest(data),'originalFilename':filename})
                if evidence:
                    package['status']='COMPILED'
                    package['compilerEvidence']={'message':message,'files':evidence}
                    package['reason']='One compiler-artifact target physically retained; target kind may be build-script, not final library; not LINKED evidence'

        r['stage']='controlled-resolution-completed'
        r['limitations']=['Not the recovered historical upstream lock/index state','No full native sysroot, cargo-c, compiler-artifact or linker-map capture','librsvg code patch occurs after upstream update and is not applied in metadata-only phase']
    except (OSError,ValueError,KeyError,urllib.error.URLError,tarfile.TarError,subprocess.SubprocessError) as e:
        r['failure']={'type':type(e).__name__,'code':str(e) if isinstance(e,ValueError) else 'ACQUISITION_OR_EXECUTION_FAILED'}
        if not (root/'generated-Cargo.lock').is_file():
            r.update(status='BLOCKED',generatedLockSha256=None,generatedLockFile=None)
    finally:
        subprocess.run(['docker','rm','--force','s05d-cargo-'+os.environ['GITHUB_RUN_ID']],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    scope['counts']={s:sum(p['status']==s for p in scope['records']) for s in ['RESOLVED','COMPILED','LINKED — EVIDENCED','NOT SELECTED — EVIDENCED','UNKNOWN']}
    write(root/'cargo-resolution.json',r);write(root/'rust-compile-link-scope.json',scope)
    return r


def license_record(root, old):
    r={'name':old['name'],'version':old['version'],'decision':'BLOCKED','evidence':[],
       'cargoChecksum':old['lockChecksum'],'licenseDeclaration':old.get('license'),
       'licenseFileDeclaration':old.get('licenseFile'),'scope':'source/notice acquisition; legal approval and binary obligations remain open'}
    key=r['name']+'-'+r['version'];archive=root/(key+'.crate')
    try:
        fetch('https://static.crates.io/crates/'+r['name']+'/'+key+'.crate',archive,r['cargoChecksum'],25*1024**2)
        safe_members(archive);r.update(archiveFile=archive.name,archiveSha256=digest(archive.read_bytes()))
        with tarfile.open(archive) as t:
            regular={e.name:t.extractfile(e).read() for e in t if e.isfile() and e.size<=2*1024**2}
        cargo=tomllib.loads(regular[key+'/Cargo.toml'].decode());p=cargo['package']
        r['licenseDeclaration']=p.get('license');r['licenseFileDeclaration']=p.get('license-file')
        vcs=json.loads(regular.get(key+'/.cargo_vcs_info.json',b'{}'))
        commit=vcs.get('git',{}).get('sha1');r['repositoryCommit']=commit;r['pathInVcs']=vcs.get('path_in_vcs','')
        repository=p.get('repository','');r['repository']=repository
        # MPL Exhibit-A style text can be an applicable original source notice.
        for name,data in regular.items():
            if name.endswith('.rs') and p.get('license')=='MPL-2.0':
                header=data[:3000]
                if mpl_header(header):
                    name_out=key+'-header-'+digest(header)[:16]+'.txt';(root/name_out).write_bytes(header)
                    r['evidence'].append({'kind':'source-header','file':name_out,'sha256':digest(header),'archiveMember':name,
                                          'completeSourceSha256':digest(data)})
        match=re.match(r'https?://github.com/([^/]+)/([^/#]+)',repository)
        if match and not commit:
            repo=match.group(1)+'/'+match.group(2).removesuffix('.git')
            r['tagProbes']=[]
            for tag in ['v'+r['version'],r['version']]:
                tagurl='https://api.github.com/repos/'+repo+'/git/ref/tags/'+urllib.parse.quote(tag,safe='')
                try:
                    ref=json.loads(fetch(tagurl,root/(key+'-tag.json'),maximum=1024*1024))
                    obj=ref['object']
                    if obj['type']=='tag':
                        annotated=json.loads(fetch(obj['url'],root/(key+'-annotated-tag.json'),maximum=1024*1024))
                        obj=annotated['object']
                    if obj['type']=='commit' and re.fullmatch('[a-f0-9]{40}',obj['sha']):
                        commit=obj['sha'];r['repositoryCommit']=commit;r['revisionBasis']='exact version tag candidate; only accepted with source-byte matches'
                        break
                except (urllib.error.URLError,ValueError,KeyError) as e:
                    r['tagProbes'].append({'url':tagurl,'failure':type(e).__name__,'httpStatus':getattr(e,'code',None)})
        if match and re.fullmatch('[a-f0-9]{40}',commit or ''):
            repo=match.group(1)+'/'+match.group(2).removesuffix('.git')
            url='https://api.github.com/repos/'+repo+'/git/trees/'+commit+'?recursive=1'
            data=fetch(url,root/(key+'-tree.json'),maximum=10*1024**2)
            tree=json.loads(data)
            if tree.get('truncated'):raise ValueError('TRUNCATED_UPSTREAM_TREE')
            entries={e['path']:e for e in tree['tree'] if e['type']=='blob'}
            prefix=vcs.get('path_in_vcs','').strip('/')
            # Old Cargo versions omitted path_in_vcs. Infer only a unique prefix shared by all exact Rust file blobs.
            if not prefix:
                candidates=None
                for archive_name,raw in regular.items():
                    relative=archive_name[len(key)+1:]
                    if not relative.endswith('.rs'):continue
                    blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
                    found={name[:-len(relative)].rstrip('/') for name,e in entries.items()
                           if name.endswith(relative) and (name==relative or name.endswith('/'+relative)) and e['sha']==blob}
                    candidates=found if candidates is None else candidates & found
                if candidates and len(candidates)==1:
                    prefix=next(iter(candidates));r['inferredPathInVcs']=prefix
            matched=[];mismatched=[]
            for name,data in regular.items():
                relative=name[len(key)+1:]
                if relative.endswith('.rs'):
                    upstream=(prefix+'/' if prefix else '')+relative
                    blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
                    if entries.get(upstream,{}).get('sha')==blob:matched.append(relative)
                    else:mismatched.append(relative)
            r['matchedSourceFiles']=matched;r['unmatchedSourceFiles']=mismatched
            ancestors={''}
            parts=PurePosixPath(prefix).parts
            ancestors.update('/'.join(parts[:n]) for n in range(1,len(parts)+1))
            notices=[(name,e) for name,e in entries.items()
                     if ('' if str(PurePosixPath(name).parent)=='.' else str(PurePosixPath(name).parent)) in ancestors
                     and re.match(r'(?i)^(licen[sc]e|copying|notice|copyright)([._-]|$)',PurePosixPath(name).name)]
            for i,(name,e) in enumerate(notices[:12]):
                bloburl='https://api.github.com/repos/'+repo+'/git/blobs/'+e['sha']
                response=json.loads(fetch(bloburl,root/(key+'-blob-'+str(i)+'.json'),maximum=4*1024**2))
                if response.get('encoding')!='base64':raise ValueError('UPSTREAM_BLOB_ENCODING')
                raw=base64.b64decode(response['content'],validate=False)
                actual=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
                if actual!=e['sha']:raise ValueError('UPSTREAM_GIT_BLOB')
                evidence=key+'-upstream-'+str(i)+'.txt';(root/evidence).write_bytes(raw)
                if matched and not mismatched and len(raw)>100 and any(s in raw for s in [b'Permission is hereby granted',b'Apache License',b'Mozilla Public License']):
                    r['evidence'].append({'kind':'upstream-notice','file':evidence,'sha256':digest(raw),
                                          'upstreamPath':name,'url':bloburl,'gitBlobSha':e['sha']})
        if r['evidence']:
            from verify_s05d_evidence import verify_notice
            r['decision']='PASS';verify_notice(r,root)
            r['reason']='Original source header or exact-commit upstream notice physically acquired; no binary/legal clearance'
        else:
            r['reason']='No sufficient original notice acquired; repository revision/applicability may remain unknown'
    except (OSError,ValueError,KeyError,urllib.error.URLError,tarfile.TarError) as e:
        r['decision']='BLOCKED';r['failureType']=type(e).__name__;r['httpStatus']=getattr(e,'code',None)
    return r


def full_preflight(root, cargo):
    parent=json.loads(PARENT.read_text())
    r={'schemaVersion':1,'status':'BLOCKED','executed':False,'recipeCommit':RECIPE,
       'intendedProfile':'original sharp-libvips 1.3.4 Linux x64 static native/Rust bundle',
       'profile':None,'controlSha256':None,'modifiedSha256':None,'abiComparison':None,'sharpTests':'NOT_RUN',
       'stage':'prerequisite-review','blockers':[
           'Original Rocky 8 base was a floating tag; exact compiler image digest not recovered',
           'gcc-toolset-15 RPM versions/hashes, cargo-c version, Meson/Ninja versions not pinned by original recipe',
           'Full native/Rust sysroot and compiler/linker capture not acquired; unsafe curl-to-tar/rustup recipe not executed',
           'No full CONTROL/MODIFIED build or original matching object/archive acquisition'],
       'sources':[{'name':d['name'],'version':d['version'],'url':d['url'],'sha256':d.get('sha256'),
                   's05dArchiveReverified':False} for d in parent['dependencies']],
       'patches':parent['patches'],'recipeSha256':parent['buildFiles']['upstream/build/posix.sh'],
       'cargoStatus':cargo['status'],'reducedProfileSubstitution':False,
       'resourcePolicy':{'cpus':2,'memoryGiB':3,'jobTimeoutMinutes':25},
       'commandsReference':'docs/evidence/s05b/upstream/build/posix.sh (reviewed, NOT executed)',
       'binaryDistributionReadiness':'BLOCKED'}
    write(root/'full-bundle-rebuild.json',r)
    write(root/'static-relinking-inputs.json',{'schemaVersion':1,'status':'BLOCKED','archives':[],'objects':[],
           'originalBundleComplete':False,'sources':r['sources'],'required':['per-library source+patch','static archive members','object hashes','compiler/linker command files','link maps','installation/relink instructions'],
           'reason':'No S05-D full bundle executed; S05-C reduced-profile archives are not substituted'})
    return r


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out',type=Path,required=True);a=parser.parse_args()
    if os.environ.get('GITHUB_ACTIONS')!='true':raise SystemExit('DEDICATED_CI_ONLY')
    a.out.mkdir(parents=True,exist_ok=True)
    if a.out.is_symlink():raise SystemExit('UNSAFE_OUTPUT_DIRECTORY')
    cargo=capture_cargo(a.out)
    old=json.loads((ROOT/'docs/evidence/s05c/rust-source-manifest.json').read_text())
    records=[]
    for r in old['records']:
        if r['decision']=='BLOCKED':records.append(license_record(a.out,r))
    write(a.out/'rust-license-resolution.json',{'schemaVersion':1,'records':records,
         'counts':{s:sum(r['decision']==s for r in records) for s in ['PASS','BLOCKED','UNKNOWN','NOT_APPLICABLE']},
         'legalApproval':False,'binaryDistributionReadiness':'BLOCKED'})
    full=full_preflight(a.out,cargo)
    from verify_s05d_evidence import verify_resolution, verify_scope, verify_full_bundle
    scope=json.loads((a.out/'rust-compile-link-scope.json').read_text())
    write(a.out/'technical-validation.json',{'resolution':verify_resolution(cargo,a.out),
          'scope':verify_scope(scope,a.out),'full':verify_full_bundle(full)})

    print(json.dumps({'cargo':cargo['status'],'licenses':{s:sum(r['decision']==s for r in records) for s in ['PASS','BLOCKED','UNKNOWN']},
                      'fullBundle':'BLOCKED','binaryDistributionReadiness':'BLOCKED'}))
    # Only public source receipts/notices; never environment/config/credentials or binary archives.
    wanted=['cargo-resolution.json','rust-compile-link-scope.json','rust-license-resolution.json','full-bundle-rebuild.json','static-relinking-inputs.json','technical-validation.json','generated-Cargo.lock','rustc.stdout','cargo.stdout','compiler.stderr']
    wanted += [p.name for p in a.out.glob('*-header-*.txt')]
    wanted += [p.name for p in a.out.glob('*-upstream-*.txt')]
    for name in wanted:
        p=a.out/name
        if p.is_file() and p.stat().st_size<=1024*1024:
            data=p.read_text()
            for offset in range(0,len(data),5000):
                print('S05D_FILE '+json.dumps({'path':name,'offset':offset,'data':data[offset:offset+5000]}))
    raise SystemExit(1)  # Honest partial/blocked experiment, never a successful full build.
