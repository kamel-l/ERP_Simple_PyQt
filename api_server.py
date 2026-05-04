"""
api_server.py â€” Serveur API REST pour DAR ELSSALEM ERP
=======================================================
Lance un serveur Flask dans un thread sÃ©parÃ©.
Accessible en WiFi local ET via Internet (ngrok optionnel).

Endpoints :
  GET    /api/ping                  â†’ test de connexion
  GET    /api/produits              â†’ liste produits
  GET    /api/produits/<id>         â†’ un produit
  POST   /api/produits              â†’ crÃ©er produit
  PUT    /api/produits/<id>         â†’ modifier produit
  GET    /api/clients               â†’ liste clients
  POST   /api/clients               â†’ crÃ©er client
  PUT    /api/clients/<id>          â†’ modifier client
  GET    /api/ventes                â†’ liste ventes
  POST   /api/ventes                â†’ crÃ©er vente
  GET    /api/ventes/<id>           â†’ dÃ©tail vente
  GET    /api/factures              â†’ alias ventes
  GET    /api/sync                  â†’ tout d'un coup (sync complÃ¨te)
  POST   /api/sync/push             â†’ reÃ§oit donnÃ©es du mobile
  GET    /api/status                â†’ stats globales
"""

import threading
import hashlib
import json
import base64
import os
import re
import secrets
import logging
import ipaddress
from datetime import datetime, timedelta, timezone
from functools import wraps

from flask import Flask, jsonify, request, g
from db_manager import get_database
from auth import verify_password

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
#  Configuration
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

API_PORT    = 5000
API_HOST    = "127.0.0.1" if os.getenv("ERP_API_EXPOSE_NETWORK", "").lower() not in {"1", "true", "yes", "on"} else "0.0.0.0"
API_TOKEN   = os.getenv("ERP_API_TOKEN", "").strip() or secrets.token_urlsafe(24)
API_VERSION = "1.0.0"
API_TOKEN_TTL_HOURS = int(os.getenv("ERP_API_TOKEN_TTL_HOURS", "12"))
API_RATE_LIMIT_MAX_REQUESTS = int(os.getenv("ERP_API_RATE_LIMIT_MAX_REQUESTS", "120"))
API_RATE_LIMIT_WINDOW_SEC = int(os.getenv("ERP_API_RATE_LIMIT_WINDOW_SEC", "60"))
API_ALLOWED_SUBNETS = [s.strip() for s in os.getenv("ERP_API_ALLOWED_SUBNETS", "").split(",") if s.strip()]

app = Flask(__name__)
app.config["JSON_ENSURE_ASCII"] = False
logger = logging.getLogger(__name__)
_rate_limit_state = {}


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
#  Authentification par token
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def _utc_now_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _hash_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def _extract_request_token() -> str | None:
    token = request.headers.get("X-API-Token") or request.args.get("token")
    auth_header = request.headers.get("Authorization", "")
    if not token and auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1]
    return token


def _client_ip() -> str:
    xff = request.headers.get("X-Forwarded-For", "")
    if xff:
        return xff.split(",")[0].strip()
    return request.remote_addr or "unknown"


def _is_ip_allowed(client_ip: str) -> bool:
    if not API_ALLOWED_SUBNETS:
        return True
    try:
        ip_obj = ipaddress.ip_address(client_ip)
    except Exception:
        return False
    for subnet in API_ALLOWED_SUBNETS:
        try:
            if ip_obj in ipaddress.ip_network(subnet, strict=False):
                return True
        except Exception:
            logger.warning("Subnet ignoree (invalide): %s", subnet)
    return False


def _is_rate_limited(client_ip: str, token: str | None) -> bool:
    now = datetime.now(timezone.utc).timestamp()
    token_part = (token or "")[:12]
    key = f"{client_ip}:{token_part}"
    bucket = _rate_limit_state.get(key)
    if not bucket:
        _rate_limit_state[key] = {"start": now, "count": 1}
        return False
    if now - bucket["start"] > API_RATE_LIMIT_WINDOW_SEC:
        bucket["start"] = now
        bucket["count"] = 1
        return False
    bucket["count"] += 1
    return bucket["count"] > API_RATE_LIMIT_MAX_REQUESTS


