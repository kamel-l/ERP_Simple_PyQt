from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QTableWidget, QTableWidgetItem, QScrollArea, QPushButton
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QObject, pyqtProperty, QPropertyAnimation
from styles import COLORS
from db_manager import get_database, get_statistics, get_top_products


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

        # --------------------------------------------------------
        # HEADER
        # --------------------------------------------------------
        header = QHBoxLayout()
        title = QLabel("📊 Statistiques")
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
            QPushButton:hover {{
                background: {COLORS['accent_light']};
            }}
        """)
        refresh_btn.clicked.connect(self.refresh)
        header.addWidget(refresh_btn)

        layout.addLayout(header)

        # --------------------------------------------------------
        # KPI CARDS
        # --------------------------------------------------------
        kpi_row = QHBoxLayout()
        kpi_row.setSpacing(20)

        self.kpi_sales = self.kpi_card("💰 Ventes Totales", "0 DA", COLORS["accent"])
        self.kpi_purchases = self.kpi_card("🛒 Achats Totaux", "0 DA", COLORS["warning"])
        self.kpi_profit = self.kpi_card("📈 Bénéfice Net", "0 DA", COLORS["success"])

        kpi_row.addWidget(self.kpi_sales)
        kpi_row.addWidget(self.kpi_purchases)
        kpi_row.addWidget(self.kpi_profit)
        layout.addLayout(kpi_row)

        # --------------------------------------------------------
        # TABLE STATS
        # --------------------------------------------------------
        table_title = QLabel("📋 Ventes par Produit")
        table_title.setFont(QFont("Inter", 20, QFont.Weight.Bold))
        layout.addWidget(table_title)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Produit", "Quantité", "Total DA"])
        self.table.verticalHeader().setVisible(False)
        self.table.setMinimumHeight(350)
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background: {COLORS['bg_card']};
                border-radius: 8px;
                gridline-color: {COLORS['border']};
            }}
        """)
        layout.addWidget(self.table)

        scroll.setWidget(container)
        page_layout = QVBoxLayout(self)
        page_layout.addWidget(scroll)

        self.refresh()

    # ============================================================
    #                     KPI CARD CREATOR
    # ============================================================
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

    # ============================================================
    #                     DATA LOADING
    # ============================================================
    def refresh(self):
        # ✅ CORRIGÉ : get_statistics() au lieu de self.get_statistics()
        stats = get_statistics() or {}

        self.animate(self.kpi_sales.value_label, stats.get("total_sales", 0), " DA")
        self.animate(self.kpi_purchases.value_label, stats.get("total_purchases", 0), " DA")

        profit = stats.get("total_sales", 0) - stats.get("total_purchases", 0)
        self.animate(self.kpi_profit.value_label, profit, " DA")

        self.load_table()

    def animate(self, label, value, suffix=""):
        anim_obj = KpiAnimator(label)
        anim_obj.suffix = suffix
        animation = QPropertyAnimation(anim_obj, b"value")
        animation.setDuration(700)
        animation.setStartValue(0)
        animation.setEndValue(float(value))
        animation.start()
        label.anim = animation

    def load_table(self):
        try:
            data = get_top_products(10)
            self.table.setRowCount(len(data))
            for r, item in enumerate(data):
                self.table.setItem(r, 0, QTableWidgetItem(item.get("name", "")))
                self.table.setItem(r, 1, QTableWidgetItem(str(item.get("quantity", 0))))
                self.table.setItem(r, 2, QTableWidgetItem(str(item.get("total", 0))))
        except Exception as e:
            print(f"Erreur lors du chargement du tableau: {e}")
            self.table.setRowCount(0)