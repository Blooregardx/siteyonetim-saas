#!/bin/sh
set -eu
export MIGRATOR_PASSWORD="$(cat /run/secrets/migrator_password)"
export RUNTIME_PASSWORD="$(cat /run/secrets/runtime_password)"
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<'SQL'
\getenv migration_password MIGRATOR_PASSWORD
\getenv runtime_password RUNTIME_PASSWORD
\getenv database POSTGRES_DB
CREATE ROLE sy_migrator LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION CONNECTION LIMIT 5 PASSWORD :'migration_password';
CREATE ROLE sy_runtime LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION CONNECTION LIMIT 10 PASSWORD :'runtime_password';
REVOKE ALL ON DATABASE :"database" FROM PUBLIC;
GRANT CONNECT, CREATE ON DATABASE :"database" TO sy_migrator;
GRANT CONNECT ON DATABASE :"database" TO sy_runtime;
ALTER SCHEMA public OWNER TO sy_migrator;
REVOKE ALL ON SCHEMA public FROM PUBLIC;
GRANT USAGE ON SCHEMA public TO sy_runtime;
SQL
