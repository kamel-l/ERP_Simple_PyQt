"""
dashboard.py — Tableau de Bord Personnalisable
==============================================
"""

from PyQt6.QtWidgets import (
    QProgressBar, QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame,
    QPushButton, QScrollArea, QHeaderView, QTableWidget,
    QTableWidgetItem, QSizePolicy, QDialog, QCheckBox,
    QGridLayout, QMessageBox, QListWidget, QListWidgetItem,
    QAbstractItemView, QSpacerItem, QSizePolicy
)
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import (
    Qt, QObject, pyqtProperty, QPropertyAnimation, QEasingCurve,
    pyqtSignal
)
import json
from db_manager import get_database
try:
    from sales_history import InvoiceDetailsDialog
    _DETAIL_AVAILABLE = True
except ImportError:
    _DETAIL_AVAILABLE = False
from styles import COLORS
from currency import fmt_da, fmt, currency_manager


# ─────────────────────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────────────────────

def divider():
    f = QFrame()
    f.setFrameShape(QFrame.Shape.HLine)
    f.setStyleSheet(f"background:{COLORS['BORDER']}; border:none; max-height:1px;")
    return f

def _lbl(text, size=11, bold=False, color=""):
    l = QLabel(text)
    l.setFont(QFont("Segoe UI", size,
                    QFont.Weight.Bold if bold else QFont.Weight.Normal))
    l.setStyleSheet(f"color:{color or COLORS['TXT_PRI']}; background:transparent; border:none;")
    return l

def _card_frame(obj_name="card"):
    f = QFrame()
    f.setObjectName(obj_name)
    f.setStyleSheet(f"""
        QFrame#{obj_name} {{
            background: {COLORS['BG_CARD']};
            border-radius: 16px;
            border: 1px solid {COLORS['BORDER']};
        }}
    """)
    return f


# ─────────────────────────────────────────────────────────────
#  Animateur de compteur
# ─────────────────────────────────────────────────────────────

class KpiAnimator(QObject):
    def __init__(self, label, suffix=""):
        super().__init__()
        self._value = 0
        self.label  = label
        self.suffix = suffix

    def get_value(self): return self._value
    def set_value(self, v):
        self._value = v
        self.label.setText(f"{v:,.0f}{self.suffix}")

    value = pyqtProperty(float, get_value, set_value)

def animate_value(label, target, suffix=""):
    anim = KpiAnimator(label, suffix)
    a = QPropertyAnimation(anim, b"value")
    a.setDuration(900)
    a.setStartValue(0)
    a.setEndValue(float(target))
    a.setEasingCurve(QEasingCurve.Type.OutCubic)
    label._anim_ref = a
    label._anim_obj = anim
    a.start()


# ─────────────────────────────────────────────────────────────
#  Catalogue des widgets disponibles
# ─────────────────────────────────────────────────────────────

WIDGET_CATALOG = {
    "kpi_row":       {"id": "kpi_row",       "title": "Indicateurs KPI",       "icon": "📊", "desc": "Ventes, Achats, Bénéfice, Clients",    "default": True},
    "activities":    {"id": "activities",    "title": "Activités Récentes",    "icon": "🕒", "desc": "Dernières ventes et achats",             "default": True},
    "quick_info":    {"id": "quick_info",    "title": "Informations Rapides",  "icon": "⚡", "desc": "Ventes du jour, top client, stock",      "default": True},
    "invoice_table": {"id": "invoice_table", "title": "Dernières Factures",    "icon": "🧾", "desc": "Tableau des 10 dernières factures",      "default": True},
    "low_stock":     {"id": "low_stock",     "title": "Alertes Stock Faible",  "icon": "⚠️", "desc": "Produits sous le seuil minimum",         "default": False},
    "top_clients":   {"id": "top_clients",   "title": "Top Clients",           "icon": "🏆", "desc": "Classement par chiffre d'affaires",      "default": False},
    "sales_chart":   {"id": "sales_chart",   "title": "Résumé des Ventes",     "icon": "📈", "desc": "Ventes des 7 derniers jours",            "default": False},
}

DEFAULT_ORDER = [
    "kpi_row", "activities", "quick_info",
    "invoice_table"
]


# ─────────────────────────────────────────────────────────────
#  Persistance de la configuration
# ─────────────────────────────────────────────────────────────

class DashboardConfig:
    """Lit/écrit la configuration du dashboard dans la table settings."""

    _KEY = "dashboard_config"

    def __init__(self, db=None):
        self._db = db or get_database()

    def load(self) -> dict:
        """Charge la configuration (ou retourne les valeurs par défaut)."""
        try:
            raw = self._db.get_setting(self._KEY, None)
            if raw:
                cfg = json.loads(raw)
                for wid in DEFAULT_ORDER:
                    if wid not in cfg.get("order", []):
                        cfg.setdefault("order", []).append(wid)
                return cfg
        except Exception:
            pass
        return {
            "enabled": [w for w, m in WIDGET_CATALOG.items() if m["default"]],
            "order":   list(DEFAULT_ORDER),
        }

    def save(self, cfg: dict) -> None:
        """Persiste la configuration."""
        try:
            self._db.set_setting(self._KEY, json.dumps(cfg))
        except Exception as e:
            print(f"DashboardConfig.save: {e}")


