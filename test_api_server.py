import api_server
from auth import hash_password
from db_manager import get_database


class _DummyDB:
    def get_setting(self, key, default=None):
        return "TEST_COMPANY"

    def get_statistics(self):
        return {
            "total_products": 1,
            "total_clients": 2,
            "total_sales": 3,
            "total_purchases": 4,
            "sales_total": 100.0,
            "stock_value": 50.0,
        }


def _create_user(username="api_tester", password="secret123", role="admin"):
    db = get_database()
    db.cursor.execute(
        """
        INSERT INTO users (username, password_hash, role, is_active)
        VALUES (?, ?, ?, 1)
        """,
        (username, hash_password(password), role),
    )
    db.conn.commit()
    return db


def test_ping_without_token(monkeypatch):
    monkeypatch.setattr(api_server, "get_database", lambda: _DummyDB())
    client = api_server.app.test_client()

    response = client.get("/api/ping")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True
    assert payload["message"] == "pong"


def test_status_requires_token(monkeypatch):
    monkeypatch.setattr(api_server, "get_database", lambda: _DummyDB())
    client = api_server.app.test_client()

    response = client.get("/api/status")
    assert response.status_code == 401


def test_status_accepts_bearer_token(monkeypatch):
    monkeypatch.setattr(api_server, "get_database", lambda: _DummyDB())
    monkeypatch.setattr(api_server, "API_TOKEN", "test-token")
    client = api_server.app.test_client()

    response = client.get(
        "/api/status", headers={"Authorization": "Bearer test-token"}
    )
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True


def test_login_masks_internal_errors(monkeypatch):
    def _boom():
        raise RuntimeError("secret stack details")

    monkeypatch.setattr(api_server, "get_database", _boom)
    client = api_server.app.test_client()

    response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "pw"},
    )
    assert response.status_code == 500
    payload = response.get_json()
    assert payload["success"] is False
    assert payload["error"] == "Erreur interne du serveur"


def test_login_returns_dynamic_token():
    _create_user(username="u_login", password="pw_login")
    client = api_server.app.test_client()

    response = client.post(
        "/api/auth/login",
        json={"username": "u_login", "password": "pw_login"},
    )
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True
    data = payload["data"]
    assert data["access_token"]
    assert data["token_type"] == "Bearer"
    assert data["expires_at"]


def test_rotate_then_revoke_token_flow():
    _create_user(username="u_rotate", password="pw_rotate")
    client = api_server.app.test_client()

    login = client.post(
        "/api/auth/login",
        json={"username": "u_rotate", "password": "pw_rotate"},
    )
    token = login.get_json()["data"]["access_token"]

    rotate = client.post(
        "/api/auth/rotate",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert rotate.status_code == 200
    rotated = rotate.get_json()["data"]["access_token"]
    assert rotated and rotated != token

    old_use = client.get(
        "/api/status",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert old_use.status_code == 401

    ok_use = client.get(
        "/api/status",
        headers={"Authorization": f"Bearer {rotated}"},
    )
    assert ok_use.status_code == 200

    revoke = client.post(
        "/api/auth/revoke",
        headers={"Authorization": f"Bearer {rotated}"},
    )
    assert revoke.status_code == 200

    revoked_use = client.get(
        "/api/status",
        headers={"Authorization": f"Bearer {rotated}"},
    )
    assert revoked_use.status_code == 401


def test_expired_token_is_rejected():
    db = _create_user(username="u_expired", password="pw_expired")
    token = "expired-token-123"
    token_hash = api_server._hash_token(token)
    db.cursor.execute(
        """
        INSERT INTO api_tokens(token_hash, expires_at, is_revoked, created_by_user_id)
        VALUES (?, ?, 0, 1)
        """,
        (token_hash, "2000-01-01 00:00:00"),
    )
    db.conn.commit()

    client = api_server.app.test_client()
    response = client.get(
        "/api/status",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 401


def test_ip_whitelist_blocks_non_allowed_ip(monkeypatch):
    monkeypatch.setattr(api_server, "API_ALLOWED_SUBNETS", ["10.0.0.0/8"])
    monkeypatch.setattr(api_server, "API_TOKEN", "test-token")
    api_server._rate_limit_state.clear()
    monkeypatch.setattr(api_server, "get_database", lambda: _DummyDB())
    client = api_server.app.test_client()

    response = client.get(
        "/api/status",
        headers={"Authorization": "Bearer test-token"},
        environ_overrides={"REMOTE_ADDR": "127.0.0.1"},
    )
    assert response.status_code == 403


def test_rate_limit_returns_429(monkeypatch):
    monkeypatch.setattr(api_server, "API_ALLOWED_SUBNETS", [])
    monkeypatch.setattr(api_server, "API_TOKEN", "test-token")
    monkeypatch.setattr(api_server, "API_RATE_LIMIT_MAX_REQUESTS", 2)
    monkeypatch.setattr(api_server, "API_RATE_LIMIT_WINDOW_SEC", 60)
    api_server._rate_limit_state.clear()
    monkeypatch.setattr(api_server, "get_database", lambda: _DummyDB())
    client = api_server.app.test_client()

    h = {"Authorization": "Bearer test-token"}
    r1 = client.get("/api/status", headers=h, environ_overrides={"REMOTE_ADDR": "127.0.0.1"})
    r2 = client.get("/api/status", headers=h, environ_overrides={"REMOTE_ADDR": "127.0.0.1"})
    r3 = client.get("/api/status", headers=h, environ_overrides={"REMOTE_ADDR": "127.0.0.1"})
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r3.status_code == 429


def test_failed_login_writes_security_audit():
    db = _create_user(username="u_audit_fail", password="pw_ok")
    client = api_server.app.test_client()

    before = db.cursor.execute("SELECT COUNT(*) FROM audit_log").fetchone()[0]
    response = client.post(
        "/api/auth/login",
        json={"username": "u_audit_fail", "password": "wrong_pw"},
    )
    after = db.cursor.execute("SELECT COUNT(*) FROM audit_log").fetchone()[0]

    assert response.status_code == 401
    assert after >= before + 1
