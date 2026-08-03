#!/usr/bin/env bash
set -euo pipefail
# Used inside container to choose stub vs enforced killswitch behavior.
# If KILL_MODE==ENFORCE the container expects the real killswitch binary to be present
# and the container to run with required privileges. Default is STUB (safe).
echo "[entrypoint] KILL_MODE=${KILL_MODE:-STUB}"
if [ "${KILL_MODE:-STUB}" = "STUB" ]; then
  echo "[entrypoint] Using killswitch stub (safe mode)."
  # Already using compiled stub source for CI/demo; just ensure log location exists
  mkdir -p "$(dirname "${Z12_KILL_LOG:-/tmp/z12_kill.log}")"
  touch "${Z12_KILL_LOG:-/tmp/z12_kill.log}"
else
  echo "[entrypoint] Enforcement mode enabled. Ensure this container is deployed on a dedicated host and you have admin consent."
  # Real enforcement: require presence of killswitch binary or compile it here.
  # Validate log dir
  mkdir -p "$(dirname "${Z12_KILL_LOG:-/var/log/z12/kill.log}")"
  touch "${Z12_KILL_LOG:-/var/log/z12/kill.log}"
fi
exec "$@"
