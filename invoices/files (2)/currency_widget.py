"""
currency_widget.py — Widget de gestion multi-devises pour les Paramètres
=========================================================================

Fournit deux composants :

  CurrencySettingsWidget — panneau complet intégrable dans SettingsPage :
    • Sélecteur de devise principale
    • Sélecteur de devise secondaire (optionnel)
    • Tableau de tous les taux de change modifiables
    • Bouton de rafraîchissement depuis une API publique
    • Aperçu en temps réel du formatage

  CurrencySelector — combobox stylisée réutilisable ailleurs
"""

import json
import urllib.request
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QDoubleSpinBox, QFrame, QScrollArea,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QGridLayout, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QObject
from PyQt6.QtGui import QFont, QColor

from styles import COLORS
from currency import (
    currency_manager, CURRENCIES, DEFAULT_RATES_TO_DZD,
    Currency, fmt
)


# ──────────────────────────────────────────────────────────────────
# Helpers visuels
# ──────────────────────────────────────────────────────────────────

def _lbl(text: str, size: int = 11, bold: bool = False,
         color: str = "") -> QLabel:
    l = QLabel(text)
    l.setFont(QFont("Segoe UI", size,
                    QFont.Weight.Bold if bold else QFont.Weight.Normal))
    l.setStyleSheet(f"color: {color or COLORS['TXT_PRI']}; background: transparent;")
    return l


def _sep() -> QFrame:
    f = QFrame()
    f.setFrameShape(QFrame.Shape.HLine)
    f.setStyleSheet(f"color: {COLORS['BORDER']};")
    return f


# ──────────────────────────────────────────────────────────────────
# Thread de récupération des taux en ligne
# ──────────────────────────────────────────────────────────────────

class RateFetchWorker(QObject):
    """Récupère les taux depuis l'API publique open.er-api.com.

    Signals:
        finished (dict): Taux récupérés {code: taux_vers_DZD}.
        error (str): Message d'erreur en cas d'échec.
    """

    finished = pyqtSignal(dict)
    error    = pyqtSignal(str)

    def run(self) -> None:
        """Lance la requête HTTP dans le thread courant."""
        try:
            url = "https://open.er-api.com/v6/latest/DZD"
            req = urllib.request.Request(url, headers={"User-Agent": "ERP-DAR/1.0"})
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode())

            if data.get("result") != "success":
                self.error.emit("L'API n'a pas retourné de données valides.")
                return

            rates_from_dzd = data.get("rates", {})
            # Inverser : on veut taux_vers_DZD = 1 / (1 DZD en X)
            converted = {}
            for code in CURRENCIES:
                if code == "DZD":
                    converted["DZD"] = 1.0
                elif code in rates_from_dzd and rates_from_dzd[code] != 0:
                    converted[code] = round(1.0 / rates_from_dzd[code], 4)

            self.finished.emit(converted)
        except Exception as e:
            self.error.emit(f"Impossible de récupérer les taux : {e}")


# ──────────────────────────────────────────────────────────────────
# ComboBox de sélection de devise
# ──────────────────────────────────────────────────────────────────

class CurrencySelector(QComboBox):
    """ComboBox stylisée affichant le drapeau, le code et le nom.

    Args:
        allow_none (bool): Si True, ajoute « — Aucune —» en première option.
    """

    def __init__(self, allow_none: bool = False, parent=None):
        super().__init__(parent)
        self.setFixedHeight(44)
        self.setStyleSheet(f"""
            QComboBox {{
                background: {COLORS['BG_DEEP']};
                border: 1.5px solid {COLORS['BORDER']};
                border-radius: 8px;
                color: {COLORS['TXT_PRI']};
                padding: 0 14px;
                font-size: 13px;
            }}
            QComboBox:focus {{ border-color: {COLORS['primary']}; }}
            QComboBox::drop-down {{ border: none; width: 28px; }}
            QComboBox QAbstractItemView {{
                background: {COLORS['BG_CARD']};
                color: {COLORS['TXT_PRI']};
                selection-background-color: {COLORS['primary']}44;
                border: 1px solid {COLORS['BORDER']};
                font-size: 12px;
            }}
        """)

        if allow_none:
            self.addItem("— Aucune —", userData="")

        for code, cur in CURRENCIES.items():
            self.addItem(f"{cur.flag}  {code} — {cur.name}", userData=code)

    def set_currency(self, code: str) -> None:
        """Sélectionne une devise par son code ISO.

        Args:
            code (str): Code ISO (ex: 'DZD').
        """
        for i in range(self.count()):
            if self.itemData(i) == code:
                self.setCurrentIndex(i)
                return

    def current_code(self) -> str:
        """Retourne le code de la devise sélectionnée."""
        return self.currentData() or ""


