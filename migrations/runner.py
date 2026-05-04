from __future__ import annotations

from pathlib import Path
import logging
import sqlite3

logger = logging.getLogger(__name__)


def _ensure_migrations_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version TEXT PRIMARY KEY,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()


def _applied_versions(conn: sqlite3.Connection) -> set[str]:
    rows = conn.execute("SELECT version FROM schema_migrations").fetchall()
    return {row[0] for row in rows}


def _migration_files() -> list[Path]:
    sql_dir = Path(__file__).parent / "sql"
    if not sql_dir.exists():
        return []
    return sorted(sql_dir.glob("V*.sql"))


def run_migrations(conn: sqlite3.Connection) -> list[str]:
    """
    Applique les migrations SQL non executees dans l'ordre lexicographique.
    Retourne la liste des versions appliquees pendant ce run.
    """
    _ensure_migrations_table(conn)
    applied = _applied_versions(conn)
    applied_now: list[str] = []

    for sql_file in _migration_files():
        version = sql_file.stem
        if version in applied:
            continue

        script = sql_file.read_text(encoding="utf-8")
        try:
            conn.executescript(script)
            conn.execute(
                "INSERT INTO schema_migrations(version) VALUES (?)",
                (version,),
            )
            conn.commit()
            applied_now.append(version)
            logger.info("Migration appliquee: %s", version)
        except Exception:
            conn.rollback()
            logger.exception("Echec migration: %s", version)
            raise

    return applied_now

