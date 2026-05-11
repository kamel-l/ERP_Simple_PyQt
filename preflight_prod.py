#!/usr/bin/env python3
"""
Preflight production checks for ERP_Simple_PyQt.

Usage:
  python preflight_prod.py
"""

from __future__ import annotations

import os
import sqlite3
import json
from urllib import request as urlrequest
from urllib.error import URLError, HTTPError


DB_PATH = "erp_database.db"
API_BASE = os.getenv("ERP_API_BASE_URL", "http://127.0.0.1:5000")


def check_env() -> list[dict]:
    checks = []
    expected = {
        "ERP_API_STRICT_DYNAMIC_TOKENS": "true",
        "ERP_API_RATE_LIMIT_MAX_REQUESTS": "120",
        "ERP_API_RATE_LIMIT_WINDOW_SEC": "60",
        "ERP_API_TOKEN_TTL_HOURS": "12",
    }
    for key, wanted in expected.items():
        val = os.getenv(key)
        ok = val is not None
        checks.append(
            {
                "name": f"env:{key}",
                "ok": ok,
                "value": val,
                "hint": f"expected around '{wanted}'" if ok else f"missing; recommended '{wanted}'",
            }
        )
    subnet = os.getenv("ERP_API_ALLOWED_SUBNETS")
    checks.append(
        {
            "name": "env:ERP_API_ALLOWED_SUBNETS",
            "ok": subnet is not None and subnet.strip() != "",
            "value": subnet,
            "hint": "set LAN CIDR list like 192.168.1.0/24,10.0.0.0/8",
        }
    )
    return checks


def check_db() -> list[dict]:
    checks = []
    if not os.path.exists(DB_PATH):
        return [{"name": "db:file", "ok": False, "hint": f"missing {DB_PATH}"}]

    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("PRAGMA integrity_check")
        row = cur.fetchone()
        checks.append({"name": "db:integrity", "ok": bool(row and row[0] == "ok"), "value": row[0] if row else None})

        for table in ("schema_migrations", "api_tokens", "audit_log", "users"):
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
            checks.append({"name": f"db:table:{table}", "ok": cur.fetchone() is not None})

        cur.execute("SELECT COUNT(*) FROM api_tokens WHERE is_revoked=0")
        checks.append({"name": "db:active_tokens_count", "ok": True, "value": cur.fetchone()[0]})
        conn.close()
    except Exception as exc:
        checks.append({"name": "db:exception", "ok": False, "hint": str(exc)})

    return checks


def _http_json(url: str, headers: dict | None = None) -> tuple[int, dict | None, str | None]:
    req = urlrequest.Request(url, headers=headers or {})
    try:
        with urlrequest.urlopen(req, timeout=4) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            try:
                return resp.getcode(), json.loads(body), None
            except Exception:
                return resp.getcode(), None, body
    except HTTPError as exc:
        try:
            body = exc.read().decode("utf-8", errors="replace")
        except Exception:
            body = None
        return exc.code, None, body
    except URLError as exc:
        return 0, None, str(exc)


def check_api() -> list[dict]:
    checks = []

    code, payload, err = _http_json(f"{API_BASE}/api/ping")
    checks.append({"name": "api:ping", "ok": code == 200, "value": code, "hint": err})

    code, _, err = _http_json(f"{API_BASE}/api/status")
    checks.append({"name": "api:status_requires_auth", "ok": code in (401, 403, 429), "value": code, "hint": err})

    return checks


def print_report(items: list[dict]) -> int:
    failed = 0
    for it in items:
        ok = bool(it.get("ok"))
        status = "OK  " if ok else "FAIL"
        name = it.get("name", "?")
        value = it.get("value")
        hint = it.get("hint")
        line = f"[{status}] {name}"
        if value is not None:
            line += f" | value={value}"
        if hint:
            line += f" | {hint}"
        print(line)
        if not ok:
            failed += 1
    return failed


def main() -> int:
    print("== ERP Preflight Prod ==")
    failed = 0
    failed += print_report(check_env())
    failed += print_report(check_db())
    failed += print_report(check_api())
    print(f"\nSummary: {'PASS' if failed == 0 else 'FAIL'} ({failed} issue(s))")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

