"""Acquire checksum-bound candidate Rust sources; never equate resolution with compilation."""
import concurrent.futures
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tarfile
import tomllib
from research_libvips_sources import inspect_archive

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/evidence/s05c'
CACHE=Path('/tmp/s05c-crates')


def compilation_pairs(observations):
    # The archived excerpt is bounded by Project name:librsvg and its cbuild command.
    if observations['commit']!='ebb95f8add54eee8bed840e3fb587e4cbec857d7' or observations['job']!=108609814156:raise ValueError('UPSTREAM_SCOPE')
    pairs={}
    for line in observations['compiledLines']:
        if re.search(r'#\d+\s+\d+\.',line):raise ValueError('TOOLCHAIN_INSTALL_IS_NOT_LIBRSVG')
        match=re.search(r'Compiling ([\w-]+) v([^\s]+)',line)
        if match:pairs.setdefault(match.groups(),[]).append(line)
    return pairs


def acquire(record):
    r=dict(record)
    if not r['source'].startswith('registry+'):
        return {**r,'decision':'UNKNOWN','reason':'Git/path requires exact revision/tree and local-source evidence; not fetched as registry'}
    if not re.fullmatch(r'[A-Za-z0-9_-]+',r['name']) or not re.fullmatch(r'[0-9][A-Za-z0-9.+_-]*',r['version']):return {**r,'decision':'BLOCKED','reason':'INVALID_PACKAGE_PATH'}
    key=r['name']+'-'+r['version'];path=CACHE/(key+'.crate')
    try:
        if path.is_symlink() or CACHE.is_symlink():raise ValueError('CACHE_SYMLINK')
        if sum(p.stat().st_size for p in CACHE.glob('*.crate') if p.is_file())>400*1024**2:raise ValueError('SOURCE_CACHE_RESOURCE_LIMIT')
        url='https://static.crates.io/crates/'+r['name']+'/'+key+'.crate'
        expected=r.get('lockChecksum')
        if not expected:
            meta=CACHE/(key+'.json')
            subprocess.run(['curl','--proto','=https','-fLsS','--max-time','40','https://crates.io/api/v1/crates/'+r['name']+'/'+r['version'],'-o',str(meta)],check=True,stderr=subprocess.DEVNULL)
            expected=json.loads(meta.read_text())['version']['checksum']
        # A cache hit is trusted only after hashing its actual bytes.
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=expected:
            subprocess.run(['curl','--proto','=https','-fLsS','--max-time','50','--max-filesize','25000000',url,'-o',str(path)],check=True,stderr=subprocess.DEVNULL)
        actual=hashlib.sha256(path.read_bytes()).hexdigest()
        if actual!=expected:raise ValueError('CRATE_CHECKSUM')
        notices=inspect_archive(path)
        with tarfile.open(path) as archive:
            entry=next(e for e in archive if e.isfile() and e.name==key+'/Cargo.toml')
            cargo=tomllib.loads(archive.extractfile(entry).read().decode())
            scripts=[e.name for e in archive if e.isfile() and e.name.endswith('/build.rs')]
            for n in notices:
                raw=archive.extractfile(n['path']).read();relative='rust-notices/'+key+'/'+n['sha256'][:16]+'-'+Path(n['path']).name
                if relative.endswith('.md'):relative+='.txt'
                target=OUT/relative
                if target.is_symlink() or not target.resolve().is_relative_to(OUT.resolve()):raise ValueError('NOTICE_PATH')
                target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
                n.pop('text',None);n['evidenceFile']=relative
        return {**r,'url':url,'archiveSha256':actual,'expectedChecksum':expected,'checksumAuthority':'original Cargo.lock' if r.get('lockChecksum') else 'crates.io version API; generated upstream lock unavailable','license':cargo['package'].get('license'),'licenseFile':cargo['package'].get('license-file'),'notices':notices,'buildScripts':scripts,'archiveIntegrity':'PASS','decision':'PASS' if notices and cargo['package'].get('license') else 'BLOCKED','reason':'Archive/notice acquisition only; compilation source checksum and distribution obligations are separate'}
    except (OSError,ValueError,KeyError,StopIteration,tarfile.TarError,subprocess.SubprocessError):
        return {**r,'archiveIntegrity':'BLOCKED','decision':'BLOCKED','reason':'Download/checksum/safe archive/notice inspection incomplete; no replacement or inferred source'}


