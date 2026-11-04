"""Network-free reduced-feature source rebuild inside the dedicated pinned container."""
import difflib
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import tarfile

OUT=Path('/out')
WORK=Path('/work')
MARKER='S05C_MODIFIED_SOURCE_MARKER_20261104'
FLAGS=['--default-library=shared','--buildtype=release','--libdir=lib','--prefix=/opt/s05c','--wrap-mode=nodownload','-Dauto_features=disabled','-Dmodules=disabled','-Dintrospection=disabled','-Dexamples=false','-Ddeprecated=false','-Dcplusplus=true','-Dpng=enabled','-Djpeg=enabled']


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def execute(args,cwd=None):
    with (OUT/'build.log').open('a') as log:
        log.write(json.dumps(args)+'\n');log.flush()
        return subprocess.run(args,cwd=cwd,check=True,stdout=log,stderr=log)


def capture(args):return subprocess.check_output(args,text=True,stderr=subprocess.DEVNULL).strip()


def extract(path,destination):
    total=0
    with tarfile.open(path) as t:
        for e in t:
            p=PurePosixPath(e.name)
            if p.is_absolute() or '..' in p.parts:raise ValueError('ARCHIVE_PATH')
            if e.issym() or e.islnk():continue  # Never follow links.
            if not e.isfile():continue
            total+=e.size
            if e.size>64*1024**2 or total>512*1024**2:raise ValueError('ARCHIVE_SIZE')
            relative=Path(*p.parts[1:]);target=destination/relative;target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(t.extractfile(e).read())


def symbols(path):
    return sorted(set(line.split()[-1].split('@')[0] for line in capture(['nm','-D','--defined-only',str(path)]).splitlines() if line.split()))


