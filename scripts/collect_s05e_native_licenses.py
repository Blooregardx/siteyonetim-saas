"""Acquire exact-version original texts, never infer a whole-bundle SPDX grant."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import tarfile

from s05e_source_protocol import file_sha
from run_s05e_native import NATIVE_MANIFEST_SHA

ROOT=Path(__file__).resolve().parents[1]
FILES={
    'glib':['glib/gmain.c','gobject/gobject.c'],
    'pango':['COPYING','pango/pango-layout.c'],
    'cairo':['COPYING','COPYING-LGPL-2.1','COPYING-MPL-1.1','src/cairo.c'],
    'heif':['COPYING','libheif/api/libheif/heif.cc'],
    'rsvg':['COPYING.LIB','Cargo.toml'],
    'vips':['LICENSE','libvips/iofuncs/init.c'],
}


def collect(inputs,out):
    manifest=ROOT/'docs/evidence/s05b/libvips-source-manifest.json'
    if file_sha(manifest)!=NATIVE_MANIFEST_SHA:raise ValueError('HISTORICAL_MANIFEST')
    data=json.loads(manifest.read_text());rows=[]
    for component in data['dependencies']:
        name=component['name']
        if name not in FILES:continue
        archive=inputs/'sources'/(name+'.tar')
        if file_sha(archive)!=component['sha256']:raise ValueError('SOURCE_ARCHIVE_HASH')
        evidence=[];found=set()
        with tarfile.open(archive) as t:
            for e in t:
                if not e.isfile():continue
                p=PurePosixPath(e.name)
                relative='/'.join(p.parts[1:])
                reuse=name=='glib' and relative.startswith('LICENSES/') and relative.endswith('.txt')
                if relative not in FILES[name] and not reuse:continue
                if relative in found or '..' in p.parts or e.size>1024**2:raise ValueError('NOTICE_MEMBER')
                found.add(relative);raw=t.extractfile(e).read();complete=hashlib.sha256(raw).hexdigest()
                role='original-license-text'
                if relative.endswith(('.c','.cc')):
                    # Preserve the complete leading source notice/comments.
                    end=raw.find(b'#include')
                    if end<0 or end>16000:raise ValueError('HEADER_BOUNDARY')
                    raw=raw[:end];role='original-source-header'
                elif relative.endswith('Cargo.toml'):role='license-declaration-only'
                dest=out/'licenses'/name/(relative+'.header.txt' if role=='original-source-header' else relative)
                dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
                evidence.append({'archiveMember':e.name,'completeSourceFileSha256':complete,'file':str(dest.relative_to(out)),
                                 'sha256':file_sha(dest),'role':role})
        if not set(FILES[name])<=found:raise ValueError('MISSING_ORIGINAL_NOTICE')
        rows.append({'name':name,'version':component['version'],'sourceArchiveSha256':component['sha256'],'sourceUrl':component['url'],
                     'originalEvidence':evidence,'upstreamBundleStatement':component.get('upstreamLicenseStatement'),
                     'evidenceAcquisition':'PASS','complianceDecision':'UNKNOWN','legalReview':'REQUIRES LEGAL REVIEW — per-file compiled/static scope and selected license version',
                     'note':'GLib docs/reference/COPYING is not substituted for core REUSE license texts' if name=='glib' else 'Original file terms are distinct from the npm bundle license expression'})
    result={'schemaVersion':1,'components':rows,'legalApproval':False,'binaryDistributionReadiness':'BLOCKED'}
    (out/'native-license-evidence.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--inputs',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();r=collect(a.inputs,a.out);print('Exact source evidence acquired:',len(r['components']),'components; legal decisions UNKNOWN')
