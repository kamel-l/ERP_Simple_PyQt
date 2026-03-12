"""
currency.py — Moteur multi-devises avec taux de change
=======================================================

Ce module est le point d'entrée unique pour tout ce qui touche
aux devises dans l'ERP. Il expose :

  • CURRENCIES — catalogue des 12 devises supportées
  • CurrencyManager — singleton qui lit/écrit les préférences en BDD
  • fmt() — remplace fmt_da() partout dans l'application
  • convert() — convertit un montant d'une devise vers une autre

Utilisation dans n'importe quel fichier :
    from currency import fmt, convert, currency_manager

    label.setText(fmt(montant))                 # devise principale
    label.setText(fmt(montant, 'USD'))           # devise secondaire
    eur = convert(1000, from_='DZD', to='EUR')  # conversion
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import sqlite3


# ──────────────────────────────────────────────────────────────────
# Catalogue des devises supportées
# ──────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class Currency:
    """Définition d'une devise.

    Attributes:
        code (str): Code ISO 4217 (ex: 'DZD').
        symbol (str): Symbole affiché (ex: 'DA').
        name (str): Nom complet.
        symbol_after (bool): True → montant SYMBOL, False → SYMBOL montant.
        decimals (int): Nombre de décimales à afficher.
        flag (str): Emoji drapeau.
    """
    code:         str
    symbol:       str
    name:         str
    symbol_after: bool  = True
    decimals:     int   = 2
    flag:         str   = "🏳"


CURRENCIES: dict[str, Currency] = {
    "DZD": Currency("DZD", "DA",  "Dinar Algérien",     symbol_after=True,  decimals=2, flag="🇩🇿"),
    "EUR": Currency("EUR", "€",   "Euro",                symbol_after=False, decimals=2, flag="🇪🇺"),
    "USD": Currency("USD", "$",   "Dollar Américain",    symbol_after=False, decimals=2, flag="🇺🇸"),
    "GBP": Currency("GBP", "£",   "Livre Sterling",      symbol_after=False, decimals=2, flag="🇬🇧"),
    "SAR": Currency("SAR", "﷼",   "Riyal Saoudien",      symbol_after=True,  decimals=2, flag="🇸🇦"),
    "MAD": Currency("MAD", "MAD", "Dirham Marocain",     symbol_after=True,  decimals=2, flag="🇲🇦"),
    "TND": Currency("TND", "TND", "Dinar Tunisien",      symbol_after=True,  decimals=3, flag="🇹🇳"),
    "AED": Currency("AED", "AED", "Dirham Émirati",      symbol_after=True,  decimals=2, flag="🇦🇪"),
    "CHF": Currency("CHF", "CHF", "Franc Suisse",        symbol_after=True,  decimals=2, flag="🇨🇭"),
    "TRY": Currency("TRY", "₺",   "Livre Turque",        symbol_after=True,  decimals=2, flag="🇹🇷"),
    "CNY": Currency("CNY", "¥",   "Yuan Chinois",        symbol_after=False, decimals=2, flag="🇨🇳"),
    "CAD": Currency("CAD", "CA$", "Dollar Canadien",     symbol_after=False, decimals=2, flag="🇨🇦"),
}

# Taux par rapport au DZD (1 unité de devise = X DZD)
# Source : taux indicatifs — l'utilisateur peut les ajuster dans les paramètres
DEFAULT_RATES_TO_DZD: dict[str, float] = {
    "DZD": 1.0,
    "EUR": 147.50,
    "USD": 135.20,
    "GBP": 171.30,
    "SAR": 36.05,
    "MAD": 13.40,
    "TND": 43.80,
    "AED": 36.80,
    "CHF": 152.60,
    "TRY": 4.15,
    "CNY": 18.65,
    "CAD": 99.80,
}


# ──────────────────────────────────────────────────────────────────
# Manager de devise — singleton
# ──────────────────────────────────────────────────────────────────

class CurrencyManager:
    """Gestionnaire central des devises et des taux de change.

    Lit la devise principale + la devise secondaire + les taux
    depuis la base de données (table settings).

    Utiliser l'instance globale ``currency_manager``.
    """

    def __init__(self) -> None:
        self._primary_code:   str   = "DZD"
        self._secondary_code: Optional[str] = None
        self._rates: dict[str, float] = dict(DEFAULT_RATES_TO_DZD)
        self._db = None          # injecté via load()

    # ── Initialisation ────────────────────────────────────────────

    def load(self, db=None) -> None:
        """Charge les préférences depuis la base de données.

        Args:
            db: Instance Database (db_manager). Si None, utilise
                get_database() automatiquement.
        """
        if db is None:
            try:
                from db_manager import get_database
                db = get_database()
            except Exception:
                return
        self._db = db

        try:
            # Devise principale
            primary = db.get_setting("currency_primary", "DZD")
            if primary in CURRENCIES:
                self._primary_code = primary

            # Devise secondaire (peut être vide)
            secondary = db.get_setting("currency_secondary", "")
            self._secondary_code = secondary if secondary in CURRENCIES else None

            # Taux de change stockés en BDD
            for code in CURRENCIES:
                key  = f"rate_{code}_to_DZD"
                val  = db.get_setting(key, None)
                if val is not None:
                    try:
                        self._rates[code] = float(val)
                    except (ValueError, TypeError):
                        pass
        except Exception as e:
            print(f"⚠️ CurrencyManager.load: {e}")

    def save(self, db=None) -> None:
        """Persiste les préférences en base de données.

        Args:
            db: Instance Database. Si None, utilise l'instance chargée.
        """
        db = db or self._db
        if db is None:
            return
        try:
            db.set_setting("currency_primary",   self._primary_code)
            db.set_setting("currency_secondary", self._secondary_code or "")
            for code, rate in self._rates.items():
                db.set_setting(f"rate_{code}_to_DZD", str(rate))
        except Exception as e:
            print(f"⚠️ CurrencyManager.save: {e}")

    # ── Propriétés ────────────────────────────────────────────────

    @property
    def primary(self) -> Currency:
        """Devise principale de l'application."""
        return CURRENCIES[self._primary_code]

    @property
    def secondary(self) -> Optional[Currency]:
        """Devise secondaire affichée en complément (ou None)."""
        if self._secondary_code:
            return CURRENCIES.get(self._secondary_code)
        return None

    @property
    def primary_code(self) -> str:
        return self._primary_code

    @primary_code.setter
    def primary_code(self, code: str) -> None:
        if code in CURRENCIES:
            self._primary_code = code

    @property
    def secondary_code(self) -> Optional[str]:
        return self._secondary_code

    @secondary_code.setter
    def secondary_code(self, code: Optional[str]) -> None:
        self._secondary_code = code if code in CURRENCIES else None

    # ── Taux de change ────────────────────────────────────────────

    def get_rate_to_dzd(self, code: str) -> float:
        """Retourne le taux de conversion vers le DZD.

        Args:
            code (str): Code ISO de la devise source.

        Returns:
            float: 1 unité de ``code`` = X DZD.
        """
        return self._rates.get(code, 1.0)

    def set_rate_to_dzd(self, code: str, rate: float) -> None:
        """Met à jour le taux de conversion d'une devise vers le DZD.

        Args:
            code (str): Code ISO de la devise.
            rate (float): Nouveau taux (1 unité = rate DZD).
        """
        if code in CURRENCIES and rate > 0:
            self._rates[code] = rate

    def get_rate(self, from_code: str, to_code: str) -> float:
        """Calcule le taux de change entre deux devises.

        Args:
            from_code (str): Devise source.
            to_code (str): Devise cible.

        Returns:
            float: 1 unité de ``from_code`` = X ``to_code``.
        """
        if from_code == to_code:
            return 1.0
        from_to_dzd = self._rates.get(from_code, 1.0)
        to_to_dzd   = self._rates.get(to_code,   1.0)
        if to_to_dzd == 0:
            return 0.0
        return from_to_dzd / to_to_dzd

    # ── Conversion ────────────────────────────────────────────────

    def convert(self, amount: float,
                from_: str = "DZD", to: str = "DZD") -> float:
        """Convertit un montant d'une devise vers une autre.

        Les montants stockés en base sont TOUJOURS en devise principale.
        Cette méthode sert uniquement à l'affichage.

        Args:
            amount (float): Montant à convertir.
            from_ (str): Code devise source (défaut: devise principale).
            to (str): Code devise cible.

        Returns:
            float: Montant converti.
        """
        if from_ == to:
            return float(amount)
        rate = self.get_rate(from_, to)
        return float(amount) * rate

    def to_primary(self, amount: float, from_code: str) -> float:
        """Convertit vers la devise principale.

        Args:
            amount (float): Montant dans ``from_code``.
            from_code (str): Devise source.

        Returns:
            float: Montant en devise principale.
        """
        return self.convert(amount, from_=from_code, to=self._primary_code)

    def from_primary(self, amount: float, to_code: str) -> float:
        """Convertit depuis la devise principale.

        Args:
            amount (float): Montant en devise principale.
            to_code (str): Devise cible.

        Returns:
            float: Montant converti.
        """
        return self.convert(amount, from_=self._primary_code, to=to_code)

    # ── Formatage ─────────────────────────────────────────────────

    def format(self, amount, code: str = "", decimals: int = -1) -> str:
        """Formate un montant avec le symbole de la devise.

        Les montants stockés en BDD sont dans la devise principale.
        ``format()`` les affiche directement sans conversion.

        Args:
            amount: Montant numérique.
            code (str): Code devise (vide = devise principale).
            decimals (int): Décimales (-1 = selon la devise).

        Returns:
            str: Montant formaté ex: '1,250.00 DA' ou '€ 1,250.00'.
        """
        try:
            v = float(amount)
        except (TypeError, ValueError):
            v = 0.0

        currency = CURRENCIES.get(code or self._primary_code, CURRENCIES["DZD"])
        d = decimals if decimals >= 0 else currency.decimals

        if d == 0:
            formatted = f"{v:,.0f}"
        elif d == 3:
            formatted = f"{v:,.3f}"
        else:
            formatted = f"{v:,.2f}"

        if currency.symbol_after:
            return f"{formatted} {currency.symbol}"
        else:
            return f"{currency.symbol} {formatted}"

    def format_with_secondary(self, amount,
                               decimals: int = -1) -> tuple[str, str]:
        """Formate un montant en devise principale ET secondaire.

        Args:
            amount: Montant en devise principale.
            decimals (int): Décimales pour la devise principale.

        Returns:
            tuple[str, str]: (texte_principal, texte_secondaire).
                             Le secondaire est '' si aucune devise secondaire.
        """
        primary_text = self.format(amount, self._primary_code, decimals)
        if self._secondary_code:
            converted    = self.from_primary(float(amount or 0), self._secondary_code)
            secondary_text = self.format(converted, self._secondary_code, decimals)
        else:
            secondary_text = ""
        return primary_text, secondary_text

    def all_rates(self) -> list[tuple[str, float]]:
        """Retourne tous les taux sous forme de liste triée.

        Returns:
            list[tuple[str, float]]: [(code, taux_vers_DZD), ...]
        """
        return sorted(
            [(c, self._rates.get(c, DEFAULT_RATES_TO_DZD.get(c, 1.0)))
             for c in CURRENCIES],
            key=lambda x: x[0]
        )


