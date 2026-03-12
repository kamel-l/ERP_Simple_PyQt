"""
auth.py — Gestion des utilisateurs, rôles et permissions
=========================================================

Trois rôles disponibles :

  ADMIN   → Accès complet (tout voir, tout modifier, tout supprimer,
             gérer les utilisateurs, paramètres système)

  MANAGER → Accès étendu (ventes, achats, clients, produits, stats,
             historique) — ne peut PAS supprimer en masse ni gérer
             les utilisateurs ni modifier les paramètres système

  VENDEUR → Accès restreint (point de vente uniquement, consultation
             produits et clients) — aucune modification de prix,
             pas d'accès aux achats ni aux statistiques financières

Usage :
    from auth import session

    # Vérifier un droit avant une action
    if not session.can('delete_product'):
        QMessageBox.warning(self, "Accès refusé", "Action non autorisée.")
        return

    # Vérifier l'accès à une page
    if not session.can_access_page('statistics'):
        ...
"""

import hashlib
import secrets
from dataclasses import dataclass, field
from typing import Optional
from PyQt6.QtCore import Qt, pyqtSignal


# ──────────────────────────────────────────────────────────────────
# Définition des rôles et de leurs permissions
# ──────────────────────────────────────────────────────────────────

#  Matrice complète des permissions par rôle
#  Clé = identifiant de permission, Valeur = ensemble des rôles autorisés
PERMISSIONS: dict[str, set[str]] = {

    # ── Navigation ───────────────────────────────────────────
    "page_dashboard":    {"admin", "manager", "vendeur"},
    "page_clients":      {"admin", "manager", "vendeur"},
    "page_products":     {"admin", "manager", "vendeur"},
    "page_sales":        {"admin", "manager", "vendeur"},
    "page_purchases":    {"admin", "manager"},
    "page_history":      {"admin", "manager"},
    "page_statistics":   {"admin", "manager"},
    "page_settings":     {"admin"},
    "page_users":        {"admin"},

    # ── Clients ──────────────────────────────────────────────
    "add_client":        {"admin", "manager"},
    "edit_client":       {"admin", "manager"},
    "delete_client":     {"admin"},

    # ── Produits ─────────────────────────────────────────────
    "add_product":       {"admin", "manager"},
    "edit_product":      {"admin", "manager"},
    "edit_product_price":{"admin"},            # modification de prix uniquement admin
    "delete_product":    {"admin"},
    "delete_all_products":{"admin"},
    "import_products":   {"admin", "manager"},

    # ── Ventes ───────────────────────────────────────────────
    "create_sale":       {"admin", "manager", "vendeur"},
    "view_sale_details": {"admin", "manager"},
    "delete_sale":       {"admin"},
    "export_sales":      {"admin", "manager"},
    "apply_discount":    {"admin", "manager"},

    # ── Achats ───────────────────────────────────────────────
    "create_purchase":   {"admin", "manager"},
    "edit_purchase":     {"admin"},
    "delete_purchase":   {"admin"},
    "add_supplier":      {"admin", "manager"},

    # ── Statistiques / Rapports ──────────────────────────────
    "view_statistics":   {"admin", "manager"},
    "export_statistics": {"admin", "manager"},
    "view_margins":      {"admin", "manager"},

    # ── Paramètres système ───────────────────────────────────
    "edit_settings":     {"admin"},
    "backup_database":   {"admin"},
    "restore_database":  {"admin"},
    "cleanup_database":  {"admin"},

    # ── Gestion des utilisateurs ─────────────────────────────
    "manage_users":      {"admin"},
    "add_user":          {"admin"},
    "edit_user":         {"admin"},
    "delete_user":       {"admin"},
    "reset_password":    {"admin"},
}

# Pages de la sidebar et les permissions nécessaires
PAGE_PERMISSIONS: dict[str, str] = {
    "dashboard":  "page_dashboard",
    "clients":    "page_clients",
    "products":   "page_products",
    "sales":      "page_sales",
    "purchases":  "page_purchases",
    "history":    "page_history",
    "statistics": "page_statistics",
    "settings":   "page_settings",
    "users":      "page_users",
}

