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
printf '%s\n' "$id" > "$out/image-id.txt"
"$work/syft" scan "docker:$id" --scope squashed -o "syft-json=$out/sbom.syft.json" -o "cyclonedx-json=$out/sbom.cdx.json"
docker run --rm --network=none --read-only --cap-drop=ALL --security-opt=no-new-privileges:true --entrypoint=node "$id" docker/image-license-audit.mjs > "$out/filesystem.json"
printf '{}\n' > "$out/evidence.json"
set +e
python3 scripts/distribution_gate.py --sbom "$out/sbom.syft.json" --image-id "$id" --evidence "$out/evidence.json" > "$out/gate.json"
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
