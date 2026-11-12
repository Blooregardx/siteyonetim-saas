"""Acquire frozen inputs and prepare a local offline Docker build context.

No remote installers. Exact byte hashes and RPM publisher signatures are both
required; cache hits never bypass hashes. Does not run a native libvips build.
"""
import argparse
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import urllib.parse
import urllib.request

from collect_s05d_evidence import extract_regular
from s05e_source_protocol import file_sha
from verify_s05d_evidence import safe_members

ROOT=Path(__file__).resolve().parents[1]


class HTTPSRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        if urllib.parse.urlparse(newurl).scheme!='https':raise ValueError('NON_HTTPS_REDIRECT')
        return super().redirect_request(req,fp,code,msg,headers,newurl)


def download(url,path,expected,maximum=256*1024**2):
    if path.is_symlink():raise ValueError('SYMLINK_CACHE')
    if path.is_file() and file_sha(path)==expected:return
    if urllib.parse.urlparse(url).scheme!='https':raise ValueError('HTTPS_REQUIRED')
    path.parent.mkdir(parents=True,exist_ok=True)
    temporary=path.with_name(path.name+'.incomplete')
    if temporary.exists():raise ValueError('STALE_DOWNLOAD_REQUIRES_REVIEW')
    h=hashlib.sha256();size=0
    try:
        opener=urllib.request.build_opener(HTTPSRedirect())
        with opener.open(urllib.request.Request(url,headers={'User-Agent':'SiteYonetim-S05E-input-audit'}),timeout=45) as response,temporary.open('xb') as f:
            while chunk:=response.read(1024*1024):
                size+=len(chunk)
                if size>maximum:raise ValueError('DOWNLOAD_LIMIT')
                f.write(chunk);h.update(chunk)
        if h.hexdigest()!=expected:raise ValueError('DOWNLOAD_HASH')
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def prepare(out):
    evidence=ROOT/'docs/evidence/s05e'
    out.mkdir(parents=True,exist_ok=True);context=out/'context';context.mkdir(exist_ok=False)
    rpm_manifest=json.loads((evidence/'historical-rpm-files.json').read_text())
    def rpm(r):
        target=out/r['file']
        locations=r.get('metadataLocations',[])
        if not locations:raise ValueError('RPM_LOCATION_MISSING')
        errors=[]
        for url in locations:
            try:download(url,target,r['sha256']);break
            except (OSError,ValueError) as e:errors.append(type(e).__name__)
        else:raise ValueError('RPM_ACQUISITION_BLOCKED '+target.name+' '+','.join(errors))
        dest=context/r['stage']/target.name;dest.parent.mkdir(exist_ok=True)
        os.link(target,dest)
        return str(dest.relative_to(context)),r['sha256']
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        rpm_hashes=dict(pool.map(rpm,rpm_manifest['records']))
    (context/'rpm-hashes.json').write_text(json.dumps(rpm_hashes,indent=2)+'\n')
    expected=json.loads((evidence/'python-input-hashes.json').read_text())
    py=context/'python';py.mkdir()
    for package,version in [('meson','1.12.1'),('ninja','1.13.2')]:
        with urllib.request.urlopen('https://pypi.org/pypi/'+package+'/'+version+'/json',timeout=30) as response:
            raw=response.read(1024**2+1)
        if len(raw)>1024**2:raise ValueError('PYPI_METADATA_LIMIT')
        metadata=json.loads(raw)
        for name,h in expected.items():
            if not name.startswith(package+'-'):continue
            item=next(x for x in metadata['urls'] if x['filename']==name)
            if item['digests']['sha256']!=h or urllib.parse.urlparse(item['url']).hostname!='files.pythonhosted.org':
                raise ValueError('PYPI_VERSION_OR_HASH')
            download(item['url'],py/name,h)
            if name.endswith('.tar.gz'):safe_members(py/name)  # No links accepted before Docker tar extraction.
    shutil.copy(evidence/'python-input-hashes.json',context/'python-hashes.json')
    baseline=json.loads((evidence/'baseline.json').read_text())
    if file_sha(evidence/'RPM-GPG-KEY-EPEL-8')!=baseline['epel8KeySha256']:raise ValueError('PUBLISHER_KEY_HASH')
    shutil.copy(evidence/'RPM-GPG-KEY-EPEL-8',context)
    shutil.copy(ROOT/'docker/s05e-toolchain.Dockerfile',context/'Dockerfile')
    rust=out/'rust';rust.mkdir(exist_ok=True)
    for r in json.loads((evidence/'rust-component-inputs.json').read_text()):
        p=rust/(r['name']+'.tar.xz');download(r['url'],p,r['sha256'],512*1024**2)
        extract_regular(p,rust/'toolchain',2)
    # Check installed trusted Cargo bytes before executing only cargo fetch.
    if file_sha(rust/'toolchain/bin/cargo')!='96c2dd303135a1fd8735145997192ff59a4ea1af9c94f9b656b30a7728a9b60f':
        raise ValueError('INSTALLED_CARGO_HASH')
    source=rust/'cargo-c-0.10.25+cargo-0.99.0.crate'
    download('https://static.crates.io/crates/cargo-c/cargo-c-0.10.25+cargo-0.99.0.crate',source,'6b2ddde58a8a773ccce4b6384acacd3ce01373f52717dd2424633ed46755c627')
    extract_regular(source,rust/'cargo-c-source',1)
    env={**os.environ,'CARGO_HOME':str(out/'cargo-cache'),'HOME':str(out/'cargo-home'),
         'PATH':str(rust/'toolchain/bin')+os.pathsep+os.environ['PATH']}
    (out/'cargo-home').mkdir(exist_ok=True)
    with (out/'cargo-fetch.log').open('wb') as log:
        subprocess.run([str(rust/'toolchain/bin/cargo'),'fetch','--locked','--manifest-path',str(rust/'cargo-c-source/Cargo.toml')],env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=600)
    import tomllib
    count=0
    for r in tomllib.loads((rust/'cargo-c-source/Cargo.lock').read_text())['package']:
        if not r.get('source'):continue
        if not r['source'].startswith('registry+'):raise ValueError('UNVERIFIED_GIT_OR_PATH_SOURCE')
        p=out/'cargo-cache/registry/cache/index.crates.io-1949cf8c6b5b557f'/(r['name']+'-'+r['version']+'.crate')
        if file_sha(p)!=r['checksum']:raise ValueError('CARGO_CACHE_HASH')
        safe_members(p,allow_internal_links=True);count+=1
    result={'rpmCount':len(rpm_hashes),'cargoBootstrapRegistryCount':count,'scope':'toolchain input acquisition only; no legal clearance'}
    (out/'input-acquisition.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();print(json.dumps(prepare(a.out.resolve())))
