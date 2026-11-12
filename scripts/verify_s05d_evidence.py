"""S05-D physical evidence checks; technical validity never grants distribution permission."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import tarfile
import tomllib

LOCK_SHA = 'e79e2a2735a0b5b151bb4133becd3008223fabedd34a8b787a872edab9854941'
RECIPE = 'ebb95f8add54eee8bed840e3fb587e4cbec857d7'
TARGET = 'x86_64-unknown-linux-gnu'
ROOT = Path(__file__).resolve().parents[1]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def physical(root, path, expected):
    p = PurePosixPath(path)
    if p.is_absolute() or '..' in p.parts or not re.fullmatch('[a-f0-9]{64}', expected or ''):
        raise ValueError('UNSAFE_PATH_OR_CHECKSUM')
    f = root / str(p)
    if not f.is_file() or f.is_symlink() or not f.resolve().is_relative_to(root.resolve()):
        raise ValueError('MISSING_PHYSICAL_EVIDENCE')
    if digest(f.read_bytes()) != expected:
        raise ValueError('PHYSICAL_HASH')
    return f


def safe_members(path):
    result = []
    total = 0
    with tarfile.open(path) as archive:
        for i, e in enumerate(archive):
            p = PurePosixPath(e.name)
            if p.is_absolute() or '..' in p.parts or e.issym() or e.islnk() or not (e.isfile() or e.isdir()):
                raise ValueError('ARCHIVE_PATH_OR_LINK')
            total += e.size
            if i >= 100000 or e.size > 128*1024**2 or total > 512*1024**2:
                raise ValueError('ARCHIVE_LIMIT')
            if e.isfile():
                result.append((e.name, e.size))
    if not result:
        raise ValueError('EMPTY_ARCHIVE')
    return result


def lock_changes(before, after):
    def entries(data):
        return {(p['name'], p['version'], p.get('source', 'path')): p for p in tomllib.loads(data)['package']}
    a, b = entries(before), entries(after)
    return {
        'added': [b[k] for k in sorted(b.keys()-a.keys())],
        'removed': [a[k] for k in sorted(a.keys()-b.keys())],
        'changed': [{'before': a[k], 'after': b[k]} for k in sorted(a.keys() & b.keys()) if a[k] != b[k]],
        'checksumChanges': [{'identity': list(k), 'before': a[k].get('checksum'), 'after': b[k].get('checksum')}
                            for k in sorted(a.keys() & b.keys()) if a[k].get('checksum') != b[k].get('checksum')]
    }


def verify_resolution(r, root):
    if r.get('schemaVersion') != 1 or r.get('recipeCommit') != RECIPE or r.get('target') != TARGET:
        raise ValueError('RECIPE_TARGET_SCHEMA')
    if r.get('inputLockSha256') != LOCK_SHA:
        raise ValueError('ORIGINAL_LOCK')
    original = ROOT/'docs/evidence/s05b/upstream/librsvg-Cargo.lock'
    if digest(original.read_bytes()) != LOCK_SHA:
        raise ValueError('HISTORICAL_LOCK_CHANGED')
    if r.get('status') == 'BLOCKED':
        if r.get('generatedLockSha256') is not None or r.get('generatedLockFile') is not None:
            raise ValueError('FABRICATED_GENERATED_LOCK')
        return {'generatedLock': 'BLOCKED', 'binaryDistributionReadiness': 'BLOCKED'}
    if r.get('status') != 'PARTIAL' or r.get('historicalUpstreamLock') is not False:
        raise ValueError('GENERATED_IS_NOT_HISTORICAL_ATTESTATION')
    toolchain = r['toolchain']
    if not toolchain.get('verified') or not toolchain.get('components'):
        raise ValueError('UNVERIFIED_TOOLCHAIN')
    for c in toolchain['components']:
        physical(root, c['file'], c['sha256'])
    for label in ['rustc', 'cargo']:
        f = physical(root, toolchain[label+'Log'], toolchain[label+'LogSha256'])
        if not f.read_text().strip():
            raise ValueError('EMPTY_TOOLCHAIN_OUTPUT')
    if '1.101.0-nightly' not in physical(root, toolchain['rustcLog'], toolchain['rustcLogSha256']).read_text() or '75a75c3e0' not in physical(root, toolchain['rustcLog'], toolchain['rustcLogSha256']).read_text():
        raise ValueError('WRONG_RUST_TOOLCHAIN')
    runs = r['attempts']
    if len(runs) != 2:
        raise ValueError('SECOND_RESOLUTION_MISSING')
    hashes = []
    for a in runs:
        if a['command'] != ['cargo', 'update', '--workspace'] or a['exitCode'] != 0 or a['beforeSha256'] != LOCK_SHA:
            raise ValueError('COMMAND_EXIT_OR_INPUT')
        lock = physical(root, a['lockFile'], a['afterSha256'])
        if a['changes'] != lock_changes(original.read_text(), lock.read_text()):
            raise ValueError('LOCK_DIFF')
        hashes.append(a['afterSha256'])
    if hashes[0] != hashes[1] or hashes[0] != r['generatedLockSha256']:
        raise ValueError('NONMATCHING_RESOLUTIONS')
    physical(root, r['generatedLockFile'], hashes[0])
    return {'generatedLock': 'PARTIAL', 'reason': 'Repeatable controlled resolution, not recovered original upstream lock',
            'binaryDistributionReadiness': 'BLOCKED'}


def verify_scope(scope):
    if scope.get('schemaVersion') != 1 or scope.get('target') != TARGET:
        raise ValueError('SCOPE_TARGET')
    allowed = {'RESOLVED', 'COMPILED', 'LINKED — EVIDENCED', 'NOT SELECTED — EVIDENCED', 'UNKNOWN'}
    if any(r.get('status') not in allowed for r in scope['records']):
        raise ValueError('SCOPE_STATE')
    counts = {s: sum(r['status'] == s for r in scope['records']) for s in sorted(allowed)}
    if counts != scope['counts']:
        raise ValueError('SCOPE_COUNTS')
    # This collector has no authenticated compiler-artifact/link-map capture.
    if any(counts[s] for s in ['COMPILED', 'LINKED — EVIDENCED', 'NOT SELECTED — EVIDENCED']):
        raise ValueError('UNIMPLEMENTED_COMPILE_LINK_PROOF')
    for r in scope['records']:
        if r['status'] == 'RESOLVED' and (not r.get('packageId') or not isinstance(r.get('features'), list) or not scope.get('metadataSha256')):
            raise ValueError('RESOLUTION_FIELDS')
    return {'scope': 'PARTIAL' if counts['RESOLVED'] else 'BLOCKED', 'counts': counts,
            'binaryDistributionReadiness': 'BLOCKED'}


def verify_notice(record, root):
    archive = physical(root, record['archiveFile'], record['archiveSha256'])
    if record['archiveSha256'] != record['cargoChecksum']:
        raise ValueError('CRATE_CHECKSUM')
    safe_members(archive)
    with tarfile.open(archive) as t:
        archived={e.name:t.extractfile(e).read() for e in t if e.isfile() and e.size<=2*1024**2}
    if record['decision'] == 'PASS':
        if not record.get('licenseDeclaration') or not record.get('evidence'):
            raise ValueError('LICENSE_EVIDENCE')
        for e in record['evidence']:
            raw = physical(root, e['file'], e['sha256']).read_bytes()
            if e['kind'] == 'source-header':
                member=archived.get(e.get('archiveMember',''))
                if member is None or not member.startswith(raw) or digest(member)!=e.get('completeSourceSha256'):
                    raise ValueError('HEADER_NOT_IN_EXACT_CRATE')
                if record['licenseDeclaration'] != 'MPL-2.0' or b'Mozilla Public License' not in raw or b'mozilla.org/MPL/2.0' not in raw:
                    raise ValueError('INVALID_MPL_HEADER')
            elif e['kind'] == 'upstream-notice':
                if not record.get('repositoryCommit') or not re.fullmatch('[a-f0-9]{40}', record['repositoryCommit']) or not record.get('matchedSourceFiles'):
                    raise ValueError('UNBOUND_UPSTREAM_NOTICE')
                # Acquisition is narrower than a legal finding about the whole package.
                if len(raw) < 100 or not any(x in raw for x in [b'Permission is hereby granted', b'Apache License', b'Mozilla Public License']):
                    raise ValueError('INVALID_LICENSE_TEXT')
            else:
                raise ValueError('UNKNOWN_NOTICE_PROTOCOL')
    elif record['decision'] not in ['BLOCKED', 'UNKNOWN', 'NOT_APPLICABLE']:
        raise ValueError('LICENSE_DECISION')
    return {'notice': record['decision'], 'legalApproval': False, 'binaryDistributionReadiness': 'BLOCKED'}


def verify_full_bundle(r):
    if r.get('profile') == 'reduced-feature PNG/JPEG' or r.get('claimedEquivalentToS05C'):
        raise ValueError('REDUCED_PROFILE_IS_NOT_FULL')
    # Full compiler/linker capture and original static bundle acquisition have not been implemented.
    # Refuse ALL asserted successes rather than trusting filled metadata.
    if r.get('status') != 'BLOCKED' or r.get('controlSha256') is not None or r.get('modifiedSha256') is not None:
        raise ValueError('FULL_BUILD_PROOF_UNAVAILABLE')
    if not r.get('blockers') or r.get('executed') is not False:
        raise ValueError('MISSING_HONEST_STAGE')
    return {'fullBundle': 'BLOCKED', 'staticInputs': 'BLOCKED', 'binaryDistributionReadiness': 'BLOCKED'}


def verify_source_package(manifest, root):
    if manifest.get('schemaVersion') != 1 or not re.fullmatch('sha256:[a-f0-9]{64}', manifest.get('imageConfigDigest', '')):
        raise ValueError('IMAGE_ID')
    sbom = json.loads(physical(root, manifest['sbomFile'], manifest['sbomSha256']).read_text())
    if sbom['source']['metadata']['imageID'] != manifest['imageConfigDigest']:
        raise ValueError('FOREIGN_SBOM')
    for category in ['sources', 'notices', 'buildScripts', 'staticInputs']:
        if not manifest.get(category):
            raise ValueError('MISSING_'+category)
        for f in manifest[category]:
            p = physical(root, f['file'], f['sha256'])
            if category == 'sources':
                safe_members(p)
            if category == 'notices' and (p.stat().st_size < 100 or not f.get('license')):
                raise ValueError('LICENSE_NOTICE')
    if manifest.get('retentionMethod') == 'github-actions-artifact' or manifest.get('durabilityClaim') == 'guaranteed':
        raise ValueError('ARTIFACT_IS_NOT_DURABLE_GUARANTEE')
    # Physical synthetic packages can exercise inventory integrity, never legal approval.
    return {'technicalInventory': 'VALIDATED', 'legalApproval': False,
            'durableSourceProvision': 'DESIGN READY', 'binaryDistributionReadiness': 'BLOCKED'}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, required=True)
    p.add_argument('--resolution', type=Path, required=True)
    a = p.parse_args()
    try:
        print(json.dumps(verify_resolution(json.loads(a.resolution.read_text()), a.root)))
        raise SystemExit(1)  # No distribution clearance, including technically valid PARTIAL.
    except (OSError, ValueError, KeyError, TypeError, AttributeError, IndexError, tarfile.TarError):
        print('{"error":"INVALID_S05D_EVIDENCE","binaryDistributionReadiness":"BLOCKED"}')
        raise SystemExit(2)