# ──────────────────────────────────────────────────────────────────
# Instance globale unique
# ──────────────────────────────────────────────────────────────────

currency_manager = CurrencyManager()


# ──────────────────────────────────────────────────────────────────
# Fonctions utilitaires publiques (drop-in replacement de fmt_da)
# ──────────────────────────────────────────────────────────────────

def fmt(amount, decimals: int = -1, code: str = "") -> str:
    """Formate un montant en devise principale (remplace fmt_da).

    Rétrocompatible avec fmt_da(value, decimals) :
        fmt_da(1250, 0)  →  fmt(1250, 0)

    Args:
        amount: Montant numérique.
        decimals (int): Décimales (-1 = selon la devise).
        code (str): Code devise spécifique (vide = principale).

    Returns:
        str: Montant formaté ex: '1,250.00 DA'.
    """
    return currency_manager.format(amount, code=code, decimals=decimals)


def fmt_da(value, decimals: int = 2) -> str:
    """Alias rétrocompatible avec l'ancienne fonction fmt_da.

    Args:
        value: Montant numérique.
        decimals (int): Nombre de décimales (0 ou 2).

    Returns:
        str: Montant formaté dans la devise principale.
    """
    return currency_manager.format(value, decimals=decimals)


def convert(amount: float, from_: str = "", to: str = "") -> float:
    """Convertit un montant entre deux devises.

    Args:
        amount (float): Montant source.
        from_ (str): Code devise source (vide = principale).
        to (str): Code devise cible (vide = principale).

    Returns:
        float: Montant converti.
    """
    f = from_ or currency_manager.primary_code
    t = to    or currency_manager.primary_code
    return currency_manager.convert(amount, from_=f, to=t)
