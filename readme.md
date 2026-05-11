ERP Simple PyQt

Application ERP desktop (PyQt6) avec base SQLite et API mobile (Flask).

Demarrage rapide

1. Installer les dependances Python (PyQt6, Flask, etc.).
2. Lancer l'application via `main.py`.
3. Se connecter depuis la fenetre de login.

Configuration API (important)

- `ERP_API_TOKEN` : token d'acces API (fortement recommande).
- `ERP_API_EXPOSE_NETWORK` : mettre `true` pour autoriser l'acces reseau local.
- Par defaut, l'API est limitee a `127.0.0.1` (machine locale uniquement).

Exemple (PowerShell)

```powershell
$env:ERP_API_TOKEN = "remplacez-par-un-token-fort"
$env:ERP_API_EXPOSE_NETWORK = "true"
python main.py
```

Notes projet

- Le dossier `New folder` contient une copie de travail ancienne/dupliquee.
- Conserver une seule source de verite reduit les erreurs de maintenance.

Tests automatiques (pytest)

- Tests API: `test_api_server.py`
- Tests numerotation facture: `test_invoice_numbering.py`
- Lancer tous les tests:

```powershell
python -m pytest -q
```

Runbook production (API securisee)

- Variables d'environnement critiques:
- `ERP_API_TOKEN`: token statique de transition (optionnel).
- `ERP_API_STRICT_DYNAMIC_TOKENS=true`: force les tokens dynamiques DB uniquement.
- `ERP_API_TOKEN_TTL_HOURS=12`: duree de vie des tokens dynamiques.
- `ERP_API_EXPOSE_NETWORK=true`: expose l'API sur le reseau local.
- `ERP_API_ALLOWED_SUBNETS=192.168.1.0/24,10.0.0.0/8`: whitelist CIDR optionnelle.
- `ERP_API_RATE_LIMIT_MAX_REQUESTS=120`
- `ERP_API_RATE_LIMIT_WINDOW_SEC=60`

Rotation et revocation

- Login: `POST /api/auth/login` retourne `access_token`.
- Rotation: `POST /api/auth/rotate` avec `Authorization: Bearer <token>`.
- Revocation: `POST /api/auth/revoke` avec le token courant.

Maintenance securite

- Stats: `GET /api/admin/security/stats`
- Purge: `POST /api/admin/security/maintenance`
  - body JSON exemple: `{"purge_expired_tokens": true, "audit_retention_days": 90}`
