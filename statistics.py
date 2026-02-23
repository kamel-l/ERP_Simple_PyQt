from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QTableWidget, QTableWidgetItem, QScrollArea, QPushButton, QHeaderView
)
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt, QObject, pyqtProperty, QPropertyAnimation
from datetime import datetime
from styles import COLORS, TABLE_STYLE
from db_manager import get_database, get_statistics, get_recent_sales


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


class StatisticsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.db = get_database()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(25)

        # -------------------------------------------------------- HEADER
        header = QHBoxLayout()
        title = QLabel("📈 Statistiques")
        title.setFont(QFont("Inter", 32, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['accent']};")
        header.addWidget(title)
        header.addStretch()

        refresh_btn = QPushButton("🔄 Actualiser")
        refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh_btn.setStyleSheet(f"""
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
        refresh_btn.clicked.connect(self.refresh)
        header.addWidget(refresh_btn)
        layout.addLayout(header)

        # -------------------------------------------------------- KPI CARDS
        kpi_row = QHBoxLayout()
        kpi_row.setSpacing(20)
        self.kpi_sales     = self.kpi_card("💰 Ventes Totales", "0 DA", COLORS["accent"])
        self.kpi_purchases = self.kpi_card("🛒 Achats Totaux",  "0 DA", COLORS["warning"])
        self.kpi_profit    = self.kpi_card("📈 Bénéfice Net",   "0 DA", COLORS["success"])
        kpi_row.addWidget(self.kpi_sales)
        kpi_row.addWidget(self.kpi_purchases)
        kpi_row.addWidget(self.kpi_profit)
        layout.addLayout(kpi_row)

        # -------------------------------------------------------- TABLE VENTES (même style Historique)
        table_title = QLabel("🧾 Liste des Ventes")
        table_title.setFont(QFont("Inter", 20, QFont.Weight.Bold))
        layout.addWidget(table_title)

        self.table = self._build_sales_table()
        layout.addWidget(self.table)

        scroll.setWidget(container)
        page_layout = QVBoxLayout(self)
        page_layout.addWidget(scroll)

        self.refresh()

    # ============================================================ KPI CARD
    def kpi_card(self, title, value, color):
        card = QFrame()
        card.setFixedHeight(140)
        card.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_card']};
                border-radius: 12px;
                border: 1px solid {COLORS['border']};
            }}
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(8)

        lbl_title = QLabel(title)
        lbl_title.setFont(QFont("Inter", 14))
        lbl_title.setStyleSheet(f"color: {COLORS['text_secondary']};")
        layout.addWidget(lbl_title)

        lbl_value = QLabel(value)
        lbl_value.setFont(QFont("Inter", 28, QFont.Weight.Bold))
        lbl_value.setStyleSheet(f"color: {color};")
        layout.addWidget(lbl_value)

        card.value_label = lbl_value
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
        table.setMinimumHeight(400)
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

    def _fill_row(self, row, sale):
        """Remplit une ligne exactement comme dans l'Historique des Ventes."""
        # N° Facture
        inv = QTableWidgetItem(sale.get("invoice_number", f"FAC-{sale['id']:05d}"))
        inv.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        inv.setData(Qt.ItemDataRole.UserRole, sale["id"])
        self.table.setItem(row, 0, inv)

        # Date
        raw_date = sale.get("sale_date") or sale.get("date", "")
        try:
            date_str = datetime.fromisoformat(raw_date).strftime("%d/%m/%Y %H:%M")
        except Exception:
            date_str = str(raw_date)
        self.table.setItem(row, 1, QTableWidgetItem(date_str))

        # Client
        client = sale.get("client_name") or sale.get("client", "Anonyme")
        self.table.setItem(row, 2, QTableWidgetItem(client))

        # Articles
        details = self.db.get_sale_by_id(sale["id"])
        nb = len(details["items"]) if details else 0
        art = QTableWidgetItem(f"{nb} article(s)")
        art.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(row, 3, art)

        # Sous-total
        total = sale.get("total", 0)
        subtotal = sale.get("subtotal", round(total / 1.19, 2))
        st = QTableWidgetItem(f"{subtotal:,.2f} DA")
        st.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.table.setItem(row, 4, st)

        # TVA
        tax = sale.get("tax_amount", round(total - subtotal, 2))
        tv = QTableWidgetItem(f"{tax:,.2f} DA")
        tv.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.table.setItem(row, 5, tv)

        # Total TTC
        tot = QTableWidgetItem(f"{total:,.2f} DA")
        tot.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        tot.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        tot.setForeground(QColor(COLORS["success"]))
        self.table.setItem(row, 6, tot)

    # ============================================================ REFRESH
    def refresh(self):
        stats = get_statistics() or {}
        total_sales     = stats.get("total_sales", 0)
        total_purchases = stats.get("total_purchases", 0)
        profit          = total_sales - total_purchases

        self.animate(self.kpi_sales.value_label,     total_sales,     " DA")
        self.animate(self.kpi_purchases.value_label, total_purchases, " DA")
        self.animate(self.kpi_profit.value_label,    profit,          " DA")

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

    def load_table(self):
        """Toutes les ventes — mêmes colonnes et style que l'Historique des Ventes."""
        try:
            data = get_recent_sales(50)   # 50 dernières ventes
            self.table.setRowCount(len(data))
            for r, sale in enumerate(data):
                self._fill_row(r, sale)
        except Exception as e:
            print(f"Erreur chargement table statistiques : {e}")
            self.table.setRowCount(0)