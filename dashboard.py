from PyQt6.QtWidgets import (




    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame,
    QPushButton, QScrollArea, QHeaderView, QTableWidget,
    QTableWidgetItem, QSizePolicy
)
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt, QObject, pyqtProperty, QPropertyAnimation, QEasingCurve
from db_manager import get_database
try:
    from sales_history import InvoiceDetailsDialog
    _DETAIL_AVAILABLE = True
except ImportError:
    _DETAIL_AVAILABLE = False
from styles import COLORS, BUTTON_STYLES, INPUT_STYLE, TABLE_STYLE


# ─────────────────────────────────────────────────────────────
#  Constantes de style
# ─────────────────────────────────────────────────────────────
def fmt_da(value, decimals=2):
    """Format monétaire algérien : 1,200.00 DA"""
    try:
        v = float(value)
    except (TypeError, ValueError):
        v = 0.0
    if decimals == 0:
        return f"{v:,.0f} DA"
    return f"{v:,.2f} DA"



# ─────────────────────────────────────────────────────────────
#  Animateur de compteur KPI
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

    value = pyqtProperty(float, fget=get_value, fset=set_value)


def animate_value(label, target, suffix="", duration=800):
    anim_obj = KpiAnimator(label, suffix)
    anim = QPropertyAnimation(anim_obj, b"value")
    anim.setDuration(duration)
    anim.setStartValue(0.0)
    anim.setEndValue(float(target))
    anim.setEasingCurve(QEasingCurve.Type.OutCubic)
    anim.start()
    label._anim_ref = anim
    label._anim_obj = anim_obj


# ─────────────────────────────────────────────────────────────
#  Composants UI réutilisables
# ─────────────────────────────────────────────────────────────

def section_label(text):
    lbl = QLabel(text)
    lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
    lbl.setStyleSheet(f"color: {COLORS['TXT_MUTED']}; background: transparent; letter-spacing: 1px;")
    return lbl


def divider():
    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)
    line.setFixedHeight(1)
    line.setStyleSheet(f"background: {COLORS['BORDER']}; border: none;")
    return line


# ─────────────────────────────────────────────────────────────
#  Dashboard principal
# ─────────────────────────────────────────────────────────────

