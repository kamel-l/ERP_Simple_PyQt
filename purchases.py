from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QComboBox, QHBoxLayout, QFrame,
    QMessageBox, QDialog, QLineEdit, QFormLayout, QInputDialog
)
from currency import fmt_da, fmt, currency_manager
from auth import session
from PyQt6.QtGui import QFont, QDoubleValidator, QIntValidator, QColor
from PyQt6.QtCore import Qt, pyqtSignal
from db_manager import get_database
from datetime import datetime

# ── Palette Midnight Amber ────────────────────────────────────────────────
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
}

BTN = {
    'primary': f"""
        QPushButton {{
            background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                stop:0 {C['amber']}, stop:1 {C['amber_d']});
            color: #0D0D0F; border: none; border-radius: 6px;
            padding: 10px 20px; font-size: 13px; font-weight: bold; min-height: 36px;
        }}
        QPushButton:hover {{ background: {C['amber_l']}; }}
        QPushButton:pressed {{ background: {C['amber_d']}; }}
        QPushButton:disabled {{ background: #2A2A35; color: #4A4450; }}
    """,
    'success': f"""
        QPushButton {{
            background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                stop:0 {C['teal']}, stop:1 #3AAA9F);
            color: #0D0D0F; border: none; border-radius: 6px;
            padding: 10px 20px; font-size: 13px; font-weight: bold; min-height: 36px;
        }}
        QPushButton:hover {{ background: #7EDBD5; }}
        QPushButton:pressed {{ background: #3AAA9F; }}
    """,
    'danger': f"""
        QPushButton {{
            background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                stop:0 {C['coral']}, stop:1 #CC4444);
            color: {C['txt']}; border: none; border-radius: 6px;
            padding: 10px 20px; font-size: 13px; font-weight: bold; min-height: 36px;
        }}
        QPushButton:hover {{ background: #FF9090; }}
        QPushButton:pressed {{ background: #CC4444; }}
    """,
    'secondary': f"""
        QPushButton {{
            background: transparent; color: {C['amber']};
            border: 1.5px solid rgba(245,166,35,0.4); border-radius: 6px;
            padding: 10px 20px; font-size: 13px; font-weight: bold; min-height: 36px;
        }}
        QPushButton:hover {{ background: rgba(245,166,35,0.10); border-color:{C['amber']}; }}
        QPushButton:pressed {{ background: rgba(245,166,35,0.20); }}
    """,
}

INPUT_STYLE = f"""
    QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit {{
        background-color: {C['bg_input']}; border: 1.5px solid {C['border']};
        border-radius: 6px; padding: 8px 12px;
        color: {C['txt']}; font-size: 13px; min-height: 36px;
    }}
    QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
        border: 1.5px solid {C['amber']}; background-color: {C['bg_card']};
    }}
    QLineEdit:hover, QComboBox:hover {{ border: 1.5px solid rgba(245,166,35,0.40); }}
    QComboBox::drop-down {{ border:none; width:30px; }}
    QComboBox::down-arrow {{
        image:none; border-left:5px solid transparent; border-right:5px solid transparent;
        border-top:5px solid {C['amber']}; margin-right:10px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {C['bg_card']}; border:1px solid rgba(245,166,35,0.25);
        selection-background-color: rgba(245,166,35,0.18); color: {C['txt']};
    }}
"""

TABLE_STYLE = f"""
    QTableWidget {{
        background-color: {C['bg_card']}; alternate-background-color: {C['bg_row']};
        border: 1px solid {C['border']}; border-radius: 8px;
        gridline-color: rgba(255,255,255,0.04); color: {C['txt']};
        selection-background-color: rgba(245,166,35,0.18); font-size: 13px;
    }}
    QTableWidget::item {{ padding: 10px 8px; border:none; }}
    QTableWidget::item:selected {{ background-color:rgba(245,166,35,0.22); color:{C['txt']}; }}
    QTableWidget::item:hover {{ background-color:rgba(245,166,35,0.08); }}
    QHeaderView::section {{
        background: {C['bg']}; color: {C['amber']};
        padding: 10px 8px; border:none;
        border-bottom: 2px solid rgba(245,166,35,0.30);
        font-weight:bold; font-size:11px; letter-spacing:0.8px;
    }}
    QScrollBar:vertical {{ background:{C['bg']}; width:6px; border-radius:3px; }}
    QScrollBar::handle:vertical {{ background:rgba(245,166,35,0.35); border-radius:3px; }}
    QScrollBar::handle:vertical:hover {{ background:{C['amber']}; }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height:0; }}
"""


