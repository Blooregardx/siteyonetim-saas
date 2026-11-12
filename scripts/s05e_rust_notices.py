"""Reacquire nine unresolved crates; recognize exact r-efi AUTHORS evidence.

PASS is source/notice acquisition under the MIT option, not legal approval or
evidence that a crate was compiled/linked into a particular image.
"""
import argparse
import json
from pathlib import Path
import tarfile
import tomllib

from collect_s05d_evidence import fetch
from s05e_source_protocol import physical, regular_tar, sha

ROOT = Path(__file__).resolve().parents[1]
AUTHORS = {
    '5.3.0': ('69cdb34c158ceb288df11e18b4bd39de994f6657d83847bdffdbd7f346754b0f', 'ff92bed461f50338dd703a9ba9aee496a425957873df1d91192776e4bdf5dda7'),
    '6.0.0': ('f8dcc9c7d52a811697d2151c701e0d08956f92b0e24136cf4cf27b57a6a0d9bf', 'd027e91dbc9cdbb2f1190068e498bd6b61cff022b6a032b191021ba658d96111'),
}


def verify_authors(record, root, cache):
    if record['name'] != 'r-efi' or record['version'] not in AUTHORS:
        raise ValueError('UNREVIEWED_NOTICE_RULE')
    crate_sha, notice_sha = AUTHORS[record['version']]
    if record['cargoChecksum'] != crate_sha or record['archiveSha256'] != crate_sha:
        raise ValueError('CRATE_CHECKSUM')
    key = 'r-efi-'+record['version']
    if record['archiveFile'] != key+'.crate' or record['notice']['member'] != key+'/AUTHORS' or record['notice']['sha256'] != notice_sha:
        raise ValueError('WRONG_VERSION_OR_MEMBER')
    crate = physical(cache, record['archiveFile'],crate_sha)
    regular_tar(crate,64*1024**2)
    notice = physical(root,record['notice']['file'],notice_sha).read_bytes()
    with tarfile.open(crate) as t:
        archived = t.extractfile(key+'/AUTHORS').read()
        declaration = tomllib.loads(t.extractfile(key+'/Cargo.toml').read().decode())['package']['license']
    if archived != notice or declaration != 'MIT OR Apache-2.0 OR LGPL-2.1-or-later':
        raise ValueError('NOTICE_NOT_FROM_CRATE')
    normalized = b' '.join(notice.split())
    for text in [b'Permission is hereby granted, free of charge', b'The above copyright notice and this permission notice',
                 b'THE SOFTWARE IS PROVIDED "AS IS"', b'Copyright (C) 2017-2023 Red Hat, Inc.', b'AUTHORS-MIT:']:
        if text not in normalized:
            raise ValueError('INCOMPLETE_ORIGINAL_NOTICE')
    if record.get('selectedLicenseForNoticeReview') != 'MIT' or record.get('legalApproval') is not False:
        raise ValueError('LICENSE_OPTION_OR_LEGAL_CLAIM')
    return {'decision':'PASS','scope':'Exact source archive and original AUTHORS/MIT notice acquisition only',
            'binaryDistributionReadiness':'BLOCKED','legalApproval':False}


def collect(out, cache):
    out.mkdir(parents=True,exist_ok=True);cache.mkdir(parents=True,exist_ok=True)
    old=json.loads((ROOT/'docs/evidence/s05d/rust-license-resolution.json').read_text())
    result=[]
    for r in old['records']:
        if r['decision']!='BLOCKED':
            continue
        key=r['name']+'-'+r['version']
        item={'name':r['name'],'version':r['version'],'decision':'BLOCKED','cargoChecksum':r['cargoChecksum'],
              'archiveFile':key+'.crate','archiveSha256':None,'licenseDeclaration':None,
              'compileLinkScope':'UNKNOWN — this acquisition does not add compilation/link evidence',
              'legalApproval':False,'reason':'No sufficient original applicable notice yet verified'}
        try:
            archive=cache/item['archiveFile']
            raw=fetch('https://static.crates.io/crates/'+r['name']+'/'+archive.name,archive,r['cargoChecksum'],25*1024**2)
            regular_tar(archive,64*1024**2)
            item['archiveSha256']=sha(raw)
            with tarfile.open(archive) as t:
                cargo=t.extractfile(key+'/Cargo.toml').read()
                item['licenseDeclaration']=tomllib.loads(cargo.decode())['package'].get('license')
                texts=[]
                for e in t:
                    if not e.isfile() or e.size>1024**2 or not e.name.endswith(('.rs','.md','/AUTHORS','Cargo.toml','Cargo.toml.orig')):
                        continue
                    data=t.extractfile(e).read()
                    if any(s in data.lower() for s in [b'copyright',b'license',b'permission is hereby']):
                        texts.append({'member':e.name,'sha256':sha(data),
                                      'licenseLines':[line[:300] for line in data.decode('utf8',errors='replace').splitlines()
                                                      if any(s in line.lower() for s in ['copyright','license','permission is hereby'])][:40]})
                item['inspectedTextEvidence']=texts
                if r['name']=='r-efi' and r['version'] in AUTHORS:
                    data=t.extractfile(key+'/AUTHORS').read();name=key+'-AUTHORS.txt'
                    (out/name).write_bytes(data)
                    item['notice']={'file':name,'member':key+'/AUTHORS','sha256':sha(data)}
                    item['selectedLicenseForNoticeReview']='MIT'
                    verify_authors(item,out,cache)
                    item['decision']='PASS'
                    item['reason']='Full original AUTHORS-MIT grant/disclaimer and copyright match exact crate; filename-only gap resolved'
        except (OSError,ValueError,KeyError,tarfile.TarError) as e:
            item['decision']='BLOCKED';item['failureType']=type(e).__name__
        result.append(item)
    report={'schemaVersion':1,'scope':'Nine S05-D unresolved records only; historical evidence unchanged',
            'records':result,'counts':{s:sum(r['decision']==s for r in result) for s in ['PASS','BLOCKED','UNKNOWN','NOT_APPLICABLE']},
            'legalApproval':False,'binaryDistributionReadiness':'BLOCKED'}
    (out/'rust-notice-resolution.json').write_text(json.dumps(report,indent=2)+'\n')
    return report


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',type=Path,required=True);p.add_argument('--cache',type=Path,required=True)
    a=p.parse_args()
    print(json.dumps(collect(a.out,a.cache)['counts']))
