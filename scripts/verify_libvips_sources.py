"""Verify pinned libvips evidence bytes. Technical checks do not grant legal approval."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import tarfile

BUILD_COMMIT='ebb95f8add54eee8bed840e3fb587e4cbec857d7'
VIPS_COMMIT='24ad4d042940e6bf99a68871ba886ca8847c9c82'
SHARP_COMMIT='51a990faa26ade5586a4934ac9673c98d8893326'
BUILD_ANCHORS={'upstream/versions.properties': 'c0ad634f7c2ac8994f831dd0bcb5c60043db7ba4ddd9cc2dbc3703b15f4ec7e5', 'upstream/THIRD-PARTY-NOTICES.md': '6f0d5086e3bcbee12bcdacf5878b31d1104002aeecaeb241d3fff466108082fe', 'upstream/LICENSE': 'b40930bbcf80744c86c46a12bc9da056641d722716c378f5659b9e555ef833e1', 'upstream/build.sh': 'f32e344b1355b6bcf3836e7f25e2c2de7f25eefeb8c96d02711ad3fcea487488', 'upstream/build/posix.sh': '333031b3b49bf1a16d0b9d6812d98f67c404218932ef8c0b389388524a524b36', 'upstream/platforms/linuxmusl-x64/meson.ini': '9b9ac8223114dbe407673195f64c075468f394426c5bacbcc233b9048830debf', 'upstream/platforms/linuxmusl-x64/Toolchain.cmake': 'eaf601b65260c4ff1991063f248346d51fe6751e84f7dc83b7fcd3fd4658cad6', 'upstream/platforms/linuxmusl-x64/Dockerfile': '547187f4c281e8aba140047a4cd1fe1c056004b7ce45495df561705f6561de0a', 'upstream/platforms/linux-x64/meson.ini': '0d85749d3921b1877e3d68615265a7f158856bf615ab56d6beb75d71a7fd0a41', 'upstream/platforms/linux-x64/x86_64-linux-gnu-pkgconf': 'c256bf8fcad1bcee36872c22c007d41980ace7cfe74072af130d336ddd92f61e', 'upstream/platforms/linux-x64/Toolchain.cmake': 'eaf601b65260c4ff1991063f248346d51fe6751e84f7dc83b7fcd3fd4658cad6', 'upstream/platforms/linux-x64/Dockerfile': '1e8bc3981c8f1718cd99ea4fcd6d2e511afb9969f2fe3e0d2dc1ebf5a338a6e3', 'upstream/.github/workflows/ci.yml': '0a0c730ee600f2b95298ead170a84e0b7933a8878db0664c9858321f416cda7d'}
SHARP_BINDING_ANCHOR='aa0750bba07e0de556ccdf1463e148a21e373ea43ac0ee622d23ad287890e658'
HEX=re.compile(r'[a-f0-9]{64}')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def local(root, name):
    p=Path(name)
    if p.is_absolute() or '..' in p.parts:raise ValueError('UNSAFE_EVIDENCE_PATH')
    result=root/p
    if result.is_symlink() or not result.is_file():raise ValueError('MISSING_EVIDENCE_FILE')
    if not result.resolve().is_relative_to(root.resolve()):raise ValueError('UNSAFE_EVIDENCE_PATH')
    return result


def verify(manifest, root, image=None, image_id=None, cache=None):
    errors=[]
    checked_archives=0
    if manifest.get('schemaVersion')!=1:raise ValueError('SCHEMA')
    if manifest['package']['commit']!=BUILD_COMMIT or manifest['package']['version']!='1.3.4':raise ValueError('BUILD_COMMIT_VERSION')
    if manifest['libvips']!={'version':'8.18.7','commit':VIPS_COMMIT}:raise ValueError('SOURCE_COMMIT_VERSION')
    if manifest['sharp']!={'version':'0.35.5','commit':SHARP_COMMIT}:raise ValueError('SHARP_COMMIT_VERSION')
    if manifest['buildFiles']!=BUILD_ANCHORS:raise ValueError('BUILD_ANCHORS')
    sharp=manifest['sharpSource']
    if sharp['url']!='https://codeload.github.com/lovell/sharp/tar.gz/'+SHARP_COMMIT or not HEX.fullmatch(sharp['sha256']):raise ValueError('SHARP_ARCHIVE')
    binding=sharp['bindingRecipe']
    if binding['sha256']!=SHARP_BINDING_ANCHOR or sha(local(root,binding['path']))!=SHARP_BINDING_ANCHOR:raise ValueError('SHARP_BUILD_RECIPE')
    for notice in sharp['notices']:
        if sha(local(root,notice['evidenceFile']))!=notice['sha256']:raise ValueError('SHARP_NOTICE')
    if not sharp['notices']:raise ValueError('SHARP_NOTICE_MISSING')
    if cache is not None:
        if sha(local(cache,'sharp.tar'))!=sharp['sha256']:raise ValueError('SHARP_ARCHIVE_HASH')
        if sha(local(cache.parent,'commit.tar.gz'))!=manifest['buildArchive']['sha256']:raise ValueError('BUILD_ARCHIVE_HASH')
        from research_libvips_sources import inspect_archive
        sharp_notices={n['path']:n['sha256'] for n in inspect_archive(local(cache,'sharp.tar'))}
        if any(sharp_notices.get(n['path'])!=n['sha256'] for n in sharp['notices']):raise ValueError('SHARP_ARCHIVE_NOTICE_MATCH')
        inspect_archive(local(cache.parent,'commit.tar.gz'))
    for name,expected in manifest['buildFiles'].items():
        if not HEX.fullmatch(expected) or sha(local(root,name))!=expected:raise ValueError('BUILD_FILE_HASH')
    versions=dict(re.findall(r'^VERSION_(\w+)=(.+)$',local(root,'upstream/versions.properties').read_text(),re.M))
    expected={k.lower().replace('_','-'):v for k,v in versions.items()}
    records=manifest['dependencies']
    if {r['name']:r['version'] for r in records}!=expected or len(records)!=len(expected):raise ValueError('DEPENDENCY_SET_VERSION')
    for record in records:
        if cache is not None:
            from research_libvips_sources import inspect_archive
            archive=local(cache,record['name']+'.tar')
            if sha(archive)!=record.get('sha256'):raise ValueError('SOURCE_ARCHIVE_HASH')
            actual={n['path']:n['sha256'] for n in inspect_archive(archive)}
            if any(actual.get(n['path'])!=n['sha256'] for n in record.get('notices',[])):raise ValueError('ARCHIVE_NOTICE_MATCH')
            checked_archives+=1
        if record.get('archiveStatus')!='PASS':errors.append(record['name']+':SOURCE_ARCHIVE_MISSING')
        if not HEX.fullmatch(record.get('sha256','')):
            if record.get('archiveStatus')=='PASS':raise ValueError('SOURCE_CHECKSUM_INVALID')
            errors.append(record['name']+':SOURCE_CHECKSUM_MISSING')
        if not record.get('notices'):errors.append(record['name']+':NOTICE_MISSING')
        for notice in record.get('notices',[]):
            if sha(local(root,notice['evidenceFile']))!=notice['sha256']:raise ValueError('NOTICE_HASH')
        # Same version is not authenticated binary build provenance.
        if record.get('sourceMatch')!='VERIFIED':errors.append(record['name']+':BINARY_SOURCE_PROVENANCE_MISSING')
    for patch in manifest['patches']:
        if patch.get('status')!='PASS':errors.append('PATCH_MISSING')
        elif not HEX.fullmatch(patch.get('sha256','')) or sha(local(root,patch['evidenceFile']))!=patch['sha256']:raise ValueError('PATCH_HASH')
    if image is not None:
        if not image_id or not re.fullmatch(r'sha256:[a-f0-9]{64}',image_id) or image.get('imageID')!=image_id:raise ValueError('IMAGE_ID')
        if image.get('sharpVersion')!='0.35.5':raise ValueError('IMAGE_SHARP_VERSION')
        platforms={b['platform']:b for b in image['binaries']}
        if set(platforms)!={'linux-x64','linuxmusl-x64'}:raise ValueError('PLATFORM_SET')
        for platform,binary in platforms.items():
            if binary['package']!='@img/sharp-libvips-'+platform or binary['packageVersion']!='1.3.4':raise ValueError('PLATFORM_PACKAGE')
            if binary['elf']!={'magic':'7f454c46','class':2,'machine':62}:raise ValueError('ELF_ARCH')
            if not HEX.fullmatch(binary['sha256']):raise ValueError('BINARY_HASH')
            if not any(b.get('platform')==platform and b.get('sha256')==binary['sha256'] and b.get('imageID')==image_id for b in manifest.get('images',[])):errors.append(platform+':UNREVIEWED_BINARY_BINDING')
            if binary['versions']['vips']!='8.18.7':raise ValueError('IMAGE_VIPS_VERSION')
            if any(binary['versions'].get(r['name'])!=r['version'] for r in records):raise ValueError('IMAGE_DEPENDENCY_VERSION')
        if not (image.get('relocation',{}).get('alternativeLoaded') and not image.get('relocation',{}).get('originalLoaded') and image.get('relocation',{}).get('imageProduced')):errors.append('ALTERNATE_LOAD_NOT_PROVEN')
    else:errors.append('FRESH_IMAGE_EVIDENCE_REQUIRED')
    errors.extend(manifest.get('gaps',[]))
    if manifest.get('rustDependencies'):errors.append('RUST_TRANSITIVE_SOURCES_AND_NOTICES_UNVERIFIED')
    errors.append('MODIFIED_LIBRARY_AND_STATIC_SUBLIBRARY_REBUILD_NOT_PROVEN')
    # Explicit human approval cannot be replaced by populated evidence strings.
    if manifest.get('maintainerReview',{}).get('approved') is not True:errors.append('MAINTAINER_REVIEW_REQUIRED')
    return {'archivesReverified':checked_archives,'sourceEvidence':'PARTIAL','binarySourceEvidence':'BLOCKED','relinkingEvidence':'PARTIAL' if image and image.get('relocation',{}).get('alternativeLoaded') and not image.get('relocation',{}).get('originalLoaded') and image.get('relocation',{}).get('imageProduced') else 'BLOCKED','binaryDistributionReadiness':'BLOCKED','errors':errors}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--manifest',type=Path,required=True);p.add_argument('--root',type=Path,required=True);p.add_argument('--image',type=Path);p.add_argument('--image-id');p.add_argument('--cache',type=Path);a=p.parse_args()
    try:
        result=verify(json.loads(a.manifest.read_text()),a.root,json.loads(a.image.read_text()) if a.image else None,a.image_id,a.cache)
        print(json.dumps(result));raise SystemExit(1)
    except (OSError,ValueError,KeyError,TypeError,tarfile.TarError):
        print('{"binaryDistributionReadiness":"BLOCKED","error":"INVALID_LIBVIPS_EVIDENCE"}');raise SystemExit(2)
