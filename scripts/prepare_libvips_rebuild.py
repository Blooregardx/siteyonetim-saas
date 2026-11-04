"""Prepare only pinned public inputs; no upstream installers or shell scripts executed."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[1]


def fetch(url,path,expected):
    if not url.startswith('https://') or len(expected)!=64:raise ValueError('UNPINNED_INPUT')
    if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=expected:
        subprocess.run(['curl','--proto','=https','--fail','--location','--silent','--show-error','--max-time','120','--max-filesize','100000000',url,'-o',str(path)],check=True)
    if hashlib.sha256(path.read_bytes()).hexdigest()!=expected:raise ValueError('INPUT_CHECKSUM')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('directory',type=Path);a=p.parse_args();a.directory.mkdir(parents=True,exist_ok=True)
    spec=json.load(open(ROOT/'docs/evidence/s05c/toolchain-spec.json'))
    fetch(spec['source']['url'],a.directory/'vips.tar',spec['source']['sha256'])
    fetch(spec['mesonWheel']['url'],a.directory/spec['mesonWheel']['filename'],spec['mesonWheel']['sha256'])
    patch=ROOT/'docs/evidence/s05b'/spec['sonamePatch']['evidenceFile']
    if hashlib.sha256(patch.read_bytes()).hexdigest()!=spec['sonamePatch']['sha256']:raise ValueError('PATCH_HASH')
    shutil.copyfile(patch,a.directory/'soname.patch');(a.directory/'spec.json').write_text(json.dumps(spec,indent=2)+'\n')
