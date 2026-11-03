#!/bin/sh
# Host-only, local Docker evidence; never push or start the app.
set -eu
image=$1
out=$2
mkdir -p "$out"
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
curl -fLsS --retry 2 https://github.com/anchore/syft/releases/download/v1.18.1/syft_1.18.1_linux_amd64.tar.gz -o "$work/syft.tar.gz"
printf '%s  %s\n' 066c251652221e4d44fcc4d115ce3df33a91769da38c830a8533199db2f65aab "$work/syft.tar.gz" | sha256sum -c -
tar -xzf "$work/syft.tar.gz" -C "$work" syft
# Pin the local socket; do not inspect complete image configuration (may contain env).
export DOCKER_HOST=unix:///var/run/docker.sock
unset DOCKER_CONTEXT DOCKER_TLS DOCKER_TLS_VERIFY DOCKER_CERT_PATH
id=$(docker image inspect --format '{{.Id}}' "$image")
printf '%s\n' "$id" > "$out/docker-inspect-id.txt"
# Export the immutable local reference; Docker containerd stores may expose an index ID.
docker image save "$id" -o "$work/image.tar"
config_id=$(python3 - "$work/image.tar" <<'PYCODE'
import hashlib,json,sys,tarfile
with tarfile.open(sys.argv[1]) as t:
    manifest=json.load(t.extractfile('manifest.json'))
    if len(manifest)!=1:raise ValueError('Expected one exported image')
    config=t.extractfile(manifest[0]['Config']).read()
    print('sha256:'+hashlib.sha256(config).hexdigest())
PYCODE
)
printf '%s\n' "$config_id" > "$out/image-id.txt"
"$work/syft" scan "docker-archive:$work/image.tar" --scope squashed -o "syft-json=$out/sbom.syft.json" -o "cyclonedx-json=$out/sbom.cdx.json"
# Syft includes encoded image configuration by default; do not retain env/history.
python3 - "$out/sbom.syft.json" <<'PYCODE'
import json,sys
p=sys.argv[1]
s=json.load(open(p))
m=s['source']['metadata']
s['source']['metadata']={k:m[k] for k in ['imageID','manifestDigest','architecture','os'] if k in m}
with open(p,'w') as f:json.dump(s,f)
PYCODE
docker run --rm --network=none --read-only --cap-drop=ALL --security-opt=no-new-privileges:true --entrypoint=node "$id" docker/image-license-audit.mjs > "$out/filesystem.json"
docker run --rm --network=none --read-only --tmpfs /tmp:size=160m,mode=1777,exec --cap-drop=ALL --security-opt=no-new-privileges:true --entrypoint=node "$id" docker/libvips-evidence.mjs > "$out/libvips.json"
python3 - "$out/libvips.json" "$config_id" <<'PYCODE'
import json,sys
p=sys.argv[1];data=json.load(open(p));data['imageID']=sys.argv[2]
with open(p,'w') as f:json.dump(data,f)
PYCODE
set +e
python3 scripts/verify_libvips_sources.py --manifest docs/evidence/s05b/libvips-source-manifest.json --root docs/evidence/s05b --image "$out/libvips.json" --image-id "$config_id" > "$out/libvips-validation.json"
source_status=$?
set -e
[ "$source_status" -eq 1 ]
printf '{}\n' > "$out/evidence.json"
set +e
python3 scripts/distribution_gate.py --sbom "$out/sbom.syft.json" --image-id "$config_id" --evidence "$out/evidence.json" > "$out/gate.json"
status=$?
set -e
# Collection can succeed while distribution remains blocked. Invalid evidence is a CI error.
[ "$status" -eq 1 ]
python3 - "$out/gate.json" <<'PY'
import json,sys
r=json.load(open(sys.argv[1]))
assert r['readiness']=='BLOCKED' and r['components']
print(json.dumps({'imageID':r['imageID'],'readiness':r['readiness'],'counts':r['counts']}))
PY
