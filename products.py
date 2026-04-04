from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog,
    QLineEdit, QFormLayout, QHBoxLayout, QFrame, QFileDialog, QMessageBox,
    QSpinBox, QDoubleSpinBox, QComboBox, QGraphicsDropShadowEffect
)
from currency import fmt_da, fmt, currency_manager
from auth import session
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt
from db_manager import get_database
import csv

# ── Nouveau thème Midnight Amber ──────────────────────────────────────────
C = {
    'bg':        '#0D0D0F',
    'bg_card':   '#1C1C23',
    'bg_input':  '#12121A',
    'bg_row':    '#141418',
    'amber':     '#F5A623',
    'amber_d':   '#C4841A',
    'amber_l':   '#FFD080',
    'teal':      '#4ECDC4',
    'coral':     '#FF6B6B',
    'yellow':    '#FFE66D',
    'txt':       '#F0EDE8',
    'txt_sec':   '#B0A99A',
    'txt_dim':   '#6B6460',
    'border':    '#2A2A35',
    'border_a':  'rgba(245,166,35,0.18)',
}

BTN = {
    'primary': f"""
        QPushButton {{
            background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                stop:0 {C['amber']}, stop:1 {C['amber_d']});
            color: #0D0D0F; border: none; border-radius: 6px;
            padding: 10px 20px; font-size: 13px; font-weight: bold;
            min-height: 36px;
        }}
        QPushButton:hover {{
            background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                stop:0 {C['amber_l']}, stop:1 {C['amber']});
        }}
        QPushButton:pressed {{ background: {C['amber_d']}; }}
        QPushButton:disabled {{ background: #2A2A35; color: #4A4450; }}
    """,
    'success': f"""
        QPushButton {{
            background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                stop:0 {C['teal']}, stop:1 #3AAA9F);
            color: #0D0D0F; border: none; border-radius: 6px;
            padding: 10px 20px; font-size: 13px; font-weight: bold;
            min-height: 36px;
        }}
        QPushButton:hover {{ background: #7EDBD5; }}
        QPushButton:pressed {{ background: #3AAA9F; }}
    """,
    'danger': f"""
        QPushButton {{
            background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                stop:0 {C['coral']}, stop:1 #CC4444);
            color: {C['txt']}; border: none; border-radius: 6px;
            padding: 10px 20px; font-size: 13px; font-weight: bold;
            min-height: 36px;
        }}
        QPushButton:hover {{ background: #FF9090; }}
        QPushButton:pressed {{ background: #CC4444; }}
    """,
    'secondary': f"""
        QPushButton {{
            background: transparent; color: {C['amber']};
            border: 1.5px solid rgba(245,166,35,0.4); border-radius: 6px;
            padding: 10px 20px; font-size: 13px; font-weight: bold;
            min-height: 36px;
        }}
        QPushButton:hover {{ background: rgba(245,166,35,0.10); border-color: {C['amber']}; }}
        QPushButton:pressed {{ background: rgba(245,166,35,0.20); }}
    """,
}

INPUT_STYLE = f"""
    QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit {{
        background-color: {C['bg_input']};
        border: 1.5px solid {C['border']};
        border-radius: 6px; padding: 8px 12px;
        color: {C['txt']}; font-size: 13px; min-height: 36px;
        selection-background-color: rgba(245,166,35,0.25);
    }}
    QLineEdit:focus, QComboBox:focus, QSpinBox:focus,
    QDoubleSpinBox:focus, QTextEdit:focus {{
        border: 1.5px solid {C['amber']}; background-color: {C['bg_card']};
    }}
    QLineEdit:hover, QComboBox:hover, QSpinBox:hover,
    QDoubleSpinBox:hover, QTextEdit:hover {{
        border: 1.5px solid rgba(245,166,35,0.40);
    }}
    QComboBox::drop-down {{ border:none; width:30px; }}
    QComboBox::down-arrow {{
        image:none;
        border-left:5px solid transparent; border-right:5px solid transparent;
        border-top:5px solid {C['amber']}; margin-right:10px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {C['bg_card']}; border:1px solid rgba(245,166,35,0.25);
        selection-background-color: rgba(245,166,35,0.18); color: {C['txt']};
    }}
    QSpinBox::up-button, QDoubleSpinBox::up-button,
    QSpinBox::down-button, QDoubleSpinBox::down-button {{
        background-color: {C['bg_card']}; border:none; width:20px;
    }}
    QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
    QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{
        background-color: {C['amber']};
    }}
"""

