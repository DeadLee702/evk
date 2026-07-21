#!/usr/bin/env python3
"""
Z-12 Judge — COP v1  (evolved from DEC FORCE 10 "JUDGE COP_v1").

Consumes GAUNTLET_HEALTH_REPORT.json and renders a PURA / MALPURA verdict.

Exit codes (per Phase 6 contract):
    0 = PURA             (clean, proceed)
    1 = MALPURA          (compromised, halt)
    2 = Critical failure (EVK core not verified, or report unreadable)

COP = "Chance Of Probability" of disaster. COP > 15% => HALT (MALPURA).
The threshold reads ``cop_score`` when present, falling back to the legacy
``health_score`` field for backward compatibility with older reports.
"""
import json
import sys

COP_THRESHOLD = 15.0

report_path = sys.argv[1] if len(sys.argv) > 1 else "GAUNTLET_HEALTH_REPORT.json"

try:
    with open(report_path) as f:
        report = json.load(f)
except (OSError, json.JSONDecodeError) as exc:
    print(f"[JUDGE] CRITICAL: cannot read report '{report_path}': {exc}")
    sys.exit(2)

# Rule 1: EVK Core must be VERIFIED (deterministic integrity is the trust anchor).
evk_core = report.get("audit_results", {}).get("evk_core")
if evk_core != "VERIFIED":
    print(f"[JUDGE] HALT: EVK Core malpura (evk_core={evk_core}). Kitchen is dirty.")
    sys.exit(2)

# Rule 2: COP score threshold.
cop_score = report.get("cop_score", report.get("health_score", 0.0))
if cop_score > COP_THRESHOLD:
    print(f"[JUDGE] HALT: COP Score {cop_score}% exceeds {COP_THRESHOLD}% threshold.")
    print("[JUDGE] VERDICT: MALPURA")
    sys.exit(1)

# Rule 3: Gauntlet must have completed.
if report.get("status") != "GAUNTLET_COMPLETE":
    print(f"[JUDGE] HALT: Gauntlet incomplete (status={report.get('status')}).")
    sys.exit(1)

print(f"[JUDGE] COP: {cop_score}% | VERDICT: PURA")
print("[JUDGE] Lingvo sen esceptoj. Relenthol engaĝita.")
sys.exit(0)