# ─────────────────────────────────────────────────────────────
#  Dialogue de personnalisation
# ─────────────────────────────────────────────────────────────

class DashboardEditor(QDialog):
    """Dialogue de personnalisation : activer/réordonner les widgets."""

    config_changed = pyqtSignal(dict)

    def __init__(self, current_cfg: dict, parent=None):
        super().__init__(parent)
        self._cfg = {
            "enabled": list(current_cfg.get("enabled", [])),
            "order":   list(current_cfg.get("order", DEFAULT_ORDER)),
        }
        self.setWindowTitle("Personnaliser le Tableau de Bord")
        self.setMinimumSize(740, 580)
        self.setStyleSheet(f"background: {COLORS['BG_PAGE']};")
        self._build_ui()

    def _build_ui(self) -> None:
        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 24, 28, 24)
        lay.setSpacing(20)

        # En-tête
        hdr = QHBoxLayout()
        hdr.addWidget(_lbl("✨  Personnaliser le Tableau de Bord", 16, bold=True))
        hdr.addStretch()
        hdr.addWidget(_lbl("Cochez les widgets à afficher · Glissez pour réordonner",
                           10, color=COLORS['TXT_SEC']))
        lay.addLayout(hdr)
        lay.addWidget(divider())

        # Corps
        body = QHBoxLayout()
        body.setSpacing(20)

        # --- Gauche : catalogue ---
        left = _card_frame("left_c")
        ll   = QVBoxLayout(left)
        ll.setContentsMargins(16, 14, 16, 14)
        ll.setSpacing(10)
        ll.addWidget(_lbl("Widgets disponibles", 12, bold=True,
                          color=COLORS['primary']))
        ll.addWidget(divider())

        self._checks = {}
        for wid in self._cfg["order"]:
            meta = WIDGET_CATALOG.get(wid)
            if not meta:
                continue

            row = QHBoxLayout()
            row.setSpacing(12)

            # Icône
            icon_l = QLabel(meta["icon"])
            icon_l.setFont(QFont("Segoe UI", 16))
            icon_l.setFixedSize(38, 38)
            icon_l.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon_l.setStyleSheet(f"""
                background:{COLORS['primary']}22;
                border-radius:9px; border:none;
            """)
            row.addWidget(icon_l)

            # Texte
            tc = QVBoxLayout()
            tc.setSpacing(1)
            tc.addWidget(_lbl(meta["title"], 11, bold=True))
            tc.addWidget(_lbl(meta["desc"],   9, color=COLORS['TXT_SEC']))
            row.addLayout(tc)
            row.addStretch()

            # Checkbox
            cb = QCheckBox()
            cb.setChecked(wid in self._cfg["enabled"])
            cb.setStyleSheet(f"""
                QCheckBox::indicator {{
                    width:22px; height:22px;
                    border-radius:6px;
                    border:2px solid {COLORS['BORDER']};
                    background:{COLORS['BG_DEEP']};
                }}
                QCheckBox::indicator:checked {{
                    background:{COLORS['primary']};
                    border-color:{COLORS['primary']};
                }}
            """)
            cb.toggled.connect(lambda checked, w=wid: self._on_toggle(w, checked))
            self._checks[wid] = cb
            row.addWidget(cb)

            item_f = QFrame()
            item_f.setStyleSheet(f"""
                QFrame {{
                    background:{COLORS['BG_DEEP']};
                    border-radius:10px;
                    border:1px solid {COLORS['BORDER']};
                }}
                QFrame:hover {{ border-color:{COLORS['primary']}66; }}
            """)
            item_f.setLayout(row)
            item_f.layout().setContentsMargins(12, 10, 12, 10)
            ll.addWidget(item_f)

        ll.addStretch()
        body.addWidget(left, 3)

        # --- Droite : ordre ---
        right = _card_frame("right_c")
        rl    = QVBoxLayout(right)
        rl.setContentsMargins(16, 14, 16, 14)
        rl.setSpacing(10)
        rl.addWidget(_lbl("Ordre d'affichage", 12, bold=True,
                          color=COLORS['primary']))
        rl.addWidget(_lbl("↕  Glissez pour réordonner", 9,
                          color=COLORS['TXT_SEC']))
        rl.addWidget(divider())

        self._order_list = QListWidget()
        self._order_list.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self._order_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._order_list.setSpacing(4)
        self._order_list.setStyleSheet(f"""
            QListWidget {{ background:transparent; border:none; outline:none; }}
            QListWidget::item {{
                background:{COLORS['BG_DEEP']};
                border:1px solid {COLORS['BORDER']};
                border-radius:8px;
                padding:10px 14px;
                color:{COLORS['TXT_PRI']};
                font-size:12px;
                font-family:'Segoe UI';
                margin:2px 0;
            }}
            QListWidget::item:selected {{
                background:{COLORS['primary']}33;
                border-color:{COLORS['primary']};
            }}
            QListWidget::item:hover {{
                border-color:{COLORS['primary']}55;
            }}
        """)
        self._populate_order_list()
        rl.addWidget(self._order_list)
        body.addWidget(right, 2)
        lay.addLayout(body)

        # Boutons
        btn_row = QHBoxLayout()

        def styled_btn(text, color, bg="transparent"):
            b = QPushButton(text)
            b.setFixedHeight(42)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            b.setStyleSheet(f"""
                QPushButton {{
                    background:{bg};
                    color:{color};
                    border:1.5px solid {color}66;
                    border-radius:9px;
                    padding:0 20px;
                }}
                QPushButton:hover {{ background:{color}22; }}
            """)
            return b

        reset_btn  = styled_btn("↩️  Réinitialiser", COLORS['TXT_SEC'])
        cancel_btn = styled_btn("Annuler",            COLORS['TXT_SEC'])
        apply_btn  = styled_btn("✅  Appliquer",      "#FFFFFF", COLORS['primary'])
        apply_btn.setStyleSheet(apply_btn.styleSheet().replace(
            f"border:1.5px solid #FFFFFF66;", "border:none;"))

        reset_btn.clicked.connect(self._reset)
        cancel_btn.clicked.connect(self.reject)
        apply_btn.clicked.connect(self._apply)

        btn_row.addWidget(reset_btn)
        btn_row.addStretch()
        btn_row.addWidget(cancel_btn)
        btn_row.addSpacing(8)
        btn_row.addWidget(apply_btn)
        lay.addLayout(btn_row)

    def _populate_order_list(self) -> None:
        self._order_list.clear()
        for wid in self._cfg["order"]:
            meta = WIDGET_CATALOG.get(wid)
            if not meta:
                continue
            item = QListWidgetItem(f"  {meta['icon']}  {meta['title']}")
            item.setData(Qt.ItemDataRole.UserRole, wid)
            if wid not in self._cfg["enabled"]:
                item.setForeground(QColor(COLORS['TXT_SEC']))
            self._order_list.addItem(item)

    def _on_toggle(self, wid: str, checked: bool) -> None:
        if checked and wid not in self._cfg["enabled"]:
            self._cfg["enabled"].append(wid)
        elif not checked and wid in self._cfg["enabled"]:
            self._cfg["enabled"].remove(wid)
        self._populate_order_list()

    def _reset(self) -> None:
        self._cfg = {
            "enabled": [w for w, m in WIDGET_CATALOG.items() if m["default"]],
            "order":   list(DEFAULT_ORDER),
        }
        for wid, cb in self._checks.items():
            cb.blockSignals(True)
            cb.setChecked(wid in self._cfg["enabled"])
            cb.blockSignals(False)
        self._populate_order_list()

    def _apply(self) -> None:
        order = [self._order_list.item(i).data(Qt.ItemDataRole.UserRole)
                 for i in range(self._order_list.count())]
        self._cfg["order"] = [w for w in order if w]
        self.config_changed.emit(dict(self._cfg))
        self.accept()