def _audit_security_event(action: str, status: str = "success", details: dict | None = None):
    try:
        db = get_database()
        db.cursor.execute(
            """
            INSERT INTO audit_log(actor_id, actor_username, action, entity_type, entity_id, status, details, source_ip)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                None,
                "api",
                action,
                "security",
                None,
                status,
                json.dumps(details or {}, ensure_ascii=False),
                _client_ip(),
            ),
        )
        db.conn.commit()
    except Exception:
        pass


def _issue_dynamic_token(db, user_id: int | None = None, ttl_hours: int = API_TOKEN_TTL_HOURS) -> tuple[str, str]:
    raw_token = secrets.token_urlsafe(32)
    token_hash = _hash_token(raw_token)
    expires_at = (datetime.now(timezone.utc) + timedelta(hours=max(1, ttl_hours))).strftime("%Y-%m-%d %H:%M:%S")
    db.cursor.execute(
        """
        INSERT INTO api_tokens(token_hash, expires_at, is_revoked, created_by_user_id)
        VALUES (?, ?, 0, ?)
        """,
        (token_hash, expires_at, user_id),
    )
    db.conn.commit()
    return raw_token, expires_at


def _validate_dynamic_token(db, raw_token: str):
    token_hash = _hash_token(raw_token)
    db.cursor.execute(
        """
        SELECT id, created_by_user_id, expires_at, is_revoked
        FROM api_tokens
        WHERE token_hash = ?
        LIMIT 1
        """,
        (token_hash,),
    )
    row = db.cursor.fetchone()
    if not row:
        return None
    item = dict(row) if hasattr(row, "keys") else {
        "id": row[0], "created_by_user_id": row[1], "expires_at": row[2], "is_revoked": row[3]
    }
    if int(item.get("is_revoked") or 0) == 1:
        return None
    expires_at = item.get("expires_at")
    if expires_at and str(expires_at) <= _utc_now_str():
        return None
    return item


def _revoke_dynamic_token(db, raw_token: str) -> bool:
    token_hash = _hash_token(raw_token)
    db.cursor.execute(
        "UPDATE api_tokens SET is_revoked = 1 WHERE token_hash = ? AND is_revoked = 0",
        (token_hash,),
    )
    db.conn.commit()
    return db.cursor.rowcount > 0


def require_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = _extract_request_token()
        client_ip = _client_ip()

        if not _is_ip_allowed(client_ip):
            _audit_security_event("api.ip_blocked", "failed", {"ip": client_ip})
            return jsonify({"error": "Acces refuse", "code": 403}), 403

        if _is_rate_limited(client_ip, token):
            _audit_security_event("api.rate_limited", "failed", {"ip": client_ip})
            return jsonify({"error": "Trop de requetes", "code": 429}), 429

        if not token:
            _audit_security_event("api.token_missing", "failed")
            return jsonify({"error": "Token invalide", "code": 401}), 401

        # Compatibilite transitoire: token statique
        if token == API_TOKEN:
            g.auth_user_id = None
            g.auth_token_kind = "static"
            return f(*args, **kwargs)

        try:
            db = get_database()
            token_row = _validate_dynamic_token(db, token)
            if not token_row:
                _audit_security_event("api.token_invalid", "failed", {"kind": "dynamic"})
                return jsonify({"error": "Token invalide", "code": 401}), 401
            g.auth_user_id = token_row.get("created_by_user_id")
            g.auth_token_kind = "dynamic"
            return f(*args, **kwargs)
        except Exception as exc:
            log_api_exception("auth.require_token", exc)
            _audit_security_event("api.token_check_error", "failed")
            return jsonify({"error": "Token invalide", "code": 401}), 401
    return decorated


def ok(data=None, message="OK", **kwargs):
    resp = {"success": True, "message": message}
    if data is not None:
        resp["data"] = data
    resp.update(kwargs)
    return jsonify(resp)


def err(message, code=400):
    if code >= 500:
        # Eviter d'exposer les details internes aux clients API
        message = "Erreur interne du serveur"
    return jsonify({"success": False, "error": message}), code


def log_api_exception(context, exc):
    """Journalise une erreur API avec contexte, sans interrompre la reponse."""
    logger.exception("API error in %s: %s", context, exc)


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
#  Routes de base
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@app.route("/api/ping")
def ping():
    """Test de connectivitÃ© â€” pas besoin de token."""
    db = get_database()
    company = db.get_setting("company_name", "DAR ELSSALEM")
    return ok({"version": API_VERSION, "company": company,
                "time": datetime.now().isoformat()}, "pong")


@app.route("/api/status")
@require_token
def status():
    db = get_database()
    stats = db.get_statistics()
    return ok({
        "total_produits":  stats.get("total_products", 0),
        "total_clients":   stats.get("total_clients",  0),
        "total_ventes":    stats.get("total_sales",    0),
        "total_achats":    stats.get("total_purchases",0),
        "ca_total":        float(stats.get("sales_total", 0)),
        "valeur_stock":    float(stats.get("stock_value", 0)),
        "derniere_sync":   datetime.now().isoformat(),
    })


@app.route("/api/dashboard/stats")
@require_token
def dashboard_stats():
    """Stats pour le tableau de bord mobile."""
    db = get_database()
    stats = db.get_statistics()
    return ok({
        'salesToday': float(stats.get('sales_today', 0)),
        'growth': float(stats.get('growth_rate', 0)),
        'activeOrders': stats.get('total_sales', 0),
        'lowStockCount': stats.get('low_stock_count', 0),
        'totalProducts': stats.get('total_products', 0),
        'monthlyRevenue': float(stats.get('sales_total', 0)),
        'netProfit': float(stats.get('profit', 0)),
        'grossMargin': 0, 
    })


@app.route("/api/dashboard/sales-week")
@require_token
def sales_week():
    """DonnÃ©es pour le graphique des ventes (7 derniers jours)."""
    db = get_database()
    from datetime import timedelta, date
    result = []
    labels_map = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim']
    
    for i in range(7):
        target_date = (date.today() - timedelta(days=6-i)).strftime('%Y-%m-%d')
        db.cursor.execute("SELECT COALESCE(SUM(total), 0) as t FROM sales WHERE DATE(sale_date) = ?", (target_date,))
        total = db.cursor.fetchone()['t']
        
        day_idx = (date.today() - timedelta(days=6-i)).weekday()
        result.append({'day': labels_map[day_idx], 'total': float(total)})
        
    return ok(result)


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
#  AUTHENTIFICATION  /api/auth
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@app.route("/api/auth/login", methods=["POST"])
def login():
    """Authentification pour le mobile."""
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return err("Identifiants manquants", 400)

    try:
        db = get_database()
        db.cursor.execute("""
            SELECT id, username, password_hash, role, is_active
            FROM users WHERE username = ?
        """, (username,))
        row = db.cursor.fetchone()

        if not row:
            _audit_security_event("auth.login_failed", "failed", {"username": username, "reason": "not_found"})
            return err("Identifiant ou mot de passe incorrect", 401)

        # GÃ©rer Row ou tuple
        u_id, u_name, u_hash, u_role, u_active = (
            row['id'], row['username'], row['password_hash'], row['role'], row['is_active']
        ) if hasattr(row, 'keys') else row

        if not u_active:
            _audit_security_event("auth.login_failed", "failed", {"username": username, "reason": "inactive"})
            return err("Compte dÃ©sactivÃ©", 403)

        if not verify_password(password, u_hash):
            _audit_security_event("auth.login_failed", "failed", {"username": username, "reason": "bad_password"})
            return err("Identifiant ou mot de passe incorrect", 401)

        access_token, expires_at = _issue_dynamic_token(db, user_id=u_id)
        return ok({
            "token": access_token,  # compatibilite mobile existante
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_at": expires_at,
            "user": {
                "id": u_id,
                "username": u_name,
                "role": u_role
            }
        }, "Connexion rÃ©ussie")

    except Exception as e:
        log_api_exception("auth.login", e)
        _audit_security_event("auth.login_error", "failed", {"username": username})
        return err(str(e), 500)


@app.route("/api/auth/logout", methods=["POST"])
def logout():
    return ok(None, "DÃ©connexion rÃ©ussie")
@app.route("/api/auth/rotate", methods=["POST"])
@require_token
def rotate_token():
    current_token = _extract_request_token()
    if not current_token:
        return err("Token invalide", 401)
    if current_token == API_TOKEN:
        return err("Rotation non supportee pour le token statique", 400)
    try:
        db = get_database()
        old_row = _validate_dynamic_token(db, current_token)
        if not old_row:
            return err("Token invalide", 401)
        _revoke_dynamic_token(db, current_token)
        new_token, expires_at = _issue_dynamic_token(
            db,
            user_id=old_row.get("created_by_user_id"),
            ttl_hours=API_TOKEN_TTL_HOURS,
        )
        _audit_security_event("auth.rotate", "success", {"user_id": old_row.get("created_by_user_id")})
        return ok({
            "access_token": new_token,
            "token_type": "Bearer",
            "expires_at": expires_at,
        }, "Token rotate")
    except Exception as exc:
        log_api_exception("auth.rotate", exc)
        return err(str(exc), 500)


@app.route("/api/auth/revoke", methods=["POST"])
@require_token
def revoke_token():
    current_token = _extract_request_token()
    if not current_token:
        return err("Token invalide", 401)
    if current_token == API_TOKEN:
        return err("Revocation non supportee pour le token statique", 400)
    try:
        db = get_database()
        revoked = _revoke_dynamic_token(db, current_token)
        if not revoked:
            return err("Token introuvable", 404)
        _audit_security_event("auth.revoke", "success")
        return ok(None, "Token revoque")
    except Exception as exc:
        log_api_exception("auth.revoke", exc)
        return err(str(exc), 500)


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
#  PRODUITS
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def _serialize_product(p):
    """Convertit un produit SQLite en dict JSON propre."""
    d = dict(p) if not isinstance(p, dict) else p
    # Encoder l'image en base64 si prÃ©sente
    img = d.get("image") or d.get("image_base64")
    if img and isinstance(img, bytes):
        d["image_base64"] = base64.b64encode(img).decode("utf-8")
    elif img and isinstance(img, str) and not img.startswith("data:"):
        d["image_base64"] = img
    else:
        d["image_base64"] = img
    d.pop("image", None)
    return d


@app.route("/api/produits", methods=["GET"])
@require_token
def get_produits():
    db = get_database()
    since = request.args.get("since")   # filtre: modifiÃ©s aprÃ¨s cette date ISO
    try:
        if since:
            db.cursor.execute("""
                SELECT p.*, c.name AS category_name
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.id
                WHERE p.updated_at >= ? OR p.created_at >= ?
                ORDER BY p.name
            """, (since, since))
        else:
            db.cursor.execute("""
                SELECT p.*, c.name AS category_name
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.id
                ORDER BY p.name
            """)
        products = [_serialize_product(dict(r)) for r in db.cursor.fetchall()]
        return ok(products, f"{len(products)} produit(s)", count=len(products))
    except Exception as e:
        log_api_exception("produits.list", e)
        return err(str(e))


@app.route("/api/products", methods=["GET"])
@require_token
def get_products_alias():
    """Alias pour l'app mobile."""
    return get_produits()


@app.route("/api/produits/<int:product_id>", methods=["GET"])
@require_token
def get_produit(product_id):
    db = get_database()
    product = db.get_product_by_id(product_id)
    if not product:
        return err("Produit introuvable", 404)
    return ok(_serialize_product(product))


@app.route("/api/produits", methods=["POST"])
@require_token
def create_produit():
    db = get_database()
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    if not name:
        return err("Le champ 'name' est obligatoire")
    try:
        pid = db.add_product(
            name=name,
            selling_price=float(data.get("selling_price", 0)),
            purchase_price=float(data.get("purchase_price", 0)),
            stock_quantity=int(data.get("stock_quantity", 0)),
            category_id=data.get("category_id"),
            description=data.get("description", ""),
            min_stock=int(data.get("min_stock", 5)),
            barcode=data.get("barcode", ""),
        )
        # Image base64 optionnelle
        img = data.get("image_base64")
        if img and pid:
            _save_product_image(db, pid, img)
        return ok({"id": pid}, "Produit crÃ©Ã©", status_code=201)
    except Exception as e:
        log_api_exception("produits.create", e)
        return err(str(e))


@app.route("/api/produits/<int:product_id>", methods=["PUT"])
@require_token
def update_produit(product_id):
    db = get_database()
    data = request.get_json(silent=True) or {}
    product = db.get_product_by_id(product_id)
    if not product:
        return err("Produit introuvable", 404)
    try:
        db.update_product(
            product_id=product_id,
            name=data.get("name", product["name"]),
            selling_price=float(data.get("selling_price", product["selling_price"])),
            purchase_price=float(data.get("purchase_price", product.get("purchase_price", 0))),
            stock_quantity=int(data.get("stock_quantity", product["stock_quantity"])),
            category_id=data.get("category_id", product.get("category_id")),
            description=data.get("description", product.get("description", "")),
            min_stock=int(data.get("min_stock", product.get("min_stock", 5))),
            barcode=data.get("barcode", product.get("barcode", "")),
        )
        img = data.get("image_base64")
        if img:
            _save_product_image(db, product_id, img)
        return ok({"id": product_id}, "Produit mis Ã  jour")
    except Exception as e:
        log_api_exception("produits.update", e)
        return err(str(e))


def _save_product_image(db, product_id, image_base64):
    """Sauvegarde une image base64 dans la colonne image du produit."""
    try:
        db.cursor.execute(
            "UPDATE products SET image_base64=? WHERE id=?",
            (image_base64, product_id)
        )
        db.conn.commit()
    except Exception:
        pass


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
#  CLIENTS
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@app.route("/api/clients", methods=["GET"])
@require_token
def get_clients():
    db = get_database()
    since = request.args.get("since")
    try:
        if since:
            db.cursor.execute(
                "SELECT * FROM clients WHERE created_at >= ? ORDER BY name",
                (since,))
        else:
            db.cursor.execute("SELECT * FROM clients ORDER BY name")
        clients = [dict(r) for r in db.cursor.fetchall()]
        return ok(clients, f"{len(clients)} client(s)", count=len(clients))
    except Exception as e:
        log_api_exception("clients.list", e)
        return err(str(e))


@app.route("/api/clients", methods=["GET"])
@require_token
def get_clients_alias():
    """Alias pour l'app mobile."""
    return get_clients()


@app.route("/api/clients", methods=["POST"])
@require_token
def create_client():
    db = get_database()
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    if not name:
        return err("Le champ 'name' est obligatoire")
    try:
        cid = db.add_client(
            name=name,
            phone=data.get("phone", ""),
            email=data.get("email", ""),
            address=data.get("address", ""),
        )
        return ok({"id": cid}, "Client crÃ©Ã©")
    except Exception as e:
        log_api_exception("clients.create", e)
        return err(str(e))


@app.route("/api/clients/<int:client_id>", methods=["PUT"])
@require_token
def update_client(client_id):
    db = get_database()
    data = request.get_json(silent=True) or {}
    client = db.get_client_by_id(client_id)
    if not client:
        return err("Client introuvable", 404)
    try:
        db.update_client(
            client_id,
            name=data.get("name", client["name"]),
            phone=data.get("phone", client.get("phone", "")),
            email=data.get("email", client.get("email", "")),
            address=data.get("address", client.get("address", "")),
        )
        return ok({"id": client_id}, "Client mis Ã  jour")
    except Exception as e:
        log_api_exception("clients.update", e)
        return err(str(e))


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
#  VENTES / FACTURES
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@app.route("/api/ventes", methods=["GET"])
@app.route("/api/factures", methods=["GET"])
@require_token
def get_ventes():
    db = get_database()
    since  = request.args.get("since")
    limit  = int(request.args.get("limit", 100))
    try:
        if since:
            db.cursor.execute("""
                SELECT s.*, c.name AS client_name
                FROM sales s
                LEFT JOIN clients c ON s.client_id = c.id
                WHERE s.sale_date >= ?
                ORDER BY s.sale_date DESC
                LIMIT ?
            """, (since, limit))
        else:
            db.cursor.execute("""
                SELECT s.*, c.name AS client_name
                FROM sales s
                LEFT JOIN clients c ON s.client_id = c.id
                ORDER BY s.sale_date DESC
                LIMIT ?
            """, (limit,))
        ventes = [dict(r) for r in db.cursor.fetchall()]
        return ok(ventes, f"{len(ventes)} vente(s)", count=len(ventes))
    except Exception as e:
        log_api_exception("ventes.list", e)
        return err(str(e))


@app.route("/api/sales", methods=["GET", "POST"])
@require_token
def handle_sales_alias():
    """Alias pour l'app mobile."""
    if request.method == "POST":
        return create_vente()
    return get_ventes()


@app.route("/api/ventes/<int:sale_id>", methods=["GET"])
@app.route("/api/factures/<int:sale_id>", methods=["GET"])
@require_token
def get_vente(sale_id):
    db = get_database()
    sale = db.get_sale_by_id(sale_id)
    if not sale:
        return err("Vente introuvable", 404)
    return ok(dict(sale))


@app.route("/api/ventes", methods=["POST"])
@require_token
def create_vente():
    db = get_database()
    data = request.get_json(silent=True) or {}
    try:
        items   = data.get("items", [])
        if not items:
            return err("La vente doit contenir au moins un article")

        client_id = data.get("client_id")
        # CrÃ©er le client Ã  la volÃ©e si nom fourni sans ID
        if not client_id and data.get("client_name"):
            found = db.search_clients(data["client_name"])
            client_id = found[0]["id"] if found else db.add_client(data["client_name"])

        invoice_number = data.get("invoice_number") or db.generate_invoice_number()

        sale_id = db.create_sale(
            invoice_number=invoice_number,
            client_id=client_id,
            items=items,
            payment_method=data.get("payment_method", "cash"),
            tax_rate=float(data.get("tax_rate", 19)),
            notes=data.get("notes", ""),
            sale_date=data.get("sale_date", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        )
        return ok({"id": sale_id, "invoice_number": invoice_number}, "Vente crÃ©Ã©e")
    except Exception as e:
        log_api_exception("ventes.create", e)
        return err(str(e))


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
#  SYNC COMPLÃˆTE  GET /api/sync
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@app.route("/api/sync", methods=["GET"])
@require_token
def full_sync():
    """
    Retourne tout ce dont le mobile a besoin en un seul appel.
    ParamÃ¨tre optionnel : ?since=2026-01-01T00:00:00
    """
    db = get_database()
    since = request.args.get("since")

    try:
        # Produits
        if since:
            db.cursor.execute("""
                SELECT p.*, c.name AS category_name
                FROM products p LEFT JOIN categories c ON p.category_id = c.id
                WHERE p.updated_at >= ? OR p.created_at >= ?
            """, (since, since))
        else:
            db.cursor.execute("""
                SELECT p.*, c.name AS category_name
                FROM products p LEFT JOIN categories c ON p.category_id = c.id
                ORDER BY p.name
            """)
        products = [_serialize_product(dict(r)) for r in db.cursor.fetchall()]

        # Clients
        if since:
            db.cursor.execute("SELECT * FROM clients WHERE created_at >= ?", (since,))
        else:
            db.cursor.execute("SELECT * FROM clients ORDER BY name")
        clients = [dict(r) for r in db.cursor.fetchall()]

        # Ventes rÃ©centes (30 derniÃ¨res)
        db.cursor.execute("""
            SELECT s.*, c.name AS client_name
            FROM sales s LEFT JOIN clients c ON s.client_id = c.id
            ORDER BY s.sale_date DESC LIMIT 50
        """)
        ventes = [dict(r) for r in db.cursor.fetchall()]

        # ParamÃ¨tres entreprise
        settings = {
            "company_name":    db.get_setting("company_name", ""),
            "company_address": db.get_setting("company_address", ""),
            "company_phone":   db.get_setting("company_phone", ""),
            "company_email":   db.get_setting("company_email", ""),
            "vat":             db.get_setting("vat", "19"),
            "currency":        db.get_setting("currency", "DA"),
        }

        return ok({
            "produits":  products,
            "clients":   clients,
            "ventes":    ventes,
            "settings":  settings,
            "sync_time": datetime.now().isoformat(),
            "counts": {
                "produits": len(products),
                "clients":  len(clients),
                "ventes":   len(ventes),
            }
        }, "Synchronisation complÃ¨te")

    except Exception as e:
        log_api_exception("sync.full", e)
        return err(str(e))


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
#  SYNC PUSH  POST /api/sync/push  (mobile â†’ ERP)
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@app.route("/api/sync/push", methods=["POST"])
@require_token
def sync_push():
    """
    ReÃ§oit les donnÃ©es crÃ©Ã©es/modifiÃ©es sur le mobile.
    Body JSON :
    {
      "ventes":  [...],    # nouvelles ventes crÃ©Ã©es hors ligne
      "clients": [...],    # nouveaux clients
      "produits_images": [{"id": 1, "image_base64": "..."}]
    }
    """
    db = get_database()
    data = request.get_json(silent=True) or {}
    results = {"ventes": [], "clients": [], "images": [], "errors": []}

    # â”€â”€ Clients â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    for c in data.get("clients", []):
        try:
            name = (c.get("name") or "").strip()
            if not name:
                continue
            existing = db.search_clients(name)
            if existing:
                results["clients"].append(
                    {"name": name, "action": "existe", "id": existing[0]["id"]})
            else:
                cid = db.add_client(
                    name, c.get("phone",""), c.get("email",""), c.get("address",""))
                results["clients"].append({"name": name, "action": "crÃ©Ã©", "id": cid})
        except Exception as e:
            log_api_exception("sync.push.client", e)
            results["errors"].append(f"Client '{c.get('name')}': {e}")

    # â”€â”€ Ventes â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    for v in data.get("ventes", []):
        try:
            items = v.get("items", [])
            if not items:
                continue
            client_id = v.get("client_id")
            if not client_id and v.get("client_name"):
                found = db.search_clients(v["client_name"])
                client_id = found[0]["id"] if found else db.add_client(v["client_name"])

            inv = v.get("invoice_number") or db.generate_invoice_number()
            # VÃ©rifier doublon
            db.cursor.execute(
                "SELECT id FROM sales WHERE invoice_number=?", (inv,))
            if db.cursor.fetchone():
                results["ventes"].append(
                    {"invoice": inv, "action": "doublon ignorÃ©"})
                continue

            sid = db.create_sale(
                invoice_number=inv,
                client_id=client_id,
                items=items,
                payment_method=v.get("payment_method", "cash"),
                tax_rate=float(v.get("tax_rate", 19)),
                notes=v.get("notes", ""),
                sale_date=v.get("sale_date",
                                datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            )
            results["ventes"].append(
                {"invoice": inv, "action": "crÃ©Ã©e", "id": sid})
        except Exception as e:
            log_api_exception("sync.push.sale", e)
            results["errors"].append(
                f"Vente '{v.get('invoice_number')}': {e}")

    # â”€â”€ Images produits â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    for img_data in data.get("produits_images", []):
        try:
            pid = img_data.get("id")
            img = img_data.get("image_base64")
            if pid and img:
                _save_product_image(db, pid, img)
                results["images"].append({"id": pid, "action": "image sauvegardÃ©e"})
        except Exception as e:
            log_api_exception("sync.push.image", e)
            results["errors"].append(f"Image produit {img_data.get('id')}: {e}")

    return ok(results, "Push reÃ§u avec succÃ¨s")


@app.route("/api/employees", methods=["GET"])
@require_token
def get_employees():
    """Liste des employÃ©s (utilisateurs)."""
    db = get_database()
    try:
        db.cursor.execute("SELECT id, username as name, role, is_active FROM users")
        users = [dict(r) for r in db.cursor.fetchall()]
        return ok(users)
    except Exception as e:
        log_api_exception("employees.list", e)
        return err(str(e))


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
#  Lancement dans un thread sÃ©parÃ©
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

_server_thread = None
_server_running = False


def start_api_server(port=API_PORT, token=None):
    """DÃ©marre le serveur Flask dans un thread daemon."""
    global _server_thread, _server_running, API_TOKEN
    if token:
        API_TOKEN = token
    if _server_running:
        print(f"âš ï¸  Serveur API dÃ©jÃ  en cours sur le port {port}")
        return
    import logging
    log = logging.getLogger("werkzeug")
    log.setLevel(logging.ERROR)   # silencer les logs Flask dans la console PyQt

    def run():
        global _server_running
        _server_running = True
        print(f"[API] Serveur API dÃ©marrÃ© -> http://{API_HOST}:{port}")
        if os.getenv("ERP_API_TOKEN", "").strip() == "":
            print("[SECURITY] ERP_API_TOKEN non dÃ©fini: token temporaire alÃ©atoire actif pour cette session.")
        _print_local_ip(port)
        app.run(host=API_HOST, port=port, debug=False, use_reloader=False)

    _server_thread = threading.Thread(target=run, daemon=True)
    _server_thread.start()


def _print_local_ip(port):
    """Affiche l'adresse IP locale pour la config mobile."""
    if API_HOST == "127.0.0.1":
        print(f"[API] AccÃ¨s local uniquement: http://127.0.0.1:{port}/api")
        print("[API] Pour autoriser le rÃ©seau local, dÃ©finissez ERP_API_EXPOSE_NETWORK=true")
        return
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        print(f"[IP] URL WiFi local  : http://{ip}:{port}/api")
        print(f"[IP] Test ping       : http://{ip}:{port}/api/ping")
    except Exception:
        pass


def get_local_ip():
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def is_running():
    return _server_running

