#!/bin/bash

# find the real directory this script is in (follows symlinks)
SCRIPT_DIR="$(dirname "$(realpath "${BASH_SOURCE[0]}")")"

# exec the qbot entry‑point from the venv next to the script
exec "$SCRIPT_DIR/venv/bin/py-qbot" "$@"
