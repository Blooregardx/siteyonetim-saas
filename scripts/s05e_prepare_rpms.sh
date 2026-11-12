#!/bin/sh
# SPDX-License-Identifier: AGPL-3.0-only
# Online acquisition ONLY, inside a disposable pinned Rocky container.
# Full native source builds use a different, network-disabled stage.
set -eu
: "${S05E_OUTPUT:=/evidence}"
: "${S05E_CA:=/run/ca.pem}"
mkdir -p "$S05E_OUTPUT/inventory"
stage=bootstrap
trap 'status=$?; printf "{\"stage\":\"%s\",\"exitCode\":%s}\n" "$stage" "$status" > "$S05E_OUTPUT/inventory/rpm-acquisition-status.json"' EXIT

capture() {
    mkdir -p "$S05E_OUTPUT/rpm-stage-$stage"
    find /var/cache/dnf -type f -path '*/packages/*.rpm' -exec cp '{}' "$S05E_OUTPUT/rpm-stage-$stage/" \;
    # Only this disposable container's already-preserved package cache.
    find /var/cache/dnf -type f -path '*/packages/*.rpm' -delete
}

# The original base has a minimal root. Preserve the upstream update/install
# order instead of forcing every alternative repoquery provider into it.
stage=update
dnf -y --setopt=keepcache=True --setopt=sslcacert="$S05E_CA" update
capture
stage=epel
dnf -y --setopt=keepcache=True --setopt=sslcacert="$S05E_CA" install epel-release dnf-plugins-core
capture
dnf config-manager --set-enabled powertools
stage=build-dependencies
dnf -y --setopt=keepcache=True --setopt=sslcacert="$S05E_CA" --setopt=tsflags=nodocs install \
    autoconf automake bzip2 cmake curl-devel findutils \
    gcc-toolset-15-gcc-15.2.1-7.1.el8_10 \
    gcc-toolset-15-gcc-c++-15.2.1-7.1.el8_10 \
    gcc-toolset-15-binutils-2.44-3.el8 gettext git gperf jq make nasm \
    openssl-devel patch pkgconf python3.12-pip-23.2.1-4.el8 tar xz \
    libabigail-2.10-1.el8
capture
rpm -qa --qf '%{NAME}\t%{EPOCHNUM}:%{VERSION}-%{RELEASE}\t%{ARCH}\t%{SOURCERPM}\t%{SHA256HEADER}\n' | sort > "$S05E_OUTPUT/inventory/transaction-installed-rpms.tsv"
find "$S05E_OUTPUT" -path '*/rpm-stage-*/*.rpm' -type f -exec rpmkeys --checksig '{}' \; > "$S05E_OUTPUT/inventory/transaction-signatures.txt"
if grep -E 'NOKEY|NOT OK|BAD|NOTTRUSTED' "$S05E_OUTPUT/inventory/transaction-signatures.txt"; then exit 2; fi
mkdir -p "$S05E_OUTPUT/inventory/rpm-keys"
cp /etc/pki/rpm-gpg/* "$S05E_OUTPUT/inventory/rpm-keys/"
stage=completed
