#!/bin/sh
# Synthetic acceptance only; invoke from a clean checkout. Never use on a real volume.
set -eu
[ "${POSTGRES_DB:-}" = siteyonetim_test ] || { echo 'Requires synthetic siteyonetim_test'; exit 1; }
[ ! -e .env.selfhost ] || { echo 'Refusing existing env file'; exit 1; }
[ ! -e secrets ] || { echo 'Refusing existing secrets directory'; exit 1; }
umask 077
sed -e 's/^POSTGRES_DB=.*/POSTGRES_DB=siteyonetim_test/' -e 's|^APP_URL=.*|APP_URL=https://example.invalid|' .env.selfhost.example > .env.selfhost
mkdir secrets
for role in db migrator runtime; do openssl rand -hex 32 > "secrets/${role}_password"; done
: > secrets/smtp_url
# UID 1000 is the image user; GitHub runner UID may differ.
sudo chown 1000:999 secrets/*
compose() { docker compose -p s04a-ci -f compose.selfhost.yaml "$@"; }
sudo chmod 640 secrets/*
sh scripts/selfhost-preflight.sh
compose config --quiet
compose --profile tools build
# A build parser error must remain nonzero; this is not a second app build.
python3 scripts/test_install_negatives.py build
# Reject connection failure before DB is started, independently of missing schema.
reject_app() {
  set +e
  timeout 30 docker compose -p s04a-ci -f compose.selfhost.yaml run --rm --no-deps "$@" app
  rejected=$?
  set -e
  [ "$rejected" -eq 1 ] || { echo 'Expected explicit startup rejection'; exit 1; }
}
reject_app
compose up -d --wait db
# No DB port binding, and native Prisma works as the restricted runtime before migration.
[ "$(docker inspect --format '{{json .HostConfig.PortBindings}}' "$(compose ps -q db)")" = '{}' ]
compose run --rm --no-deps app node docker/acceptance.mjs before
# Startup must fail before migration.
set +e
timeout 30 docker compose -p s04a-ci -f compose.selfhost.yaml run --rm --no-deps app
startup_status=$?
set -e
[ "$startup_status" -eq 1 ] || { echo 'Expected explicit startup rejection'; exit 1; }
compose run --rm migrate
# All role/history mutations below are bounded synthetic negative fixtures only.
reject_app -e POSTGRES_DB=nonexistent_test_target
compose exec -T db psql -U postgres -d siteyonetim_test -v ON_ERROR_STOP=1 -q -c 'GRANT CREATE ON SCHEMA public TO sy_runtime;'
reject_app
compose exec -T db psql -U postgres -d siteyonetim_test -v ON_ERROR_STOP=1 -q -c 'REVOKE CREATE ON SCHEMA public FROM sy_runtime;'
compose exec -T db psql -U postgres -d siteyonetim_test -v ON_ERROR_STOP=1 -q -c 'ALTER ROLE sy_runtime NOLOGIN;'
reject_app
compose exec -T db psql -U postgres -d siteyonetim_test -v ON_ERROR_STOP=1 -q -c 'ALTER ROLE sy_runtime LOGIN;'
python3 scripts/test_install_negatives.py history
compose up -d --wait app
curl --fail --silent http://127.0.0.1:3000/demo > /dev/null
compose exec -T app node docker/health.mjs
compose exec -T app node docker/acceptance.mjs write
compose restart db
compose up -d --wait db
compose exec -T app node docker/health.mjs
compose exec -T app node docker/acceptance.mjs read
# Gate queries migration rows after restart; persisted history must still match all checksums.
docker run --rm --network=none --read-only --cap-drop=ALL --security-opt=no-new-privileges:true --entrypoint=node s04a-ci-app docker/image-license-audit.mjs
compose stop app db