# Libellés affichés dans l'interface
ROLE_LABELS: dict[str, str] = {
    "admin":   "Administrateur",
    "manager": "Manager",
    "vendeur": "Vendeur",
}

ROLE_COLORS: dict[str, str] = {
    "admin":   "#FF6B6B",   # Rouge
    "manager": "#00B4FF",   # Bleu
    "vendeur": "#00E5A0",   # Vert
}

ROLE_ICONS: dict[str, str] = {
    "admin":   "👑",
    "manager": "🏢",
    "vendeur": "🛒",
}


# ──────────────────────────────────────────────────────────────────
# Session utilisateur courante
# ──────────────────────────────────────────────────────────────────

@dataclass
class UserSession:
    """Session de l'utilisateur connecté.

    Attributes:
        user_id (int | None): ID en base, None si non connecté.
        username (str): Nom d'utilisateur.
        role (str): Rôle actif ('admin', 'manager', 'vendeur').
        display_name (str): Nom complet affiché dans l'interface.
        is_authenticated (bool): True si l'utilisateur est connecté.
    """
    user_id:          Optional[int] = None
    username:         str           = ""
    role:             str           = ""
    display_name:     str           = ""
    is_authenticated: bool          = False

    def login(self, user_id: int, username: str, role: str,
              display_name: str = "") -> None:
        """Ouvre la session après authentification réussie."""
        self.user_id          = user_id
        self.username         = username
        self.role             = role
        self.display_name     = display_name or username
        self.is_authenticated = True

    def logout(self) -> None:
        """Ferme la session courante."""
        self.user_id          = None
        self.username         = ""
        self.role             = ""
        self.display_name     = ""
        self.is_authenticated = False

    def can(self, permission: str) -> bool:
        """Vérifie si l'utilisateur possède une permission.

        Args:
            permission (str): Identifiant de la permission (ex: 'delete_product').

        Returns:
            bool: True si autorisé, False sinon.
        """
        if not self.is_authenticated:
            return False
        allowed_roles = PERMISSIONS.get(permission, set())
        return self.role in allowed_roles

    def can_access_page(self, page_key: str) -> bool:
        """Vérifie si l'utilisateur peut accéder à une page.

        Args:
            page_key (str): Clé de la page (ex: 'statistics').

        Returns:
            bool: True si l'accès est autorisé.
        """
        perm = PAGE_PERMISSIONS.get(page_key)
        if perm is None:
            return True     # Page inconnue = accessible par défaut
        return self.can(perm)

    @property
    def role_label(self) -> str:
        """Libellé localisé du rôle."""
        return ROLE_LABELS.get(self.role, self.role)

    @property
    def role_color(self) -> str:
        """Couleur CSS associée au rôle."""
        return ROLE_COLORS.get(self.role, "#AAAAAA")

    @property
    def role_icon(self) -> str:
        """Emoji associé au rôle."""
        return ROLE_ICONS.get(self.role, "👤")


# Instance unique partagée dans toute l'application
session = UserSession()


# ──────────────────────────────────────────────────────────────────
# Utilitaires de hachage
# ──────────────────────────────────────────────────────────────────

def hash_password(password: str, salt: str = "") -> str:
    """Hache un mot de passe avec SHA-256 + sel.

    Args:
        password (str): Mot de passe en clair.
        salt (str): Sel optionnel (généré automatiquement si vide).

    Returns:
        str: Chaîne 'salt:hash' prête pour la base de données.
    """
    if not salt:
        salt = secrets.token_hex(16)
    hashed = hashlib.sha256(f"{salt}{password}".encode()).hexdigest()
    return f"{salt}:{hashed}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Vérifie un mot de passe contre son hash stocké.

    Args:
        password (str): Mot de passe saisi par l'utilisateur.
        stored_hash (str): Hash stocké en base ('salt:hash').

    Returns:
        bool: True si le mot de passe est correct.
    """
    try:
        salt, _ = stored_hash.split(":", 1)
        return hash_password(password, salt) == stored_hash
    except (ValueError, AttributeError):
        return False