TABLE_STYLE = f"""
    QTableWidget {{
        background-color: {C['bg_card']};
        alternate-background-color: {C['bg_row']};
        border: 1px solid {C['border']}; border-radius: 8px;
        gridline-color: rgba(255,255,255,0.04);
        color: {C['txt']}; selection-background-color: rgba(245,166,35,0.18);
        font-size: 13px;
    }}
    QTableWidget::item {{ padding: 10px 8px; border: none; }}
    QTableWidget::item:selected {{
        background-color: rgba(245,166,35,0.22); color: {C['txt']};
    }}
    QTableWidget::item:hover {{ background-color: rgba(245,166,35,0.08); }}
    QHeaderView::section {{
        background: {C['bg']};
        color: {C['amber']}; padding: 10px 8px;
        border: none; border-bottom: 2px solid rgba(245,166,35,0.30);
        font-weight: bold; font-size: 11px; letter-spacing: 0.8px;
    }}
    QHeaderView::section:hover {{ background: {C['bg_card']}; color: {C['amber_l']}; }}
    QScrollBar:vertical {{ background:{C['bg']}; width:6px; border-radius:3px; }}
    QScrollBar::handle:vertical {{ background:rgba(245,166,35,0.35); border-radius:3px; }}
    QScrollBar::handle:vertical:hover {{ background:{C['amber']}; }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height:0; }}
"""


def _lbl(text, size=11, bold=False, color=None):
    l = QLabel(text)
    l.setFont(QFont("Segoe UI", size, QFont.Weight.Bold if bold else QFont.Weight.Normal))
    l.setStyleSheet(f"color:{color or C['txt']}; background:transparent; border:none;")
    return l


def _sep_h():
    f = QFrame()
    f.setFrameShape(QFrame.Shape.HLine)
    f.setStyleSheet(f"background:{C['border']}; border:none; max-height:1px;")
    return f


