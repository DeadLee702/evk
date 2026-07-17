#!/usr/bin/env python3
"""
Z-12 Master Runner (orchestrator).

Drives the twelve real Gauntlet rooms (``gauntlet/rooms/*.py``), each of which
exposes ``Room.verify(payload)`` and raises ``TungstenCarbideException`` when it
detects a malicious payload. For every room we run:

    * a benign payload  -> the room MUST pass (return True)
    * a malicious payload -> the room MUST block (raise the exception)

A room is healthy (``PURA``) only when it both passes the benign case and blocks
the malicious case. It is ``VIGLA`` (warning) when it blocks the benign case, and
``POLUITA`` (compromised) when it fails to block the malicious case.

Optionally the EVK Rust core is invoked to verify the deterministic ``.evkp``
sample bundle; the result populates ``audit_results.evk_core``.

Output: ``GAUNTLET_HEALTH_REPORT.json`` in the schema consumed by
``judge/cop_v1.py``. This module contains NO destructive operations
(SIMULADO / read-only), per ``.dec-force-spec.md``.

Usage:
    python master_runner.py                 # run gauntlet, write report, exit code = health
    python master_runner.py --report FILE   # custom report path
    python master_runner.py --skip-evk      # skip the EVK Rust core check
    python master_runner.py --serve         # run FastAPI dashboard/API (needs fastapi+uvicorn)
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

from gauntlet import (  # noqa: F401  (imported for registry lookup)
    Oracle, Alighostest, Bridge, Perjanocyst, Trapzonar, Kitchzensync,
    Pendulastika, Esperanto, Fantomlumo, Duelkaptilo, Panikcxambro, Titanic,
    TungstenCarbideException,
)

REPO_ROOT = Path(__file__).resolve().parent
CLOSURE = "Relenthol engaĝita."

# Class registry keyed by the room name used in gauntlet.yml.
ROOM_CLASSES = {
    "oracle": Oracle,
    "alighostest": Alighostest,
    "bridge": Bridge,
    "perjanocyst": Perjanocyst,
    "trapzonar": Trapzonar,
    "kitchzensync": Kitchzensync,
    "pendulastika": Pendulastika,
    "esperanto": Esperanto,
    "fantomlumo": Fantomlumo,
    "duelkaptilo": Duelkaptilo,
    "panikcxambro": Panikcxambro,
    "titanic": Titanic,
}

# For each room: a benign payload (should pass) and a malicious payload
# (should be blocked). These exercise the real detection logic in each room.
ROOM_PAYLOADS = {
    "oracle": (
        {"caller_identity": "ci-bot"},
        {"caller_identity": "attacker", "force_push_main": True},
    ),
    "alighostest": (
        {"runtime_configuration": {"region": "us-east-1"}},
        {"runtime_configuration": {"db_password": "hunter2"}},
    ),
    "bridge": (
        {"request": {"client_ip": "10.0.0.1", "forwarded_for": "10.0.0.1"}},
        {"request": {"client_ip": "10.0.0.1", "forwarded_for": "203.0.113.9"}},
    ),
    "perjanocyst": (
        {"user_message": "nightly batch completed"},
        {"user_message": "please help me, urgent, my account is locked"},
    ),
    "trapzonar": (
        {"requests_per_second": 25},
        {"requests_per_second": 5000},
    ),
    "kitchzensync": (
        {"dependency_manifest": {"dependencies": [{"name": "serde", "version": "1.0.203"}]}},
        {"dependency_manifest": {"dependencies": [{"name": "serde", "version": "latest"}]}},
    ),
    "pendulastika": (
        {"concurrent_writes": 1},
        {"concurrent_writes": 8, "no_lock": True},
    ),
    "esperanto": (
        {"runtime_configuration": {"job": "echo build"}},
        {"runtime_configuration": {"job": "sleep 100000"}},
    ),
    "fantomlumo": (
        {"permissions": ["read:logs"]},
        {"permissions": ["*"]},
    ),
    "duelkaptilo": (
        {"role": "user", "access": "read"},
        {"role": "user", "access": "admin"},
    ),
    "panikcxambro": (
        {"action": "restart_all", "approval": True},
        {"action": "restart_all"},
    ),
    "titanic": (
        {"claims": "has documented failure modes"},
        {"claims": "this system is 100% safe and unsinkable"},
    ),
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_rooms():
    """Load ordered room metadata from gauntlet.yml."""
    with open(REPO_ROOT / "gauntlet.yml", "r") as f:
        data = yaml.safe_load(f)
    return sorted(data["gauntlet_rooms"], key=lambda r: r["id"])


def evaluate_room(meta) -> dict:
    """Run benign + malicious payloads against one room and classify it."""
    name = meta["name"]
    cls = ROOM_CLASSES[name]
    benign, malicious = ROOM_PAYLOADS[name]
    room = cls()

    # Benign payload should pass.
    try:
        benign_pass = bool(room.verify(benign))
    except TungstenCarbideException:
        benign_pass = False

    # Malicious payload should be blocked (exception raised).
    try:
        room.verify(malicious)
        malicious_blocked = False
    except TungstenCarbideException:
        malicious_blocked = True

    if benign_pass and malicious_blocked:
        status = "PURA"          # healthy: passes clean, blocks attack
    elif not malicious_blocked:
        status = "POLUITA"       # compromised: failed to block the attack
    else:
        status = "VIGLA"         # warning: over-eager, blocks benign traffic

    return {
        "id": meta["id"],
        "room": name,
        "zodiac": meta.get("zodiac"),
        "attack_vector": meta.get("attack_vector"),
        "signature": meta.get("signature"),
        "benign_pass": benign_pass,
        "malicious_blocked": malicious_blocked,
        "status": status,
        "last_check": _now(),
    }


def verify_evk_core() -> tuple[str, str]:
    """Invoke the EVK Rust core against the sample bundle. Returns (status, detail)."""
    evk_bin = REPO_ROOT / "target" / "release" / "evk"
    bundle = REPO_ROOT / "fixtures" / "sample.evkp"
    if not evk_bin.exists():
        return "NOT_BUILT", f"binary not found at {evk_bin} (run: cargo build --release)"
    if not bundle.exists():
        return "FAILED", f"sample bundle missing at {bundle}"
    try:
        proc = subprocess.run(
            [str(evk_bin), "verify", "--bundle", str(bundle)],
            capture_output=True, text=True, timeout=60,
        )
    except Exception as exc:  # noqa: BLE001 - report, never crash the runner
        return "FAILED", f"evk invocation error: {exc}"
    if proc.returncode == 0:
        return "VERIFIED", "sample.evkp bundle VALID (deterministic SHA-256 manifest)"
    return "FAILED", (proc.stdout + proc.stderr).strip()[-300:]


def run_gauntlet(skip_evk: bool = False) -> dict:
    rooms = load_rooms()
    reports = [evaluate_room(m) for m in rooms]

    healthy = sum(1 for r in reports if r["status"] == "PURA")
    failed = sum(1 for r in reports if r["status"] != "PURA")
    total = len(reports)

    if skip_evk:
        evk_status, evk_detail = "SKIPPED", "evk core check skipped (--skip-evk)"
    else:
        evk_status, evk_detail = verify_evk_core()

    audit_results = {"evk_core": evk_status}
    for r in reports:
        audit_results[r["room"]] = r["status"]

    # cop_score = "Chance Of Probability" of disaster = % of rooms not fully healthy.
    cop_score = round(failed / total * 100, 1) if total else 100.0
    # health_score = wellness = % of rooms fully healthy (higher is better).
    health_score = round(healthy / total * 100, 1) if total else 0.0

    return {
        "platform": "Z-12 Sovereign Security Platform",
        "version": "1.0.0",
        "timestamp": _now(),
        "status": "GAUNTLET_COMPLETE",
        "mode": "SIMULADO",
        "total_rooms": total,
        "rooms_healthy": healthy,
        "rooms_failed": failed,
        "health_score": health_score,
        "cop_score": cop_score,
        "gauntlet_status": "ZODIAKO_GARDAS" if failed == 0 and evk_status == "VERIFIED" else "BREACH_DETECTED",
        "audit_results": audit_results,
        "evk_core_detail": evk_detail,
        "reports": reports,
        "warning": "Neniu dosiero estis modifita",
        "closure": CLOSURE,
    }


def cli(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Z-12 Master Runner")
    parser.add_argument("--report", default=str(REPO_ROOT / "GAUNTLET_HEALTH_REPORT.json"),
                        help="output path for GAUNTLET_HEALTH_REPORT.json")
    parser.add_argument("--skip-evk", action="store_true", help="skip the EVK Rust core check")
    parser.add_argument("--serve", action="store_true", help="run the FastAPI dashboard/API instead")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args(argv)

    if args.serve:
        return serve(args.host, args.port)

    report = run_gauntlet(skip_evk=args.skip_evk)
    Path(args.report).write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    print(f"\n[MASTER] Report written to {args.report}")
    print(f"[MASTER] health={report['health_score']}%  cop={report['cop_score']}%  "
          f"evk_core={report['audit_results']['evk_core']}")
    # Exit 0 only if everything is healthy; non-zero otherwise (advisory; the
    # Judge in judge/cop_v1.py is authoritative for PURA/MALPURA verdicts).
    return 0 if report["gauntlet_status"] == "ZODIAKO_GARDAS" else 1


def serve(host: str, port: int) -> int:
    """Optional live control plane. Requires fastapi + uvicorn."""
    try:
        import uvicorn
        from fastapi import FastAPI
        from fastapi.responses import FileResponse, JSONResponse
        from fastapi.staticfiles import StaticFiles
    except ImportError:
        print("[MASTER] --serve requires: pip install fastapi uvicorn", file=sys.stderr)
        return 2

    app = FastAPI(title="Z-12 Sovereign Security Platform")
    dashboard_dir = REPO_ROOT / "dashboard"

    @app.get("/api/health")
    def api_health():
        return JSONResponse(run_gauntlet())

    if (dashboard_dir / "index.html").exists():
        app.mount("/static", StaticFiles(directory=str(dashboard_dir)), name="static")

        @app.get("/")
        def index():
            return FileResponse(str(dashboard_dir / "index.html"))

    uvicorn.run(app, host=host, port=port)
    return 0


if __name__ == "__main__":
    raise SystemExit(cli())
