#!/bin/sh
# Synthetic acceptance only; invoke from a clean checkout. Never use on a real volume.
set -eu
[ "${POSTGRES_DB:-}" = siteyonetim_test ] || { echo 'Requires synthetic siteyonetim_test'; exit 1; }
[ ! -e secrets ] || { echo 'Refusing existing secrets directory'; exit 1; }
umask 077
mkdir secrets
for role in db migrator runtime; do openssl rand -hex 32 > "secrets/${role}_password"; done
: > secrets/smtp_url
# UID 1000 is the image user; GitHub runner UID may differ.
sudo chown 1000:999 secrets/*
compose() { docker compose -p s04a-ci -f compose.selfhost.yaml "$@"; }
sudo chmod 640 secrets/*
compose config --quiet
compose build
compose up -d --wait db
# Startup must fail before migration.
set +e
timeout 30 docker compose -p s04a-ci -f compose.selfhost.yaml run --rm --no-deps app
startup_status=$?
set -e
[ "$startup_status" -eq 1 ] || { echo 'Expected explicit startup rejection'; exit 1; }
compose run --rm migrate
compose up -d --wait app
curl --fail --silent http://127.0.0.1:3000/demo > /dev/null
curl --silent -D /tmp/s04a-panel-headers http://127.0.0.1:3000/panel > /dev/null
rg -q '^HTTP/1.1 30[37]' /tmp/s04a-panel-headers
compose exec -T app node docker/health.mjs
compose restart db
compose up -d --wait db
compose exec -T app node docker/health.mjs
# Gate queries migration rows after restart; persisted history must still match all checksums.
compose stop app db