def clean_num(value):
    try:
        text = value.text() if hasattr(value, 'text') else str(value)
        text = text.replace(f" {currency_manager.primary.symbol}", "").replace(",", "").strip()
        return float(text) if text else 0.0
    except:
        return 0.0


class NewProductDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nouveau Produit")
        self.setMinimumWidth(500)
        self.setStyleSheet(f"QDialog {{ background-color: {C['bg']}; }} QLabel {{ color: {C['txt']}; }} {INPUT_STYLE}")
        main = QVBoxLayout(self)
        main.setSpacing(16)
        main.setContentsMargins(24, 24, 24, 24)

        header = QFrame()
        header.setStyleSheet(f"""
            QFrame {{ background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 #1C1408, stop:1 #121812);
                border-radius: 10px; border: 1px solid rgba(245,166,35,0.20); }}
        """)
        hl = QHBoxLayout(header)
        hl.setContentsMargins(16, 14, 16, 14)
        hl.setSpacing(12)
        ic = QLabel("📦")
        ic.setFont(QFont("Segoe UI", 20))
        ic.setStyleSheet("background:transparent; border:none;")
        hl.addWidget(ic)
        titles = QVBoxLayout()
        t = QLabel("Créer un Nouveau Produit")
        t.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        t.setStyleSheet(f"color:{C['amber']}; background:transparent; border:none;")
        titles.addWidget(t)
        s = QLabel("Remplissez les informations du produit")
        s.setFont(QFont("Segoe UI", 10))
        s.setStyleSheet(f"color:{C['txt_sec']}; background:transparent; border:none;")
        titles.addWidget(s)
        hl.addLayout(titles)
        main.addWidget(header)

        form_card = QFrame()
        form_card.setStyleSheet(f"QFrame {{ background:{C['bg_card']}; border-radius:10px; border:1px solid {C['border']}; }}")
        fl = QFormLayout(form_card)
        fl.setContentsMargins(20, 16, 20, 16)
        fl.setSpacing(12)

        def mk_lbl(t):
            l = QLabel(t)
            l.setStyleSheet(f"color:{C['txt_sec']}; border:none; font-size:12px;")
            return l

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Ex: Pantalon Jean")
        self.name_edit.setMinimumHeight(40)
        fl.addRow(mk_lbl("Nom *"), self.name_edit)

        self.purchase_price_edit = QLineEdit()
        self.purchase_price_edit.setPlaceholderText("Ex: 1500")
        self.purchase_price_edit.setMinimumHeight(40)
        self.purchase_price_edit.setValidator(QDoubleValidator(0.01, 9999999.99, 2))
        fl.addRow(mk_lbl("Prix d'achat *"), self.purchase_price_edit)

        self.selling_price_edit = QLineEdit()
        self.selling_price_edit.setPlaceholderText("Ex: 2500")
        self.selling_price_edit.setMinimumHeight(40)
        self.selling_price_edit.setValidator(QDoubleValidator(0.01, 9999999.99, 2))
        fl.addRow(mk_lbl("Prix de vente *"), self.selling_price_edit)

        self.stock_edit = QLineEdit()
        self.stock_edit.setPlaceholderText("Ex: 10")
        self.stock_edit.setText("0")
        self.stock_edit.setMinimumHeight(40)
        self.stock_edit.setValidator(QIntValidator(0, 999999))
        fl.addRow(mk_lbl("Stock initial"), self.stock_edit)
        main.addWidget(form_card)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        cancel_btn = QPushButton("Annuler")
        cancel_btn.setStyleSheet(BTN['secondary'])
        cancel_btn.setMinimumHeight(44)
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn = QPushButton("✦  Créer")
        save_btn.setStyleSheet(BTN['success'])
        save_btn.setMinimumHeight(44)
        save_btn.setFixedWidth(150)
        save_btn.clicked.connect(self.validate_and_accept)
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_row.addWidget(cancel_btn)
        btn_row.addStretch()
        btn_row.addWidget(save_btn)
        main.addLayout(btn_row)

    def validate_and_accept(self):
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Erreur", "Le nom est obligatoire!")
            return
        for field, label in [(self.purchase_price_edit, "prix d'achat"),
                              (self.selling_price_edit, "prix de vente")]:
            try:
                float(field.text())
            except:
                QMessageBox.warning(self, "Erreur", f"Le {label} est invalide!")
                return
        self.accept()


