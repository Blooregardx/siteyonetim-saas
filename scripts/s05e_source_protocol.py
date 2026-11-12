"""Offline prepublication integrity/restore protocol. Never grants legal clearance.

Only synthetic fixtures may be published as CI test artifacts by this module.
An OCI image layout must already exist locally; no registry or remote commands.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import tarfile

from verify_s05d_evidence import archive_members, compiled_shape

LIMIT = 1024**3
ROLES = {'source', 'patch', 'notice', 'build-script', 'toolchain-source',
         'cargo-lock', 'compile-log', 'link-map', 'static-archive', 'object', 'relink-instructions'}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def file_sha(path):
    if not path.is_file() or path.is_symlink() or path.stat().st_size > LIMIT:
        raise ValueError('MISSING_OR_OVERSIZED_FILE')
    h = hashlib.sha256()
    with path.open('rb') as f:
        while chunk := f.read(1024*1024):
            h.update(chunk)
    return h.hexdigest()


def physical(root, name, expected):
    p = relative(name)
    if not re.fullmatch('[a-f0-9]{64}', expected or ''):
        raise ValueError('CHECKSUM_FORMAT')
    for n in range(1, len(p.parts)+1):
        if (root/Path(*p.parts[:n])).is_symlink():
            raise ValueError('SYMLINK_INPUT')
    f = root/str(p)
    if not f.resolve().is_relative_to(root.resolve()) or file_sha(f) != expected:
        raise ValueError('PHYSICAL_HASH')
    return f


def relative(name):
    p = PurePosixPath(name)
    if not name or p.is_absolute() or '..' in p.parts or str(p) != name or '\\' in name:
        raise ValueError('UNSAFE_PATH')
    return p


def strict_json(raw):
    if len(raw) > 4*1024**2:
        raise ValueError('JSON_LIMIT')
    def pairs(items):
        result = {}
        for k, v in items:
            if k in result:
                raise ValueError('DUPLICATE_JSON_KEY')
            result[k] = v
        return result
    return json.loads(raw, object_pairs_hook=pairs)


def read_json(path):
    if path.stat().st_size>4*1024**2:raise ValueError('JSON_LIMIT')
    return strict_json(path.read_bytes())


def regular_tar(path, maximum=LIMIT):
    """Inspect without extracting, following links or trusting declared sizes."""
    names = set()
    total = 0
    records = {}
    with tarfile.open(path, 'r:*') as t:
        for i, e in enumerate(t):
            relative(e.name)
            if e.name in names or i >= 100000:
                raise ValueError('DUPLICATE_OR_EXCESS_MEMBERS')
            names.add(e.name)
            if e.isdir():
                continue
            if not e.isfile() or e.size < 0:
                raise ValueError('ARCHIVE_LINK_OR_SPECIAL')
            total += e.size
            if total > maximum:
                raise ValueError('ARCHIVE_LIMIT')
            h = hashlib.sha256()
            count = 0
            with t.extractfile(e) as f:
                while chunk := f.read(1024*1024):
                    count += len(chunk)
                    if count > e.size:
                        raise ValueError('ARCHIVE_SIZE')
                    h.update(chunk)
            if count != e.size:
                raise ValueError('TRUNCATED_ARCHIVE')
            records[e.name] = {'sha256': h.hexdigest(), 'size': count}
    if not records:
        raise ValueError('EMPTY_ARCHIVE')
    return records


def blob(root, descriptor):
    d = descriptor['digest']
    if not re.fullmatch('sha256:[a-f0-9]{64}', d) or type(descriptor['size']) is not int:
        raise ValueError('OCI_DESCRIPTOR')
    path = physical(root, 'blobs/sha256/'+d[7:], d[7:])
    if path.stat().st_size != descriptor['size'] or path.stat().st_size > LIMIT:
        raise ValueError('OCI_SIZE')
    return path


def image_binding(root, m):
    layout = root / str(relative(m['ociLayout']))
    if layout.is_symlink() or not layout.resolve().is_relative_to(root.resolve()):
        raise ValueError('OCI_LAYOUT_PATH')
    index = read_json(physical(layout, 'index.json', m['ociIndexSha256']))
    if len(index['manifests']) != 1 or index['manifests'][0]['digest'] != m['imageManifestDigest']:
        raise ValueError('FOREIGN_IMAGE')
    manifest = read_json(blob(layout, index['manifests'][0]))
    if manifest['config']['digest'] != m['imageConfigDigest']:
        raise ValueError('FOREIGN_CONFIG')
    config = read_json(blob(layout, manifest['config']))
    if config['architecture'] != 'amd64' or config['os'] != 'linux':
        raise ValueError('WRONG_PLATFORM')
    target = str(relative(m['binaryPath']))
    actual = None
    diff_ids = []
    for layer in manifest['layers']:
        path = blob(layout, layer)
        if layer['mediaType'] != 'application/vnd.oci.image.layer.v1.tar':
            raise ValueError('UNSUPPORTED_LAYER_ENCODING')
        # Uncompressed OCI only: descriptor digest is also the diff ID.
        diff_ids.append(layer['digest'])
        seen = set()
        replacement = None
        removed = False
        with tarfile.open(path, 'r:') as t:
            total = 0
            for i, e in enumerate(t):
                name = str(relative(e.name))
                if name in seen or i >= 100000:
                    raise ValueError('OCI_DUPLICATE_MEMBER')
                seen.add(name)
                total += e.size
                if total > LIMIT:
                    raise ValueError('OCI_LAYER_LIMIT')
                parent = str(PurePosixPath(name).parent)
                basename = PurePosixPath(name).name
                prefix = '' if parent == '.' else parent+'/'
                if basename.startswith('.wh.') and (not e.isfile() or e.size!=0):
                    raise ValueError('OCI_WHITEOUT_SHAPE')
                if basename == '.wh..wh..opq' and target.startswith(prefix):
                    removed = True
                elif basename.startswith('.wh.'):
                    deleted = prefix+basename[4:]
                    if target == deleted or target.startswith(deleted+'/'):
                        removed = True
                if target == name or target.startswith(name+'/'):
                    if e.issym() or e.islnk():
                        raise ValueError('OCI_BINARY_ALIAS_UNSUPPORTED')
                    if target.startswith(name+'/') and not e.isdir():
                        raise ValueError('OCI_BINARY_ANCESTOR_NOT_DIRECTORY')
                if name == target:
                    if not e.isfile() or e.size > 256*1024**2:
                        raise ValueError('OCI_BINARY_NOT_REGULAR')
                    raw = t.extractfile(e).read()
                    if len(raw) != e.size or not compiled_shape(raw):
                        raise ValueError('OCI_BINARY_SHAPE')
                    replacement = sha(raw)
        if removed:
            actual = None
        if replacement is not None:
            actual = replacement
    if config['rootfs']['diff_ids'] != diff_ids or actual != m['binarySha256']:
        raise ValueError('BINARY_OR_LAYER_MISMATCH')


def verify(root, expected_index):
    manifest_path = physical(root, 'source-index.json', expected_index)
    m = read_json(manifest_path)
    if m.get('schemaVersion') != 1 or m.get('purpose') not in {'SYNTHETIC_PROTOCOL_TEST', 'PREPUBLICATION_CANDIDATE'}:
        raise ValueError('SCHEMA_OR_PURPOSE')
    image_binding(root, m)
    sbom = read_json(physical(root, m['sbom']['file'], m['sbom']['sha256']))
    if sbom['source']['type'] != 'image' or sbom['source']['metadata']['imageID'] != m['imageConfigDigest']:
        raise ValueError('FOREIGN_SBOM')
    inventory = m['inventory']
    if {r['role'] for r in inventory} != ROLES or len({r['file'] for r in inventory}) != len(inventory):
        raise ValueError('MISSING_OR_DUPLICATE_INPUTS')
    for r in inventory:
        p = physical(root, r['file'], r['sha256'])
        if not p.stat().st_size:
            raise ValueError('EMPTY_INPUT')
        if r['role'] in {'source', 'toolchain-source'}:
            regular_tar(p)
        if r['role'] == 'static-archive' and not archive_members(p.read_bytes()):
            raise ValueError('INVALID_STATIC_ARCHIVE')
        if r['role'] == 'object' and (p.read_bytes()[:4] != b'\x7fELF' or not compiled_shape(p.read_bytes())):
            raise ValueError('INVALID_OBJECT')
        # Content hashes prove inventory integrity, never legal/notice sufficiency.
    if m.get('legalApproval') is not False or m.get('durabilityGuarantee') is not False:
        raise ValueError('AUTOMATIC_LEGAL_OR_DURABILITY_PASS')
    return {'protocolIntegrity': 'PASS', 'purpose': m['purpose'],
            'legalApproval': False, 'durableSourceProvision': 'PARTIAL',
            'binaryDistributionReadiness': 'BLOCKED', 'sourceIndexSha256': expected_index}


def restore(bundle, expected_bundle, expected_index, destination):
    if file_sha(bundle) != expected_bundle:
        raise ValueError('RESTORE_BUNDLE_HASH')
    records = regular_tar(bundle)
    if 'source-index.json' not in records or records['source-index.json']['sha256'] != expected_index:
        raise ValueError('RESTORE_INDEX_HASH')
    if destination.exists():
        raise ValueError('RESTORE_REQUIRES_EMPTY_NEW_DIRECTORY')
    destination.mkdir(parents=True)
    try:
        with tarfile.open(bundle) as t:
            seen=set()
            for e in t:
                relative(e.name)
                if e.isdir():
                    continue
                if not e.isfile() or e.name in seen or e.name not in records or records[e.name]['size']!=e.size:
                    raise ValueError('RESTORE_ARCHIVE_CHANGED')
                seen.add(e.name)
                out = destination/e.name
                out.parent.mkdir(parents=True, exist_ok=True)
                with t.extractfile(e) as source, out.open('xb') as dest:
                    shutil.copyfileobj(source, dest)
                if file_sha(out)!=records[e.name]['sha256']:raise ValueError('RESTORE_FILE_CHANGED')
            if seen!=set(records):raise ValueError('RESTORE_MEMBERS_CHANGED')
        return verify(destination, expected_index)
    except Exception:
        shutil.rmtree(destination)
        raise


def fixture(root):
    """Deliberately synthetic bytes; they cannot be mistaken for real libvips."""
    root.mkdir(parents=True, exist_ok=False)
    def put(name, raw):
        p = root/name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(raw)
        return {'file': name, 'sha256': sha(raw)}
    def tar_bytes(name, raw):
        b = io.BytesIO()
        with tarfile.open(fileobj=b, mode='w') as t:
            e = tarfile.TarInfo(name);e.size=len(raw);t.addfile(e, io.BytesIO(raw))
        return b.getvalue()
    elf = b'\x7fELF\x02\x01'+b'\0'*12+b'\x3e\0'+b'\0'*44+b'SYNTHETIC-NOT-LIBVIPS'
    layer = tar_bytes('usr/lib/libsynthetic.so', elf)
    def descriptor(raw, media):
        h = sha(raw);put('oci/blobs/sha256/'+h, raw)
        return {'digest': 'sha256:'+h, 'size': len(raw), 'mediaType': media}
    ld = descriptor(layer, 'application/vnd.oci.image.layer.v1.tar')
    cd = descriptor(json.dumps({'architecture': 'amd64', 'os': 'linux', 'rootfs': {'type':'layers','diff_ids':[ld['digest']]}}).encode(), 'application/vnd.oci.image.config.v1+json')
    md = descriptor(json.dumps({'schemaVersion':2, 'config':cd, 'layers':[ld]}).encode(), 'application/vnd.oci.image.manifest.v1+json')
    idx = put('oci/index.json', json.dumps({'schemaVersion':2,'manifests':[md]}).encode())
    put('oci/oci-layout', b'{"imageLayoutVersion":"1.0.0"}')
    sbom = put('sbom.json', json.dumps({'source':{'type':'image','metadata':{'imageID':cd['digest']}},'artifacts':[]}).encode())
    inv = []
    ar = b'!<arch>\n'+b'fixture.o/'.ljust(16)+b'0'.ljust(12)+b'0'.ljust(6)+b'0'.ljust(6)+b'100644'.ljust(8)+str(len(elf)).encode().ljust(10)+b'`\n'+elf+(b'\n' if len(elf)%2 else b'')
    for role in sorted(ROLES):
        raw = tar_bytes('source.txt',b'SYNTHETIC source') if role in {'source','toolchain-source'} else ar if role=='static-archive' else elf if role=='object' else ('SYNTHETIC '+role+'; not real compliance evidence\n').encode()
        inv.append({'role':role, **put('inputs/'+role,raw)})
    m = {'schemaVersion':1,'purpose':'SYNTHETIC_PROTOCOL_TEST','ociLayout':'oci','ociIndexSha256':idx['sha256'],
         'imageManifestDigest':md['digest'],'imageConfigDigest':cd['digest'],'binaryPath':'usr/lib/libsynthetic.so',
         'binarySha256':sha(elf),'sbom':sbom,'inventory':inv,'legalApproval':False,'durabilityGuarantee':False}
    return put('source-index.json',json.dumps(m,indent=2).encode())['sha256']


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command', required=True)
    f = sub.add_parser('fixture');f.add_argument('root',type=Path)
    v = sub.add_parser('verify');v.add_argument('root',type=Path);v.add_argument('index_sha256')
    r = sub.add_parser('restore');r.add_argument('bundle',type=Path);r.add_argument('bundle_sha256');r.add_argument('index_sha256');r.add_argument('destination',type=Path)
    args = p.parse_args()
    try:
        if args.command == 'fixture':
            h = fixture(args.root);result = verify(args.root,h)
        elif args.command == 'verify':
            result = verify(args.root,args.index_sha256)
        else:
            result = restore(args.bundle,args.bundle_sha256,args.index_sha256,args.destination)
        print(json.dumps(result,sort_keys=True))
    except (OSError, ValueError, KeyError, TypeError, tarfile.TarError):
        print('{"protocolIntegrity":"BLOCKED","binaryDistributionReadiness":"BLOCKED"}')
        return 2
    return 0  # Protocol integrity only; result always retains distribution BLOCKED.


if __name__ == '__main__':
    raise SystemExit(main())
