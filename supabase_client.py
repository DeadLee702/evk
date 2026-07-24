#!/usr/bin/env python3
"""Z-12 Supabase persistence layer — stores scans, gauntlet runs, and audit events."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

# Load .env file if present
_env_path = Path(__file__).resolve().parent.parent / ".env"
if _env_path.exists():
    for _line in _env_path.read_text().splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _key, _, _val = _line.partition("=")
            os.environ.setdefault(_key.strip(), _val.strip())

SUPABASE_URL = os.environ.get("VITE_SUPABASE_URL") or os.environ.get("SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.environ.get("VITE_SUPABASE_ANON_KEY") or os.environ.get("SUPABASE_ANON_KEY", "")


def _post(table: str, payload: dict[str, Any]) -> dict[str, Any] | None:
    """Insert a row into a Supabase table via the REST API. Returns the inserted row or None."""
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        return None
    import urllib.request
    import urllib.error

    url = f"{SUPABASE_URL}/rest/v1/{table}"
    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body) if body else None
    except (urllib.error.URLError, urllib.error.HTTPError, OSError):
        return None


def _get(table: str, params: str = "") -> list[dict[str, Any]]:
    """Fetch rows from a Supabase table via the REST API."""
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        return []
    import urllib.request
    import urllib.error

    url = f"{SUPABASE_URL}/rest/v1/{table}?{params}" if params else f"{SUPABASE_URL}/rest/v1/{table}"
    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
    }
    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body) if body else []
    except (urllib.error.URLError, urllib.error.HTTPError, OSError):
        return []


def store_scan(artifact_name: str, status_code: str, verdict: str,
               incident_type: str, severity: str, enforcement_action: str,
               confidence: float, report: dict) -> None:
    """Persist a scan result to the z12_scans table."""
    _post("z12_scans", {
        "artifact_name": artifact_name,
        "status_code": status_code,
        "verdict": verdict,
        "incident_type": incident_type,
        "severity": severity,
        "enforcement_action": enforcement_action,
        "confidence": confidence,
        "report_json": json.dumps(report),
    })


def store_gauntlet_run(report: dict) -> None:
    """Persist a gauntlet run to the z12_gauntlet_runs table."""
    _post("z12_gauntlet_runs", {
        "gauntlet_status": report.get("gauntlet_status"),
        "total_rooms": report.get("total_rooms"),
        "rooms_healthy": report.get("rooms_healthy"),
        "rooms_failed": report.get("rooms_failed"),
        "health_score": report.get("health_score"),
        "cop_score": report.get("cop_score"),
        "evk_core_status": report.get("audit_results", {}).get("evk_core"),
        "full_report": json.dumps(report),
    })


def store_audit_event(event_type: str, component: str, severity: str,
                      action: str, details: dict, message: str) -> None:
    """Persist an audit event to the z12_audit_log table."""
    _post("z12_audit_log", {
        "event_type": event_type,
        "component": component,
        "severity": severity,
        "action": action,
        "details": json.dumps(details),
        "message": message,
    })


def get_recent_scans(limit: int = 20) -> list[dict[str, Any]]:
    """Fetch recent scans from Supabase."""
    return _get("z12_scans", f"order=created_at.desc&limit={limit}")


def get_recent_gauntlet_runs(limit: int = 10) -> list[dict[str, Any]]:
    """Fetch recent gauntlet runs from Supabase."""
    return _get("z12_gauntlet_runs", f"order=created_at.desc&limit={limit}")


def get_recent_audit_events(limit: int = 50) -> list[dict[str, Any]]:
    """Fetch recent audit events from Supabase."""
    return _get("z12_audit_log", f"order=created_at.desc&limit={limit}")


def store_enforcement_request(req: dict[str, Any]) -> dict[str, Any] | None:
    """Persist an enforcement request to the z12_enforcement_requests table."""
    return _post("z12_enforcement_requests", {
        "request_id": req.get("id"),
        "pid": req.get("pid"),
        "reason": req.get("reason"),
        "lineage": req.get("lineage"),
        "status": req.get("status"),
        "decided_by": req.get("decided_by"),
    })


def update_enforcement_status(request_id: str, status: str,
                               decided_by: str = "") -> dict[str, Any] | None:
    """Update an enforcement request status via the REST API (PATCH)."""
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        return None
    import urllib.request
    import urllib.error

    url = f"{SUPABASE_URL}/rest/v1/z12_enforcement_requests?request_id=eq.{request_id}"
    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }
    payload = json.dumps({"status": status, "decided_by": decided_by}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers=headers, method="PATCH")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body) if body else None
    except (urllib.error.URLError, urllib.error.HTTPError, OSError):
        return None


def get_enforcement_requests(limit: int = 50) -> list[dict[str, Any]]:
    """Fetch enforcement requests from Supabase."""
    return _get("z12_enforcement_requests", f"order=created_at.desc&limit={limit}")
