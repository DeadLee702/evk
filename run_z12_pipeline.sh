#!/usr/bin/env bash
set -euo pipefail

# run_z12_pipeline.sh - deterministic demo driver for Z-12 -> Gemini-Box -> EVK -> ACM
# Usage:
#   ./run_z12_pipeline.sh [--run-kill-vector-test]
#
# Environment overrides:
#   Z12_EVK_PATH
#   Z12_GEMINI_PATH
#   Z12_ACM_PATH
#   FIXTURE_PATH

# Deterministic environment
export SOURCE_DATE_EPOCH="${SOURCE_DATE_EPOCH:-1700000000}"  # fixed epoch (deterministic)
export TZ=UTC
export LANG=C
export LC_ALL=C

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EVK_PATH="${Z12_EVK_PATH:-$SCRIPT_DIR}"
GEMINI_PATH="${Z12_GEMINI_PATH:-$SCRIPT_DIR/../gemini-box}"
ACM_PATH="${Z12_ACM_PATH:-$SCRIPT_DIR/../adversarial-compliance-matrix}"

# Output files (overwrite each run)
OUT_JSON="$SCRIPT_DIR/z12_demo_report.json"
OUT_HTML="$SCRIPT_DIR/z12_demo_report.html"
OUT_EVIDENCE="$SCRIPT_DIR/z12_demo_evidence.html"

RUN_KV_TEST=0
if [[ "${1:-}" == "--run-kill-vector-test" ]]; then
  RUN_KV_TEST=1
fi

# Prefer fixture passed via env, else default expected test path
FIXTURE_PATH="${FIXTURE_PATH:-}"
if [[ -z "$FIXTURE_PATH" ]]; then
  # Search common locations (gemini-box/test, acm/test, evk/fixtures)
  if [[ -f "$GEMINI_PATH/test/incident_7f3a.evkp" ]]; then
    FIXTURE_PATH="$GEMINI_PATH/test/incident_7f3a.evkp"
  elif [[ -f "$ACM_PATH/test/incident_7f3a.evkp" ]]; then
    FIXTURE_PATH="$ACM_PATH/test/incident_7f3a.evkp"
  elif [[ -f "$EVK_PATH/fixtures/incident_7f3a.evkp" ]]; then
    FIXTURE_PATH="$EVK_PATH/fixtures/incident_7f3a.evkp"
  else
    if [[ -f "$EVK_PATH/test/incident_7f3a.evkp" ]]; then
      FIXTURE_PATH="$EVK_PATH/test/incident_7f3a.evkp"
    fi
  fi
fi

if [[ -z "$FIXTURE_PATH" || ! -f "$FIXTURE_PATH" ]]; then
  echo "ERROR: fixture test/incident_7f3a.evkp not found. Set FIXTURE_PATH or ensure it exists in gemini-box/test or acm/test or evk/fixtures."
  exit 2
fi

echo "Using:"
echo "  EVK_PATH   = $EVK_PATH"
echo "  GEMINI_PATH= $GEMINI_PATH"
echo "  ACM_PATH   = $ACM_PATH"
echo "  FIXTURE    = $FIXTURE_PATH"
echo "  SOURCE_DATE_EPOCH = $SOURCE_DATE_EPOCH"
echo

# Helper: run and capture stdout/stderr/rc
run_capture() {
  local label="$1"; shift
  local cwd="${1:-}"; shift || true
  local cmd=( "$@" )
  echo ">>> [$label] ${cmd[*]}"
  local tmp_out tmp_err
  tmp_out="$(mktemp)"; tmp_err="$(mktemp)"
  if [[ -n "$cwd" ]]; then
    (cd "$cwd" && "${cmd[@]}" >"$tmp_out" 2>"$tmp_err") || true
    rc=$?
  else
    "${cmd[@]}" >"$tmp_out" 2>"$tmp_err" || true
    rc=$?
  fi
  out="$(cat "$tmp_out")"
  err="$(cat "$tmp_err")"
  rm -f "$tmp_out" "$tmp_err"
  printf -v __LAST_RC "%d" "$rc"
  printf -v __LAST_OUT "%s" "$out"
  printf -v __LAST_ERR "%s" "$err"
}

stages=()

# Stage: build EVK
run_capture "EVK: cargo build" "$EVK_PATH" cargo build --release
stages+=("EVK: cargo build|$__LAST_RC|$__LAST_OUT|$__LAST_ERR")

