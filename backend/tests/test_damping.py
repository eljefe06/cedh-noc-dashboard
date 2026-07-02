"""Tests for flap damping (scheduler.dampen_status) and latency thresholds.

These two pieces are the anti-false-positive core: a single transient
failure must never turn the dashboard red or open an incident.
"""
from __future__ import annotations

from app.collectors.http import _latency_status
from app.scheduler import _CONFIRM_FAILS, dampen_status


# ─── dampen_status ────────────────────────────────────────────────────────────

def test_single_failure_does_not_confirm_down():
    damp: dict = {}
    dampen_status("srv/svc", "ok", damp)
    assert dampen_status("srv/svc", "down", damp) == "ok"  # keeps last known good


def test_consecutive_failures_confirm_down():
    damp: dict = {}
    dampen_status("srv/svc", "ok", damp)
    for _ in range(_CONFIRM_FAILS - 1):
        assert dampen_status("srv/svc", "down", damp) == "ok"
    assert dampen_status("srv/svc", "down", damp) == "down"


def test_critical_also_requires_confirmation():
    damp: dict = {}
    dampen_status("srv/svc", "ok", damp)
    assert dampen_status("srv/svc", "critical", damp) == "ok"
    assert dampen_status("srv/svc", "critical", damp) == "critical"


def test_good_cycle_resets_counter():
    damp: dict = {}
    dampen_status("srv/svc", "ok", damp)
    dampen_status("srv/svc", "down", damp)          # 1 fail
    assert dampen_status("srv/svc", "ok", damp) == "ok"   # reset
    assert dampen_status("srv/svc", "down", damp) == "ok"  # counting from zero again


def test_recovery_is_immediate():
    damp: dict = {}
    dampen_status("srv/svc", "down", damp)
    dampen_status("srv/svc", "down", damp)  # confirmed down
    assert dampen_status("srv/svc", "ok", damp) == "ok"  # no delay on recovery


def test_warning_passes_through_immediately():
    damp: dict = {}
    dampen_status("srv/svc", "ok", damp)
    assert dampen_status("srv/svc", "warning", damp) == "warning"


def test_cold_start_failure_shows_unknown_not_down():
    damp: dict = {}
    assert dampen_status("srv/svc", "down", damp) == "unknown"


def test_cold_start_sustained_failure_confirms_down():
    damp: dict = {}
    for _ in range(_CONFIRM_FAILS - 1):
        assert dampen_status("srv/svc", "down", damp) == "unknown"
    assert dampen_status("srv/svc", "down", damp) == "down"


def test_targets_are_independent():
    damp: dict = {}
    dampen_status("srv/a", "ok", damp)
    dampen_status("srv/b", "ok", damp)
    dampen_status("srv/a", "down", damp)
    assert dampen_status("srv/a", "down", damp) == "down"
    assert dampen_status("srv/b", "ok", damp) == "ok"


def test_flapping_service_never_confirms():
    """down/ok/down/ok... alternation must never show red."""
    damp: dict = {}
    dampen_status("srv/svc", "ok", damp)
    for _ in range(10):
        assert dampen_status("srv/svc", "down", damp) == "ok"
        assert dampen_status("srv/svc", "ok", damp) == "ok"


# ─── _latency_status ──────────────────────────────────────────────────────────

def test_latency_none_is_down():
    assert _latency_status(None) == "down"


def test_latency_fast_is_ok():
    assert _latency_status(180) == "ok"
    assert _latency_status(1499) == "ok"


def test_latency_slow_is_warning_never_critical():
    assert _latency_status(1500) == "warning"
    assert _latency_status(5000) == "warning"
    assert _latency_status(60000) == "warning"
