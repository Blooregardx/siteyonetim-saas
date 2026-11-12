"""Measure real binaries, symbols, archive members and native Sharp binding.

No builds or publications. Run after the controlled offline experiment. ABI
type coverage and legal/source provision decisions remain separate.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import re
import tarfile

from s05e_source_protocol import file_sha
from verify_s05d_evidence import archive_members

ROOT=Path(__file__).resolve().parents[1]
ABI_IMAGE='sha256:49cad6a30bbe7deedc40da7b06f9de69836e726cf467e105c8c8e20f02be4e9c'
ABI_SCRIPT=r'''
import subprocess,json,pathlib,hashlib
r=pathlib.Path('/evidence')
checks=[]
for command in [['rpmkeys','--checksig','/abi-tool.rpm'],['rpm','-V','libabigail'],['rpm','-V','gcc-toolset-15-binutils']]:
 p=subprocess.run(command,capture_output=True,text=True)
 checks.append({'command':command,'exitCode':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
if any(c['exitCode'] for c in checks):
 (r/'abi-measurement.json').write_text(json.dumps({'status':'BLOCKED','toolVerification':checks}));raise SystemExit(1)
version=subprocess.check_output(['abidiff','--version'],text=True).strip()
tool=pathlib.Path('/usr/bin/abidiff')
for phase,path in [('original','/original.so'),('control','/evidence/control/libvips-cpp.so.8.18.7'),('modified','/evidence/modified/libvips-cpp.so.8.18.7')]:
 for label,opts in [('dynsym',['--dyn-syms','--wide']),('dynamic',['-d']),('sections',['--sections','--wide']),('version-info',['--version-info'])]:
  p=subprocess.run(['readelf']+opts+[path],capture_output=True)
  (r/(phase+'-'+label+'.txt')).write_bytes(p.stdout)
  if p.returncode:raise SystemExit(p.returncode)
commands=[]
for label,command in [('control-modified',['abidiff','/evidence/control/libvips-cpp.so.8.18.7','/evidence/modified/libvips-cpp.so.8.18.7']),('original-control',['abidiff','/original.so','/evidence/control/libvips-cpp.so.8.18.7']),('typed-control-modified',['abidiff','--fail-no-debug-info','/evidence/control/libvips-cpp.so.8.18.7','/evidence/modified/libvips-cpp.so.8.18.7'])]:
 p=subprocess.run(command,capture_output=True,timeout=180)
 (r/(label+'.abidiff.stdout')).write_bytes(p.stdout);(r/(label+'.abidiff.stderr')).write_bytes(p.stderr)
 commands.append({'label':label,'command':command,'exitCode':p.returncode})
data={'status':'PARTIAL','toolVerification':checks,'version':version,'toolSha256':hashlib.sha256(tool.read_bytes()).hexdigest(),'commands':commands,'typeCoverage':'No full type ABI claim without DWARF','legalApproval':False}
(r/'abi-measurement.json').write_text(json.dumps(data,indent=2)+'\n')
'''


def exports(text):
    names=set()
    for line in text.splitlines():
        f=line.split()
        if len(f)>=8 and f[4] in {'GLOBAL','WEAK'} and f[5] in {'DEFAULT','PROTECTED'} and f[6]!='UND':names.add(f[7])
    return names


def provenance(run,control_run,inputs,control_container,modified_container):
    from run_s05e_native import preflight
    spec=json.loads((ROOT/'docs/evidence/s05e/toolchain.json').read_text())
    check=preflight(inputs,spec['preparedConfigDigest'])
    (run/'final-input-preflight.json').write_text(json.dumps(check,indent=2)+'\n')
    if check['decision']!='PASS':raise ValueError('PHYSICAL_INPUT_PREFLIGHT')
    runtime=[]
    for name in [control_container,modified_container]:
        if not re.fullmatch('s05e-[a-z-]+',name):raise ValueError('EXPERIMENT_CONTAINER_NAME')
        i=json.loads(subprocess.check_output(['docker','inspect',name],timeout=30))[0]
        h=i['HostConfig'];c=i['Config'];s=i['State']
        item={'name':name,'configDigest':i['Image'],'network':h['NetworkMode'],'readOnlyRootfs':h['ReadonlyRootfs'],
              'capDrop':h['CapDrop'],'securityOptions':h['SecurityOpt'],'user':c['User'],
              'memoryBytes':h['Memory'],'nanoCpus':h['NanoCpus'],'exitCode':s['ExitCode'],'running':s['Running'],'oomKilled':s['OOMKilled']}
        if i['Image']!=spec['preparedConfigDigest'] or h['NetworkMode']!='none' or not h['ReadonlyRootfs'] or 'ALL' not in h['CapDrop'] or not any('no-new-privileges' in x for x in h['SecurityOpt']):
            raise ValueError('RUNTIME_SECURITY_OR_IDENTITY')
        if int(c['User'].split(':')[0])<=0 or s['Running'] or s['ExitCode']!=0 or s['OOMKilled'] or h['Memory']!=6*1024**3 or h['NanoCpus']!=2*10**9:
            raise ValueError('RUNTIME_EXECUTION_OR_LIMITS')
        runtime.append(item)
    before=run/'control/vips/libvips/iofuncs/init.c';after=run/'modified/vips/libvips/iofuncs/init.c'
    with tarfile.open(inputs/'sources/vips.tar') as t:
        found=[e for e in t if e.name.endswith('/libvips/iofuncs/init.c') and e.isfile()]
        if len(found)!=1:raise ValueError('UPSTREAM_SOURCE_MEMBER')
        original=t.extractfile(found[0]).read()
    if before.read_bytes()!=original:raise ValueError('CONTROL_NOT_ORIGINAL_INIT')
    appended=b'\n/* S05-E: private retained marker, no public API or image algorithm change. */\nstatic const char s05e_native_rebuild_marker[] __attribute__((used, retain)) = "S05E_MODIFIED_SOURCE_EVIDENCE";\n'
    if after.read_bytes()!=original+appended:raise ValueError('UNREVIEWED_SOURCE_MODIFICATION')
    def tree(base):
        result={}
        for p in base.rglob('*'):
            relative=p.relative_to(base)
            if '_build' in relative.parts:continue
            if p.is_symlink():result[str(relative)]={'link':os.readlink(p)}
            elif p.is_file():result[str(relative)]=file_sha(p)
        return result
    a=tree(run/'control/vips');b=tree(run/'modified/vips')
    differences=[p for p in sorted(a.keys()|b.keys()) if a.get(p)!=b.get(p)]
    if differences!=['libvips/iofuncs/init.c']:raise ValueError('UNEXPECTED_SOURCE_TREE_DIFF')
    def commands(phase):
        data=json.loads((run/phase/'vips/_build/compile_commands.json').read_text())
        return sorted((r['file'],r['directory'],r['command']) for r in data)
    if commands('control')!=commands('modified'):raise ValueError('COMPILER_FLAGS_OR_FEATURES_DIFFER')
    def excluded(log):
        values=re.findall(r"EXCLUDE_LIBS='([^']+)'",log.read_text())
        if not values:raise ValueError('ACTUAL_EXCLUDE_COMMAND_MISSING')
        return sorted(set(values[-1].split()))
    control_excluded=excluded(control_run/'control.log');modified_excluded=excluded(run/'modified.log')
    if control_excluded!=modified_excluded or '-Wl,--exclude-libs=libvips.a' in modified_excluded:
        raise ValueError('PREFIX_POLLUTION_OR_LINK_PROFILE')
    def deps(base):
        result={}
        for p in (base/'target/lib').glob('*.a'):
            if p.name.startswith('libvips'):continue
            target=p.resolve()
            if not target.is_relative_to((base/'target').resolve()):raise ValueError('STATIC_ALIAS_ESCAPE')
            result[p.name]=file_sha(target)
        return result
    dependency_hashes=deps(control_run)
    if dependency_hashes!=deps(run):raise ValueError('STATIC_DEPENDENCIES_CHANGED')
    result={'schemaVersion':1,'decision':'PASS','scope':'Controlled full-profile source/compiler/static-input correspondence; not historical bit reproduction',
            'runtime':runtime,'sourceDifferences':differences,'sourceBeforeSha256':file_sha(before),'sourceAfterSha256':file_sha(after),
            'compileCommandsIdentical':True,'compileCommandCount':len(commands('control')),'linkExclusionsIdentical':True,
            'excludedArchives':control_excluded,'nativeArchiveHashes':dependency_hashes,'preflightSha256':file_sha(run/'final-input-preflight.json'),
            'legalApproval':False,'binaryDistributionReadiness':'BLOCKED'}
    (run/'source-build-provenance.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


def capture(run,inputs,control_run=None):
    control_run=control_run or run
    def container_name(base):
        command=json.loads((base/'invocation.json').read_text())['command']
        return command[command.index('--name')+1]
    proof=provenance(run,control_run,inputs,container_name(control_run),container_name(run))
    for phase in ['control','modified']:
        p=run/phase/'libvips-cpp.so.8.18.7'
        raw=p.read_bytes() if p.is_file() else b''
        if raw[:6]!=b'\x7fELF\x02\x01' or int.from_bytes(raw[16:18],'little')!=3 or int.from_bytes(raw[18:20],'little')!=62:raise ValueError('MISSING_REAL_ELF')
    original=ROOT/'node_modules/@img/sharp-libvips-linux-x64/lib/libvips-cpp.so.8.18.7'
    original=original.resolve();old=file_sha(original)
    (run/'npm-original-library.json').write_text(json.dumps({'file':str(original),'sha256':old,'scope':'npm comparison input, not runtime/migration image identity'},indent=2)+'\n')
    # Preserve every earlier failed probe instead of replacing its result.
    for phase in ['control','modified','original-negative']:
        binary=run/('control' if phase=='original-negative' else phase)/'libvips-cpp.so.8.18.7'
        expected=file_sha(binary)
        env={**os.environ,'LD_PRELOAD':str(original if phase=='original-negative' else binary),
             'S05E_LIBRARY_PATH':str(binary),'S05E_LIBRARY_SHA256':expected,'S05E_ORIGINAL_SHA256':old,
             'S05E_PACKAGE_JSON':str(ROOT/'package.json')}
        result=subprocess.run(['node',str(ROOT/'docker/s05e-sharp-probe.mjs')],env=env,capture_output=True,timeout=60)
        dest=run/(phase+'-sharp.json')
        if dest.exists():
            i=1
            while (run/(phase+'-sharp.previous-'+str(i)+'.json')).exists():i+=1
            dest.rename(run/(phase+'-sharp.previous-'+str(i)+'.json'))
        dest.write_bytes(result.stdout);(run/(phase+'-sharp.stderr')).write_bytes(result.stderr)
    rpm=inputs/'rpm-stage-build-dependencies/libabigail-2.10-1.el8.x86_64.rpm'
    command=['docker','run','--name','s05e-abi-measurement','--network=none','--read-only','--cap-drop=ALL',
             '--security-opt=no-new-privileges','--user',str(os.getuid())+':'+str(os.getgid()),'--memory=1g','--cpus=2','--pids-limit=128',
             '-v',str(run)+':/evidence:rw','-v',str(original)+':/original.so:ro','-v',str(rpm)+':/abi-tool.rpm:ro',
             ABI_IMAGE,'python3.12','-c',ABI_SCRIPT]
    with (run/'abi-executor.log').open('wb') as log:
        result=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,timeout=600,check=False)
    if result.returncode:raise ValueError('ABI_TOOL_EXECUTION_OR_SIGNATURE_FAILED')
    sets={p:exports((run/(p+'-dynsym.txt')).read_text()) for p in ['original','control','modified']}
    plain=lambda values:{v.split('@',1)[0] for v in values}
    symbols={'exportCounts':{k:len(v) for k,v in sets.items()},
             'originalControlMissing':sorted(plain(sets['original'])-plain(sets['control'])),
             'originalControlAdded':sorted(plain(sets['control'])-plain(sets['original'])),
             'controlModifiedMissing':sorted(plain(sets['control'])-plain(sets['modified'])),
             'controlModifiedAdded':sorted(plain(sets['modified'])-plain(sets['control'])),
             'versionedMissing':sorted(sets['control']-sets['modified']),
             'versionedAdded':sorted(sets['modified']-sets['control']),
             'historicalS05CReducedMissing':1946,'typeAbiConclusion':'PARTIAL; exported names are not a type-level ABI proof'}
    def imports(text):
        return {f[7] for line in text.splitlines() if len(f:=line.split())>=8 and f[6]=='UND' and '@' in f[7]}
    imported={p:imports((run/(p+'-dynsym.txt')).read_text()) for p in ['original','control','modified']}
    symbols.update(versionedImportCounts={p:len(v) for p,v in imported.items()},
                   versionedImportMissing=sorted(imported['control']-imported['modified']),
                   versionedImportAdded=sorted(imported['modified']-imported['control']))
    (run/'symbol-comparison.json').write_text(json.dumps(symbols,indent=2)+'\n')
    archives=[]
    paths=list((run/'target/lib').glob('*.a'))
    paths += [run/phase/'vips/_build/libvips/libvips.a' for phase in ['control','modified']]
    for p in sorted(paths):
        if not p.is_file() or p.is_symlink():continue
        raw=p.read_bytes();members=archive_members(raw)
        if not members:raise ValueError('EMPTY_STATIC_ARCHIVE')
        archives.append({'file':str(p.relative_to(run)),'sha256':hashlib.sha256(raw).hexdigest(),'size':len(raw),'members':members})
    objects=[]
    for base in [run/'control/vips/_build',run/'modified/vips/_build']:
        for p in sorted(base.rglob('*.o')):
            objects.append({'file':str(p.relative_to(run)),'sha256':file_sha(p),'size':p.stat().st_size})
    static={'scope':'Actual retained static files; archive presence/member != proof each member linked',
            'archives':archives,'objects':objects,'archiveCount':len(archives),'objectCount':len(objects),
            'archiveMemberCount':sum(len(a['members']) for a in archives),'legalApproval':False}
    (run/'static-inputs.json').write_text(json.dumps(static,indent=2)+'\n')
    # This inventory lives in the experiment workspace, not a source offer.
    probe={p:json.loads((run/(p+'-sharp.json')).read_text()) for p in ['control','modified','original-negative']}
    marker=b'S05E_MODIFIED_SOURCE_EVIDENCE'
    pair={'controlSha256':file_sha(run/'control/libvips-cpp.so.8.18.7'),'modifiedSha256':file_sha(run/'modified/libvips-cpp.so.8.18.7'),
          'markerInControl':marker in (run/'control/libvips-cpp.so.8.18.7').read_bytes(),
          'markerInModified':marker in (run/'modified/libvips-cpp.so.8.18.7').read_bytes()}
    full_ok=pair['controlSha256']!=pair['modifiedSha256'] and not pair['markerInControl'] and pair['markerInModified']
    sharp_ok=all(probe[p]['status']=='PASS' and probe[p]['targetLoaded'] and not probe[p]['originalLibraryLoaded'] for p in ['control','modified'])
    negative=probe['original-negative']['status']=='BLOCKED' and probe['original-negative']['originalLibraryLoaded'] and not probe['original-negative']['targetLoaded']
    result={'schemaVersion':1,'fullRebuild':'PASS' if full_ok else 'BLOCKED','binaryPair':pair,
            'sharpSyntheticCompatibility':'PASS' if sharp_ok and negative else 'BLOCKED',
            'abiCompatibility':'PARTIAL','staticRelinkingInputs':'PARTIAL','durableSourceProvision':'PARTIAL',
            'symbolComparison':symbols,'archiveCount':len(archives),'objectCount':len(objects),'archiveMemberCount':static['archiveMemberCount'],
            'abiToolImage':ABI_IMAGE,'abiToolRpmSha256':file_sha(rpm),
            'sourceBuildProvenanceSha256':file_sha(run/'source-build-provenance.json'),'sourceBuildProvenance':proof['decision'],
            'legalApproval':False,'binaryDistributionReadiness':'BLOCKED'}
    (run/'native-validation.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',type=Path,required=True);p.add_argument('--inputs',type=Path,required=True)
    p.add_argument('--control-run',type=Path)
    a=p.parse_args();print(json.dumps(capture(a.run.resolve(),a.inputs.resolve(),a.control_run.resolve() if a.control_run else None),indent=2))