# Optional kill vector test
if [[ "$RUN_KV_TEST" -eq 1 ]]; then
  run_capture "EVK: make test_killswitch" "$EVK_PATH" make test_killswitch
  stages+=("EVK: make test_killswitch|$__LAST_RC|$__LAST_OUT|$__LAST_ERR")
fi

# Stage: build Gemini-Box
run_capture "GEMINI-BOX: cargo build" "$GEMINI_PATH" cargo build --release
stages+=("GEMINI-BOX: cargo build|$__LAST_RC|$__LAST_OUT|$__LAST_ERR")

# Stage: build ACM
run_capture "ACM: cargo build" "$ACM_PATH" cargo build --release
stages+=("ACM: cargo build|$__LAST_RC|$__LAST_OUT|$__LAST_ERR")

# Stage: run Gemini-Box analyze on fixture
GEMINI_BIN="$GEMINI_PATH/target/release/analyze"
if [[ -x "$GEMINI_BIN" ]]; then
  run_capture "GEMINI-BOX: analyze (bin)" "$GEMINI_PATH" "$GEMINI_BIN" "$FIXTURE_PATH"
else
  run_capture "GEMINI-BOX: analyze (cargo run)" "$GEMINI_PATH" cargo run --release --bin analyze -- "$FIXTURE_PATH"
fi
stages+=("GEMINI-BOX: analyze|$__LAST_RC|$__LAST_OUT|$__LAST_ERR")

# Stage: EVK verify (cert)
EVK_BIN="$EVK_PATH/target/release/evk"
if [[ -x "$EVK_BIN" ]]; then
  run_capture "EVK: verify (bin)" "$EVK_PATH" "$EVK_BIN" verify --bundle "$FIXTURE_PATH" --cert
else
  run_capture "EVK: verify (cargo run)" "$EVK_PATH" cargo run --release -- verify --bundle "$FIXTURE_PATH" --cert
fi
stages+=("EVK: verify|$__LAST_RC|$__LAST_OUT|$__LAST_ERR")

# Stage: ACM verify (--json)
ACM_BIN="$ACM_PATH/target/release/evk"
if [[ -x "$ACM_BIN" ]]; then
  run_capture "ACM: verify (bin)" "$ACM_PATH" "$ACM_BIN" verify --bundle "$FIXTURE_PATH" --json
else
  run_capture "ACM: verify (cargo run)" "$ACM_PATH" cargo run --release --bin evk -- verify "$FIXTURE_PATH" --json
fi
stages+=("ACM: verify|$__LAST_RC|$__LAST_OUT|$__LAST_ERR")

# Produce JSON, HTML, Evidence HTML
timestamp="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
summary_evk="FAIL"
summary_gem="FAIL"
summary_acm="FAIL"

jq_escape() { python3 - <<PY
import json,sys
s=sys.stdin.read()
print(json.dumps(s))
PY
}

json_entries=()
for s in "${stages[@]}"; do
  IFS='|' read -r name rc out err <<< "$s"
  pass_flag="false"
  if [[ "$rc" -eq 0 ]]; then pass_flag="true"; fi
  case "$name" in
    "EVK: verify"*|"EVK: cargo build"*)
      if [[ "$pass_flag" == "true" ]]; then summary_evk="PASS"; fi
      ;;
    "GEMINI-BOX: analyze"*|"GEMINI-BOX: cargo build"*)
      if [[ "$pass_flag" == "true" ]]; then summary_gem="PASS"; fi
      ;;
    "ACM: verify"*|"ACM: cargo build"*)
      if [[ "$pass_flag" == "true" ]]; then summary_acm="PASS"; fi
      ;;
  esac
  json_entries+=("{\"name\":$(printf '%q' "$name"),\"pass\":$pass_flag,\"rc\":$rc,\"output\":$(jq_escape <<<"$out"),\"error\":$(jq_escape <<<"$err"),\"timestamp\":\"$timestamp\"}")
done