class ProductEditDialog(QDialog):
    def __init__(self, product, parent=None):
        super().__init__(parent)
        self.product = product
        self.quantity = 1
        self.setWindowTitle("Détails du Produit")
        self.setMinimumWidth(480)
        self.setStyleSheet(f"QDialog {{ background-color:{C['bg']}; }} QLabel {{ color:{C['txt']}; }} {INPUT_STYLE}")

        main = QVBoxLayout(self)
        main.setSpacing(16)
        main.setContentsMargins(24, 24, 24, 24)

        header = QFrame()
        header.setStyleSheet(f"""
            QFrame {{ background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 #1C1408, stop:1 #121812);
                border-radius: 10px; border: 1px solid rgba(245,166,35,0.20); }}
        """)
        hl = QHBoxLayout(header)
        hl.setContentsMargins(16, 14, 16, 14)
        t = QLabel(f"✎  {product['name']}")
        t.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        t.setStyleSheet(f"color:{C['amber']}; background:transparent; border:none;")
        hl.addWidget(t)
        main.addWidget(header)

        form_card = QFrame()
        form_card.setStyleSheet(f"QFrame {{ background:{C['bg_card']}; border-radius:10px; border:1px solid {C['border']}; }}")
        fl = QFormLayout(form_card)
        fl.setContentsMargins(20, 16, 20, 16)
        fl.setSpacing(12)

        def mk_lbl(t):
            l = QLabel(t)
            l.setStyleSheet(f"color:{C['txt_sec']}; border:none; font-size:12px;")
            return l

        self.name_edit = QLineEdit(product['name'])
        self.name_edit.setMinimumHeight(40)
        fl.addRow(mk_lbl("Nom du produit"), self.name_edit)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background:rgba(255,255,255,0.06); border:none;")
        fl.addRow(sep)

        self.purchase_price_edit = QLineEdit(str(product.get('purchase_price', 0)))
        self.purchase_price_edit.setMinimumHeight(40)
        self.purchase_price_edit.setValidator(QDoubleValidator(0.0, 9999999.99, 2))
        fl.addRow(mk_lbl("Prix d'achat (DA)"), self.purchase_price_edit)

        self.selling_price_edit = QLineEdit(str(product.get('selling_price', 0)))
        self.selling_price_edit.setMinimumHeight(40)
        self.selling_price_edit.setValidator(QDoubleValidator(0.0, 9999999.99, 2))
        fl.addRow(mk_lbl("Prix de vente (DA)"), self.selling_price_edit)

        stock_lbl = QLabel(f"  {product.get('stock_quantity', 0)} unités")
        stock_lbl.setMinimumHeight(40)
        stock_lbl.setStyleSheet(f"""
            color:{C['teal']}; font-weight:bold;
            background:rgba(78,205,196,0.08); border-radius:6px; padding:0 8px;
        """)
        fl.addRow(mk_lbl("Stock actuel"), stock_lbl)

        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setFixedHeight(1)
        sep2.setStyleSheet(f"background:rgba(255,255,255,0.06); border:none;")
        fl.addRow(sep2)

        self.qty_edit = QLineEdit("1")
        self.qty_edit.setMinimumHeight(40)
        self.qty_edit.setValidator(QIntValidator(1, 999999))
        self.qty_edit.setPlaceholderText("Ex: 10")
        self.qty_edit.setStyleSheet(INPUT_STYLE + f"""
            QLineEdit {{ font-size:16px; font-weight:bold; color:{C['amber']}; }}
        """)
        fl.addRow(mk_lbl("Quantité à acheter *"), self.qty_edit)
        main.addWidget(form_card)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        cancel_btn = QPushButton("Annuler")
        cancel_btn.setStyleSheet(BTN['secondary'])
        cancel_btn.setMinimumHeight(44)
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        confirm_btn = QPushButton("✓  Confirmer")
        confirm_btn.setStyleSheet(BTN['success'])
        confirm_btn.setMinimumHeight(44)
        confirm_btn.setFixedWidth(160)
        confirm_btn.clicked.connect(self.validate_and_accept)
        confirm_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_row.addWidget(cancel_btn)
        btn_row.addStretch()
        btn_row.addWidget(confirm_btn)
        main.addLayout(btn_row)

    def validate_and_accept(self):
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Erreur", "Le nom est obligatoire!")
            return
        for field, label in [(self.purchase_price_edit, "prix d'achat"),
                              (self.selling_price_edit, "prix de vente")]:
            try:
                float(field.text())
            except ValueError:
                QMessageBox.warning(self, "Erreur", f"Le {label} est invalide!")
                return
        qty_text = self.qty_edit.text().strip()
        if not qty_text:
            QMessageBox.warning(self, "Erreur", "Veuillez saisir une quantité!")
            self.qty_edit.setText("1")
            return
        try:
            qty = int(qty_text)
            if qty < 1:
                raise ValueError()
        except ValueError:
            QMessageBox.warning(self, "Erreur", "La quantité doit être un entier ≥ 1!")
            return
        self.quantity = qty
        self.accept()


