# SPDX-License-Identifier: AGPL-3.0-only
# Isolated development toolchain adapter; no application image changes.
FROM rockylinux/rockylinux@sha256:ae0813ccb1bb83f4e0220acdd1539f52831517de334368e960824db7e37ee210
COPY update /inputs/update
COPY epel /inputs/epel
COPY build-dependencies /inputs/build-dependencies
COPY rpm-hashes.json /inputs/rpm-hashes.json
COPY RPM-GPG-KEY-EPEL-8 /epel-key
RUN --network=none /usr/libexec/platform-python -c 'import hashlib,json,pathlib; m=json.load(open("/inputs/rpm-hashes.json")); assert all(hashlib.sha256((pathlib.Path("/inputs")/n).read_bytes()).hexdigest()==s for n,s in m.items())' \
 && rpmkeys --import /epel-key \
 && rpmkeys --checksig /inputs/*/*.rpm \
 && dnf -y --disablerepo='*' update /inputs/update/*.rpm \
 && dnf -y --disablerepo='*' install /inputs/epel/*.rpm \
 && dnf -y --disablerepo='*' --setopt=tsflags=nodocs install /inputs/build-dependencies/*.rpm \
 && rpm -qa --qf '%{NAME}\t%{EPOCHNUM}:%{VERSION}-%{RELEASE}\t%{ARCH}\t%{SOURCERPM}\t%{SHA256HEADER}\n' > /installed-rpms.tsv
ENV PATH=/opt/rh/gcc-toolset-15/root/usr/bin:/opt/s05e/bin:/usr/local/bin:/usr/bin:/bin
COPY python /python-inputs
COPY python-hashes.json /python-hashes.json
RUN --network=none python3.12 -c 'import hashlib,json,pathlib; m=json.load(open("/python-hashes.json")); assert all(hashlib.sha256((pathlib.Path("/python-inputs")/n).read_bytes()).hexdigest()==s for n,s in m.items())' \
 && python3.12 -m pip install --no-index --no-deps /python-inputs/meson-1.12.1-py3-none-any.whl \
 && mkdir -p /opt/s05e/ninja-source \
 && tar -xf /python-inputs/ninja-1.13.2.tar.gz -C /opt/s05e/ninja-source --strip-components=1 \
 && cmake -S /opt/s05e/ninja-source/ninja-upstream -B /opt/s05e/ninja-build -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=OFF -DCMAKE_INSTALL_PREFIX=/opt/s05e \
 && cmake --build /opt/s05e/ninja-build --parallel 2 \
 && cmake --install /opt/s05e/ninja-build