# ─────────────────────────────────────────────────────────────
#  Constructeurs de widgets individuels
# ─────────────────────────────────────────────────────────────

class WidgetBuilder:
    """Construit chaque widget du dashboard."""

    def __init__(self, db, page):
        self.db   = db
        self.page = page

    # KPI
    def build_kpi_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(16)
        sym = currency_manager.primary.symbol
        kpis = [
            ("Ventes Totales", "0", "#6366F1", "💳", f" {sym}"),
            ("Achats",         "0", "#F59E0B", "🛒", f" {sym}"),
            ("Bénéfice Net",   "0", "#A855F7", "📈", f" {sym}"),
            ("Clients",        "0", "#06B6D4", "👥", ""),
        ]
        self.page._kpi_cards = []
        for title, val, color, icon, suffix in kpis:
            card = self._kpi_card(icon, title, val, color, suffix)
            row.addWidget(card)
            self.page._kpi_cards.append(card)
        return row

    def _kpi_card(self, icon, title, value, color, suffix):
        card = QFrame()
        card.setObjectName("kpi")
        card.setStyleSheet(f"""
            QFrame#kpi {{
                background:{COLORS['BG_CARD']};
                border-radius:16px;
                border:1px solid {COLORS['BORDER']};
            }}
        """)
        card.setMinimumHeight(130)
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(20, 18, 20, 18)
        lay.setSpacing(8)

        top = QHBoxLayout()
        badge = QLabel(icon)
        badge.setFont(QFont("Segoe UI", 14))
        badge.setFixedSize(36, 36)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setStyleSheet(f"background:{color}22; border-radius:10px; border:none;")
        top.addWidget(badge)
        top.addSpacing(8)
        tl = QLabel(title)
        tl.setFont(QFont("Segoe UI", 11))
        tl.setStyleSheet(f"color:{COLORS['TXT_SEC']}; background:transparent; border:none;")
        top.addWidget(tl)
        top.addStretch()
        lay.addLayout(top)

        lv = QLabel(value)
        lv.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        lv.setStyleSheet(f"color:{color}; background:transparent; border:none;")
        lay.addWidget(lv)

        bar = QFrame()
        bar.setFixedHeight(3)
        bar.setStyleSheet(f"""
            background:qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 {color}, stop:1 transparent);
            border-radius:2px; border:none;
        """)
        lay.addWidget(bar)
        card.value_label = lv
        card._suffix     = suffix
        return card

    # Activités
    def build_activities(self) -> QFrame:
        card = _card_frame("act")
        lay  = QVBoxLayout(card)
        lay.setContentsMargins(20, 18, 20, 18)
        lay.setSpacing(12)
        hdr = QHBoxLayout()
        hdr.addWidget(_lbl("🕒  Activités Récentes", 13, bold=True))
        hdr.addStretch()
        lay.addLayout(hdr)
        lay.addWidget(divider())
        self.page._activities_layout = QVBoxLayout()
        self.page._activities_layout.setSpacing(6)
        lay.addLayout(self.page._activities_layout)
        lay.addStretch()
        return card

    # Infos rapides
    def build_quick_info(self) -> QVBoxLayout:
        col = QVBoxLayout()
        col.setSpacing(16)
        sym = currency_manager.primary.symbol
        infos = [
            ("Ventes Aujourd'hui", f"0 {sym}", "#6366F1", "📅"),
            ("Top Client",         "—",          "#A855F7", "🏆"),
            ("Stock Faible",       "0 produits", "#F59E0B", "⚠️"),
        ]
        self.page._info_cards = []
        for title, val, color, icon in infos:
            c = self._info_card(icon, title, val, color)
            col.addWidget(c)
            self.page._info_cards.append(c)
        return col

    def _info_card(self, icon, title, value, color):
        card = QFrame()
        card.setObjectName("info")
        card.setStyleSheet(
            f"QFrame#info {{ background:{COLORS['BG_CARD']}; "
            f"border-radius:14px; border:1px solid {COLORS['BORDER']}; }}")
        card.setFixedHeight(90)
        lay = QHBoxLayout(card)
        lay.setContentsMargins(16, 12, 16, 12)
        lay.setSpacing(14)
        badge = QLabel(icon)
        badge.setFont(QFont("Segoe UI", 16))
        badge.setFixedSize(40, 40)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setStyleSheet(f"background:{color}22; border-radius:12px; border:none;")
        lay.addWidget(badge)
        txt = QVBoxLayout()
        txt.setSpacing(2)
        tl = QLabel(title)
        tl.setFont(QFont("Segoe UI", 9))
        tl.setStyleSheet(f"color:{COLORS['TXT_SEC']}; background:transparent; border:none;")
        txt.addWidget(tl)
        vl = QLabel(value)
        vl.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        vl.setStyleSheet(f"color:{color}; background:transparent; border:none;")
        txt.addWidget(vl)
        lay.addLayout(txt)
        lay.addStretch()
        card.value_label = vl
        return card

    # Tableau factures
    def build_invoice_table(self) -> QFrame:
        card = _card_frame("inv")
        lay  = QVBoxLayout(card)
        lay.setContentsMargins(20, 18, 20, 18)
        lay.setSpacing(14)
        hdr = QHBoxLayout()
        hdr.addWidget(_lbl("🧾  Dernières Factures", 13, bold=True))
        hdr.addStretch()
        hdr.addWidget(_lbl("10 dernières", 9, color=COLORS['TXT_SEC']))
        lay.addLayout(hdr)
        lay.addWidget(divider())

        tbl = QTableWidget(0, 6)
        tbl.setHorizontalHeaderLabels(["Facture","Client","Total","Date","Paiement",""])
        tbl.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        tbl.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        tbl.setColumnWidth(5, 90)
        tbl.verticalHeader().setVisible(False)
        tbl.setAlternatingRowColors(True)
        tbl.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        tbl.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        tbl.setShowGrid(False)
        tbl.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        tbl.setMinimumHeight(260)
        tbl.setStyleSheet(f"""
            QTableWidget {{ background:transparent; alternate-background-color:rgba(255,255,255,0.03);
                color:{COLORS['TXT_PRI']}; border:none; font-size:12px; }}
            QHeaderView::section {{ background:{COLORS['BG_DEEP']}; color:{COLORS['TXT_SEC']};
                font-size:11px; font-weight:bold; padding:10px 8px; border:none;
                border-bottom:1px solid {COLORS['BORDER']}; }}
            QTableWidget::item {{ padding:10px 8px; border-bottom:1px solid rgba(255,255,255,0.04); }}
            QTableWidget::item:selected {{ background:rgba(99,102,241,0.15); color:#A855F7; }}
        """)
        lay.addWidget(tbl)
        self.page.invoice_table = tbl  # Stocker la référence
        return card

    # Stock faible
    def build_low_stock(self) -> QFrame:
        card = _card_frame("low")
        lay  = QVBoxLayout(card)
        lay.setContentsMargins(20, 18, 20, 18)
        lay.setSpacing(10)
        hdr = QHBoxLayout()
        hdr.addWidget(_lbl("⚠️  Alertes Stock Faible", 13, bold=True))
        hdr.addStretch()
        lay.addLayout(hdr)
        lay.addWidget(divider())
        self.page._low_stock_layout = QVBoxLayout()
        self.page._low_stock_layout.setSpacing(6)
        lay.addLayout(self.page._low_stock_layout)
        lay.addStretch()
        return card

    # Top clients
    def build_top_clients(self) -> QFrame:
        card = _card_frame("topcli")
        lay  = QVBoxLayout(card)
        lay.setContentsMargins(20, 18, 20, 18)
        lay.setSpacing(10)
        hdr = QHBoxLayout()
        hdr.addWidget(_lbl("🏆  Top Clients", 13, bold=True))
        hdr.addStretch()
        lay.addLayout(hdr)
        lay.addWidget(divider())
        self.page._top_clients_layout = QVBoxLayout()
        self.page._top_clients_layout.setSpacing(6)
        lay.addLayout(self.page._top_clients_layout)
        lay.addStretch()
        return card

    # Résumé ventes
    def build_sales_chart(self) -> QFrame:
        card = _card_frame("schart")
        lay  = QVBoxLayout(card)
        lay.setContentsMargins(20, 18, 20, 18)
        lay.setSpacing(10)
        hdr = QHBoxLayout()
        hdr.addWidget(_lbl("📈  Ventes — 7 derniers jours", 13, bold=True))
        hdr.addStretch()
        lay.addLayout(hdr)
        lay.addWidget(divider())
        self.page._sales_chart_layout = QVBoxLayout()
        self.page._sales_chart_layout.setSpacing(4)
        lay.addLayout(self.page._sales_chart_layout)
        return card