def main():
    OUT.mkdir(parents=True,exist_ok=True);WORK.mkdir(parents=True,exist_ok=True)
    spec=json.load(open('/input/spec.json'));state={'schemaVersion':1,'sourceCommit':spec['sourceCommit'],'target':spec['target'],'baseImage':spec['baseImage'],'profile':spec['profile'],'fullUpstreamRecipe':False,'stage':'source-verification','status':'BLOCKED','binaryDistributionReadiness':'BLOCKED'}
    def save():(OUT/'rebuild-result.json').write_text(json.dumps(state,indent=2)+'\n')
    save()
    try:
        source=Path('/input/vips.tar');patch=Path('/input/soname.patch')
        if sha(source)!=spec['source']['sha256'] or sha(patch)!=spec['sonamePatch']['sha256']:raise ValueError('SOURCE_OR_PATCH_HASH')
        tools={'gcc':capture(['gcc','-dumpfullversion']),'linker':capture(['ld','--version']).splitlines()[0],'meson':capture(['meson','--version']),'ninja':capture(['ninja','--version']),'target':capture(['gcc','-dumpmachine']),'python':capture(['python3','--version']),'rust':'NOT_USED: librsvg disabled in reduced profile'}
        state['toolchain']=tools
        for name,expected in spec['expectedTools'].items():
            if tools[name]!=expected:raise ValueError('TOOLCHAIN_'+name)
        if tools['target']!=spec['target']:raise ValueError('TARGET')
        (OUT/'dpkg-packages.txt').write_text(capture(['dpkg-query','-W','-f=${Package}\t${Version}\n']))
        state['stage']='control-build';save();control=WORK/'control';extract(source,control)
        execute(['patch','--batch','--forward','-p1','-i',str(patch)],control)
        meson=control/'libvips/meson.build';text=meson.read_text()
        if text.count("library('vips'")!=1:raise ValueError('STATIC_CORE_RECIPE')
        text=text.replace("library('vips'","static_library('vips'")
        lines=text.splitlines(True);remove=set()
        for i,l in enumerate(lines):
            if 'version: library_version' in l:remove.update([i,i+1])
        meson.write_text(''.join(l for i,l in enumerate(lines) if i not in remove))
        modified=WORK/'modified';shutil.copytree(control,modified)
        target=modified/'libvips/iofuncs/init.c';before=target.read_bytes()
        addition=('\n/* S05-C scratch experiment; inherits this upstream file LGPL terms. */\n__attribute__((used,retain)) static const char s05c_marker[] = "'+MARKER+'";\n').encode()
        target.write_bytes(before+addition)
        diff=''.join(difflib.unified_diff(before.decode().splitlines(True),(before+addition).decode().splitlines(True),fromfile='a/libvips/iofuncs/init.c',tofile='b/libvips/iofuncs/init.c'))
        (OUT/'source-change.patch').write_text(diff)
        state['sourceModification']={'file':'libvips/iofuncs/init.c','beforeSha256':hashlib.sha256(before).hexdigest(),'afterSha256':sha(target),'patchSha256':sha(OUT/'source-change.patch'),'marker':MARKER,'behavior':'retained internal data only, no new exported API or algorithm change'}
        binaries={}
        for kind,root in [('control',control),('modified',modified)]:
            state['stage']=kind+'-build';state.setdefault('buildFlags',{})[kind]={'meson':FLAGS,'CFLAGS':'-O2 -fPIC -ffile-prefix-map='+str(root)+'=.','CXXFLAGS':'-O2 -fPIC -ffile-prefix-map='+str(root)+'=.','SOURCE_DATE_EPOCH':'1793750400'}
            os.environ.update({k:v for k,v in state['buildFlags'][kind].items() if k!='meson'});save()
            execute(['meson','setup','build',*FLAGS],root);execute(['ninja','-C','build','-j2'],root)
            execute(['meson','install','-C','build','--destdir',str(OUT/kind)],root)
            installed=next((OUT/kind).rglob('libvips-cpp.so.8.18.7'))
            binary=OUT/kind/'libvips-cpp.so.8.18.7';shutil.copyfile(installed.resolve(),binary)
            binaries[kind]={'path':str(binary),'sha256':sha(binary),'soname':capture(['readelf','-d',str(binary)]),'symbols':symbols(binary)}
        state['binaries']=binaries
        state['abi']={'controlVsModifiedEqual':binaries['control']['symbols']==binaries['modified']['symbols'],'missingFromModified':sorted(set(binaries['control']['symbols'])-set(binaries['modified']['symbols']))}
        old=Path('/app/node_modules/@img/sharp-libvips-linux-x64/lib/libvips-cpp.so.8.18.7');state['distributedBinarySha256']=sha(old);shutil.copyfile(old,OUT/'distributed-libvips.so')
        state['abi']['missingComparedWithDistributed']=sorted(set(symbols(old))-set(binaries['modified']['symbols']))
        new=Path(binaries['modified']['path'])
        if binaries['control']['sha256']==sha(new) or sha(old)==sha(new) or MARKER.encode() not in new.read_bytes():raise ValueError('NOT_A_DIFFERENT_SOURCE_REBUILD')
        env={**os.environ,'LD_PRELOAD':str(new),'S05C_NEW_LIBRARY':str(new),'S05C_OLD_LIBRARY':str(old)}
        code="""const fs=require('fs'),c=require('crypto'),sharp=require('/app/node_modules/sharp');(async()=>{const p=await sharp({create:{width:2,height:2,channels:3,background:'#123456'}}).resize(1,1).png().toBuffer();const meta=await sharp(p).metadata();fs.writeFileSync('/out/result.png',p);const maps=fs.readFileSync('/proc/self/maps','utf8');console.log(JSON.stringify({png:p.subarray(0,8).toString('hex')==='89504e470d0a1a0a',width:meta.width,height:meta.height,newLoaded:maps.includes(process.env.S05C_NEW_LIBRARY),oldLoaded:maps.includes(process.env.S05C_OLD_LIBRARY),loadedSha256:c.createHash('sha256').update(fs.readFileSync(process.env.S05C_NEW_LIBRARY)).digest('hex')}));})().catch(()=>process.exit(1));"""
        state['stage']='sharp-png';save();r=subprocess.run(['node','-e',code],env=env,capture_output=True,text=True,timeout=45)
        state['sharp']={'exitCode':r.returncode,**(json.loads(r.stdout) if r.returncode==0 else {}),'stderrCode':'CHILD_FAILED' if r.returncode else None}
        state['staticInputs']={'originalFullBundleAvailable':False,'reason':'System dynamic dependencies replace original static native/Rust bundle; not equivalent source/relinking inputs','newCoreArchives':[{'path':str(p),'sha256':sha(p)} for p in WORK.rglob('libvips.a')]}
        if r.returncode or not state['sharp']['newLoaded'] or state['sharp']['oldLoaded'] or not state['sharp']['png'] or state['sharp']['loadedSha256']!=sha(new):raise ValueError('MODIFIED_LIBRARY_NOT_PROVEN_LOADED')
        if not state['abi']['controlVsModifiedEqual']:raise ValueError('ABI_CHANGED')
        state.update(stage='completed',status='PARTIAL',modifiedSourceBuild='VERIFIED_FOR_REDUCED_PROFILE',fullCorrespondingSource='BLOCKED',bitReproducibleBuild='NOT_TESTED')
        save()
    except (OSError,ValueError,StopIteration,subprocess.SubprocessError) as error:
        state['failureType']=type(error).__name__;save();raise


if __name__=='__main__':main()
