"""Download exact URLs from pinned upstream recipe; inspect without extraction/execution."""
import concurrent.futures
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import posixpath
import subprocess
import tarfile

COMMIT = 'ebb95f8add54eee8bed840e3fb587e4cbec857d7'
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'docs/evidence/s05b'
CACHE = Path('/tmp/s05b-upstream/sources')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def inspect_archive(path):
    notices = []
    with tarfile.open(path) as archive:
        members = archive.getmembers()
        if not members or len(members)>150000:raise ValueError('EMPTY_OR_OVERSIZE_ARCHIVE')
        for member in members:
            p = PurePosixPath(member.name)
            if p.is_absolute() or '..' in p.parts:raise ValueError('UNSAFE_ARCHIVE_PATH')
            if member.issym() or member.islnk():
                q = PurePosixPath(member.linkname)
                target=posixpath.normpath(posixpath.join(str(p.parent),member.linkname) if member.issym() else member.linkname)
                if q.is_absolute() or target.startswith('../') or target.split('/')[0]!=p.parts[0]:raise ValueError('UNSAFE_ARCHIVE_LINK')
                continue  # Never follow or extract links.
            if member.isfile() and re.match(r'^(license|copying|notice|copyright)([._-]|$)', p.name, re.I):
                if member.size>2*1024*1024:raise ValueError('OVERSIZE_NOTICE')
                data = archive.extractfile(member).read()
                notices.append({'path':member.name,'sha256':digest(data),'text':data.decode('utf8',errors='replace')})
    return notices


def download(record):
    path=CACHE/(record['name']+'.tar')
    try:
        subprocess.run(['curl','--proto','=https','--tlsv1.2','--fail','--location','--silent','--show-error','--max-time','90','--max-filesize','100000000','--output',str(path),record['url']],check=True,stderr=subprocess.DEVNULL)
        record['sha256']=digest(path.read_bytes())
        record['notices']=inspect_archive(path)
        record['archiveStatus']='PASS'
        record['sourceMatch']='BLOCKED'
        record['missingEvidence']='Archive integrity observed, not authenticated binary build provenance; no bit-reproducible rebuild.'
    except (OSError,ValueError,tarfile.TarError,subprocess.SubprocessError):
        record.update(archiveStatus='BLOCKED',sourceMatch='BLOCKED',missingEvidence='Download or safe archive validation incomplete; no substituted source.')
    return record


if __name__=='__main__':
    CACHE.mkdir(parents=True,exist_ok=True)
    versions=dict(re.findall(r'^VERSION_(\w+)=(.+)$',(OUT/'upstream/versions.properties').read_text(),re.M))
    recipe=(OUT/'upstream/build/posix.sh').read_text()
    records=[]
    for line in recipe.splitlines():
        if '$CURL https://' not in line or '| tar ' not in line:continue
        url=line.split('$CURL ')[1].split(' | ')[0]
        keys=re.findall(r'VERSION_(\w+)',url)
        key=keys[0]
        for k,v in versions.items():
            url=url.replace('$(without_patch $VERSION_'+k+')','.'.join(v.split('.')[:2]))
            url=url.replace('$(without_prerelease $VERSION_'+k+')',v.split('-')[0])
            url=url.replace('${VERSION_'+k+'//./-}',v.replace('.','-')).replace('${VERSION_'+k+'//./_}',v.replace('.','_'))
            url=url.replace('${VERSION_'+k+'}',v)
        if '$' in url:raise ValueError('UNRESOLVED_SOURCE_URL')
        records.append({'name':key.lower().replace('_','-'),'version':versions[key],'url':url,'imagePresence':'PENDING_NEW_IMAGE_VERSION_COMPARISON','linkage':'statically bundled into libvips-cpp per pinned recipe; platform conditions apply','licenseDecision':'UNKNOWN until original per-file licenses reviewed'})
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:records=list(pool.map(download,records))
    for record in records:
        if record.get('archiveStatus')!='PASS':continue
        with tarfile.open(CACHE/(record['name']+'.tar')) as archive:
            for notice in record['notices']:
                data=archive.extractfile(notice['path']).read()
                relative='notices/'+record['name']+'/'+notice['sha256'][:16]+'-'+Path(notice['path']).name
                relative += '.txt' if relative.endswith('.md') else ''
                output=OUT/relative;output.parent.mkdir(parents=True,exist_ok=True);output.write_bytes(data)
                notice.pop('text',None);notice['evidenceFile']=relative
    files={str(p.relative_to(OUT)):digest(p.read_bytes()) for p in (OUT/'upstream').rglob('*') if p.is_file() and p.name!='librsvg-Cargo.lock'}
    patches=re.findall(r'\$CURL (https://\S+) \| patch -p1',recipe)
    patch_records=[]
    for i,url in enumerate(patches):
        record={'url':url,'status':'BLOCKED'}
        output=OUT/'patches'/f'{i}.patch';output.parent.mkdir(parents=True,exist_ok=True)
        result=subprocess.run(['curl','--proto','=https','-fLsS','--max-time','60',url,'-o',str(output)],stderr=subprocess.DEVNULL)
        if result.returncode==0:record.update(status='PASS',sha256=digest(output.read_bytes()),evidenceFile=str(output.relative_to(OUT)))
        patch_records.append(record)
    manifest={'schemaVersion' :1,'package':{'name':'sharp-libvips','version':'1.3.4','tagObject':'158bf3bfb1e11de50032645873d52e5920c26986','commit':COMMIT,'githubSignatureVerified':True},'sharp':{'version':'0.35.5','commit':'51a990faa26ade5586a4934ac9673c98d8893326'},'libvips':{'version':'8.18.7','commit':'24ad4d042940e6bf99a68871ba886ca8847c9c82'},'buildArchive':{'url':'https://codeload.github.com/lovell/sharp-libvips/tar.gz/'+COMMIT,'sha256':digest(Path('/tmp/s05b-upstream/commit.tar.gz').read_bytes()),'note':'Downloaded exact commit archive; signed tag resolves to this commit'},'buildFiles':files,'patches':patch_records,'dependencies':records,'images':[],'sourceDecision':'PARTIAL','binarySourceDecision':'BLOCKED','relinkingDecision':'BLOCKED','maintainerReview':{'approved':False},'gaps':['No signed per-binary source/build attestation','Unpinned upstream toolchains/nightly/base images','No full rebuild of static LGPL sublibraries','Fresh image evidence is produced as CI artifact, not inherited from S05-A']}
    (CACHE.parent/'source-research-draft.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'dependencies':len(records),'archives':{s:sum(r.get('archiveStatus')==s for r in records) for s in ['PASS','BLOCKED']}}))
