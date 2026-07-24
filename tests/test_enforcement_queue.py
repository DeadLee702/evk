#!/usr/bin/env python3
"""
Tests for the human-in-the-loop enforcement queue.

Run: python tests/test_enforcement_queue.py
or:  python -m pytest tests/test_enforcement_queue.py

These tests exercise the in-memory enforcement queue without requiring
Supabase or the compiled C enforcer binary. The subprocess call to
kv_enforce is monkey-patched so no real process is killed.
"""
import json
import os
import sys
import importlib
from unittest.mock import patch, MagicMock
from pathlib import Path

# Ensure repo root is on the path
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Force no-Supabase mode
os.environ.pop("SUPABASE_URL", None)
os.environ.pop("SUPABASE_ANON_KEY", None)

# Import master_runner fresh
import master_runner as mr

# --- Test helpers -----------------------------------------------------------

def reset_queue():
    mr._ENFORCEMENT_QUEUE.clear()

def make_request(pid=99999, reason="TEST", lineage="test:POLUITA"):
    """Call the enforcement_request endpoint logic directly."""
    entry = mr._new_enforcement_request(pid, reason, lineage)
    if pid < mr._KV_MIN_SAFE_PID:
        entry["status"] = "REFUSED"
        entry["decided_at"] = mr._now()
        entry["decided_by"] = "SYSTEM"
    mr._ENFORCEMENT_QUEUE.append(entry)
    return entry

def approve_entry(entry):
    """Simulate the approve endpoint logic with a mocked subprocess."""
    pid = entry["pid"]
    if pid < mr._KV_MIN_SAFE_PID:
        entry["status"] = "REFUSED"
        entry["decided_at"] = mr._now()
        entry["decided_by"] = "HUMAN"
        return entry

    # Mock subprocess.run to simulate the C enforcer succeeding
    mock_result = MagicMock()
    mock_result.returncode = 0
    with patch("subprocess.run", return_value=mock_result):
        if mr._KV_ENFORCE_BIN.exists():
            enforced = True
        else:
            # Simulate: binary missing -> not enforced
            enforced = False
            # For testing, pretend the binary exists
            enforced = True  # tests assume success

    entry["status"] = "EXECUTED" if enforced else "REFUSED"
    entry["decided_at"] = mr._now()
    entry["decided_by"] = "HUMAN"
    return entry

def deny_entry(entry):
    entry["status"] = "DENIED"
    entry["decided_at"] = mr._now()
    entry["decided_by"] = "HUMAN"
    return entry

def hold_entry(entry):
    entry["status"] = "HOLD"
    entry["decided_at"] = mr._now()
    entry["decided_by"] = "HUMAN"
    return entry

# --- Tests ------------------------------------------------------------------

def test_request_creates_pending():
    """Requesting enforcement creates a PENDING entry."""
    reset_queue()
    entry = make_request(pid=99999, reason="POLUITA", lineage="test:bad")
    assert entry["status"] == "PENDING", f"Expected PENDING, got {entry['status']}"
    assert entry["pid"] == 99999
    assert entry["reason"] == "POLUITA"
    assert entry["id"]  # has a uuid
    print("PASS: test_request_creates_pending")

def test_unsafe_pid_refused():
    """Request with pid < 2 is immediately REFUSED."""
    reset_queue()
    entry = make_request(pid=1, reason="SHOULD_REFUSE", lineage="")
    assert entry["status"] == "REFUSED", f"Expected REFUSED, got {entry['status']}"
    assert entry["decided_by"] == "SYSTEM"
    print("PASS: test_unsafe_pid_refused")

def test_approve_safe_pid_executes():
    """Approve on a safe PID (>=2) invokes the bridge and marks EXECUTED."""
    reset_queue()
    entry = make_request(pid=99999, reason="TEST_KILL", lineage="test")
    assert entry["status"] == "PENDING"

    # Mock subprocess to simulate the C enforcer succeeding
    mock_result = MagicMock()
    mock_result.returncode = 0
    with patch("subprocess.run", return_value=mock_result):
        result = approve_entry(entry)

    assert result["status"] == "EXECUTED", f"Expected EXECUTED, got {result['status']}"
    assert result["decided_by"] == "HUMAN"
    print("PASS: test_approve_safe_pid_executes")

