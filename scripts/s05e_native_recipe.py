"""Render the hash-pinned upstream Linux recipe into an offline experiment.

No remote script execution. The Rust resolution is explicitly S05-D's controlled
lock, NOT the unknown historical upstream post-update lock. Keeps all build
directories and static archives instead of upstream's destructive packaging.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
RECIPE_SHA='333031b3b49bf1a16d0b9d6812d98f67c404218932ef8c0b389388524a524b36'
LOCK_SHA='5723e14ce316e9058c76257848e18ab52624c98d16f758b5f8a73b5007b2ab8b'


def render():
    b=ROOT/'docs/evidence/s05b'
    recipe=(b/'upstream/build/posix.sh').read_bytes()
    if hashlib.sha256(recipe).hexdigest()!=RECIPE_SHA:
        raise ValueError('UPSTREAM_RECIPE_HASH')
    m=json.loads((b/'libvips-source-manifest.json').read_text())
    sources={r['name']:r for r in m['dependencies']}
    text=recipe.decode().split('# Cleanup\n')[0]
    text=text.replace('ROOT=/root','ROOT=/config')
    text=text.replace('export MAKEFLAGS="-j$(nproc)"','export MAKEFLAGS="-j2"')
    # Delete the entire non-applicable macOS remote-installer block.
    text=re.sub(r'if \[ "\$DARWIN" = true \]; then\n  curl --proto.*?\nfi\n','',text,flags=re.S)
    def archive(match):
        name=match.group(1)
        source='mozjpeg' if name=='jpeg' else name
        if source not in sources:raise ValueError('UNKNOWN_NATIVE_SOURCE '+name)
        r=sources[source]
        expected=r['sha256']
        return 'python3.12 /config/s05e_extract.py /inputs/sources/'+source+'.tar '+expected+' ${DEPS}/'+name
    text,count=re.subn(r'\$CURL [^\n]+ \| tar x[zJ]C \$\{DEPS\}/([a-z0-9-]+) --strip-components=1',archive,text)
    if count!=28:raise ValueError('SOURCE_RECIPE_COUNT '+str(count))
    patches=m['patches']
    for i,r in enumerate(patches):
        # Match the exact recorded URL only; no general URL substitutions.
        original='$CURL '+r['url']+' | patch -p1'
        if text.count(original)!=1:raise ValueError('PATCH_RECIPE_MATCH')
        text=text.replace(original,'patch -p1 < /inputs/patches/'+str(i)+'.patch')
    text=text.replace('cargo update --workspace','cp /inputs/generated-Cargo.lock Cargo.lock\nsha256sum Cargo.lock\ncargo metadata --offline --locked --format-version=1 > /evidence/rust-metadata.json\ncargo tree --offline --locked -e features > /evidence/rust-tree.txt')
    text=text.replace('meson install -C _build','meson compile -v -j2 -C _build\nmeson install -C _build')
    # Never leave an executable network acquisition or upstream installer.
    if re.search(r'(?m)^\s*(?:\$CURL|curl |wget |.*rustup\.rs)',text):
        raise ValueError('UNREPLACED_NETWORK_COMMAND')
    return text


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('output',type=Path)
    a=p.parse_args();a.output.write_text(render())
