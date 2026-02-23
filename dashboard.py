from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame,
    QPushButton, QScrollArea, QTableWidget, QTableWidgetItem,
    QListWidget, QHeaderView
)
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt, QObject, pyqtProperty, QPropertyAnimation
from datetime import datetime
from styles import COLORS, TABLE_STYLE
from db_manager import get_database
from db_manager import (
    get_statistics,
    get_recent_sales,
    get_recent_purchases,
    get_top_clients,
    get_low_stock_products,
)


# ============================================================
#                KPI VALUE ANIMATOR
# ============================================================
class KpiAnimator(QObject):
    def __init__(self, label):
        super().__init__()
        self._value = 0
        self.label = label
        self.suffix = ""

    def getValue(self):
        return self._value

    def setValue(self, value):
        self._value = value
        self.label.setText(f"{value:,.0f}{self.suffix}")

    value = pyqtProperty(float, fget=getValue, fset=setValue)


# ============================================================
#                     DASHBOARD PAGE
# ============================================================
class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()
        self.db = get_database()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(25)

        # -------------------------------------------------------- HEADER
        header = QHBoxLayout()
        title = QLabel("📊 Tableau de Bord")
        title.setFont(QFont("Inter", 32, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['accent']};")
        header.addWidget(title)

        subtitle = QLabel("Vue générale des opérations")
        subtitle.setFont(QFont("Inter", 15))
        subtitle.setStyleSheet(f"color: {COLORS['text_secondary']}; margin-left: 12px;")
        header.addWidget(subtitle)
        header.addStretch()

        btn = QPushButton("🔄 Actualiser")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['accent']};
                padding: 10px 24px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
                color: black;
            }}
            QPushButton:hover {{ background: {COLORS['accent_light']}; }}
        """)
        btn.clicked.connect(self.refresh)
        header.addWidget(btn)
        main_layout.addLayout(header)

        # -------------------------------------------------------- KPI CARDS
        kpi_row = QHBoxLayout()
        kpi_row.setSpacing(25)
        self.kpi_sales    = self.create_kpi("💰", "Ventes Totales", "0 DA", COLORS["accent"])
        self.kpi_purchase = self.create_kpi("🛒", "Achats",         "0 DA", COLORS["warning"])
        self.kpi_profit   = self.create_kpi("📈", "Profit",         "0 DA", COLORS["success"])
        self.kpi_clients  = self.create_kpi("👥", "Clients",        "0",    COLORS["purple"])
        kpi_row.addWidget(self.kpi_sales)
        kpi_row.addWidget(self.kpi_purchase)
        kpi_row.addWidget(self.kpi_profit)
        kpi_row.addWidget(self.kpi_clients)
        main_layout.addLayout(kpi_row)

        # -------------------------------------------------------- ACTIVITÉS RÉCENTES
        activities_card = QFrame()
        activities_card.setMinimumHeight(200)
        activities_card.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_card']};
                border-radius: 12px;
                border: 1px solid {COLORS['border']};
            }}
        """)
        activities_inner = QVBoxLayout(activities_card)
        activities_inner.setContentsMargins(15, 15, 15, 15)
        activities_inner.setSpacing(10)

        act_title = QLabel("📋 Activités Récentes")
        act_title.setFont(QFont("Inter", 18, QFont.Weight.Bold))
        activities_inner.addWidget(act_title)

        act_row = QHBoxLayout()

        sales_col = QVBoxLayout()
        sales_lbl = QLabel("🧾 Dernières Ventes")
        sales_lbl.setStyleSheet(f"color: {COLORS['text_secondary']};")
        self.last_sales = QListWidget()
        self.last_sales.setStyleSheet(f"background: {COLORS['bg_dark']}; border-radius: 6px;")
        sales_col.addWidget(sales_lbl)
        sales_col.addWidget(self.last_sales)

        purchases_col = QVBoxLayout()
        purchases_lbl = QLabel("🛒 Derniers Achats")
        purchases_lbl.setStyleSheet(f"color: {COLORS['text_secondary']};")
        self.last_purchases = QListWidget()
        self.last_purchases.setStyleSheet(f"background: {COLORS['bg_dark']}; border-radius: 6px;")
        purchases_col.addWidget(purchases_lbl)
        purchases_col.addWidget(self.last_purchases)

        act_row.addLayout(sales_col)
        act_row.addLayout(purchases_col)
        activities_inner.addLayout(act_row)
        main_layout.addWidget(activities_card)

        # -------------------------------------------------------- INFO CARDS
        info_row = QHBoxLayout()
        info_row.setSpacing(20)
        self.info_today = self.info_card("📅", "Ventes Aujourd'hui", "0 DA",      COLORS["info"])
        self.info_best  = self.info_card("🏆", "Top Client",         "-",         COLORS["success"])
        self.info_stock = self.info_card("⚠️",  "Stock Faible",       "0 Produit", COLORS["danger"])
        info_row.addWidget(self.info_today)
        info_row.addWidget(self.info_best)
        info_row.addWidget(self.info_stock)
        main_layout.addLayout(info_row)

        # -------------------------------------------------------- TABLE DERNIÈRES FACTURES
        title2 = QLabel("🧾 Dernières Factures")
        title2.setFont(QFont("Inter", 20, QFont.Weight.Bold))
        main_layout.addWidget(title2)

        self.table = self._build_sales_table()
        main_layout.addWidget(self.table)

        scroll.setWidget(container)
        layout = QVBoxLayout(self)
        layout.addWidget(scroll)

        self.refresh()

    # ============================================================ KPI CARD
    def create_kpi(self, icon, title, value, color):
        card = QFrame()
        card.setFixedHeight(160)
        card.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_card']};
                border: 1px solid {COLORS['border']};
                border-radius: 14px;
            }}
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(6)

        icon_l = QLabel(icon)
        icon_l.setFont(QFont("Inter", 32))
        layout.addWidget(icon_l)

        label_title = QLabel(title)
        label_title.setFont(QFont("Inter", 13))
        label_title.setStyleSheet(f"color: {COLORS['text_secondary']};")
        layout.addWidget(label_title)

        label_value = QLabel(value)
        label_value.setFont(QFont("Inter", 28, QFont.Weight.Bold))
        label_value.setStyleSheet(f"color: {color};")
        layout.addWidget(label_value)

        layout.addStretch()
        card.value_label = label_value
        return card

    # ============================================================ INFO CARD
    def info_card(self, icon, title, value, color):
        card = QFrame()
        card.setFixedHeight(110)
        card.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_card']};
                border-radius: 8px;
                
            }}
        """)
        layout = QVBoxLayout(card)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon_l = QLabel(icon)
        icon_l.setFont(QFont("Inter", 28))
        layout.addWidget(icon_l)

        label_t = QLabel(title)
        label_t.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 13px;")
        layout.addWidget(label_t)

        label_v = QLabel(value)
        label_v.setFont(QFont("Inter", 18, QFont.Weight.Bold))
        label_v.setStyleSheet(f"color: {color};")
        layout.addWidget(label_v)

        card.value_label = label_v
        return card

    # ============================================================ TABLE — même style que Historique
    def _build_sales_table(self):
        table = QTableWidget(0, 7)
        table.setHorizontalHeaderLabels([
            "N° Facture", "Date", "Client", "Articles",
            "Sous-total", "TVA", "Total TTC"
        ])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.verticalHeader().setVisible(False)
        table.setMinimumHeight(320)
        table.setStyleSheet(TABLE_STYLE + f"""
            QHeaderView::section {{
                background-color: {COLORS['bg_light']};
                color: {COLORS['text_primary']};
                font-size: 13px;
                font-weight: bold;
                padding: 10px 8px;
                border: none;
                border-right: 1px solid {COLORS['border']};
                border-bottom: 2px solid {COLORS['primary']};
            }}
            QHeaderView::section:last {{
                border-right: none;
            }}
        """)
        return table

    def _fill_row(self, table, row, sale):
        """Remplit une ligne exactement comme dans l'Historique des Ventes."""
        # N° Facture
        inv = QTableWidgetItem(sale.get("invoice_number", f"FAC-{sale['id']:05d}"))
        inv.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        inv.setData(Qt.ItemDataRole.UserRole, sale["id"])
        table.setItem(row, 0, inv)

        # Date
        raw_date = sale.get("sale_date") or sale.get("date", "")
        try:
            date_str = datetime.fromisoformat(raw_date).strftime("%d/%m/%Y %H:%M")
        except Exception:
            date_str = str(raw_date)
        table.setItem(row, 1, QTableWidgetItem(date_str))

        # Client
        client = sale.get("client_name") or sale.get("client", "Anonyme")
        table.setItem(row, 2, QTableWidgetItem(client))

        # Articles — on récupère le détail pour compter les lignes
        details = self.db.get_sale_by_id(sale["id"])
        nb = len(details["items"]) if details else 0
        art = QTableWidgetItem(f"{nb} article(s)")
        art.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        table.setItem(row, 3, art)

        # Sous-total
        total = sale.get("total", 0)
        subtotal = sale.get("subtotal", round(total / 1.19, 2))
        st = QTableWidgetItem(f"{subtotal:,.2f} DA")
        st.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        table.setItem(row, 4, st)

        # TVA
        tax = sale.get("tax_amount", round(total - subtotal, 2))
        tv = QTableWidgetItem(f"{tax:,.2f} DA")
        tv.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        table.setItem(row, 5, tv)

        # Total TTC
        tot = QTableWidgetItem(f"{total:,.2f} DA")
        tot.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        tot.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        tot.setForeground(QColor(COLORS["success"]))
        table.setItem(row, 6, tot)

    # ============================================================ REFRESH
    def refresh(self):
        self.load_kpis()
        self.load_activities()
        self.load_info()
        self.load_table()

    def animate(self, label, value, suffix=""):
        obj = KpiAnimator(label)
        obj.suffix = suffix
        anim = QPropertyAnimation(obj, b"value")
        anim.setDuration(700)
        anim.setStartValue(0)
        anim.setEndValue(float(value))
        anim.start()
        label.anim = anim

    def load_kpis(self):
        stats = get_statistics() or {}
        total_sales     = stats.get("total_sales", 0)
        total_purchases = stats.get("total_purchases", 0)
        self.animate(self.kpi_sales.value_label,    total_sales,                    " DA")
        self.animate(self.kpi_purchase.value_label, total_purchases,                " DA")
        self.animate(self.kpi_profit.value_label,   total_sales - total_purchases,  " DA")
        self.animate(self.kpi_clients.value_label,  len(self.db.get_all_clients()))

    def load_activities(self):
        self.last_sales.clear()
        for s in get_recent_sales(5):
            self.last_sales.addItem(f"#{s['id']} • {s['client_name']} • {s['total']} DA")

        self.last_purchases.clear()
        for p in get_recent_purchases(3):
            self.last_purchases.addItem(f"#{p['id']} • {p['supplier']} • {p['total']} DA")

    def load_info(self):
        stats = get_statistics() or {}
        self.info_today.value_label.setText(f"{stats.get('sales_today', 0):,.0f} DA")
        top = get_top_clients(1)
        self.info_best.value_label.setText(top[0]["name"] if top else "-")
        self.info_stock.value_label.setText(f"{len(get_low_stock_products())} Produit(s)")

    def load_table(self):
        """10 dernières ventes — même colonnes et style que l'Historique des Ventes."""
        data = get_recent_sales(10)
        self.table.setRowCount(len(data))
        for r, sale in enumerate(data):
            self._fill_row(self.table, r, sale)