#!/bin/sh
# Only the dedicated synthetic GitHub runner; no app/DB/SMTP starts.
set -eu
[ "${GITHUB_ACTIONS:-}" = true ]
out="$RUNNER_TEMP/s05c-experiment"
mkdir -p "$out/input" "$out/out" "$out/work"
printf '{"status":"BLOCKED","stage":"environment-preparation"}\n' > "$out/experiment-status.json"
python3 - "$out" <<'PYCODE'
import shutil,sys
if shutil.disk_usage(sys.argv[1]).free<6*1024**3:raise ValueError('S05C_DISK_BELOW_6GIB')
PYCODE
python3 scripts/prepare_libvips_rebuild.py "$out/input"
docker build --platform linux/amd64 -f docker/s05c/Dockerfile --secret id=ca_bundle,src=/etc/ssl/certs/ca-certificates.crt --build-context "s05c_inputs=$out/input" -t s05c-rebuild-environment .
id=$(docker image inspect --format '{{.Id}}' s05c-rebuild-environment)
printf '%s\n' "$id" > "$out/environment-inspect-id.txt"
# Bind SBOM to the exact exported environment, not a mutable tag.
docker image save "$id" -o "$out/environment.tar"
python3 - "$out" <<'PYCODE'
import hashlib,json,sys,tarfile
from pathlib import Path
root=Path(sys.argv[1])
with tarfile.open(root/'environment.tar') as t:
    m=json.load(t.extractfile('manifest.json'))
    if len(m)!=1:raise ValueError('ENVIRONMENT_IMAGE_COUNT')
    image='sha256:'+hashlib.sha256(t.extractfile(m[0]['Config']).read()).hexdigest()
(root/'environment-config-id.txt').write_text(image+'\n')
PYCODE
curl -fLsS --max-time 90 https://github.com/anchore/syft/releases/download/v1.18.1/syft_1.18.1_linux_amd64.tar.gz -o "$out/syft.tar.gz"
printf '%s  %s\n' 066c251652221e4d44fcc4d115ce3df33a91769da38c830a8533199db2f65aab "$out/syft.tar.gz" | sha256sum -c -
tar -xzf "$out/syft.tar.gz" -C "$out" syft
"$out/syft" scan "docker-archive:$out/environment.tar" --scope squashed -o "syft-json=$out/out/environment-sbom.syft.json"
python3 - "$out" <<'PYCODE'
import json,sys
from pathlib import Path
root=Path(sys.argv[1]);p=root/'out/environment-sbom.syft.json';s=json.loads(p.read_text());meta=s['source']['metadata'];s['source']['metadata']={k:meta[k] for k in ['imageID','manifestDigest','architecture','os'] if k in meta};p.write_text(json.dumps(s))
if meta['imageID']!=(root/'environment-config-id.txt').read_text().strip():raise ValueError('ENVIRONMENT_SBOM_MISMATCH')
(root/'environment.tar').unlink()
PYCODE
set +e
docker run --rm --network=none --read-only --cpus=2 --memory=4g --user "$(id -u):$(id -g)" --cap-drop=ALL --security-opt=no-new-privileges:true --tmpfs /tmp:size=160m,mode=1777,exec --mount "type=bind,src=$out/input,dst=/input,readonly" --mount "type=bind,src=$out/out,dst=/out" --mount "type=bind,src=$out/work,dst=/work" -e HOME=/work/home "$id"
status=$?
set -e
printf '{"containerExitCode":%s,"binaryDistributionReadiness":"BLOCKED"}\n' "$status" > "$out/experiment-status.json"
[ "$status" -eq 0 ]
python3 - "$out" <<'PYCODE'
import json,hashlib,sys
from pathlib import Path
root=Path(sys.argv[1]);p=root/'out/rebuild-result.json';r=json.loads(p.read_text());r['imageID']=(root/'environment-config-id.txt').read_text().strip();r['sbomSha256']=hashlib.sha256((root/'out/environment-sbom.syft.json').read_bytes()).hexdigest();p.write_text(json.dumps(r,indent=2)+'\n')
PYCODE
set +e
python3 scripts/verify_libvips_rebuild.py --root "$out" --result "$out/out/rebuild-result.json" --spec "$out/input/spec.json" > "$out/validation.json"
validation=$?
set -e
[ "$validation" -eq 1 ]
# Only this experiment directory is packaged; no Docker config/env/credentials.
tar -czf "$RUNNER_TEMP/s05c-rebuild-evidence.tar.gz" -C "$out" input out work
