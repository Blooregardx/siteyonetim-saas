"""Fail-closed review of Syft JSON tied to a locally inspected image ID.
Evidence is a maintainer-reviewed artifact, never inferred from lock metadata.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path


def evaluate(sbom, image_id, evidence):
    if not re.fullmatch(r'sha256:[a-f0-9]{64}', image_id):
        raise ValueError('INVALID_IMAGE_ID')
    if sbom.get('source', {}).get('type') != 'image' or sbom['source'].get('metadata', {}).get('imageID') != image_id:
        raise ValueError('SBOM_IMAGE_MISMATCH')
    artifacts = sbom.get('artifacts', [])
    if not artifacts:
        raise ValueError('EMPTY_SBOM')
    rows = []
    for item in artifacts:
        key = item['id']
        proof = evidence.get(key, {})
        licenses = item.get('licenses', [])
        known = bool(licenses) and all(x.get('spdxExpression') and not re.search(r'LicenseRef|UNKNOWN|NOASSERTION|NONE', x['spdxExpression']) for x in licenses)
        exact = isinstance(item.get('version'), str) and bool(item['version'].strip()) and proof.get('name') == item.get('name') and proof.get('version') == item.get('version') and proof.get('imageID') == image_id
        # All applicability choices require explicit review, including permissive licenses.
        required = ['upstream', 'binarySourceMatch', 'noticeEvidence', 'sourceProvision', 'relinking', 'reviewer']
        complete = exact and all(isinstance(proof.get(k), str) and proof[k].strip() for k in required)
        if item.get('name') == 'sharp' or item.get('name', '').startswith('@img/sharp'):
            # S05-B source/relinking manifest remains incomplete; text fields cannot clear native packages.
            complete = False
        status = 'UNKNOWN' if not known else ('PASS' if complete and proof.get('decision') == 'PASS' else 'BLOCKED')
        native_trace={}
        if item.get('name') == 'sharp' or item.get('name','').startswith('@img/sharp'):
            manifest=Path(__file__).resolve().parents[1]/'docs/evidence/s05b/libvips-source-manifest.json'
            rebuild_manifest=Path(__file__).resolve().parents[1]/'docs/evidence/s05c/rebuild-manifest.json'
            native_trace={'s05cManifestSha256':hashlib.sha256(rebuild_manifest.read_bytes()).hexdigest() if rebuild_manifest.is_file() else None,'s05cGeneralDistribution':'BLOCKED','sourceManifest':'docs/evidence/s05b/libvips-source-manifest.json','sourceManifestSha256':hashlib.sha256(manifest.read_bytes()).hexdigest() if manifest.is_file() else None,'sourceDecision':'BLOCKED','maintainerApprovalRequired':True}
        rows.append({**native_trace,'id': key, 'name': item.get('name'), 'version': item.get('version'), 'status': status})
    return {'imageID': image_id, 'readiness': 'PASS' if all(r['status'] == 'PASS' for r in rows) else 'BLOCKED', 'counts': {s: sum(r['status'] == s for r in rows) for s in ['PASS', 'BLOCKED', 'UNKNOWN', 'NOT_APPLICABLE']}, 'components': rows}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--sbom', type=Path, required=True)
    p.add_argument('--image-id', required=True)
    p.add_argument('--evidence', type=Path, required=True)
    a = p.parse_args()
    try:
        result = evaluate(json.loads(a.sbom.read_text()), a.image_id, json.loads(a.evidence.read_text()))
        print(json.dumps(result))
        raise SystemExit(0 if result['readiness'] == 'PASS' else 1)
    except (ValueError, KeyError, TypeError, OSError):
        print('{"readiness":"BLOCKED","error":"INVALID_OR_MISSING_EVIDENCE"}')
        raise SystemExit(2)