if __name__=='__main__':
    CACHE.mkdir(parents=True,exist_ok=True)
    lockpath=ROOT/'docs/evidence/s05b/upstream/librsvg-Cargo.lock'
    lock=tomllib.loads(lockpath.read_text());obs=json.loads((OUT/'upstream-build-observations.json').read_text());compiled=compilation_pairs(obs)
    rows=[]
    for p in lock['package']:
        if 'source' not in p:continue
        pair=(p['name'],p['version']);seen=pair in compiled
        rows.append({'packageId':None,'lockIdentity':p['source']+'::'+p['name']+'@'+p['version'],'name':p['name'],'version':p['version'],'source':p['source'],'sourceKind':'registry' if p['source'].startswith('registry+') else 'git','lockChecksum':p.get('checksum'),'gitCommit':p['source'].split('#')[-1] if p['source'].startswith('git+') else None,'target':'x86_64-unknown-linux-gnu','targetBasis':'observed upstream rustup host tuple and Linux x64 job; cbuild has no explicit --target','features':'default librsvg-c package after pinned recipe removes image gif/webp and cairo pdf/ps; resolved per-crate features unavailable','dependencyKind':'UNKNOWN: normal/build role not encoded in Compiling lines','scopeDecision':'COMPILED — EVIDENCED' if seen else 'UNKNOWN','evidenceLines':compiled.get(pair,[]),'gaps':['Post cargo-update --workspace generated lock and compiler-artifact package IDs unavailable; source identity is original-lock registry/version, not a verified emitted package ID']})
    extras=[];known={(r['name'],r['version']) for r in rows}
    for pair,lines in compiled.items():
        if pair not in known and pair[0] not in ['librsvg','librsvg-c']:
            extras.append({'name':pair[0],'version':pair[1],'source':'registry+https://github.com/rust-lang/crates.io-index','sourceKind':'registry','lockChecksum':None,'scopeDecision':'COMPILED — EVIDENCED','sourceIdentityDecision':'UNKNOWN: registry location candidate; generated lock unavailable','evidenceLines':lines})
    scope={'schemaVersion':1,'lockSha256':hashlib.sha256(lockpath.read_bytes()).hexdigest(),'target':'x86_64-unknown-linux-gnu','librsvgVersion':'2.63.2','upstreamRecipeCommit':obs['commit'],'upstreamCargoCommand':"cargo cbuild --locked --library-type staticlib --release -p librsvg-c",'historicalLockChanged':True,'records':rows,'additionalCompilationObservations':extras,'counts':{s:sum(r['scopeDecision']==s for r in rows) for s in ['COMPILED — EVIDENCED','RESOLVED — NOT PROVEN COMPILED','NOT SELECTED — EVIDENCED','UNKNOWN']},'gaps':['357 is source-archive lock registry/git records, not all compiled records','Toolchain cargo-c installation compilation excluded','Compilation name/version evidence does not prove source checksum of the unavailable generated lock or final linked subset']}
    (OUT/'rust-build-scope.json').write_text(json.dumps(scope,indent=2)+'\n')
    # Prioritize actual compilation observations, then remaining original-lock candidates.
    candidates=sorted(rows+extras,key=lambda r:r['scopeDecision']!='COMPILED — EVIDENCED')
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:receipts=list(pool.map(acquire,candidates))
    (OUT/'rust-source-manifest.json').write_text(json.dumps({'schemaVersion':1,'scopeLockSha256':scope['lockSha256'],'records':receipts,'counts':{s:sum(r['decision']==s for r in receipts) for s in ['PASS','BLOCKED','UNKNOWN','NOT_APPLICABLE']},'decision':'PARTIAL','scope':'Candidate source acquisition and license declarations, not legal approval or proof all candidates are linked'},indent=2)+'\n')
    print(json.dumps({'scope':scope['counts'],'extra':len(extras),'source':{s:sum(r['decision']==s for r in receipts) for s in ['PASS','BLOCKED','UNKNOWN']}}))
