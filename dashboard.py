from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame,
    QPushButton, QScrollArea, QTableWidget, QTableWidgetItem, QListWidget
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QObject, pyqtProperty, QPropertyAnimation
from styles import COLORS
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
        formatted = f"{value:,.0f}{self.suffix}"
        self.label.setText(formatted)

    value = pyqtProperty(float, fget=getValue, fset=setValue)


# ============================================================
#                     DASHBOARD PAGE
# ============================================================
class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()
        self.db = get_database()

        # Scroll wrapper
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(25)

        # --------------------------------------------------------
        #                         HEADER
        # --------------------------------------------------------
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
            QPushButton:hover {{
                background: {COLORS['accent_light']};
            }}
        """)
        btn.clicked.connect(self.refresh)
        header.addWidget(btn)

        main_layout.addLayout(header)

        # --------------------------------------------------------
        #                     KPI STAT CARDS
        # --------------------------------------------------------
        kpi_row = QHBoxLayout()
        kpi_row.setSpacing(25)

        self.kpi_sales = self.create_kpi("💰", "Ventes Totales", "0 DA", COLORS["accent"])
        self.kpi_purchase = self.create_kpi("🛒", "Achats", "0 DA", COLORS["warning"])
        self.kpi_profit = self.create_kpi("📈", "Profit", "0 DA", COLORS["success"])
        self.kpi_clients = self.create_kpi("👥", "Clients", "0", COLORS["secondary"])

        kpi_row.addWidget(self.kpi_sales)
        kpi_row.addWidget(self.kpi_purchase)
        kpi_row.addWidget(self.kpi_profit)
        kpi_row.addWidget(self.kpi_clients)

        main_layout.addLayout(kpi_row)

        # --------------------------------------------------------
        #                  ACTIVITÉS RÉCENTES
        # --------------------------------------------------------
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

        # ✅ CORRIGÉ : Création des QListWidget manquants
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

        # --------------------------------------------------------
        #                   INFO QUICK METRICS
        # --------------------------------------------------------
        info_row = QHBoxLayout()
        info_row.setSpacing(20)

        self.info_today = self.info_card("📅", "Ventes Aujourd'hui", "0 DA", COLORS["info"])
        self.info_best = self.info_card("🏆", "Top Client", "-", COLORS["success"])
        self.info_stock = self.info_card("⚠️", "Stock Faible", "0 Produit", COLORS["danger"])

        info_row.addWidget(self.info_today)
        info_row.addWidget(self.info_best)
        info_row.addWidget(self.info_stock)

        main_layout.addLayout(info_row)

        # --------------------------------------------------------
        #                  DERNIÈRES FACTURES
        # --------------------------------------------------------
        title2 = QLabel("🧾 Dernières Factures")
        title2.setFont(QFont("Inter", 20, QFont.Weight.Bold))
        main_layout.addWidget(title2)

        self.table = self.create_invoice_table()
        main_layout.addWidget(self.table)

        # --------------------------------------------------------
        scroll.setWidget(container)
        layout = QVBoxLayout(self)
        layout.addWidget(scroll)

        self.refresh()

    # ============================================================
    #                      KPI CARD CREATOR
    # ============================================================
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

    # ============================================================
    #                     SMALL INFO CARDS
    # ============================================================
    def info_card(self, icon, title, value, color):
        card = QFrame()
        card.setFixedHeight(110)
        card.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_card']};
                border-radius: 8px;
                border-top: 4px solid {color};
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

    # ============================================================
    #                       INVOICE TABLE
    # ============================================================
    def create_invoice_table(self):
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["Facture", "Client", "Total", "Date", "Paiement"])
        table.verticalHeader().setVisible(False)
        table.setMinimumHeight(320)

        table.setStyleSheet(f"""
            QTableWidget {{
                background: {COLORS['bg_card']};
                alternate-background-color: {COLORS['bg_card_hover']};
                border-radius: 8px;
            }}
        """)

        return table

    # ============================================================
    #                       DATA LOADING
    # ============================================================
    def refresh(self):
        self.load_kpis()       # ✅ CORRIGÉ : méthode définie ci-dessous
        self.load_activities()
        self.load_info()       # ✅ CORRIGÉ : méthode définie ci-dessous
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

    # ✅ CORRIGÉ : méthode load_kpis() ajoutée
    def load_kpis(self):
        stats = get_statistics() or {}
        total_sales = stats.get("total_sales", 0)
        total_purchases = stats.get("total_purchases", 0)
        profit = total_sales - total_purchases

        self.animate(self.kpi_sales.value_label, total_sales, " DA")
        self.animate(self.kpi_purchase.value_label, total_purchases, " DA")
        self.animate(self.kpi_profit.value_label, profit, " DA")

        clients = self.db.get_all_clients()
        self.animate(self.kpi_clients.value_label, len(clients))

    def load_activities(self):
        recent_sales = get_recent_sales(5)
        recent_purchases = get_recent_purchases(3)

        self.last_sales.clear()
        for s in recent_sales:
            self.last_sales.addItem(
                f"#{s['id']} • {s['client_name']} • {s['total']} DA"
            )

        self.last_purchases.clear()
        for p in recent_purchases:
            self.last_purchases.addItem(
                f"#{p['id']} • {p['supplier']} • {p['total']} DA"
            )

    # ✅ CORRIGÉ : méthode load_info() ajoutée
    def load_info(self):
        stats = get_statistics() or {}
        sales_today = stats.get("sales_today", 0)
        self.info_today.value_label.setText(f"{sales_today:,.0f} DA")

        top_clients = get_top_clients(1)
        if top_clients:
            self.info_best.value_label.setText(top_clients[0]["name"])
        else:
            self.info_best.value_label.setText("-")

        low_stock = get_low_stock_products()
        self.info_stock.value_label.setText(f"{len(low_stock)} Produit(s)")

    def load_table(self):
        data = get_recent_sales(10)

        self.table.setRowCount(len(data))
        for r, item in enumerate(data):
            self.table.setItem(r, 0, QTableWidgetItem(str(item["id"])))
            self.table.setItem(r, 1, QTableWidgetItem(item["client_name"]))
            self.table.setItem(r, 2, QTableWidgetItem(str(item["total"])))
            self.table.setItem(r, 3, QTableWidgetItem(item["date"]))
            # ✅ CORRIGÉ : Colonne "Paiement" remplie (valeur par défaut)
            self.table.setItem(r, 4, QTableWidgetItem("—"))