class ProductSelectorDialog(QDialog):
    def __init__(self, products):
        super().__init__()
        self.selected_product = None
        self.products = products
        self.db = get_database()

        self.setWindowTitle("Sélectionner un Produit")
        self.setMinimumWidth(700)
        self.setMinimumHeight(500)
        self.setStyleSheet(f"QDialog {{ background-color:{C['bg']}; }}")

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header row
        header_row = QHBoxLayout()
        title = QLabel("Sélectionnez un produit")
        title.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        title.setStyleSheet(f"color:{C['amber']}; background:transparent;")
        header_row.addWidget(title)
        header_row.addStretch()
        new_btn = QPushButton("＋  Nouveau Produit")
        new_btn.setStyleSheet(BTN['primary'])
        new_btn.setMinimumHeight(38)
        new_btn.setFixedWidth(175)
        new_btn.clicked.connect(self.create_new_product)
        new_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        header_row.addWidget(new_btn)
        layout.addLayout(header_row)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher un produit...")
        self.search_input.setStyleSheet(INPUT_STYLE)
        self.search_input.textChanged.connect(self.filter_products)
        layout.addWidget(self.search_input)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Nom", "Catégorie", "Prix Achat", "Stock"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.doubleClicked.connect(self.select_product)
        self.table.setShowGrid(False)
        self.table.setStyleSheet(TABLE_STYLE)
        layout.addWidget(self.table)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        select_btn = QPushButton("✓  Sélectionner")
        select_btn.setStyleSheet(BTN['success'])
        select_btn.setMinimumHeight(42)
        select_btn.clicked.connect(self.select_product)
        select_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn = QPushButton("Annuler")
        cancel_btn.setStyleSheet(BTN['secondary'])
        cancel_btn.setMinimumHeight(42)
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_row.addStretch()
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(select_btn)
        layout.addLayout(btn_row)

        self.load_products(products)

    def load_products(self, products):
        self.table.setRowCount(0)
        for p in products:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setRowHeight(row, 44)
            name_item = QTableWidgetItem(p['name'])
            name_item.setData(Qt.ItemDataRole.UserRole, p)
            name_item.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            self.table.setItem(row, 0, name_item)
            cat_item = QTableWidgetItem(p.get('category_name', '—'))
            cat_item.setForeground(QColor(C['txt_sec']))
            self.table.setItem(row, 1, cat_item)
            price_item = QTableWidgetItem(fmt_da(p['purchase_price']))
            price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            price_item.setForeground(QColor(C['amber']))
            self.table.setItem(row, 2, price_item)
            stock_item = QTableWidgetItem(str(p['stock_quantity']))
            stock_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            stock_item.setForeground(QColor(C['teal']))
            self.table.setItem(row, 3, stock_item)

    def filter_products(self, text):
        t = text.lower().strip()
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item:
                show = item.text().lower().startswith(t) if t else True
                self.table.setRowHidden(row, not show)

    def select_product(self):
        selected = self.table.currentRow()
        if selected >= 0:
            item = self.table.item(selected, 0)
            if item:
                product = item.data(Qt.ItemDataRole.UserRole)
                edit_dialog = ProductEditDialog(product, parent=self)
                if edit_dialog.exec():
                    self.db.update_product(
                        product['id'],
                        name=edit_dialog.name_edit.text().strip(),
                        selling_price=float(edit_dialog.selling_price_edit.text()),
                        purchase_price=float(edit_dialog.purchase_price_edit.text()),
                        category_id=product.get('category_id'),
                        description=product.get('description', ''),
                        stock_quantity=product.get('stock_quantity', 0),
                        min_stock=product.get('min_stock', 0),
                        barcode=product.get('barcode', ''),
                    )
                    updated = self.db.get_product_by_id(product['id'])
                    self.selected_product = updated if updated else product
                    self.selected_product['_qty'] = edit_dialog.quantity
                    self.accept()

    def create_new_product(self):
        dialog = NewProductDialog()
        if dialog.exec():
            try:
                name = dialog.name_edit.text().strip()
                purchase_price = float(dialog.purchase_price_edit.text())
                selling_price = float(dialog.selling_price_edit.text())
                stock = int(dialog.stock_edit.text())
                product_id = self.db.add_product(
                    name=name, selling_price=selling_price,
                    purchase_price=purchase_price, stock_quantity=stock,
                    category_id=None, min_stock=5)
                if product_id:
                    product = self.db.get_product_by_id(product_id)
                    if product:
                        product['_qty'] = stock
                        self.selected_product = product
                        self.accept()
                        QMessageBox.information(self, "Succès", f"Produit '{name}' créé!")
                        self.accept()
            except Exception as e:
                QMessageBox.critical(self, "Erreur", str(e))


class SupplierDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nouveau Fournisseur")
        self.setMinimumWidth(480)
        self.setStyleSheet(f"QDialog {{ background-color:{C['bg']}; }} {INPUT_STYLE}")

        main = QVBoxLayout(self)
        main.setSpacing(16)
        main.setContentsMargins(24, 24, 24, 24)

        header = QFrame()
        header.setStyleSheet(f"""
            QFrame {{ background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 #1C1408, stop:1 #121812);
                border-radius: 10px; border: 1px solid rgba(245,166,35,0.20); }}
        """)
        hl = QHBoxLayout(header)
        hl.setContentsMargins(16, 14, 16, 14)
        t = QLabel("🏢  Nouveau Fournisseur")
        t.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        t.setStyleSheet(f"color:{C['amber']}; background:transparent; border:none;")
        hl.addWidget(t)
        main.addWidget(header)

        form_card = QFrame()
        form_card.setStyleSheet(f"QFrame {{ background:{C['bg_card']}; border-radius:10px; border:1px solid {C['border']}; }}")
        fl = QFormLayout(form_card)
        fl.setContentsMargins(20, 16, 20, 16)
        fl.setSpacing(12)

        def mk_lbl(t):
            l = QLabel(t)
            l.setStyleSheet(f"color:{C['txt_sec']}; border:none; font-size:12px;")
            return l

        fields = [
            ("Nom *", "name_edit", "Nom du fournisseur"),
            ("Téléphone", "phone_edit", "Téléphone"),
            ("Email", "email_edit", "Email"),
            ("Adresse", "address_edit", "Adresse"),
            ("NIF", "nif_edit", "Numéro fiscal"),
        ]
        for label, attr, placeholder in fields:
            field = QLineEdit()
            field.setPlaceholderText(placeholder)
            field.setMinimumHeight(40)
            setattr(self, attr, field)
            fl.addRow(mk_lbl(label), field)
        main.addWidget(form_card)

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
        save_btn.setFixedWidth(175)
        save_btn.clicked.connect(self.validate_and_accept)
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_row.addWidget(cancel_btn)
        btn_row.addStretch()
        btn_row.addWidget(save_btn)
        main.addLayout(btn_row)

    def validate_and_accept(self):
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Erreur", "Le nom du fournisseur est obligatoire!")
            return
        self.accept()


