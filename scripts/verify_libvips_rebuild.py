"""Separate structural input checks, actual source/binary files and full readiness."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import tomllib
import subprocess
import tarfile
import struct
import zlib
from run_libvips_rebuild import FLAGS

COMMIT='24ad4d042940e6bf99a68871ba886ca8847c9c82'
ROOT=Path(__file__).resolve().parents[1]
LOCK_SHA='e79e2a2735a0b5b151bb4133becd3008223fabedd34a8b787a872edab9854941'
SOURCE_SHA='5baaead3b0bb20ffdb9e9ff09aa9fda08620923df77b63b436654cb5e0b3bf94'
BASE_IMAGE='node:24-bookworm-slim@sha256:c86ecead9e55a5210ac1727de38a4ca840bf03dcaf34dc9749addbf383b1920c'
TOOLS={'gcc': '12.2.0', 'meson': '1.9.1', 'ninja': '1.11.1'}


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def file_at(root,name):
    p=Path(name)
    if p.is_absolute():
        if p.parts[1] not in ['out','work']:raise ValueError('FOREIGN_EVIDENCE_PATH')
        p=Path(*p.parts[1:])
    if '..' in p.parts:raise ValueError('TRAVERSAL')
    result=root/p
    if not result.is_file() or result.is_symlink() or not result.resolve().is_relative_to(root.resolve()):raise ValueError('MISSING_EVIDENCE_FILE')
    return result


def verify_scope(scope,lock_path,observations):
    if scope.get('schemaVersion')!=1 or scope.get('target')!='x86_64-unknown-linux-gnu' or scope.get('upstreamRecipeCommit')!='ebb95f8add54eee8bed840e3fb587e4cbec857d7':raise ValueError('RUST_TARGET_RECIPE_SCHEMA')
    if scope['lockSha256']!=LOCK_SHA or scope['lockSha256']!=sha(lock_path):raise ValueError('CARGO_LOCK')
    lock=[p for p in tomllib.loads(lock_path.read_text())['package'] if 'source' in p]
    if len(scope['records'])!=len(lock):raise ValueError('RUST_SCOPE_COUNT')
    if {(r['name'],r['version'],r['source']) for r in scope['records']}!={(p['name'],p['version'],p['source']) for p in lock}:raise ValueError('DUPLICATE_OR_MISSING_CRATE')
    if scope['counts']!={s:sum(r['scopeDecision']==s for r in scope['records']) for s in ['COMPILED — EVIDENCED','RESOLVED — NOT PROVEN COMPILED','NOT SELECTED — EVIDENCED','UNKNOWN']}:raise ValueError('SCOPE_COUNTS')
    identities={(p['name'],p['version'],p['source']):p for p in lock}
    allowed={'COMPILED — EVIDENCED','RESOLVED — NOT PROVEN COMPILED','NOT SELECTED — EVIDENCED','UNKNOWN'}
    for r in scope['records']:
        if r.get('target')!=scope['target'] or r.get('features')!='default librsvg-c package after pinned recipe removes image gif/webp and cairo pdf/ps; resolved per-crate features unavailable':raise ValueError('RUST_TARGET_FEATURES')
        old=identities.get((r['name'],r['version'],r['source']))
        if not old or r.get('lockChecksum')!=old.get('checksum'):raise ValueError('CRATE_IDENTITY_CHECKSUM')
        if r['scopeDecision'] not in allowed:raise ValueError('RUST_SCOPE_STATUS')
        if r['scopeDecision']=='COMPILED — EVIDENCED':
            if not r.get('evidenceLines'):raise ValueError('COMPILATION_EVIDENCE_MISSING')
            for line in r['evidenceLines']:
                match=re.search(r'Compiling ([\w-]+) v([^\s]+)',line)
                if line not in observations['compiledLines'] or not match or match.groups()!=(r['name'],r['version']) or re.search(r'#\d+\s+\d+\.',line):raise ValueError('NOT_LIBRSVG_COMPILATION')
        if r['scopeDecision'] in ['NOT SELECTED — EVIDENCED','RESOLVED — NOT PROVEN COMPILED']:raise ValueError('PRIMARY_UPSTREAM_SCOPE_CANNOT_USE_UNVERIFIED_CONTROLLED_GRAPH')
    return {'decision':'PARTIAL','counts':scope['counts'],'binaryDistributionReadiness':'BLOCKED'}


def verify_sources(manifest,root,archive_root=None):
    if manifest.get('schemaVersion')!=1 or manifest.get('scopeLockSha256')!=LOCK_SHA:raise ValueError('RUST_SOURCE_SCHEMA_LOCK')
    trusted={(p['name'],p['version'],p['source']):p.get('checksum') for p in tomllib.loads((ROOT/'docs/evidence/s05b/upstream/librsvg-Cargo.lock').read_text())['package'] if 'source' in p}
    if len(manifest['records'])!=len(trusted) or len({(r['name'],r['version'],r['source']) for r in manifest['records']})!=len(trusted):raise ValueError('SOURCE_RECORD_COVERAGE')
    for r in manifest['records']:
        if (r['name'],r['version'],r['source']) not in trusted:raise ValueError('UNKNOWN_CRATE_IDENTITY')
        if r.get('lockChecksum')!=trusted[(r['name'],r['version'],r['source'])]:raise ValueError('LOCK_CRATE_CHECKSUM')
        kind=r.get('sourceKind')
        actual_kind='registry' if r['source'].startswith('registry+') else 'git' if r['source'].startswith('git+') else 'path'
        if kind!=actual_kind:raise ValueError('SOURCE_KIND_IDENTITY')
        if kind not in ['registry','git','path']:raise ValueError('SOURCE_KIND')
        if r['decision']!='PASS':continue
        if kind=='registry':
            if not re.fullmatch('[a-f0-9]{64}',r.get('archiveSha256','')) or r['archiveSha256']!=r.get('expectedChecksum') or (r.get('lockChecksum') and r['archiveSha256']!=r['lockChecksum']):raise ValueError('CARGO_SOURCE_CHECKSUM')
        elif kind=='git':
            if not re.fullmatch('[a-f0-9]{40}',(r.get('gitCommit') or '')):raise ValueError('GIT_SOURCE_REVISION')
        elif not r.get('sourceArchiveSha256'):raise ValueError('PATH_SOURCE_ARCHIVE')
        if not r.get('notices') or not r.get('license'):raise ValueError('LICENSE_NOTICE_MISSING')
        archive=None
        if archive_root is not None:
            path=file_at(archive_root,r['name']+'-'+r['version']+'.crate')
            if sha(path)!=r['archiveSha256']:raise ValueError('ACTUAL_CRATE_CHECKSUM')
            from research_rust_sources import inspect_rust_archive
            found={n['path']:n['sha256'] for n in inspect_rust_archive(path)}
            if any(found.get(n['path'])!=n['sha256'] for n in r['notices']):raise ValueError('CRATE_NOTICE_BINDING')
        for n in r['notices']:
            if sha(file_at(root,n['evidenceFile']))!=n['sha256']:raise ValueError('LICENSE_NOTICE_HASH')
    return {'decision':'PARTIAL','counts':manifest['counts'],'sourceBytes':'REVALIDATED' if archive_root is not None else 'NOT_REVALIDATED_IN_THIS_CHECK','binaryDistributionReadiness':'BLOCKED'}


def verify_rebuild(result,root,spec):
    if result.get('sourceCommit')!=COMMIT:raise ValueError('SOURCE_COMMIT')
    if spec['baseImage']!=BASE_IMAGE or spec['source']['sha256']!=SOURCE_SHA or spec['expectedTools']!=TOOLS:raise ValueError('UNTRUSTED_SPECIFICATION')
    if result.get('baseImage')!=spec['baseImage'] or result.get('target')!=spec['target']:raise ValueError('BASE_OR_TARGET')
    if result.get('status')=='BLOCKED':return {'modifiedRebuild':'BLOCKED','stage':result.get('stage'),'staticInputs':'BLOCKED','binaryDistributionReadiness':'BLOCKED'}
    if result.get('packages')!={'sharp':'0.35.5','@img/sharp-libvips-linux-x64':'1.3.4','@img/sharp-linux-x64':'0.35.5'}:raise ValueError('NATIVE_PACKAGE_VERSION')
    if sha(file_at(root,'out/sharp-addon.node'))!=result['nativeAddon']['sha256']:raise ValueError('NATIVE_ADDON_HASH')
    image=(root/'environment-config-id.txt').read_text().strip()
    sbom=json.loads(file_at(root,'out/environment-sbom.syft.json').read_text())
    if result.get('imageID')!=image or sbom['source']['metadata']['imageID']!=image or result.get('sbomSha256')!=sha(file_at(root,'out/environment-sbom.syft.json')):raise ValueError('FOREIGN_SBOM_OR_IMAGE')
    if result.get('profile')!=spec['profile'] or result.get('fullUpstreamRecipe') is not False:raise ValueError('FEATURE_PROFILE')
    if any(result.get('buildFlags',{}).get(k,{}).get('meson')!=FLAGS for k in ['control','modified']):raise ValueError('FEATURE_FLAGS')
    tools=result['toolchain']
    if any(tools.get(n)!=v for n,v in spec['expectedTools'].items()):raise ValueError('TOOLCHAIN')
    change=result['sourceModification'];control=file_at(root,'work/control/'+change['file']);modified=file_at(root,'work/modified/'+change['file'])
    if sha(control)!=change['beforeSha256'] or sha(modified)!=change['afterSha256'] or sha(control)==sha(modified):raise ValueError('SOURCE_CHANGE')
    if sha(file_at(root,'out/source-change.patch'))!=change['patchSha256']:raise ValueError('SOURCE_PATCH')
    archive=file_at(root,'input/vips.tar')
    if sha(archive)!=spec['source']['sha256']:raise ValueError('SOURCE_ARCHIVE')
    with tarfile.open(archive) as t:
        entry=next(e for e in t if e.isfile() and e.name.endswith('/'+change['file']))
        if t.extractfile(entry).read()!=control.read_bytes():raise ValueError('NOT_UPSTREAM_SOURCE')
    old=result['binaries']['control'];new=result['binaries']['modified'];old_file=file_at(root,old['path']);new_file=file_at(root,new['path'])
    if sha(old_file)!=old['sha256'] or sha(new_file)!=new['sha256'] or old['sha256']==new['sha256'] or result['distributedBinarySha256']==new['sha256']:raise ValueError('SAME_OR_WRONG_BINARY')
    for binary in [old_file,new_file]:
        data=binary.read_bytes()
        if len(data)<20 or data[:6]!=b'\x7fELF\x02\x01' or int.from_bytes(data[18:20],'little')!=62:raise ValueError('ELF_PLATFORM')
    actual_soname=subprocess.check_output(['readelf','-d',str(new_file)],text=True)
    if 'libvips-cpp.so.8.18.7' not in actual_soname:raise ValueError('ACTUAL_SONAME')
    def symbols(p):return {line.split()[-1].split('@')[0] for line in subprocess.check_output(['nm','-D','--defined-only',str(p)],text=True).splitlines() if line.split()}
    if symbols(old_file)!=symbols(new_file):raise ValueError('ACTUAL_ABI')
    if sha(file_at(root,'out/distributed-libvips.so'))!=spec['distributedBinarySha256'] or result['distributedBinarySha256']!=spec['distributedBinarySha256']:raise ValueError('DISTRIBUTED_BINARY')
    png=file_at(root,'out/result.png').read_bytes()
    if png[:8]!=b'\x89PNG\r\n\x1a\n' or int.from_bytes(png[16:20],'big')!=1 or int.from_bytes(png[20:24],'big')!=1:raise ValueError('PNG_FILE')
    offset=8;idat=b'';ended=False
    while offset<len(png):
        if offset+12>len(png):raise ValueError('PNG_TRUNCATED')
        size=int.from_bytes(png[offset:offset+4],'big');kind=png[offset+4:offset+8];data=png[offset+8:offset+8+size];end=offset+12+size
        if end>len(png) or zlib.crc32(kind+data)&0xffffffff!=int.from_bytes(png[end-4:end],'big'):raise ValueError('PNG_CRC')
        if kind==b'IDAT':idat+=data
        if kind==b'IEND':ended=True
        offset=end
    decoder=zlib.decompressobj();pixels=decoder.decompress(idat,32) if idat else b''
    if not ended or not decoder.eof or len(pixels) not in [4,5] or pixels[0]>4 or pixels[1:4]!=b'\x12\x34\x56':raise ValueError('PNG_DATA')
    if change['marker'].encode() not in new_file.read_bytes():raise ValueError('SOURCE_MARKER_MISSING')
    if not result['abi']['controlVsModifiedEqual'] or result['abi']['missingFromModified']:raise ValueError('ABI')
    if 'libvips-cpp.so.8.18.7' not in new['soname']:raise ValueError('SONAME')
    actual_missing=sorted(symbols(file_at(root,'out/distributed-libvips.so'))-symbols(new_file))
    if actual_missing!=result['abi']['missingComparedWithDistributed']:raise ValueError('DISTRIBUTED_ABI_CLAIM')
    maps=file_at(root,'out/sharp-maps.txt').read_text()
    if new['path'] not in maps or '/app/node_modules/@img/sharp-libvips-linux-x64/lib/libvips-cpp.so.8.18.7' in maps:raise ValueError('RAW_LIBRARY_MAPS')
    if result['nativeAddon']['path'] not in maps:raise ValueError('NATIVE_ADDON_MAPS')
    probe=result['sharp']
    if probe['exitCode']!=0 or not probe.get('newLoaded') or probe.get('oldLoaded') or probe.get('loadedSha256')!=new['sha256'] or not probe.get('png') or probe.get('width')!=1 or probe.get('height')!=1:raise ValueError('FAKE_OR_OLD_LIBRARY_LOAD')
    # System-dynamic reduced profile cannot clear original static LGPL inputs.
    return {'modifiedRebuild':'PARTIAL','differentByteSourceBuild':'PASS','addonPng':'PASS','controlAbi':'PASS','distributedAbi':'PARTIAL' if result['abi']['missingComparedWithDistributed'] else 'PASS','staticInputs':'BLOCKED','fullRecipe':'BLOCKED','bitReproducible':'NOT_TESTED','binaryDistributionReadiness':'BLOCKED'}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True);p.add_argument('--result',type=Path,required=True);p.add_argument('--spec',type=Path,required=True);a=p.parse_args()
    try:
        r=verify_rebuild(json.loads(a.result.read_text()),a.root,json.loads(a.spec.read_text()));print(json.dumps(r));raise SystemExit(1)
    except (OSError,ValueError,KeyError,TypeError,zlib.error,subprocess.SubprocessError):
        print('{"modifiedRebuild":"BLOCKED","binaryDistributionReadiness":"BLOCKED","error":"INVALID_REBUILD_EVIDENCE"}');raise SystemExit(2)
