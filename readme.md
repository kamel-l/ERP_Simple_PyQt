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