class ProductDialog(QDialog):
    """Dialogue ajouter / modifier produit — thème Midnight Amber"""

    def __init__(self, product_data=None):
        super().__init__()
        self.db = get_database()
        self.is_edit = product_data is not None
        self.product_id = product_data.get('id') if product_data else None

        self.setWindowTitle("✦ " + ("Modifier le Produit" if self.is_edit else "Nouveau Produit"))
        self.setMinimumWidth(560)
        self.setStyleSheet(f"""
            QDialog {{ background-color: {C['bg']}; }}
            QLabel  {{ color: {C['txt']}; font-size: 13px; }}
            {INPUT_STYLE}
        """)

        main = QVBoxLayout(self)
        main.setSpacing(18)
        main.setContentsMargins(28, 28, 28, 28)

        # ── En-tête dégradé ambre ──
        header = QFrame()
        header.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #1C1408, stop:0.5 #2A1E08, stop:1 #1C1408);
                border-radius: 10px;
                border: 1px solid rgba(245,166,35,0.25);
            }}
        """)
        hl = QVBoxLayout(header)
        hl.setContentsMargins(20, 16, 20, 16)

        top_row = QHBoxLayout()
        badge = QLabel("📦")
        badge.setFont(QFont("Segoe UI", 22))
        badge.setStyleSheet("background:transparent; border:none;")
        top_row.addWidget(badge)

        titles = QVBoxLayout()
        t = QLabel("Modifier le Produit" if self.is_edit else "Nouveau Produit")
        t.setFont(QFont("Segoe UI", 17, QFont.Weight.Bold))
        t.setStyleSheet(f"color:{C['amber']}; background:transparent; border:none;")
        titles.addWidget(t)
        s = QLabel("Remplissez tous les champs obligatoires")
        s.setFont(QFont("Segoe UI", 10))
        s.setStyleSheet(f"color:{C['txt_sec']}; background:transparent; border:none;")
        titles.addWidget(s)
        top_row.addLayout(titles)
        top_row.addStretch()
        hl.addLayout(top_row)
        main.addWidget(header)

        # ── Formulaire ──
        form_card = QFrame()
        form_card.setStyleSheet(f"""
            QFrame {{
                background: {C['bg_card']};
                border-radius: 10px;
                border: 1px solid {C['border']};
            }}
        """)
        fl = QFormLayout(form_card)
        fl.setContentsMargins(22, 20, 22, 20)
        fl.setSpacing(14)
        fl.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        def mk_lbl(text):
            l = QLabel(text)
            l.setStyleSheet(f"color:{C['txt_sec']}; border:none; font-size:12px;")
            return l

        self.name = QLineEdit()
        self.name.setPlaceholderText("Ex: Ordinateur Portable HP")
        self.name.setStyleSheet(INPUT_STYLE)
        self.name.setMinimumHeight(42)
        fl.addRow(mk_lbl("Nom du produit *"), self.name)

        self.category = QComboBox()
        self.category.setStyleSheet(INPUT_STYLE)
        self.category.setMinimumHeight(42)
        self.category.setEditable(True)
        self.load_categories()
        fl.addRow(mk_lbl("Catégorie"), self.category)

        self.price_buy = QDoubleSpinBox()
        self.price_buy.setRange(0, 9999999.99)
        self.price_buy.setDecimals(2)
        self.price_buy.setStyleSheet(INPUT_STYLE)
        self.price_buy.setMinimumHeight(42)
        self.price_buy.setSuffix(" DA")
        fl.addRow(mk_lbl("Prix d'achat"), self.price_buy)

        self.price = QDoubleSpinBox()
        self.price.setRange(0, 9999999.99)
        self.price.setDecimals(2)
        self.price.setStyleSheet(INPUT_STYLE)
        self.price.setMinimumHeight(42)
        self.price.setSuffix(" DA")
        fl.addRow(mk_lbl("Prix de vente *"), self.price)

        self.quantity = QSpinBox()
        self.quantity.setRange(0, 999999)
        self.quantity.setStyleSheet(INPUT_STYLE)
        self.quantity.setMinimumHeight(42)
        fl.addRow(mk_lbl("Quantité en stock *"), self.quantity)

        self.min_stock = QSpinBox()
        self.min_stock.setRange(0, 999999)
        self.min_stock.setValue(5)
        self.min_stock.setStyleSheet(INPUT_STYLE)
        self.min_stock.setMinimumHeight(42)
        fl.addRow(mk_lbl("Stock minimum"), self.min_stock)

        main.addWidget(form_card)

        note = _lbl("* Champs obligatoires", 10, color=C['txt_dim'])
        main.addWidget(note)

        # ── Boutons ──
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        cancel_btn = QPushButton("Annuler")
        cancel_btn.setStyleSheet(BTN['secondary'])
        cancel_btn.setMinimumHeight(44)
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        save_btn = QPushButton("✦  Enregistrer")
        save_btn.setStyleSheet(BTN['success'])
        save_btn.setMinimumHeight(44)
        save_btn.setFixedWidth(180)
        save_btn.clicked.connect(self.validate_and_accept)
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        btn_row.addWidget(cancel_btn)
        btn_row.addStretch()
        btn_row.addWidget(save_btn)
        main.addLayout(btn_row)

        if self.is_edit and product_data:
            self.load_product_data(product_data)

    def load_categories(self):
        self.category.clear()
        self.category.addItem("")
        for cat in get_database().get_all_categories():
            self.category.addItem(cat['name'])

    def load_product_data(self, product):
        self.name.setText(product.get("name", ""))
        self.category.setCurrentText(product.get("category_name", ""))
        self.quantity.setValue(product.get("stock_quantity", 0))
        self.price_buy.setValue(product.get("purchase_price", 0.0))
        self.price.setValue(product.get("selling_price", 0.0))
        self.min_stock.setValue(product.get("min_stock", 5))

    def validate_and_accept(self):
        if not self.name.text().strip():
            QMessageBox.warning(self, "Erreur", "Le nom du produit est obligatoire!")
            return
        if self.price.value() <= 0:
            QMessageBox.warning(self, "Erreur", "Le prix de vente doit être supérieur à 0!")
            return
        self.accept()


# ══════════════════════════════════════════════════════════════════════════
#  PAGE PRODUITS
# ══════════════════════════════════════════════════════════════════════════

class ProductsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.db = get_database()

        self.setStyleSheet(f"background-color:{C['bg']};")
        layout = QVBoxLayout(self)
        layout.setSpacing(18)
        layout.setContentsMargins(24, 22, 24, 22)

        # ── En-tête ──────────────────────────────────────────────────────
        hdr = QHBoxLayout()
        title_col = QVBoxLayout()
        title_col.setSpacing(3)

        title = QLabel("Gestion des Produits")
        title.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
        title.setStyleSheet(f"color:{C['txt']}; background:transparent;")
        title_col.addWidget(title)

        subtitle = QLabel("Gérez votre inventaire et vos produits")
        subtitle.setFont(QFont("Segoe UI", 12))
        subtitle.setStyleSheet(f"color:{C['txt_dim']}; background:transparent;")
        title_col.addWidget(subtitle)

        hdr.addLayout(title_col)
        hdr.addStretch()

        # Accent bar vertical couleur
        accent = QFrame()
        accent.setFixedSize(4, 52)
        accent.setStyleSheet(f"""
            background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                stop:0 {C['amber']}, stop:1 {C['teal']});
            border-radius: 2px;
        """)
        hdr.insertWidget(0, accent)
        layout.addLayout(hdr)

        # ── Cartes statistiques ───────────────────────────────────────────
        self.stats_layout = QHBoxLayout()
        self.stats_layout.setSpacing(12)
        layout.addLayout(self.stats_layout)
        self.update_statistics()
        self.stats_layout.addStretch()

        # ── Barre recherche + bouton ──────────────────────────────────────
        search_row = QHBoxLayout()
        search_row.setSpacing(12)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("  Rechercher un produit...")
        self.search_input.setStyleSheet(INPUT_STYLE)
        self.search_input.textChanged.connect(self.filter_products)
        self.search_input.setMinimumHeight(44)
        search_row.addWidget(self.search_input)

        self.add_btn = QPushButton("＋  Nouveau Produit")
        self.add_btn.setStyleSheet(BTN['primary'])
        self.add_btn.setFixedWidth(185)
        self.add_btn.setMinimumHeight(44)
        self.add_btn.clicked.connect(self.add_product)
        self.add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        search_row.addWidget(self.add_btn)
        layout.addLayout(search_row)

        # ── Tableau ───────────────────────────────────────────────────────
        tbl_card = QFrame()
        tbl_card.setStyleSheet(f"""
            QFrame {{
                background:{C['bg_card']};
                border-radius: 12px;
                border: 1px solid {C['border']};
            }}
        """)
        tbl_lay = QVBoxLayout(tbl_card)
        tbl_lay.setContentsMargins(0, 0, 0, 0)
        tbl_lay.setSpacing(0)

        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Nom", "Description", "Stock",
            "Prix Achat", "Prix Vente", "Valeur Stock"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setStyleSheet(TABLE_STYLE + f"""
            QHeaderView::section {{
                background-color: {C['bg']};
                color: {C['amber']};
                font-size: 11px; font-weight: bold;
                padding: 12px 8px;
                border: none;
                border-bottom: 2px solid rgba(245,166,35,0.30);
                letter-spacing: 0.8px;
            }}
            QHeaderView::section:first {{ border-top-left-radius: 12px; }}
            QHeaderView::section:last  {{ border-top-right-radius: 12px; }}
        """)
        tbl_lay.addWidget(self.table)
        layout.addWidget(tbl_card)

        # ── Boutons d'action ──────────────────────────────────────────────
        actions = QHBoxLayout()
        actions.setSpacing(10)

        self.edit_btn = QPushButton("✎  Modifier")
        self.edit_btn.setStyleSheet(BTN['secondary'])
        self.edit_btn.clicked.connect(self.edit_product)
        self.edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.edit_btn.setMinimumHeight(40)

        self.delete_btn = QPushButton("✕  Supprimer")
        self.delete_btn.setStyleSheet(BTN['danger'])
        self.delete_btn.clicked.connect(self.delete_product)
        self.delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete_btn.setMinimumHeight(40)

        self.import_btn = QPushButton("↓  Importer CSV")
        self.import_btn.setStyleSheet(BTN['primary'])
        self.import_btn.clicked.connect(self.import_csv)
        self.import_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.import_btn.setMinimumHeight(40)

        self.export_btn = QPushButton("↑  Exporter CSV")
        self.export_btn.setStyleSheet(BTN['primary'])
        self.export_btn.clicked.connect(self.export_csv)
        self.export_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.export_btn.setMinimumHeight(40)

        self.delete_all_btn = QPushButton("✕  Tout Supprimer")
        self.delete_all_btn.setStyleSheet(BTN['danger'])
        self.delete_all_btn.clicked.connect(self.delete_all_products)
        self.delete_all_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete_all_btn.setMinimumHeight(40)

        actions.addWidget(self.import_btn)
        actions.addWidget(self.export_btn)
        actions.addStretch()
        actions.addWidget(self.edit_btn)
        actions.addWidget(self.delete_btn)
        actions.addWidget(self.delete_all_btn)
        layout.addLayout(actions)

        self.load_products()
        self.showEvent = self.refresh_page()

    def build_stat_card(self, title, value, color):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {C['bg_card']};
                border-radius: 10px;
                border: 1px solid {C['border']};
                border-left: 3px solid {color};
            }}
        """)
        card.setFixedHeight(78)
        card.setMinimumWidth(185)
        cl = QVBoxLayout(card)
        cl.setSpacing(3)
        cl.setContentsMargins(14, 10, 14, 10)
        tl = QLabel(title)
        tl.setFont(QFont("Segoe UI", 10))
        tl.setStyleSheet(f"color:{C['txt_dim']}; border:none; background:transparent;")
        cl.addWidget(tl)
        vl = QLabel(str(value))
        vl.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        vl.setStyleSheet(f"color:{color}; border:none; background:transparent;")
        cl.addWidget(vl)
        return card

    def update_statistics(self):
        while self.stats_layout.count():
            child = self.stats_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        stats = self.db.get_statistics()
        low_stock = self.db.get_low_stock_products()
        self.stats_layout.addWidget(
            self.build_stat_card("Total Produits", stats['total_products'], C['amber']))
        self.stats_layout.addWidget(
            self.build_stat_card("Valeur Stock", f"{fmt_da(stats['stock_value'])}", C['teal']))
        self.stats_layout.addWidget(
            self.build_stat_card("Stock Faible", len(low_stock), C['coral']))

    def load_products(self):
        self.table.setRowCount(0)
        for product in self.db.get_all_products():
            self.add_product_to_table(product)

    def add_product_to_table(self, product):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setRowHeight(row, 46)

        id_item = QTableWidgetItem(str(product["id"]))
        id_item.setData(Qt.ItemDataRole.UserRole, product["id"])
        id_item.setForeground(QColor(C['txt_dim']))
        self.table.setItem(row, 0, id_item)

        name_item = QTableWidgetItem(product["name"])
        name_item.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.table.setItem(row, 1, name_item)

        cat_item = QTableWidgetItem(product.get("description", "—"))
        cat_item.setForeground(QColor(C['txt_sec']))
        self.table.setItem(row, 2, cat_item)

        qty = product["stock_quantity"]
        qty_item = QTableWidgetItem(str(qty))
        qty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        if qty <= product.get("min_stock", 0):
            qty_item.setForeground(QColor(C['coral']))
            qty_item.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        else:
            qty_item.setForeground(QColor(C['teal']))
        self.table.setItem(row, 3, qty_item)

        price_buy_item = QTableWidgetItem(fmt_da(product.get('purchase_price', 0)))
        price_buy_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        price_buy_item.setForeground(QColor(C['txt_sec']))
        self.table.setItem(row, 4, price_buy_item)

        price_item = QTableWidgetItem(fmt_da(product['selling_price']))
        price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        price_item.setForeground(QColor(C['amber']))
        self.table.setItem(row, 5, price_item)

        total_value = product["stock_quantity"] * product["selling_price"]
        value_item = QTableWidgetItem(fmt_da(total_value))
        value_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        value_item.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        value_item.setForeground(QColor(C['teal']))
        self.table.setItem(row, 6, value_item)

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_page()

    def refresh_page(self):
        self.search_input.clear()
        self.load_products()
        self.update_statistics()

    def add_product(self):
        if not session.can('add_product'):
            QMessageBox.warning(self, "Accès refusé", "Votre rôle ne permet pas d'ajouter des produits.")
            return
        dialog = ProductDialog()
        if dialog.exec():
            category_name = dialog.category.currentText().strip()
            category_id = None
            if category_name:
                categories = self.db.get_all_categories()
                category = next((c for c in categories if c['name'] == category_name), None)
                category_id = category['id'] if category else self.db.add_category(category_name)
            product_id = self.db.add_product(
                name=dialog.name.text().strip(),
                selling_price=dialog.price.value(),
                category_id=category_id,
                description="",
                purchase_price=dialog.price_buy.value(),
                stock_quantity=dialog.quantity.value(),
                min_stock=dialog.min_stock.value()
            )
            if product_id:
                QMessageBox.information(self, "Succès", "Produit ajouté avec succès!")
                self.load_products()
                self.update_statistics()
            else:
                QMessageBox.critical(self, "Erreur", "Impossible d'ajouter le produit!")

    def edit_product(self):
        if not session.can('edit_product'):
            QMessageBox.warning(self, "Accès refusé", "Votre rôle ne permet pas de modifier des produits.")
            return
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un produit!")
            return
        product_id = self.table.item(selected, 0).data(Qt.ItemDataRole.UserRole)
        product = self.db.get_product_by_id(product_id)
        if not product:
            QMessageBox.critical(self, "Erreur", "Produit introuvable!")
            return
        dialog = ProductDialog(product)
        if dialog.exec():
            category_name = dialog.category.currentText().strip()
            category_id = None
            if category_name:
                categories = self.db.get_all_categories()
                category = next((c for c in categories if c['name'] == category_name), None)
                category_id = category['id'] if category else self.db.add_category(category_name)
            if self.db.update_product(
                product_id=product_id,
                name=dialog.name.text().strip(),
                selling_price=dialog.price.value(),
                category_id=category_id,
                purchase_price=dialog.price_buy.value(),
                stock_quantity=dialog.quantity.value(),
                min_stock=dialog.min_stock.value()
            ):
                QMessageBox.information(self, "Succès", "Produit modifié avec succès!")
                self.load_products()
                self.update_statistics()
            else:
                QMessageBox.critical(self, "Erreur", "Impossible de modifier le produit!")

    def delete_product(self):
        if not session.can('delete_product'):
            QMessageBox.warning(self, "Accès refusé", "Seul un administrateur peut supprimer des produits.")
            return
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un produit!")
            return
        product_id = self.table.item(selected, 0).data(Qt.ItemDataRole.UserRole)
        product_name = self.table.item(selected, 1).text()
        reply = QMessageBox.question(self, "Confirmation",
            f"Voulez-vous vraiment supprimer '{product_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            if self.db.delete_product(product_id):
                QMessageBox.information(self, "Succès", "Produit supprimé!")
                self.load_products()
                self.update_statistics()
            else:
                QMessageBox.critical(self, "Erreur", "Impossible de supprimer!")

    def delete_all_products(self):
        count = self.table.rowCount()
        if count == 0:
            QMessageBox.information(self, "Info", "Aucun produit à supprimer.")
            return
        reply = QMessageBox.question(self, "⚠️ Confirmation",
            f"Vous êtes sur le point de supprimer TOUS les {count} produits.\nCette action est irréversible !\n\nVoulez-vous continuer ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes:
            return
        reply2 = QMessageBox.warning(self, "⚠️ Dernière confirmation",
            f"Êtes-vous ABSOLUMENT sûr de vouloir supprimer les {count} produits ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No)
        if reply2 != QMessageBox.StandardButton.Yes:
            return
        errors = 0
        for row in range(self.table.rowCount()):
            product_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
            if not self.db.delete_product(product_id):
                errors += 1
        self.load_products()
        self.update_statistics()
        if errors == 0:
            QMessageBox.information(self, "Succès", f"{count} produit(s) supprimé(s) avec succès!")
        else:
            QMessageBox.warning(self, "Attention", f"{count - errors} supprimé(s), {errors} échec(s).")

    def filter_products(self, text):
        if not text:
            self.load_products()
            return
        self.table.setRowCount(0)
        for product in self.db.search_products(text.strip(), starts_with=True):
            self.add_product_to_table(product)

    def import_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Sélectionner le fichier CSV", "", "Fichiers CSV (*.csv)")
        if not file_path:
            return
        try:
            imported = updated = 0
            errors = []
            with open(file_path, 'r', encoding='utf-8-sig') as file:
                for row_num, row in enumerate(csv.DictReader(file), start=2):
                    try:
                        name = row.get('name', '').strip()
                        if not name:
                            errors.append(f"Ligne {row_num}: Nom manquant")
                            continue
                        
                        # Prix de vente
                        try:
                            sp = row.get('selling_price', '0')
                            selling_price = float(str(sp).replace(' ', '').replace('DA', '').replace(',', '.') or 0)
                        except:
                            selling_price = 0.0
                        
                        # Prix d'achat
                        try:
                            pp = row.get('purchase_price', '0')
                            purchase_price = float(str(pp).replace(' ', '').replace('DA', '').replace(',', '.') or 0)
                        except:
                            purchase_price = 0.0
                        
                        # Stock quantity - CORRECTION ICI
                        try:
                            stock_val = row.get('stock_quantity', '0')
                            stock = int(float(str(stock_val).strip())) if str(stock_val).strip() else 0
                        except:
                            stock = 0
                        
                        # Stock minimum
                        try:
                            min_stock = int(row.get('min_stock', 0))
                        except:
                            min_stock = 0
                        
                        category_name = row.get('category', '').strip()
                        category_id = None
                        if category_name:
                            categories = self.db.get_all_categories()
                            cat = next((c for c in categories if c['name'] == category_name), None)
                            category_id = cat['id'] if cat else self.db.add_category(category_name)
                        
                        existing = [p for p in self.db.search_products(name)
                                    if p["name"].strip().lower() == name.lower()]
                        if existing:
                            self.db.update_product(existing[0]["id"], name, selling_price,
                                                category_id, purchase_price=purchase_price,
                                                stock_quantity=stock, min_stock=min_stock)
                            updated += 1
                        else:
                            self.db.add_product(name, selling_price, category_id, "",
                                            purchase_price, stock, min_stock)
                            imported += 1
                    except Exception as e:
                        errors.append(f"Ligne {row_num}: {str(e)}")
            
            self.load_products()
            self.update_statistics()
            
            msg = f"✅ Importés: {imported}\n🔄 Mis à jour: {updated}"
            if errors:
                msg += f"\n❌ Erreurs: {len(errors)}\n\n" + "\n".join(errors[:5])
            QMessageBox.information(self, "Import terminé", msg)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur d'import:\n{str(e)}")

    def export_csv(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Enregistrer le fichier CSV", "produits.csv", "Fichiers CSV (*.csv)")
        if not file_path:
            return
        try:
            products = self.db.get_all_products()
            with open(file_path, 'w', newline='', encoding='utf-8') as file:
                fieldnames = ['id', 'name', 'category', 'stock_quantity',
                              'purchase_price', 'selling_price', 'min_stock']
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                for product in products:
                    writer.writerow({
                        'id': product['id'], 'name': product['name'],
                        'category': product.get('category_name', ''),
                        'stock_quantity': product['stock_quantity'],
                        'purchase_price': product['purchase_price'],
                        'selling_price': product['selling_price'],
                        'min_stock': product.get('min_stock', 0)
                    })
            QMessageBox.information(self, "Succès", f"✅ {len(products)} produit(s) exporté(s)!")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur d'export:\n{str(e)}")