# ──────────────────────────────────────────────────────────────────
# Widget principal de gestion des devises
# ──────────────────────────────────────────────────────────────────

class CurrencySettingsWidget(QWidget):
    """Panneau de configuration multi-devises.

    À insérer dans la page Paramètres → onglet Finance.

    Signals:
        settings_changed: Émis quand devise ou taux sont modifiés.
    """

    settings_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")
        self._spin_widgets: dict[str, QDoubleSpinBox] = {}
        self._build_ui()
        self._load_current_values()

    # ── Construction de l'interface ───────────────────────────────

    def _build_ui(self) -> None:
        """Construit le panneau complet."""
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(16)

        # ── Section 1 : Devises ───────────────────────────────────
        lay.addWidget(self._build_currencies_section())

        # ── Section 2 : Aperçu ────────────────────────────────────
        lay.addWidget(self._build_preview_section())

        # ── Section 3 : Taux de change ────────────────────────────
        lay.addWidget(self._build_rates_section())

    def _card(self, title: str, icon: str) -> tuple[QFrame, QVBoxLayout]:
        """Crée une carte avec titre."""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['BG_CARD']};
                border-radius: 12px;
                border: 1px solid {COLORS['BORDER']};
            }}
        """)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(18, 14, 18, 14)
        lay.setSpacing(12)

        hdr = QHBoxLayout()
        hdr.addWidget(_lbl(f"{icon}  {title}", 12, bold=True,
                           color=COLORS['primary']))
        hdr.addStretch()
        lay.addLayout(hdr)
        lay.addWidget(_sep())

        return card, lay

    def _build_currencies_section(self) -> QFrame:
        """Construit la section de sélection des devises."""
        card, lay = self._card("Devises", "💱")

        grid = QGridLayout()
        grid.setSpacing(12)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(3, 1)

        # Devise principale
        grid.addWidget(_lbl("Devise principale *", color=COLORS['TXT_SEC']), 0, 0)
        self._primary_sel = CurrencySelector(allow_none=False)
        self._primary_sel.currentIndexChanged.connect(self._on_primary_changed)
        grid.addWidget(self._primary_sel, 0, 1)

        # Devise secondaire
        grid.addWidget(_lbl("Devise secondaire", color=COLORS['TXT_SEC']), 0, 2)
        self._secondary_sel = CurrencySelector(allow_none=True)
        self._secondary_sel.currentIndexChanged.connect(self._on_secondary_changed)
        grid.addWidget(self._secondary_sel, 0, 3)

        lay.addLayout(grid)

        info = _lbl(
            "💡  La devise principale est utilisée pour stocker tous les montants. "
            "La devise secondaire s'affiche en complément (ex: EUR + USD).",
            9, color=COLORS['TXT_SEC'])
        info.setWordWrap(True)
        lay.addWidget(info)

        return card

    def _build_preview_section(self) -> QFrame:
        """Construit la section d'aperçu du formatage."""
        card, lay = self._card("Aperçu du Formatage", "👁")

        row = QHBoxLayout()

        self._preview_primary = _lbl("1 250,00 DA", 20, bold=True,
                                     color=COLORS['primary'])
        self._preview_primary.setAlignment(Qt.AlignmentFlag.AlignCenter)
        row.addWidget(self._preview_primary, 2)

        arrow = _lbl("  ≈  ", 16, color=COLORS['TXT_SEC'])
        arrow.setAlignment(Qt.AlignmentFlag.AlignCenter)
        row.addWidget(arrow)

        self._preview_secondary = _lbl("—", 15, color=COLORS['TXT_SEC'])
        self._preview_secondary.setAlignment(Qt.AlignmentFlag.AlignCenter)
        row.addWidget(self._preview_secondary, 2)

        lay.addLayout(row)
        return card

    def _build_rates_section(self) -> QFrame:
        """Construit la section des taux de change."""
        card, lay = self._card("Taux de Change", "📊")

        # Bouton rafraîchir en ligne
        hdr2 = QHBoxLayout()
        hdr2.addWidget(_lbl(
            f"Taux exprimés en : 1 devise = X DZD",
            10, color=COLORS['TXT_SEC']))
        hdr2.addStretch()

        self._refresh_btn = QPushButton("🌐  Actualiser en ligne")
        self._refresh_btn.setFixedHeight(34)
        self._refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['info']}22;
                color: {COLORS['info']};
                border: 1px solid {COLORS['info']}66;
                border-radius: 6px;
                font-size: 11px;
                font-weight: bold;
                padding: 0 12px;
            }}
            QPushButton:hover {{ background: {COLORS['info']}44; }}
            QPushButton:disabled {{
                color: {COLORS['TXT_SEC']};
                border-color: {COLORS['BORDER']};
                background: transparent;
            }}
        """)
        self._refresh_btn.clicked.connect(self._fetch_rates_online)
        hdr2.addWidget(self._refresh_btn)
        lay.addLayout(hdr2)

        # Grille des taux — 4 colonnes
        rates_grid = QGridLayout()
        rates_grid.setSpacing(8)

        codes = [c for c in CURRENCIES if c != "DZD"]  # DZD toujours = 1
        for idx, code in enumerate(codes):
            cur   = CURRENCIES[code]
            col   = (idx % 2) * 3
            row_i = idx // 2

            lbl_w = _lbl(f"{cur.flag} {code}", 10, bold=True)
            lbl_w.setFixedWidth(60)
            rates_grid.addWidget(lbl_w, row_i, col)

            lbl_n = _lbl(cur.name[:18], 9, color=COLORS['TXT_SEC'])
            rates_grid.addWidget(lbl_n, row_i, col + 1)

            spin = QDoubleSpinBox()
            spin.setRange(0.0001, 999_999.0)
            spin.setDecimals(4)
            spin.setSingleStep(0.5)
            spin.setValue(DEFAULT_RATES_TO_DZD.get(code, 1.0))
            spin.setSuffix(" DZD")
            spin.setFixedHeight(36)
            spin.setFixedWidth(145)
            spin.setStyleSheet(f"""
                QDoubleSpinBox {{
                    background: {COLORS['BG_DEEP']};
                    border: 1px solid {COLORS['BORDER']};
                    border-radius: 6px;
                    color: {COLORS['TXT_PRI']};
                    padding: 0 8px;
                    font-size: 11px;
                }}
                QDoubleSpinBox:focus {{ border-color: {COLORS['primary']}; }}
            """)
            spin.valueChanged.connect(
                lambda v, c=code: self._on_rate_changed(c, v))
            rates_grid.addWidget(spin, row_i, col + 2)
            self._spin_widgets[code] = spin

        lay.addLayout(rates_grid)

        # Ligne DZD fixe
        dzd_row = QHBoxLayout()
        dzd_row.addWidget(_lbl("🇩🇿 DZD — Dinar Algérien", 10, bold=True))
        dzd_row.addStretch()
        dzd_row.addWidget(_lbl("= 1.0000 DZD  (référence)", 10,
                               color=COLORS['TXT_SEC']))
        lay.addLayout(dzd_row)

        # Bouton réinitialiser
        reset_btn = QPushButton("↩️  Réinitialiser aux taux par défaut")
        reset_btn.setFixedHeight(34)
        reset_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        reset_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {COLORS['TXT_SEC']};
                border: 1px solid {COLORS['BORDER']};
                border-radius: 6px;
                font-size: 10px;
                padding: 0 12px;
            }}
            QPushButton:hover {{
                background: {COLORS['BG_DEEP']};
                color: {COLORS['TXT_PRI']};
            }}
        """)
        reset_btn.clicked.connect(self._reset_rates)
        row_btn = QHBoxLayout()
        row_btn.addStretch()
        row_btn.addWidget(reset_btn)
        lay.addLayout(row_btn)

        return card

    # ── Chargement / Sauvegarde ───────────────────────────────────

    def _load_current_values(self) -> None:
        """Charge les valeurs courantes depuis currency_manager."""
        self._primary_sel.set_currency(currency_manager.primary_code)
        self._secondary_sel.set_currency(currency_manager.secondary_code or "")

        for code, spin in self._spin_widgets.items():
            spin.blockSignals(True)
            spin.setValue(currency_manager.get_rate_to_dzd(code))
            spin.blockSignals(False)

        self._update_preview()

    def save(self, db=None) -> None:
        """Sauvegarde les paramètres dans currency_manager et en BDD.

        Args:
            db: Instance Database pour la persistance.
        """
        currency_manager.primary_code   = self._primary_sel.current_code()
        currency_manager.secondary_code = self._secondary_sel.current_code() or None

        for code, spin in self._spin_widgets.items():
            currency_manager.set_rate_to_dzd(code, spin.value())

        currency_manager.save(db)
        self.settings_changed.emit()

    # ── Événements ────────────────────────────────────────────────

    def _on_primary_changed(self, _) -> None:
        self._update_preview()

    def _on_secondary_changed(self, _) -> None:
        self._update_preview()

    def _on_rate_changed(self, code: str, value: float) -> None:
        currency_manager.set_rate_to_dzd(code, value)
        self._update_preview()

    def _update_preview(self) -> None:
        """Met à jour l'aperçu de formatage en temps réel."""
        sample = 1250.0
        pri_code = self._primary_sel.current_code()
        sec_code = self._secondary_sel.current_code()

        if pri_code:
            self._preview_primary.setText(
                currency_manager.format(sample, pri_code))
        if sec_code and sec_code != pri_code:
            rate      = currency_manager.get_rate(pri_code, sec_code)
            converted = sample * rate
            self._preview_secondary.setText(
                f"≈  {currency_manager.format(converted, sec_code)}")
        else:
            self._preview_secondary.setText("—")

    def _reset_rates(self) -> None:
        """Réinitialise tous les taux aux valeurs par défaut."""
        reply = QMessageBox.question(
            self, "Réinitialiser les taux",
            "Remettre tous les taux de change aux valeurs par défaut ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            for code, spin in self._spin_widgets.items():
                spin.blockSignals(True)
                spin.setValue(DEFAULT_RATES_TO_DZD.get(code, 1.0))
                spin.blockSignals(False)
                currency_manager.set_rate_to_dzd(
                    code, DEFAULT_RATES_TO_DZD.get(code, 1.0))
            self._update_preview()

    def _fetch_rates_online(self) -> None:
        """Lance la récupération des taux depuis l'API publique."""
        self._refresh_btn.setEnabled(False)
        self._refresh_btn.setText("⏳  Récupération…")

        self._thread = QThread()
        self._worker = RateFetchWorker()
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.finished.connect(self._on_rates_fetched)
        self._worker.error.connect(self._on_rates_error)
        self._worker.finished.connect(self._thread.quit)
        self._worker.error.connect(self._thread.quit)
        self._thread.finished.connect(self._thread.deleteLater)
        self._thread.start()

    def _on_rates_fetched(self, rates: dict) -> None:
        """Applique les taux récupérés en ligne."""
        count = 0
        for code, rate in rates.items():
            if code in self._spin_widgets:
                self._spin_widgets[code].blockSignals(True)
                self._spin_widgets[code].setValue(rate)
                self._spin_widgets[code].blockSignals(False)
                currency_manager.set_rate_to_dzd(code, rate)
                count += 1

        self._update_preview()
        self._refresh_btn.setEnabled(True)
        self._refresh_btn.setText("🌐  Actualiser en ligne")
        QMessageBox.information(
            self, "✅ Taux mis à jour",
            f"{count} taux de change mis à jour depuis open.er-api.com\n"
            f"N'oubliez pas d'enregistrer les paramètres.")

    def _on_rates_error(self, msg: str) -> None:
        """Affiche l'erreur de récupération."""
        self._refresh_btn.setEnabled(True)
        self._refresh_btn.setText("🌐  Actualiser en ligne")
        QMessageBox.warning(self, "Connexion impossible", msg +
                            "\n\nVérifiez votre connexion internet.\n"
                            "Vous pouvez saisir les taux manuellement.")
