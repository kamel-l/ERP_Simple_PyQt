import sys
from pathlib import Path

import pytest


# Evite de collecter les tests dupliques dans la copie de travail.
collect_ignore_glob = ["New folder/test_*.py"]


@pytest.fixture(autouse=True)
def isolated_database(tmp_path):
    """
    Isole la base de donnees pour chaque test.
    - Force un fichier SQLite temporaire.
    - Reinitialise le singleton db_manager._db_instance.
    """
    import config
    import db_manager

    old_db_path = config.config._parser.get("database", "path")
    temp_db = tmp_path / "test_erp.db"
    config.config._parser.set("database", "path", str(temp_db))

    current = getattr(db_manager, "_db_instance", None)
    if current is not None and getattr(current, "conn", None) is not None:
        try:
            current.disconnect()
        except Exception:
            pass
    db_manager._db_instance = None

    yield

    current = getattr(db_manager, "_db_instance", None)
    if current is not None and getattr(current, "conn", None) is not None:
        try:
            current.disconnect()
        except Exception:
            pass
    db_manager._db_instance = None
    config.config._parser.set("database", "path", old_db_path)


@pytest.fixture(autouse=True)
def reset_api_state(monkeypatch):
    """
    Evite les effets de bord entre tests API
    (ex: monkeypatch de API_TOKEN dans un test precedent).
    """
    if "api_server" in sys.modules:
        import api_server

        monkeypatch.setattr(api_server, "API_TOKEN", "test-default-token")
    yield