# ─────────────────────────────────────────────────────────────
#  Page principale
# ─────────────────────────────────────────────────────────────

class DashboardPage(QWidget):
    """Tableau de bord avec widgets personnalisables et persistés."""

    def __init__(self):
        super().__init__()
        self.db      = get_database()
        self._config = DashboardConfig(self.db)
        self._cfg    = self._config.load()
        self.setStyleSheet(f"background:{COLORS['BG_PAGE']};")
        self._reset_refs()
        self._build_page()
        self.refresh()

    def _reset_refs(self):
        """Réinitialise toutes les références aux widgets."""
        self._kpi_cards = []
        self._info_cards = []
        self._activities_layout = None
        self.invoice_table = None
        self._low_stock_layout = None
        self._top_clients_layout = None
        self._sales_chart_layout = None
        self._sub_lbl = None

    # ── Construction ─────────────────────────────────────────

    def _build_page(self) -> None:
        """Construit (ou reconstruit) toute la page."""
        # Effacer l'ancien layout
        old = self.layout()
        if old:
            while old.count():
                item = old.takeAt(0)
                w = item.widget()
                if w is not None:
                    w.setParent(None)
                    w.deleteLater()
            # Détacher le layout
            QWidget().setLayout(old)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border:none; background:transparent; }")

        container = QWidget()
        container.setStyleSheet("background:transparent;")
        self._main = QVBoxLayout(container)
        self._main.setSpacing(24)
        self._main.setContentsMargins(32, 28, 32, 28)

        self._build_header()
        self._reset_refs()
        self._build_widgets()
        self._main.addStretch()

        scroll.setWidget(container)
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(scroll)

    def _build_header(self) -> None:
        row = QHBoxLayout()
        row.setSpacing(12)

        col = QVBoxLayout()
        col.setSpacing(3)
        col.addWidget(_lbl("📊 Tableau de Bord", 22, bold=True))
        n = len(self._cfg.get("enabled", []))
        
        # Créer le sous-titre et le stocker
        self._sub_lbl = _lbl(
            f"Vue d'ensemble de l'activité  ·  {n} widget(s) actif(s)",
            11, color=COLORS['TXT_SEC'])
        col.addWidget(self._sub_lbl)
        row.addLayout(col)
        row.addStretch()

        # Bouton Personnaliser
        cb = QPushButton("✨  Personnaliser")
        cb.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        cb.setFixedHeight(38)
        cb.setFixedWidth(155)
        cb.setCursor(Qt.CursorShape.PointingHandCursor)
        cb.setStyleSheet(f"""
            QPushButton {{
                background:{COLORS['secondary']}22;
                color:{COLORS['secondary']};
                border:1.5px solid {COLORS['secondary']}66;
                border-radius:10px; padding:0 16px;
            }}
            QPushButton:hover {{ background:{COLORS['secondary']}44; }}
        """)
        cb.clicked.connect(self._open_editor)
        row.addWidget(cb)

        self._main.addLayout(row)

    def _build_widgets(self) -> None:
        """Construit et place les widgets selon la configuration."""
        builder = WidgetBuilder(self.db, self)
        enabled = self._cfg.get("enabled", [])
        order   = self._cfg.get("order", DEFAULT_ORDER)
        to_build = [w for w in order if w in enabled]

        skip = set()
        for wid in to_build:
            if wid in skip:
                continue

            if wid == "kpi_row":
                kpi_layout = builder.build_kpi_row()
                self._main.addLayout(kpi_layout)

            elif wid == "activities":
                act = builder.build_activities()
                if "quick_info" in to_build:
                    qi  = builder.build_quick_info()
                    row = QHBoxLayout()
                    row.setSpacing(16)
                    row.addWidget(act, 3)
                    row.addLayout(qi, 2)
                    self._main.addLayout(row)
                    skip.add("quick_info")
                else:
                    self._main.addWidget(act)

            elif wid == "quick_info":
                # Seul (activities pas dans la liste)
                qi  = builder.build_quick_info()
                row = QHBoxLayout()
                row.setSpacing(16)
                row.addLayout(qi)
                self._main.addLayout(row)

            elif wid == "invoice_table":
                inv_table = builder.build_invoice_table()
                self._main.addWidget(inv_table)

            elif wid == "low_stock":
                ls = builder.build_low_stock()
                if "top_clients" in to_build:
                    tc  = builder.build_top_clients()
                    row = QHBoxLayout()
                    row.setSpacing(16)
                    row.addWidget(ls, 1)
                    row.addWidget(tc, 1)
                    self._main.addLayout(row)
                    skip.add("top_clients")
                else:
                    self._main.addWidget(ls)

            elif wid == "top_clients":
                tc = builder.build_top_clients()
                self._main.addWidget(tc)

            elif wid == "sales_chart":
                sc = builder.build_sales_chart()
                self._main.addWidget(sc)

    # ── Éditeur ──────────────────────────────────────────────

    def _open_editor(self) -> None:
        dlg = DashboardEditor(self._cfg, parent=self)
        dlg.config_changed.connect(self._apply_config)
        dlg.exec()

    def _apply_config(self, new_cfg: dict) -> None:
        self._cfg = new_cfg
        self._config.save(new_cfg)
        self._build_page()
        self.refresh()

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh()

    # ── Chargement données ────────────────────────────────────

    def refresh(self) -> None:
        enabled = self._cfg.get("enabled", [])
        if "kpi_row"       in enabled: self._load_kpis()
        if "activities"    in enabled: self._load_activities()
        if "quick_info"    in enabled: self._load_quick_info()
        if "invoice_table" in enabled: self._load_invoices()
        if "low_stock"     in enabled: self._load_low_stock()
        if "top_clients"   in enabled: self._load_top_clients()
        if "sales_chart"   in enabled: self._load_sales_chart()

    def _load_kpis(self) -> None:
        
        stats = self.db.get_statistics() or {}
        sales = float(stats.get("sales_total", 0))
        pur   = float(stats.get("purchases_total", 0))
        prof  = sales - pur
        cli   = int(stats.get("total_clients", 0))
        sym   = currency_manager.primary.symbol
        for card, val, suf in zip(
            self._kpi_cards,
            [sales, pur, prof, float(cli)],
            [f" {sym}", f" {sym}", f" {sym}", ""]
        ):
            animate_value(card.value_label, val, suf)

    def _load_activities(self) -> None:
        """Charge les activités récentes (ventes + achats)."""

        while self._activities_layout.count():
            item = self._activities_layout.takeAt(0)
            w = item.widget()
            if w is not None: w.deleteLater()
            
        try:
            sales = self.db.get_all_sales(limit=4) or []
        except Exception as e:
            print(f"❌ ERREUR get_all_sales : {e}")
            import traceback
            traceback.print_exc()   # ← affiche la vraie erreur complète
            sales = []

        try:
            purs = self.db.get_all_purchases(limit=4) or []
        except Exception as e:
            print(f"❌ ERREUR get_all_purchases : {e}")
            import traceback
            traceback.print_exc()
            purs = []

        if not sales and not purs:
            lbl = QLabel("Aucune activité récente")
            lbl.setFont(QFont("Segoe UI", 11))
            lbl.setStyleSheet(f"color:{COLORS['TXT_SEC']}; padding:12px; background:transparent;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._activities_layout.addWidget(lbl)
            return

        def add_row(dot_color, icon, text):
            rw = QWidget()
            rw.setStyleSheet("background:transparent;")
            rl = QHBoxLayout(rw)
            rl.setContentsMargins(4, 4, 4, 4)
            rl.setSpacing(10)
            dot = QLabel(icon)
            dot.setFixedSize(22, 22)
            dot.setAlignment(Qt.AlignmentFlag.AlignCenter)
            dot.setStyleSheet(f"""
                background:{dot_color}22; color:{dot_color};
                border-radius:11px; border:none; font-size:11px;
            """)
            rl.addWidget(dot)
            lbl = QLabel(text)
            lbl.setFont(QFont("Segoe UI", 10))
            lbl.setStyleSheet(f"color:{COLORS['TXT_SEC']}; background:transparent; border:none;")
            rl.addWidget(lbl, 1)
            self._activities_layout.addWidget(rw)

        for s in sales:
            inv  = s.get('invoice_number', '—')
            tot  = float(s.get('total') or 0)
            cli  = s.get('client_name', '')
            txt  = f"Vente  {inv}"
            
            if cli: txt += f"  ·  {cli[:20]}"
            txt += f"  —  {fmt_da(tot, 0)}"
            add_row("#6366F1", "🧾", txt)
            

        for p in purs:
            nom = p.get('product_name') or f"Produit #{p.get('product_id','?')}"
            tot = float(p.get('total') or 0)
            sup = p.get('supplier_name', '')
            txt = f"Achat  {nom[:22]}"
            if sup: txt += f"  ·  {sup[:16]}"
            txt += f"  —  {fmt_da(tot, 0)}"
            add_row("#F59E0B", "📦", txt)

    def _load_quick_info(self) -> None:
        
        stats = self.db.get_statistics() or {}
        self._info_cards[0].value_label.setText(
            fmt_da(float(stats.get("sales_today", 0))))
        top = self.db.get_top_clients(limit=1)
        self._info_cards[1].value_label.setText(top[0]["name"] if top else "—")
        low = self.db.get_low_stock_products() or []
        self._info_cards[2].value_label.setText(
            f"{len(low)} produit{'s' if len(low) != 1 else ''}")

    def _load_invoices(self) -> None:
        """Charge les 10 dernières factures dans le tableau."""
        if not self.invoice_table:
            print("⚠️ invoice_table est None - widget peut-être désactivé")
            return
        
        try:
            data = self.db.get_all_sales(limit=10) or []
        except Exception as e:
            print(f"❌ Erreur chargement factures: {e}")
            data = []
        
        self.invoice_table.setRowCount(len(data))
        for r, sale in enumerate(data):
            client = sale.get("client_name") or sale.get("client") or "—"
            date   = str(sale.get("sale_date") or "—").split(" ")[0]
            pay    = sale.get("payment_method") or sale.get("payment_mode") or "—"
            # Récupération robuste du total (plusieurs noms possibles)
            total  = float(sale.get("total") or sale.get("grand_total") or
                           sale.get("total_amount") or 0)
            cells  = [
                (f"{sale.get('invoice_number','—')}", "#F1F7F4"),
                (client,                              "#F1F7F4"),
                (fmt_da(total),                       "#10B981"),
                (date,                                "#F1F7F4"),
                (pay,                                 "#F1F7F4"),
            ]
            for col, (val, color) in enumerate(cells):
                item = QTableWidgetItem(str(val))
                item.setForeground(QColor(color))
                item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                self.invoice_table.setItem(r, col, item)

            btn = QPushButton("👁 Détails")
            btn.setFixedHeight(30)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background:rgba(99,102,241,0.18); color:#A5B4FC;
                    border:1px solid rgba(99,102,241,0.40);
                    border-radius:7px; font-size:11px; font-weight:bold; padding:0 8px;
                }
                QPushButton:hover { background:rgba(99,102,241,0.38); color:white; }
            """)
            sid = sale['id']
            btn.clicked.connect(lambda _, s=sid: self._open_detail(s))
            self.invoice_table.setCellWidget(r, 5, btn)
            self.invoice_table.setRowHeight(r, 44)

    def _load_low_stock(self) -> None:
        """Charge les alertes de stock faible."""
        
        while self._low_stock_layout.count():
            item = self._low_stock_layout.takeAt(0)
            w = item.widget()
            if w is not None: w.deleteLater()
        try:
            products = self.db.get_low_stock_products() or []
        except Exception:
            products = []
        if not products:
            self._low_stock_layout.addWidget(
                _lbl("✅  Aucune alerte de stock", 11, color=COLORS['success']))
            return
        for p in products[:8]:
            rw = QWidget()
            rw.setStyleSheet("background:transparent;")
            rl = QHBoxLayout(rw)
            rl.setContentsMargins(0, 4, 0, 4)
            rl.setSpacing(8)
            rl.addWidget(_lbl("⚠", 10, color=COLORS['warning']))
            rl.addWidget(_lbl(p.get('name','')[:26], 10), 1)
            stock = int(p.get('stock_quantity', 0))
            mini  = int(p.get('min_stock', 0))
            col   = COLORS['danger'] if stock == 0 else COLORS['warning']
            sl    = _lbl(f"{stock} / min {mini}", 10, color=col)
            sl.setAlignment(Qt.AlignmentFlag.AlignRight)
            rl.addWidget(sl)
            self._low_stock_layout.addWidget(rw)

    def _load_top_clients(self) -> None:
        """Charge le classement des top clients."""
        
        while self._top_clients_layout.count():
            item = self._top_clients_layout.takeAt(0)
            w = item.widget()
            if w is not None: w.deleteLater()
        try:
            clients = self.db.get_top_clients(limit=5)
        except Exception:
            clients = []
        if not clients:
            self._top_clients_layout.addWidget(
                _lbl("Aucune donnée disponible", 11, color=COLORS['TXT_SEC']))
            return
        MEDAL  = ["🥇","🥈","🥉","4️⃣","5️⃣"]
        max_t  = max((float(c.get('total_spent',0)) for c in clients), default=1) or 1
        for rank, c in enumerate(clients):
            name  = c.get('name','—')[:24]
            total = float(c.get('total_spent',0))
            pct   = total / max_t

            rw = QWidget()
            rw.setStyleSheet("background:transparent;")
            rl = QHBoxLayout(rw)
            rl.setContentsMargins(0, 4, 0, 0)
            rl.setSpacing(8)
            rl.addWidget(_lbl(MEDAL[rank], 14))
            rl.addWidget(_lbl(name, 10, bold=True), 1)
            vl = _lbl(fmt_da(total, 0), 10, color=COLORS['primary'])
            vl.setAlignment(Qt.AlignmentFlag.AlignRight)
            rl.addWidget(vl)
            self._top_clients_layout.addWidget(rw)

            bar = QFrame()
            bar.setFixedHeight(3)
            bar.setStyleSheet(f"""
                background:qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 {COLORS['primary']},
                    stop:{pct:.2f} {COLORS['primary']},
                    stop:{min(pct+0.01,1):.3f} transparent,
                    stop:1 transparent);
                border-radius:2px; border:none;
            """)
            self._top_clients_layout.addWidget(bar)

    def _load_sales_chart(self) -> None:
        """Charge le graphique ventes 7 derniers jours."""
    
        while self._sales_chart_layout.count():
            item = self._sales_chart_layout.takeAt(0)
            w = item.widget()
            if w is not None: w.deleteLater()
        try:
            self.db.cursor.execute("""
                SELECT DATE(sale_date) as day,
                       SUM(total) as total,
                       COUNT(*) as nb
                FROM sales
                WHERE sale_date >= DATE('now', '-7 days')
                GROUP BY day ORDER BY day
            """)
            rows = self.db.cursor.fetchall()
        except Exception:
            rows = []

        if not rows:
            self._sales_chart_layout.addWidget(
                _lbl("Aucune vente sur les 7 derniers jours", 11,
                     color=COLORS['TXT_SEC']))
            return

        JOURS  = ["Lun","Mar","Mer","Jeu","Ven","Sam","Dim"]
        max_v  = max((float(r[1] if not hasattr(r,'keys') else r['total'])
                      for r in rows), default=1) or 1
        grid   = QGridLayout()
        grid.setSpacing(8)
        grid.setColumnStretch(1, 1)

        for i, row in enumerate(rows):
            try:
                day   = str(row['day']   if hasattr(row,'keys') else row[0])
                total = float(row['total'] if hasattr(row,'keys') else row[1])
                nb    = int(row['nb']    if hasattr(row,'keys') else row[2])
            except Exception:
                continue
            try:
                import datetime
                dn = JOURS[datetime.date.fromisoformat(day).weekday()]
            except Exception:
                dn = day[-5:]

            grid.addWidget(_lbl(dn, 9, color=COLORS['TXT_SEC']), i, 0)

            bar_w = QProgressBar()
            bar_w.setRange(0, 1000)
            bar_w.setValue(int((total / max_v) * 1000))
            bar_w.setTextVisible(False)
            bar_w.setFixedHeight(20)
            bar_w.setStyleSheet(f"""
                QProgressBar {{
                    background: {COLORS['BG_DEEP']};
                    border-radius: 4px; border: none;
                }}
                QProgressBar::chunk {{
                    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                        stop:0 {COLORS['primary']}88, stop:1 {COLORS['primary']});
                    border-radius: 4px;
                }}
            """)
            grid.addWidget(bar_w, i, 1)

            vl = _lbl(f"{fmt_da(total,0)}  · {nb} vente{'s' if nb>1 else ''}",
                      9, color=COLORS['TXT_SEC'])
            vl.setMinimumWidth(160)
            grid.addWidget(vl, i, 2)

        self._sales_chart_layout.addLayout(grid)

    def _open_detail(self, sale_id: int) -> None:
        if not _DETAIL_AVAILABLE:
            QMessageBox.warning(self, "Module manquant",
                "Le module sales_history.py est introuvable.")
            return
        sale = self.db.get_sale_by_id(sale_id)
        if sale:
            InvoiceDetailsDialog(sale, self).exec()


