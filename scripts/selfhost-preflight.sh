#!/bin/sh
# Checks only: never repairs secrets, starts services or changes volumes.
set -eu
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
exec env PYTHONDONTWRITEBYTECODE=1 python3 "$script_dir/selfhost_preflight.py" "$@"