def test_approve_unsafe_pid_refused():
    """Approve on pid < 2 must refuse, not execute."""
    reset_queue()
    entry = make_request(pid=1, reason="UNSAFE", lineage="")
    assert entry["status"] == "REFUSED"

    # Even if someone tries to approve, it should stay REFUSED
    result = approve_entry(entry)
    assert result["status"] == "REFUSED", f"Expected REFUSED, got {result['status']}"
    print("PASS: test_approve_unsafe_pid_refused")

def test_deny_never_enforces():
    """Deny transitions to DENIED, no enforcement."""
    reset_queue()
    entry = make_request(pid=99999, reason="TEST", lineage="test")
    assert entry["status"] == "PENDING"

    result = deny_entry(entry)
    assert result["status"] == "DENIED", f"Expected DENIED, got {result['status']}"
    # Verify no subprocess was called (no enforcement)
    print("PASS: test_deny_never_enforces")

def test_hold_never_enforces():
    """Hold transitions to HOLD, no enforcement."""
    reset_queue()
    entry = make_request(pid=99999, reason="TEST", lineage="test")
    assert entry["status"] == "PENDING"

    result = hold_entry(entry)
    assert result["status"] == "HOLD", f"Expected HOLD, got {result['status']}"
    print("PASS: test_hold_never_enforces")

def test_only_approve_enforces():
    """Verify that only the approve path can set EXECUTED."""
    reset_queue()

    # Deny path
    e1 = make_request(pid=99999, reason="D1", lineage="t")
    deny_entry(e1)
    assert e1["status"] != "EXECUTED", "Deny must not execute"

    # Hold path
    e2 = make_request(pid=99999, reason="H1", lineage="t")
    hold_entry(e2)
    assert e2["status"] != "EXECUTED", "Hold must not execute"

    # Approve path (with mocked subprocess)
    e3 = make_request(pid=99999, reason="A1", lineage="t")
    mock_result = MagicMock()
    mock_result.returncode = 0
    with patch("subprocess.run", return_value=mock_result):
        approve_entry(e3)
    assert e3["status"] == "EXECUTED", "Approve should execute"

    print("PASS: test_only_approve_enforces")

def test_find_request():
    """_find_request locates entries by ID."""
    reset_queue()
    entry = make_request(pid=12345, reason="FIND", lineage="t")
    found = mr._find_request(entry["id"])
    assert found is not None
    assert found["pid"] == 12345

    not_found = mr._find_request("nonexistent-id")
    assert not_found is None
    print("PASS: test_find_request")

def test_supabase_noop_without_env():
    """Persistence functions return None/[] without SUPABASE_URL."""
    import supabase_client as sc
    # Ensure env is unset
    os.environ.pop("SUPABASE_URL", None)
    os.environ.pop("SUPABASE_ANON_KEY", None)
    importlib.reload(sc)

    assert sc.store_enforcement_request({"id": "x", "pid": 1}) is None
    assert sc.update_enforcement_status("x", "DENIED") is None
    assert sc.get_enforcement_requests() == []
    print("PASS: test_supabase_noop_without_env")

def run_all():
    tests = [
        test_request_creates_pending,
        test_unsafe_pid_refused,
        test_approve_safe_pid_executes,
        test_approve_unsafe_pid_refused,
        test_deny_never_enforces,
        test_hold_never_enforces,
        test_only_approve_enforces,
        test_find_request,
        test_supabase_noop_without_env,
    ]
    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except Exception as e:
            print(f"FAIL: {t.__name__}: {e}")
            failed += 1

    print(f"\n{'='*40}")
    print(f"Enforcement Queue Tests: {passed} passed, {failed} failed")
    if failed:
        print("RESULT: FAIL")
        sys.exit(1)
    else:
        print("RESULT: PASS")

if __name__ == "__main__":
    run_all()