{
  echo "{"
  echo "  \"generated_at\": $(jq_escape <<<"$timestamp"),"
  echo "  \"evk_path\": $(jq_escape <<<"$EVK_PATH"),"
  echo "  \"gemini_path\": $(jq_escape <<<"$GEMINI_PATH"),"
  echo "  \"acm_path\": $(jq_escape <<<"$ACM_PATH"),"
  echo "  \"fixture\": $(jq_escape <<<"$FIXTURE_PATH"),"
  echo "  \"stages\": ["
  sep=""
  for e in "${json_entries[@]}"; do
    echo "    $sep$e"
    sep="," 
  done
  echo "  ],"
  echo "  \"summary\": {"
  echo "    \"EVK\": $(jq_escape <<<"$summary_evk"),"
  echo "    \"GEMINI-BOX\": $(jq_escape <<<"$summary_gem"),"
  echo "    \"COMPLIANCE_MATRIX\": $(jq_escape <<<"$summary_acm")"
  echo "  }"
  echo "}"
} > "$OUT_JSON"

# Create HTML summary
cat > "$OUT_HTML" <<HTML
<!doctype html>
<html>
<head><meta charset="utf-8"><title>Z-12 Demo Report</title>
<style>body{font-family:Arial,Helvetica,sans-serif;margin:18px}table{border-collapse:collapse;width:100%}th,td{border:1px solid #ccc;padding:8px;text-align:left}th{background:#f6f6f6}</style>
</head>
<body>
<h1>Z-12 PLATFORM STATUS</h1>
<p>Generated: $timestamp (SOURCE_DATE_EPOCH=$SOURCE_DATE_EPOCH)</p>
<table>
<tr><th>Component</th><th>Status</th><th>Return Code</th><th>Output (truncated)</th></tr>
HTML

for s in "${stages[@]}"; do
  IFS='|' read -r name rc out err <<< "$s"
  if [[ "$rc" -eq 0 ]]; then status="PASS"; else status="FAIL"; fi
  out_short="$(printf "%s" "$out" | sed -n '1,200p' | sed 's/&/\&amp;/g; s/</\&lt;/g; s/>/\&gt;/g')"
  printf "<tr><td>%s</td><td>%s</td><td>%s</td><td><pre>%s</pre></td></tr>\n" "$name" "$status" "$rc" "$out_short" >> "$OUT_HTML"

done

cat >> "$OUT_HTML" <<HTML
</table>
<p>JSON report: <code>$(basename "$OUT_JSON")</code></p>
<p>Evidence report (PDF-ready): <code>$(basename "$OUT_EVIDENCE")</code></p>
</body>
</html>
HTML

# Create Evidence HTML (printable)
cat > "$OUT_EVIDENCE" <<HTML
<!doctype html>
<html>
<head><meta charset="utf-8"><title>Z-12 Evidence Report</title>
<style>body{font-family: Helvetica,Arial,sans-serif;margin:18px}pre{background:#fafafa;border:1px solid #eee;padding:12px;overflow:auto}</style>
</head>
<body>
<h1>Z-12 EVIDENCE REPORT</h1>
<p>Generated: $timestamp (SOURCE_DATE_EPOCH=$SOURCE_DATE_EPOCH)</p>
HTML

for s in "${stages[@]}"; do
  IFS='|' read -r name rc out err <<< "$s"
  if [[ "$rc" -eq 0 ]]; then status="PASS"; else status="FAIL"; fi
  cat >> "$OUT_EVIDENCE" <<HTML
<h2>$name — $status (rc=$rc)</h2>
<h3>stdout</h3>
<pre>$(printf "%s" "$out" | sed 's/&/\&amp;/g; s/</\&lt;/g; s/>/\&gt;/g')</pre>
<h3>stderr</h3>
<pre>$(printf "%s" "$err" | sed 's/&/\&amp;/g; s/</\&lt;/g; s/>/\&gt;/g')</pre>
HTML

done

cat >> "$OUT_EVIDENCE" <<HTML
</body>
</html>
HTML

# Print final short status to stdout
echo
echo "Z-12 PLATFORM STATUS"
echo
echo "EVK:    $summary_evk"
echo "GEMINI-BOX: $summary_gem"
echo "COMPLIANCE MATRIX: $summary_acm"
echo
echo "Reports:"
echo "  JSON:    $OUT_JSON"
echo "  HTML:    $OUT_HTML"
echo "  EVIDENCE: $OUT_EVIDENCE"

if [[ "$summary_evk" == "PASS" && "$summary_gem" == "PASS" && "$summary_acm" == "PASS" ]]; then
  exit 0
else
  exit 1
fi