class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()
        self.db = get_database()
        self.setStyleSheet(f"background: {COLORS['BG_PAGE']};")

        # Zone de défilement globale
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        self._main = QVBoxLayout(container)
        self._main.setSpacing(24)
        self._main.setContentsMargins(32, 28, 32, 28)

        self._build_header()
        self._build_kpi_row()
        self._build_middle_row()
        self._build_invoice_table()

        self._main.addStretch()

        scroll.setWidget(container)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(scroll)

        self.refresh()

    # ── En-tête ──────────────────────────────────────────────
    def _build_header(self):
        row = QHBoxLayout()
        row.setSpacing(16)

        # Colonne titre
        col = QVBoxLayout()
        col.setSpacing(3)

        title = QLabel(" 📊 Tableau de Bord")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['TXT_PRI']}; background: transparent;")
        col.addWidget(title)

        sub = QLabel("Vue d'ensemble de l'activité en temps réel")
        sub.setFont(QFont("Segoe UI", 11))
        sub.setStyleSheet(f"color: {COLORS['TXT_SEC']}; background: transparent;")
        col.addWidget(sub)

        row.addLayout(col)
        row.addStretch()



        self._main.addLayout(row)

    # ── Rangée KPI ───────────────────────────────────────────
    def _build_kpi_row(self):
        row = QHBoxLayout()
        row.setSpacing(16)

        kpis = [
            ("Ventes Totales",  "0",  "#6366F1", "💳", " DA"),
            ("Achats",          "0",  "#F59E0B", "🛒", " DA"),
            ("Bénéfice Net",    "0",  "#A855F7", "📈", " DA"),
            ("Clients",         "0",  "#06B6D4", "👥", ""),
        ]
        self._kpi_cards = []
        for title, val, color, icon, suffix in kpis:
            card = self._make_kpi_card(icon, title, val, color, suffix)
            row.addWidget(card)
            self._kpi_cards.append(card)

        self._main.addLayout(row)

    def _make_kpi_card(self, icon, title, value, color, suffix):
        card = QFrame()
        card.setObjectName("kpi")
        card.setStyleSheet(f"""
            QFrame#kpi {{
                background: {COLORS['BG_CARD']};
                border-radius: 16px;
                border: 1px solid {COLORS['BORDER']};
            }}
        """)
        card.setMinimumHeight(130)
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(8)

        # Ligne haut : icône coloré + titre
        top = QHBoxLayout()

        badge = QLabel(icon)
        badge.setFont(QFont("Segoe UI", 14))
        badge.setFixedSize(36, 36)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setStyleSheet(f"""
            background: {color}22;
            border-radius: 10px;
            border: none;
        """)
        top.addWidget(badge)

        top.addSpacing(8)

        lbl_title = QLabel(title)
        lbl_title.setFont(QFont("Segoe UI", 11))
        lbl_title.setStyleSheet(f"color: {COLORS['TXT_SEC']}; background: transparent; border: none;")
        top.addWidget(lbl_title)
        top.addStretch()

        layout.addLayout(top)

        # Valeur principale
        lbl_value = QLabel(value)
        lbl_value.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        lbl_value.setStyleSheet(f"color: {color}; background: transparent; border: none;")
        layout.addWidget(lbl_value)

        # Barre de couleur en bas
        bar = QFrame()
        bar.setFixedHeight(3)
        bar.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {color}, stop:1 transparent);
            border-radius: 2px;
            border: none;
        """)
        layout.addWidget(bar)

        card.value_label = lbl_value
        card._suffix = suffix
        return card

    # ── Rangée du milieu : activités + infos rapides ─────────
    def _build_middle_row(self):
        row = QHBoxLayout()
        row.setSpacing(16)

        # Activités récentes (2/3)
        act_card = QFrame()
        act_card.setObjectName("act")
        act_card.setStyleSheet(f"QFrame#act {{ background:{COLORS['BG_CARD']}; border-radius:16px; border:1px solid {COLORS['BORDER']}; }}")
        act_card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        act_layout = QVBoxLayout(act_card)
        act_layout.setContentsMargins(20, 18, 20, 18)
        act_layout.setSpacing(12)

        # En-tête de la carte
        act_hdr = QHBoxLayout()
        act_title = QLabel("Activités Récentes")
        act_title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        act_title.setStyleSheet(f"color: {COLORS['TXT_PRI']}; background:transparent; border:none;")
        act_hdr.addWidget(act_title)
        act_hdr.addStretch()
        act_layout.addLayout(act_hdr)
        act_layout.addWidget(divider())

        self._activities_layout = QVBoxLayout()
        self._activities_layout.setSpacing(6)
        act_layout.addLayout(self._activities_layout)
        act_layout.addStretch()

        row.addWidget(act_card, 3)

        # Panneau info rapide (1/3 — colonnes empilées)
        info_col = QVBoxLayout()
        info_col.setSpacing(16)

        infos = [
            ("Ventes Aujourd'hui", "0 DA",       "#6366F1", "📅"),
            ("Top Client",         "—",           "#A855F7", "🏆"),
            ("Stock Faible",       "0 produits",  "#F59E0B", "⚠️"),
        ]
        self._info_cards = []
        for title, val, color, icon in infos:
            c = self._make_info_card(icon, title, val, color)
            info_col.addWidget(c)
            self._info_cards.append(c)

        row.addLayout(info_col, 2)
        self._main.addLayout(row)

    def _make_info_card(self, icon, title, value, color):
        card = QFrame()
        card.setObjectName("info")
        card.setStyleSheet(f"QFrame#info {{ background:{COLORS['BG_CARD']}; border-radius:14px; border:1px solid {COLORS['BORDER']}; }}")
        card.setFixedHeight(90)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(14)

        # Badge icône
        badge = QLabel(icon)
        badge.setFont(QFont("Segoe UI", 16))
        badge.setFixedSize(40, 40)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setStyleSheet(f"""
            background: {color}22;
            border-radius: 12px;
            border: none;
        """)
        layout.addWidget(badge)

        # Textes
        txt = QVBoxLayout()
        txt.setSpacing(2)

        lbl_t = QLabel(title)
        lbl_t.setFont(QFont("Segoe UI", 9))
        lbl_t.setStyleSheet(f"color:{COLORS['TXT_SEC']}; background:transparent; border:none;")
        txt.addWidget(lbl_t)

        lbl_v = QLabel(value)
        lbl_v.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        lbl_v.setStyleSheet(f"color:{color}; background:transparent; border:none;")
        txt.addWidget(lbl_v)

        layout.addLayout(txt)
        layout.addStretch()

        card.value_label = lbl_v
        return card

    # ── Tableau des factures ─────────────────────────────────
    def _build_invoice_table(self):
        card = QFrame()
        card.setObjectName("inv")
        card.setStyleSheet(f"QFrame#inv {{ background:{COLORS['BG_CARD']}; border-radius:16px; border:1px solid {COLORS['BORDER']}; }}")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(14)

        # En-tête
        hdr = QHBoxLayout()
        t = QLabel("Dernières Factures")
        t.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        t.setStyleSheet(f"color:{COLORS['TXT_PRI']}; background:transparent; border:none;")
        hdr.addWidget(t)
        hdr.addStretch()
        nb = QLabel("10 dernières")
        nb.setFont(QFont("Segoe UI", 9))
        nb.setStyleSheet(f"color:{COLORS['TXT_MUTED']}; background:transparent; border:none;")
        hdr.addWidget(nb)
        layout.addLayout(hdr)
        layout.addWidget(divider())

        # Tableau
        self.invoice_table = QTableWidget(0, 6)
        self.invoice_table.setHorizontalHeaderLabels(
            ["Facture", "Client", "Total", "Date", "Paiement", ""])
        self.invoice_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.invoice_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        self.invoice_table.setColumnWidth(5, 90)
        self.invoice_table.verticalHeader().setVisible(False)
        self.invoice_table.setAlternatingRowColors(True)
        self.invoice_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.invoice_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.invoice_table.setShowGrid(False)
        self.invoice_table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.invoice_table.setMinimumHeight(280)
        self.invoice_table.setStyleSheet(f"""
            QTableWidget {{
                background: transparent;
                alternate-background-color: rgba(255,255,255,0.03);
                color: {COLORS['TXT_PRI']};
                border: none;
                font-size: 12px;
            }}
            QHeaderView::section {{
                background: {COLORS['BG_DEEP']};
                color: {COLORS['TXT_SEC']};
                font-size: 11px;
                font-weight: bold;
                padding: 10px 8px;
                border: none;
                border-bottom: 1px solid {COLORS['BORDER']};
                text-transform: uppercase;
            }}
            QTableWidget::item {{
                padding: 10px 8px;
                border-bottom: 1px solid rgba(255,255,255,0.04);
            }}
            QTableWidget::item:selected {{
                background: rgba(99,102,241,0.15);
                color: #A855F7;
            }}
        """)

        layout.addWidget(self.invoice_table)
        self._main.addWidget(card)

    # ── Chargement des données ────────────────────────────────
    def showEvent(self, event):
        """Rafraîchissement automatique à chaque affichage."""
        super().showEvent(event)
        self.refresh()

    def refresh(self):
        self._load_kpis()
        self._load_activities()
        self._load_quick_info()
        self._load_invoices()

    def _load_kpis(self):
        stats     = self.db.get_statistics() or {}
        sales     = float(stats.get("sales_total", 0))
        purchases = float(stats.get("purchases_total", 0))
        profit    = sales - purchases
        clients   = int(stats.get("total_clients", 0))

        values = [sales, purchases, profit, float(clients)]
        suffixes = [" DA", " DA", " DA", ""]

        for card, val, suf in zip(self._kpi_cards, values, suffixes):
            animate_value(card.value_label, val, suf)

    def _load_activities(self):
        # Nettoyer
        while self._activities_layout.count():
            item = self._activities_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        sales     = self.db.get_all_sales(limit=4)
        purchases = self.db.get_all_purchases(limit=3)
    

        if not sales and not purchases:
            empty = QLabel("Aucune activité récente")
            empty.setFont(QFont("Segoe UI", 11))
            empty.setStyleSheet(f"color:{COLORS['TXT_MUTED']}; padding: 12px; background:transparent;")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._activities_layout.addWidget(empty)
            return

        def add_row(dot_color, text):
            row_w = QWidget()
            row_w.setStyleSheet("background:transparent;")
            rl = QHBoxLayout(row_w)
            rl.setContentsMargins(0, 0, 0, 0)
            rl.setSpacing(10)

            dot = QLabel()
            dot.setFixedSize(8, 8)
            dot.setStyleSheet(f"""
                background: {dot_color};
                border-radius: 4px;
                border: none;
            """)
            rl.addWidget(dot)
            rl.setAlignment(dot, Qt.AlignmentFlag.AlignVCenter)

            lbl = QLabel(text)
            lbl.setFont(QFont("Segoe UI", 11))
            lbl.setStyleSheet(f"color: {COLORS['TXT_SEC']}; background:transparent; border:none;")
            rl.addWidget(lbl)
            rl.addStretch()

            self._activities_layout.addWidget(row_w)

        for s in sales:
            add_row("#6366F1", f"Vente  ·  Facture {s['invoice_number']}  —  {fmt_da(s['total'], 0)}")
        for p in purchases:
            # product_name est maintenant fourni par le JOIN products dans get_all_purchases()
            nom = p.get('product_name') or f"Produit #{p.get('product_id', '?')}"
            add_row("#F59E0B", f"Achat  ·  {nom}  —  {fmt_da(p['total'], 0)}")

    def _load_quick_info(self):
        stats      = self.db.get_statistics() or {}
        sales_today = float(stats.get("sales_today", 0))
        self._info_cards[0].value_label.setText(f"{fmt_da(sales_today, 0)}")

        top = self.db.get_top_clients(limit=1)
        self._info_cards[1].value_label.setText(top[0]["name"] if top else "—")

        low = self.db.get_low_stock_products() or []
        self._info_cards[2].value_label.setText(f"{len(low)} produit{'s' if len(low) != 1 else ''}")

    def _open_detail(self, sale_id):
        """Ouvre le dialogue de détail d'une facture."""
        if not _DETAIL_AVAILABLE:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Module manquant",
                "Le module sales_history.py est introuvable.")
            return
        sale = self.db.get_sale_by_id(sale_id)
        if not sale:
            return
        dlg = InvoiceDetailsDialog(sale, self)
        dlg.exec()

    def _load_invoices(self):
        data = self.db.get_all_sales(limit=10)
        self.invoice_table.setRowCount(len(data))

        for r, sale in enumerate(data):
            client = sale.get("client_name", sale.get("client", "—"))
            date   = str(sale.get("sale_date", "—")).split(" ")[0]
            pay    = sale.get("payment_method", sale.get("payment_mode", "—"))

            cells = [
                (f"{sale['invoice_number']}", "#F1F7F4"),
                (f"{client}",                "#F1F7F4"),
                (f"{fmt_da(sale['total'])}", "#10B981"),
                (f"{date}",                 "#F1F7F4"),
                (f"{pay}",                  "#F1F7F4"),
            ]

            for col, (val, color) in enumerate(cells):
                item = QTableWidgetItem(str(val))
                item.setForeground(QColor(color))
                item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                self.invoice_table.setItem(r, col, item)

            # ── Bouton Voir Détails ──────────────────────────
            btn = QPushButton("👁 Détails")
            btn.setFixedHeight(30)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background: rgba(99,102,241,0.18);
                    color: #A5B4FC;
                    border: 1px solid rgba(99,102,241,0.40);
                    border-radius: 7px;
                    font-size: 11px;
                    font-weight: bold;
                    padding: 0 8px;
                }
                QPushButton:hover {
                    background: rgba(99,102,241,0.38);
                    color: white;
                }
                QPushButton:pressed {
                    background: rgba(99,102,241,0.55);
                }
            """)
            sale_id = sale['id']
            btn.clicked.connect(lambda _, sid=sale_id: self._open_detail(sid))
            self.invoice_table.setCellWidget(r, 5, btn)

        for r in range(self.invoice_table.rowCount()):
            self.invoice_table.setRowHeight(r, 44)