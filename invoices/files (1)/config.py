"""
config.py — Lecture centralisée de config.ini
=============================================
Sépare la configuration technique (chemin BDD, thème, logs...)
des données métier stockées dans la base de données.

Usage :
    from config import config
    db_path = config.db_path
    page_size = config.page_size
"""

import configparser
import os
import logging

# Chemin du fichier config.ini (même dossier que ce script)
_CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.ini")

# Valeurs par défaut si config.ini est absent ou incomplet
_DEFAULTS = {
    "database": {
        "path":             "erp_database.db",
        "backup_dir":       "backups",
        "backup_max_count": "10",
    },
    "app": {
        "language":  "fr",
        "theme":     "dark",
        "page_size": "50",
    },
    "logs": {
        "enabled": "true",
        "path":    "erp.log",
        "level":   "INFO",
    },
}


class AppConfig:
    """Lit config.ini et expose les paramètres sous forme d'attributs typés."""

    def __init__(self):
        self._parser = configparser.ConfigParser()

        # Charger les valeurs par défaut
        self._parser.read_dict(_DEFAULTS)

        # Charger config.ini s'il existe (écrase les valeurs par défaut)
        if os.path.exists(_CONFIG_FILE):
            self._parser.read(_CONFIG_FILE, encoding="utf-8")
        else:
            # Créer le fichier avec les valeurs par défaut
            self._create_default_config()

        self._setup_logging()

    # ── Paramètres base de données ────────────────────────────────
    @property
    def db_path(self) -> str:
        """Chemin vers le fichier SQLite principal."""
        return self._parser.get("database", "path")

    @property
    def backup_dir(self) -> str:
        """Dossier de stockage des sauvegardes."""
        return self._parser.get("database", "backup_dir")

    @property
    def backup_max_count(self) -> int:
        """Nombre maximum de sauvegardes à conserver."""
        return self._parser.getint("database", "backup_max_count")

    # ── Paramètres application ────────────────────────────────────
    @property
    def language(self) -> str:
        """Code langue de l'interface (ex: 'fr')."""
        return self._parser.get("app", "language")

    @property
    def theme(self) -> str:
        """Thème visuel : 'dark' ou 'light'."""
        return self._parser.get("app", "theme")

    @property
    def page_size(self) -> int:
        """Nombre de lignes par page pour la pagination."""
        return self._parser.getint("app", "page_size")

    # ── Paramètres logs ───────────────────────────────────────────
    @property
    def logs_enabled(self) -> bool:
        """True si l'écriture des logs est activée."""
        return self._parser.getboolean("logs", "enabled")

    @property
    def log_path(self) -> str:
        """Chemin du fichier de log."""
        return self._parser.get("logs", "path")

    @property
    def log_level(self) -> str:
        """Niveau de log : DEBUG / INFO / WARNING / ERROR."""
        return self._parser.get("logs", "level")

    # ── Méthodes utilitaires ──────────────────────────────────────
    def _create_default_config(self):
        """Crée config.ini avec les valeurs par défaut si absent."""
        try:
            with open(_CONFIG_FILE, "w", encoding="utf-8") as f:
                self._parser.write(f)
            print(f"✅ config.ini créé avec les valeurs par défaut : {_CONFIG_FILE}")
        except OSError as e:
            print(f"⚠️  Impossible de créer config.ini : {e}")

    def _setup_logging(self):
        """Configure le système de logs selon config.ini."""
        if not self.logs_enabled:
            return

        level = getattr(logging, self.log_level.upper(), logging.INFO)
        handlers = [logging.StreamHandler()]

        try:
            handlers.append(logging.FileHandler(self.log_path, encoding="utf-8"))
        except OSError:
            pass  # Si le fichier n'est pas accessible, log console seulement

        logging.basicConfig(
            level=level,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            handlers=handlers,
        )

    def reload(self):
        """Recharge config.ini depuis le disque (utile après modification manuelle)."""
        self._parser.read_dict(_DEFAULTS)
        self._parser.read(_CONFIG_FILE, encoding="utf-8")
        print("✅ config.ini rechargé")

    def __repr__(self):
        return (
            f"AppConfig("
            f"db_path={self.db_path!r}, "
            f"page_size={self.page_size}, "
            f"theme={self.theme!r}, "
            f"log_level={self.log_level!r})"
        )


# Instance unique partagée dans toute l'application
config = AppConfig()
