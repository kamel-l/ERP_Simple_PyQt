from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QComboBox, QScrollArea,
    QHeaderView, QMessageBox
)
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt, QObject, pyqtProperty, QPropertyAnimation
from datetime import datetime
from styles import COLORS, TABLE_STYLE
from db_manager import get_database


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
#                       SALES PAGE
# ============================================================
class SalesPage(QWidget):
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

        title = QLabel("💰 Ventes")
        title.setFont(QFont("Inter", 32, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['accent']};")
        header.addWidget(title)

        subtitle = QLabel("Gestion des ventes et factures")
        subtitle.setFont(QFont("Inter", 15))
        subtitle.setStyleSheet(f"color: {COLORS['text_secondary']}; margin-left: 12px;")
        header.addWidget(subtitle)

        header.addStretch()

        self.search = QLineEdit()
        self.search.setPlaceholderText("🔍 Rechercher une vente…")
        self.search.setFixedWidth(260)
        self.search.textChanged.connect(self.search_sale)
        header.addWidget(self.search)

        refresh_btn = QPushButton("🔄 Actualiser")
        refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['accent']};
                padding: 10px 22px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
                color: black;
            }}
            QPushButton:hover {{ background: {COLORS['accent_light']}; }}
        """)
        refresh_btn.clicked.connect(self.load_sales)
        header.addWidget(refresh_btn)

        layout.addLayout(header)

        # -------------------------------------------------------- KPI CARDS
        kpi_row = QHBoxLayout()
        kpi_row.setSpacing(20)

        self.kpi_total  = self._kpi_card("💰", "Total Ventes",   "0 DA", COLORS["accent"])
        self.kpi_count  = self._kpi_card("🧾", "Nb de Ventes",   "0",    COLORS["info"])
        self.kpi_avg    = self._kpi_card("📊", "Panier Moyen",   "0 DA", COLORS["success"])
        self.kpi_today  = self._kpi_card("📅", "Ventes Aujourd'hui", "0 DA", COLORS["warning"])

        kpi_row.addWidget(self.kpi_total)
        kpi_row.addWidget(self.kpi_count)
        kpi_row.addWidget(self.kpi_avg)
        kpi_row.addWidget(self.kpi_today)
        layout.addLayout(kpi_row)

        # -------------------------------------------------------- FORMULAIRE
        form_card = QFrame()
        form_card.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_card']};
                border-radius: 12px;
                border: 1px solid {COLORS['border']};
            }}
        """)
        form_layout = QVBoxLayout(form_card)
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(14)

        form_title = QLabel("➕ Ajouter / Modifier une Vente")
        form_title.setFont(QFont("Inter", 18, QFont.Weight.Bold))
        form_title.setStyleSheet(f"color: {COLORS['accent']};")
        form_layout.addWidget(form_title)

        # Ligne 1 : client + produit
        row1 = QHBoxLayout()
        row1.setSpacing(12)

        client_col = QVBoxLayout()
        client_lbl = QLabel("Client")
        client_lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        self.input_client = QComboBox()
        self.input_client.addItems([c["name"] for c in self.db.get_all_clients()])
        client_col.addWidget(client_lbl)
        client_col.addWidget(self.input_client)
        row1.addLayout(client_col)

        product_col = QVBoxLayout()
        product_lbl = QLabel("Produit")
        product_lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        self.input_product = QComboBox()
        self.input_product.addItems([p["product_name"] for p in self.db.get_all_products()])
        product_col.addWidget(product_lbl)
        product_col.addWidget(self.input_product)
        row1.addLayout(product_col)

        form_layout.addLayout(row1)

        # Ligne 2 : quantité + prix
        row2 = QHBoxLayout()
        row2.setSpacing(12)

        qty_col = QVBoxLayout()
        qty_lbl = QLabel("Quantité")
        qty_lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        self.input_qty = QLineEdit()
        self.input_qty.setPlaceholderText("Ex : 3")
        qty_col.addWidget(qty_lbl)
        qty_col.addWidget(self.input_qty)
        row2.addLayout(qty_col)

        price_col = QVBoxLayout()
        price_lbl = QLabel("Prix Total (DA)")
        price_lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        self.input_price = QLineEdit()
        self.input_price.setPlaceholderText("Ex : 15000")
        price_col.addWidget(price_lbl)
        price_col.addWidget(self.input_price)
        row2.addLayout(price_col)

        form_layout.addLayout(row2)

        # Boutons action
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        add_btn = QPushButton("➕ Ajouter")
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.clicked.connect(self.add_sale)
        btn_row.addWidget(add_btn)

        edit_btn = QPushButton("✏️ Modifier")
        edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        edit_btn.clicked.connect(self.update_sale)
        btn_row.addWidget(edit_btn)

        clear_btn = QPushButton("🔃 Vider")
        clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        clear_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['bg_card_hover']};
                color: {COLORS['text_secondary']};
                padding: 10px;
                border-radius: 6px;
                font-weight: bold;
                border: 1px solid {COLORS['border']};
            }}
            QPushButton:hover {{
                background: {COLORS['border']};
                color: {COLORS['text_primary']};
            }}
        """)
        clear_btn.clicked.connect(self.clear_form)
        btn_row.addWidget(clear_btn)

        btn_row.addStretch()

        del_btn = QPushButton("🗑 Supprimer")
        del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        del_btn.clicked.connect(self.delete_sale)
        del_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['danger']};
                color: white;
                padding: 10px 18px;
                border-radius: 6px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background: #ff6b6b; }}
        """)
        btn_row.addWidget(del_btn)

        form_layout.addLayout(btn_row)
        layout.addWidget(form_card)

        # -------------------------------------------------------- TABLE VENTES
        table_header = QHBoxLayout()
        table_lbl = QLabel("📋 Liste des Ventes")
        table_lbl.setFont(QFont("Inter", 20, QFont.Weight.Bold))
        table_header.addWidget(table_lbl)
        table_header.addStretch()
        layout.addLayout(table_header)

        self.table = self._build_table()
        self.table.cellClicked.connect(self.fill_form)
        layout.addWidget(self.table)

        scroll.setWidget(container)
        page_layout = QVBoxLayout(self)
        page_layout.addWidget(scroll)

        self.load_sales()

    # ============================================================ KPI CARD
    def _kpi_card(self, icon, title, value, color):
        card = QFrame()
        card.setFixedHeight(130)
        card.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_card']};
                border: 1px solid {COLORS['border']};
                border-radius: 14px;
            }}
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(4)

        top = QHBoxLayout()
        icon_l = QLabel(icon)
        icon_l.setFont(QFont("Inter", 26))
        top.addWidget(icon_l)
        top.addStretch()
        layout.addLayout(top)

        lbl_title = QLabel(title)
        lbl_title.setFont(QFont("Inter", 12))
        lbl_title.setStyleSheet(f"color: {COLORS['text_secondary']};")
        layout.addWidget(lbl_title)

        lbl_value = QLabel(value)
        lbl_value.setFont(QFont("Inter", 24, QFont.Weight.Bold))
        lbl_value.setStyleSheet(f"color: {color};")
        layout.addWidget(lbl_value)

        card.value_label = lbl_value
        return card

    # ============================================================ TABLE
    def _build_table(self):
        table = QTableWidget(0, 6)
        table.setHorizontalHeaderLabels([
            "ID", "Client", "Produit", "Quantité", "Total (DA)", "Date"
        ])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.verticalHeader().setVisible(False)
        table.setMinimumHeight(380)
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

    def _fill_row(self, row, s):
        """Remplit une ligne de la table."""
        id_item = QTableWidgetItem(str(s["id"]))
        id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(row, 0, id_item)

        self.table.setItem(row, 1, QTableWidgetItem(s.get("client", "")))
        self.table.setItem(row, 2, QTableWidgetItem(s.get("product", "")))

        qty_item = QTableWidgetItem(str(s.get("quantity", "")))
        qty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(row, 3, qty_item)

        total = s.get("total", 0)
        total_item = QTableWidgetItem(f"{total:,.0f} DA")
        total_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        total_item.setFont(QFont("Inter", 10, QFont.Weight.Bold))
        total_item.setForeground(QColor(COLORS["success"]))
        self.table.setItem(row, 4, total_item)

        # Date formatée
        raw_date = s.get("date", "")
        try:
            date_str = datetime.fromisoformat(str(raw_date)).strftime("%d/%m/%Y %H:%M")
        except Exception:
            date_str = str(raw_date)
        self.table.setItem(row, 5, QTableWidgetItem(date_str))

    # ============================================================ KPI ANIMATE
    def _animate(self, label, value, suffix=""):
        obj = KpiAnimator(label)
        obj.suffix = suffix
        anim = QPropertyAnimation(obj, b"value")
        anim.setDuration(700)
        anim.setStartValue(0)
        anim.setEndValue(float(value))
        anim.start()
        label.anim = anim

    def _update_kpis(self, data):
        total = sum(s.get("total", 0) for s in data)
        count = len(data)
        avg   = total / count if count else 0

        today = datetime.now().strftime("%Y-%m-%d")
        today_total = sum(
            s.get("total", 0) for s in data
            if str(s.get("date", "")).startswith(today)
        )

        self._animate(self.kpi_total.value_label,  total,       " DA")
        self._animate(self.kpi_count.value_label,  count)
        self._animate(self.kpi_avg.value_label,    avg,         " DA")
        self._animate(self.kpi_today.value_label,  today_total, " DA")

    # ============================================================ DATA
    def load_sales(self):
        data = self.db.get_all_sales()
        self.table.setRowCount(len(data))
        for r, s in enumerate(data):
            self._fill_row(r, s)
        self._update_kpis(data)

    def add_sale(self):
        client  = self.input_client.currentText()
        product = self.input_product.currentText()
        qty     = self.input_qty.text().strip()
        price   = self.input_price.text().strip()

        if not client or not product or not qty or not price:
            QMessageBox.warning(self, "Champs manquants", "Veuillez remplir tous les champs.")
            return

        self.db.add_sale(client, product, qty, price)
        self.clear_form()
        self.load_sales()

    def update_sale(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Aucune sélection", "Veuillez sélectionner une vente à modifier.")
            return
        sale_id = int(self.table.item(row, 0).text())
        self.db.update_sale(
            sale_id,
            self.input_client.currentText(),
            self.input_product.currentText(),
            self.input_qty.text(),
            self.input_price.text()
        )
        self.clear_form()
        self.load_sales()

    def delete_sale(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Aucune sélection", "Veuillez sélectionner une vente à supprimer.")
            return

        reply = QMessageBox.question(
            self, "Confirmer la suppression",
            "Voulez-vous vraiment supprimer cette vente ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            sale_id = int(self.table.item(row, 0).text())
            self.db.delete_sale(sale_id)
            self.clear_form()
            self.load_sales()

    def fill_form(self, row, col):
        """Remplit le formulaire en cliquant sur une ligne."""
        self.input_client.setCurrentText(self.table.item(row, 1).text())
        self.input_product.setCurrentText(self.table.item(row, 2).text())
        self.input_qty.setText(self.table.item(row, 3).text())
        # Nettoyer le montant (retirer " DA" et les virgules)
        raw_price = self.table.item(row, 4).text().replace(" DA", "").replace(",", "")
        self.input_price.setText(raw_price)

    def clear_form(self):
        """Réinitialise le formulaire."""
        self.input_qty.clear()
        self.input_price.clear()
        self.search.clear()
        self.table.clearSelection()

    def search_sale(self, text):
        data = self.db.search_sales(text)
        self.table.setRowCount(len(data))
        for r, s in enumerate(data):
            self._fill_row(r, s)
        self._update_kpis(data)

    def get_all_products(self):
        return self.db.get_all_products()