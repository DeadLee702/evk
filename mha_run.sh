#!/usr/bin/env bash
#
# Z-12 Master Health Assessment (MHA) driver.
#
# Flow:
#   mha_run.sh
#     -> build EVK core (deterministic integrity anchor)
#     -> master_runner.py  -> GAUNTLET_HEALTH_REPORT.json
#     -> judge/cop_v1.py   -> PURA / MALPURA verdict
#
# Exit codes:
#   0 = PURA             (clean)
#   1 = MALPURA          (compromised)
#   2 = Critical failure (EVK core unverified / pipeline error)
#
set -u

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPORT="${REPO_ROOT}/GAUNTLET_HEALTH_REPORT.json"
PYTHON="${PYTHON:-python3}"

echo "[MHA] Z-12 Sovereign Security Platform — Master Health Assessment"
echo "[MHA] repo root: ${REPO_ROOT}"

# 1) Build the EVK deterministic core (skip if SKIP_BUILD=1).
if [ "${SKIP_BUILD:-0}" != "1" ]; then
  echo "[MHA] Building EVK core (cargo build --release --locked)..."
  if ! ( cd "${REPO_ROOT}" && cargo build --release --locked ); then
    echo "[MHA] CRITICAL: EVK core build failed."
    exit 2
  fi
fi

# 2) Run the gauntlet orchestrator.
echo "[MHA] Running master_runner (12-room gauntlet + EVK core check)..."
( cd "${REPO_ROOT}" && "${PYTHON}" master_runner.py --report "${REPORT}" )
echo "[MHA] master_runner exit code: $?"

if [ ! -f "${REPORT}" ]; then
  echo "[MHA] CRITICAL: ${REPORT} was not produced."
  exit 2
fi

# 3) Judge the report.
echo "[MHA] Invoking Judge (cop_v1)..."
"${PYTHON}" "${REPO_ROOT}/judge/cop_v1.py" "${REPORT}"
VERDICT=$?
echo "[MHA] Judge verdict code: ${VERDICT}"

# 4) Report the verdict. On a non-PURA verdict the Pike/Reaper sensor would route
#    ACM_DENY events to the Kill Vector (src/kill_vector) for process containment;
#    see `make reaper` and src/sensors/pike_reaper.
case "${VERDICT}" in
  0) echo "[MHA] RESULT: PURA. Zodiako gardas. Relenthol engaĝita." ;;
  1) echo "[MHA] RESULT: MALPURA. Kill Vector containment would engage on live lineage." ;;
  *) echo "[MHA] RESULT: CRITICAL FAILURE." ;;
esac

exit "${VERDICT}"