class PurchasesPage(QWidget):
    purchase_saved = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.db = get_database()

        self.setStyleSheet(f"background-color:{C['bg']};")
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(14)
        main_layout.setContentsMargins(22, 20, 22, 20)

        # ── Titre ──
        hdr = QHBoxLayout()
        accent = QFrame()
        accent.setFixedSize(4, 50)
        accent.setStyleSheet(f"""
            background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                stop:0 {C['amber']}, stop:1 {C['teal']});
            border-radius: 2px;
        """)
        hdr.addWidget(accent)
        hdr.addSpacing(10)
        titles = QVBoxLayout()
        titles.setSpacing(2)
        t = QLabel("Gestion des Achats")
        t.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        t.setStyleSheet(f"color:{C['txt']}; background:transparent;")
        titles.addWidget(t)
        s = QLabel("Gérez vos achats et vos fournisseurs")
        s.setFont(QFont("Segoe UI", 11))
        s.setStyleSheet(f"color:{C['txt_dim']}; background:transparent;")
        titles.addWidget(s)
        hdr.addLayout(titles)
        hdr.addStretch()
        main_layout.addLayout(hdr)

        # ── Fournisseur ──
        supplier_card = QFrame()
        supplier_card.setStyleSheet(f"""
            QFrame {{ background:{C['bg_card']}; border-radius:10px; border:1px solid {C['border']}; }}
        """)
        scl = QHBoxLayout(supplier_card)
        scl.setContentsMargins(16, 12, 16, 12)
        scl.setSpacing(12)

        sup_lbl = QLabel("🏢  Fournisseur")
        sup_lbl.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        sup_lbl.setStyleSheet(f"color:{C['amber']}; border:none;")

        self.supplier_combo = QComboBox()
        self.supplier_combo.setStyleSheet(INPUT_STYLE)
        self.supplier_combo.setMinimumHeight(40)
        self.supplier_combo.setMinimumWidth(240)
        self.load_suppliers()

        self.new_supplier_btn = QPushButton("＋  Fournisseur")
        self.new_supplier_btn.setStyleSheet(BTN['secondary'])
        self.new_supplier_btn.setMinimumHeight(40)
        self.new_supplier_btn.setFixedWidth(155)
        self.new_supplier_btn.clicked.connect(self.add_supplier)
        self.new_supplier_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        self.add_item_btn = QPushButton("＋  Ajouter Article")
        self.add_item_btn.setStyleSheet(BTN['primary'])
        self.add_item_btn.setMinimumHeight(40)
        self.add_item_btn.setFixedWidth(165)
        self.add_item_btn.clicked.connect(self.add_item)
        self.add_item_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        scl.addWidget(sup_lbl)
        scl.addWidget(self.supplier_combo)
        scl.addWidget(self.new_supplier_btn)
        scl.addStretch()
        scl.addWidget(self.add_item_btn)
        main_layout.addWidget(supplier_card)

        # ── Tableau ──
        tbl_card = QFrame()
        tbl_card.setStyleSheet(f"""
            QFrame {{ background:{C['bg_card']}; border-radius:12px; border:1px solid {C['border']}; }}
        """)
        tcl = QVBoxLayout(tbl_card)
        tcl.setContentsMargins(14, 12, 14, 12)
        tcl.setSpacing(8)

        tbl_title = QLabel("📦  Articles d'Achat")
        tbl_title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        tbl_title.setStyleSheet(f"color:{C['txt']}; border:none;")
        tcl.addWidget(tbl_title)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ["Produit", "Quantité", "Prix Unitaire", "Total", ""])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for i, w in [(1, 100), (2, 130), (3, 130), (4, 60)]:
            self.table.horizontalHeader().setSectionResizeMode(
                i, QHeaderView.ResizeMode.Fixed)
            self.table.setColumnWidth(i, w)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setMinimumHeight(200)
        self.table.setShowGrid(False)
        self.table.setStyleSheet(TABLE_STYLE)
        tcl.addWidget(self.table)
        main_layout.addWidget(tbl_card, 1)

        # ── Résumé ──
        summary_card = QFrame()
        summary_card.setStyleSheet(f"""
            QFrame {{
                background:{C['bg_card']}; border-radius:12px;
                border:2px solid rgba(245,166,35,0.30);
            }}
        """)
        scl2 = QVBoxLayout(summary_card)
        scl2.setContentsMargins(20, 16, 20, 20)
        scl2.setSpacing(8)

        sum_title = QLabel("💰  Résumé de l'Achat")
        sum_title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        sum_title.setStyleSheet(f"color:{C['txt']}; background:transparent;")
        scl2.addWidget(sum_title)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background:{C['border']}; border:none;")
        scl2.addWidget(sep)

        def add_summary_row(label_text, color_val=None, is_total=False):
            h = QHBoxLayout()
            lbl = QLabel(label_text)
            lbl.setFont(QFont("Segoe UI", 13 if is_total else 11))
            lbl.setStyleSheet(f"color:{C['txt_sec'] if not is_total else C['txt']}; background:transparent;")
            val = QLabel("0.00 DA")
            val.setFont(QFont("Segoe UI", 20 if is_total else 13,
                              QFont.Weight.Bold))
            val.setStyleSheet(f"color:{color_val or C['txt']}; background:transparent;")
            val.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            h.addWidget(lbl)
            h.addStretch()
            h.addWidget(val)
            scl2.addLayout(h)
            return val

        self.subtotal_label = add_summary_row("Sous-total HT")
        self.tax_title_label_widget = None

        tax_row = QHBoxLayout()
        self.tax_title_label = QLabel("Taxe (10%)")
        self.tax_title_label.setFont(QFont("Segoe UI", 11))
        self.tax_title_label.setStyleSheet(f"color:{C['txt_sec']}; background:transparent;")
        self.tax_label = QLabel("0.00 DA")
        self.tax_label.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        self.tax_label.setStyleSheet(f"color:{C['yellow']}; background:transparent;")
        self.tax_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        tax_row.addWidget(self.tax_title_label)
        tax_row.addStretch()
        tax_row.addWidget(self.tax_label)
        scl2.addLayout(tax_row)

        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setFixedHeight(1)
        sep2.setStyleSheet(f"background:rgba(245,166,35,0.30); border:none;")
        scl2.addWidget(sep2)

        self.total_label = add_summary_row("TOTAL TTC", color_val=C['amber'], is_total=True)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self.save_btn = QPushButton("✦  Enregistrer l'Achat")
        self.save_btn.setStyleSheet(BTN['success'])
        self.save_btn.setFixedSize(240, 46)
        self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_btn.clicked.connect(self.save_purchase)
        btn_row.addWidget(self.save_btn)
        scl2.addLayout(btn_row)
        main_layout.addWidget(summary_card)

        self.table.itemChanged.connect(self.update_totals)
        self.refresh_page()

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_page()

    def refresh_page(self):
        self.load_suppliers()
        self.table.setRowCount(0)
        self.update_totals()

    def load_suppliers(self):
        self.supplier_combo.clear()
        self.supplier_combo.addItem("Sélectionner un fournisseur", None)
        for s in self.db.get_all_suppliers():
            self.supplier_combo.addItem(s['name'], s['id'])

    def add_supplier(self):
        if not session.can('add_supplier'):
            QMessageBox.warning(self, "Accès refusé", "Votre rôle ne permet pas d'ajouter des fournisseurs.")
            return
        dialog = SupplierDialog()
        if dialog.exec():
            supplier_id = self.db.add_supplier(
                dialog.name_edit.text().strip(),
                dialog.phone_edit.text().strip(),
                dialog.email_edit.text().strip(),
                dialog.address_edit.text().strip(),
                dialog.nif_edit.text().strip())
            if supplier_id:
                QMessageBox.information(self, "Succès", "Fournisseur ajouté!")
                self.load_suppliers()
                index = self.supplier_combo.findData(supplier_id)
                if index >= 0:
                    self.supplier_combo.setCurrentIndex(index)

    def add_item(self):
        products = self.db.get_all_products()
        if not products:
            QMessageBox.warning(self, "Attention", "Aucun produit disponible!")
            return
        dialog = ProductSelectorDialog(products)
        if dialog.exec() and dialog.selected_product:
            product = dialog.selected_product
            quantity = product.get('_qty', 1)
            for row in range(self.table.rowCount()):
                item = self.table.item(row, 0)
                if item and item.data(Qt.ItemDataRole.UserRole) == product['id']:
                    qty_item = self.table.item(row, 1)
                    qty_item.setText(str(int(clean_num(qty_item)) + quantity))
                    self.update_totals()
                    return
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setRowHeight(row, 44)

            p_item = QTableWidgetItem(product['name'])
            p_item.setData(Qt.ItemDataRole.UserRole, product['id'])
            p_item.setFlags(p_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            p_item.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            self.table.setItem(row, 0, p_item)

            qty_item = QTableWidgetItem(str(quantity))
            qty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 1, qty_item)

            price_item = QTableWidgetItem(fmt_da(product['purchase_price']))
            price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            price_item.setForeground(QColor(C['amber']))
            self.table.setItem(row, 2, price_item)

            total = quantity * product['purchase_price']
            total_item = QTableWidgetItem(fmt_da(total))
            total_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            total_item.setFlags(total_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            total_item.setForeground(QColor(C['teal']))
            total_item.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            self.table.setItem(row, 3, total_item)

            rm_btn = QPushButton("✕")
            rm_btn.setStyleSheet(f"""
                QPushButton {{ background:transparent; color:{C['coral']};
                    border:none; font-size:14px; }}
                QPushButton:hover {{
                    background:{C['coral']}; color:white; border-radius:4px;
                }}
            """)
            rm_btn.clicked.connect(lambda checked, r=row: self.remove_item(r))
            rm_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.table.setCellWidget(row, 4, rm_btn)
            self.update_totals()

    def remove_item(self, row):
        self.table.removeRow(row)
        self.update_totals()

    def update_totals(self):
        try:
            self.table.itemChanged.disconnect(self.update_totals)
        except:
            pass
        subtotal = 0.0
        for row in range(self.table.rowCount()):
            try:
                qty = clean_num(self.table.item(row, 1))
                price = clean_num(self.table.item(row, 2))
                total_row = qty * price
                total_item = self.table.item(row, 3)
                if total_item:
                    total_item.setText(fmt_da(total_row))
                subtotal += total_row
            except Exception:
                continue
        try:
            tax_rate_pct = float(self.db.get_setting('purchase_vat', '10') or '10')
        except:
            tax_rate_pct = 10.0
        tax = subtotal * (tax_rate_pct / 100)
        total = subtotal + tax
        self.tax_title_label.setText(f"Taxe ({tax_rate_pct:.0f}%)")
        self.subtotal_label.setText(fmt_da(subtotal))
        self.tax_label.setText(fmt_da(tax))
        self.total_label.setText(fmt_da(total))
        self.table.itemChanged.connect(self.update_totals)

    def save_purchase(self):
        if not session.can('create_purchase'):
            QMessageBox.warning(self, "Accès refusé", "Votre rôle ne permet pas d'enregistrer des achats.")
            return
        if self.supplier_combo.currentIndex() == 0:
            QMessageBox.warning(self, "Attention", "Sélectionnez un fournisseur!")
            return
        if self.table.rowCount() == 0:
            QMessageBox.warning(self, "Attention", "Ajoutez au moins un article!")
            return
        supplier_id = self.supplier_combo.currentData()
        items = []
        for row in range(self.table.rowCount()):
            try:
                product_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
                product_name = self.table.item(row, 0).text()
                quantity = int(clean_num(self.table.item(row, 1)))
                unit_price = clean_num(self.table.item(row, 2))
                items.append({
                    'product_id': product_id, 'product_name': product_name,
                    'quantity': quantity, 'unit_price': unit_price})
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Ligne {row + 1}: {str(e)}")
                return
        reference = f"ACH-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        purchase_id = self.db.create_purchase(
            reference=reference, supplier_id=supplier_id, items=items,
            payment_method="cash",
            tax_rate=float(self.db.get_setting('purchase_vat', '10') or '10'))
        if purchase_id:
            QMessageBox.information(self, "Succès", f"Achat enregistré!\nRéf: {reference}")
            self.table.setRowCount(0)
            self.supplier_combo.setCurrentIndex(0)
            self.update_totals()
            self.purchase_saved.emit()
        else:
            QMessageBox.critical(self, "Erreur", "Impossible d'enregistrer l'achat!")