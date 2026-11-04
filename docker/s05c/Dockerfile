# syntax=docker/dockerfile:1@sha256:4edf897a3ffa55b89f906fc8cc78afdb3f1834cc9c7083565e611a8a7d5fe99e
FROM node:24-bookworm-slim@sha256:c86ecead9e55a5210ac1727de38a4ca840bf03dcaf34dc9749addbf383b1920c
COPY docker/s05c/debian.sources /etc/apt/sources.list.d/debian.sources
COPY docs/evidence/s05c/toolchain-spec.json /spec.json
RUN --mount=type=secret,id=ca_bundle,required=true apt-get -o Acquire::https::CaInfo=/run/secrets/ca_bundle update \
 && node -e 'const fs=require("fs"),c=require("crypto"),s=require("/spec.json"); for(const [repo,hash] of Object.entries(s.aptInRelease)){const name=fs.readdirSync("/var/lib/apt/lists").find(n=>n.includes("archive_"+repo+"_")&&n.endsWith("_InRelease"));if(!name||c.createHash("sha256").update(fs.readFileSync("/var/lib/apt/lists/"+name)).digest("hex")!==hash)throw Error("APT_SNAPSHOT_HASH");}' \
 && apt-get -o Acquire::https::CaInfo=/run/secrets/ca_bundle install -y --no-install-recommends build-essential binutils pkg-config python3 python3-pip ninja-build libglib2.0-dev libexpat1-dev libjpeg62-turbo-dev libpng-dev ca-certificates patch
RUN --mount=type=secret,id=meson_wheel,required=true \
 node -e 'const fs=require("fs"),c=require("crypto"),s=require("/spec.json");const b=fs.readFileSync("/run/secrets/meson_wheel");if(c.createHash("sha256").update(b).digest("hex")!==s.mesonWheel.sha256)throw Error("MESON_HASH");fs.writeFileSync("/tmp/"+s.mesonWheel.filename,b);' \
 && python3 -m pip install --break-system-packages --no-deps --no-index /tmp/meson-1.9.1-py3-none-any.whl
WORKDIR /app
COPY package.json package-lock.json ./
RUN --mount=type=secret,id=ca_bundle,required=true NODE_EXTRA_CA_CERTS=/run/secrets/ca_bundle npm ci --omit=dev --ignore-scripts --no-audit --fund=false
COPY scripts/run_libvips_rebuild.py scripts/verify_libvips_rebuild.py /s05c/
ENTRYPOINT ["python3","/s05c/run_libvips_rebuild.py"]
