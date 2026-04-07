from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QComboBox, QHBoxLayout, QFrame, QDialog,
    QFormLayout, QLineEdit, QSpinBox, QDoubleSpinBox, QMessageBox, QGridLayout,
    QScrollArea, QSizePolicy
)
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt, pyqtSignal
from db_manager import get_database
from datetime import datetime
from payment_module import show_payment_dialog

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
    'border_a':  'rgba(245,166,35,0.18)',
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
    QLineEdit:focus, QComboBox:focus, QSpinBox:focus,
    QDoubleSpinBox:focus, QTextEdit:focus {{
        border: 1.5px solid {C['amber']}; background-color: {C['bg_card']};
    }}
    QLineEdit:hover, QComboBox:hover, QSpinBox:hover, QDoubleSpinBox:hover {{
        border: 1.5px solid rgba(245,166,35,0.40);
    }}
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


def fmt_da(v, d=None):
    from currency import fmt_da as _fmt_da
    return _fmt_da(v) if d is None else _fmt_da(v, d)


class AddProductDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.db = get_database()
        self.selected_product = None
        self.all_products = []
        self._preserved_quantity = None
        self._just_created = False

        self.setWindowTitle("Ajouter un Article")
        self.setFixedWidth(680)
        self.setFixedHeight(880)
        self.setStyleSheet(f"""
            QDialog {{ background-color: {C['bg']}; }}
            QLabel  {{ color: {C['txt']}; font-size: 13px; }}
            {INPUT_STYLE}
        """)

        main = QVBoxLayout(self)
        main.setSpacing(12)
        main.setContentsMargins(18, 18, 18, 18)

        # Header
        header = QFrame()
        header.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #1C1408, stop:1 #121812);
                border-radius: 10px;
                border: 1px solid rgba(245,166,35,0.20);
            }}
        """)
        hl = QVBoxLayout(header)
        hl.setContentsMargins(18, 14, 18, 14)

        row = QHBoxLayout()
        ic = QLabel("🛒")
        ic.setFont(QFont("Segoe UI", 20))
        ic.setStyleSheet("background:transparent; border:none;")
        row.addWidget(ic)
        titles = QVBoxLayout()
        t = QLabel("Ajouter un Article")
        t.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        t.setStyleSheet(f"color:{C['amber']}; background:transparent; border:none;")
        titles.addWidget(t)
        s = QLabel("Recherchez et sélectionnez le produit souhaité")
        s.setFont(QFont("Segoe UI", 10))
        s.setStyleSheet(f"color:{C['txt_sec']}; background:transparent; border:none;")
        titles.addWidget(s)
        row.addLayout(titles)
        row.addStretch()
        hl.addLayout(row)
        main.addWidget(header)

        # Scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"QScrollArea {{ border:none; background:transparent; }}")
        sw = QWidget()
        sw.setStyleSheet("background:transparent;")
        sl = QVBoxLayout(sw)
        sl.setSpacing(10)
        sl.setContentsMargins(0, 0, 0, 0)

        # Search container
        search_card = QFrame()
        search_card.setStyleSheet(f"""
            QFrame {{ background:{C['bg_card']}; border-radius:10px; border:1px solid {C['border']}; }}
        """)
        scl = QVBoxLayout(search_card)
        scl.setContentsMargins(14, 12, 14, 12)
        scl.setSpacing(8)

        pl = QLabel("Rechercher un produit *")
        pl.setStyleSheet(f"color:{C['amber']}; border:none; font-weight:bold; font-size:13px;")
        scl.addWidget(pl)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Tapez le nom du produit...")
        self.search_input.setStyleSheet(INPUT_STYLE)
        self.search_input.setMinimumHeight(40)
        self.search_input.textChanged.connect(self.filter_products)
        scl.addWidget(self.search_input)

        # Bouton pour créer un nouveau produit rapidement
        self.create_product_btn = QPushButton("＋  Créer Nouveau Produit")
        self.create_product_btn.setStyleSheet(BTN['primary'])
        self.create_product_btn.setFixedHeight(40)
        self.create_product_btn.setFixedWidth(220)
        self.create_product_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.create_product_btn.clicked.connect(self.create_new_product)
        scl.addWidget(self.create_product_btn)

        self.product_table = QTableWidget(0, 3)
        self.product_table.setHorizontalHeaderLabels(["Produit", "Prix Unitaire", "Stock"])
        self.product_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.product_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.product_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.product_table.setColumnWidth(1, 120)
        self.product_table.setColumnWidth(2, 130)
        self.product_table.verticalHeader().setVisible(False)
        self.product_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.product_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.product_table.setMinimumHeight(160)
        self.product_table.setMaximumHeight(180)
        self.product_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.product_table.itemSelectionChanged.connect(self.on_product_selected_from_table)
        self.product_table.setStyleSheet(TABLE_STYLE)
        scl.addWidget(self.product_table)
        sl.addWidget(search_card)

        # Form card
        form_card = QFrame()
        form_card.setStyleSheet(f"""
            QFrame {{ background:{C['bg_card']}; border-radius:10px; border:1px solid {C['border']}; }}
        """)
        fcl = QFormLayout(form_card)
        fcl.setContentsMargins(16, 14, 16, 14)
        fcl.setSpacing(10)
        fcl.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        def mk_lbl(t):
            l = QLabel(t)
            l.setStyleSheet(f"color:{C['txt_sec']}; border:none; font-size:12px;")
            return l

        self.price_display = QLabel("0 DA")
        self.price_display.setStyleSheet(f"""
            color:{C['amber']}; border:none; font-size:18px; font-weight:bold;
            padding:10px; background:{C['bg_input']}; border-radius:5px;
        """)
        fcl.addRow(mk_lbl("Prix unitaire:"), self.price_display)

        self.stock_display = QLabel("0")
        self.stock_display.setStyleSheet(f"""
            color:{C['teal']}; border:none; font-size:16px; font-weight:bold;
            padding:10px; background:{C['bg_input']}; border-radius:5px;
        """)
        fcl.addRow(mk_lbl("Stock disponible:"), self.stock_display)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background:{C['border']}; border:none; margin:6px 0;")
        fcl.addRow(sep)

        self.quantity = QLineEdit()
        self.quantity.setText("1")
        self.quantity.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.quantity.setStyleSheet(INPUT_STYLE)
        self.quantity.setMinimumHeight(40)
        self.quantity.textChanged.connect(self.update_total)
        fcl.addRow(mk_lbl("Quantité *"), self.quantity)

        self.discount = QLineEdit()
        self.discount.setText("0")
        self.discount.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.discount.setStyleSheet(INPUT_STYLE)
        self.discount.setMinimumHeight(40)
        self.discount.textChanged.connect(self.update_total)
        fcl.addRow(mk_lbl("Remise (%)"), self.discount)
        sl.addWidget(form_card)

        # Total
        total_card = QFrame()
        total_card.setStyleSheet(f"""
            QFrame {{
                background:{C['bg_card']}; border-radius:10px;
                border:2px solid rgba(245,166,35,0.40);
            }}
        """)
        tl = QHBoxLayout(total_card)
        tl.setContentsMargins(14, 12, 18, 12)
        tl_label = QLabel("TOTAL :")
        tl_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        tl_label.setStyleSheet(f"color:{C['txt']}; border:none;")
        self.total_display = QLabel("0 DA")
        self.total_display.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        self.total_display.setStyleSheet(f"color:{C['amber']}; border:none;")
        self.total_display.setAlignment(Qt.AlignmentFlag.AlignRight)
        tl.addWidget(tl_label)
        tl.addStretch()
        tl.addWidget(self.total_display)
        sl.addWidget(total_card)

        scroll.setWidget(sw)
        main.addWidget(scroll)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        cancel_btn = QPushButton("Annuler")
        cancel_btn.setStyleSheet(BTN['secondary'])
        cancel_btn.setMinimumHeight(44)
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn = QPushButton("✓  Ajouter")
        add_btn.setStyleSheet(BTN['success'])
        add_btn.setMinimumHeight(44)
        add_btn.setFixedWidth(180)
        add_btn.clicked.connect(self.validate_and_accept)
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_row.addWidget(cancel_btn)
        btn_row.addStretch()
        btn_row.addWidget(add_btn)
        main.addLayout(btn_row)

        self.load_products()

    def load_products(self):
        self.all_products = []
        self.product_table.setRowCount(0)
        for p in self.db.get_all_products():
            self.all_products.append(p)
        self.display_products(self.all_products)

    def create_new_product(self):
        # Dialogue simple pour créer un produit rapide
        dlg = QDialog(self)
        dlg.setWindowTitle("Nouveau Produit")
        dlg.setModal(True)
        dlg.setFixedWidth(420)
        layout = QFormLayout(dlg)

        name_in = QLineEdit()
        name_in.setPlaceholderText("Nom du produit")
        price_in = QDoubleSpinBox()
        price_in.setRange(0, 10000000)
        price_in.setDecimals(2)
        price_in.setValue(0)
        stock_in = QSpinBox()
        stock_in.setRange(0, 1000000)
        stock_in.setValue(0)
        cat_in = QComboBox()
        cat_in.addItem("Aucune", None)
        try:
            for c in self.db.get_all_categories():
                cat_in.addItem(c.get('name') or str(c.get('id')), c.get('id'))
        except Exception:
            pass

        layout.addRow(QLabel("Nom *"), name_in)
        layout.addRow(QLabel("Prix de vente *"), price_in)
        layout.addRow(QLabel("Catégorie"), cat_in)
        layout.addRow(QLabel("Quantité en stock"), stock_in)

        btn_row = QHBoxLayout()
        cancel = QPushButton("Annuler")
        ok = QPushButton("Créer")
        cancel.clicked.connect(dlg.reject)
        ok.clicked.connect(dlg.accept)
        btn_row.addStretch()
        btn_row.addWidget(cancel)
        btn_row.addWidget(ok)
        layout.addRow(btn_row)

        if dlg.exec():
            name = name_in.text().strip()
            price = float(price_in.value())
            stock = int(stock_in.value())
            category_id = cat_in.currentData()
            if not name or price <= 0:
                QMessageBox.warning(self, "Erreur", "Nom et prix valides requis !")
                return

            # Vérifier si le produit existe déjà dans le stock
            for p in self.all_products:
                if p['name'].strip().lower() == name.lower():
                    QMessageBox.warning(self, "Produit Existant", f"Le produit '{name}' existe déjà dans le stock !")
                    return

            new_id = self.db.add_product(name=name, selling_price=price, stock_quantity=stock, category_id=category_id)
            if new_id:
                p = self.db.get_product_by_id(new_id)
                if p:
                    # Sauvegarder la quantité actuelle
                    current_quantity = self.quantity.text()
                    
                    # Ajouter à la liste locale
                    self.all_products.insert(0, p)
                    self.display_products(self.all_products)
                    
                    # Sélectionner le nouveau produit
                    for row in range(self.product_table.rowCount()):
                        item = self.product_table.item(row, 0)
                        if item and item.data(Qt.ItemDataRole.UserRole)['id'] == p['id']:
                            self.product_table.selectRow(row)
                            self.product_table.scrollToItem(item)
                            break
                    
                    # Restaurer la quantité
                    self.quantity.setText(current_quantity)
                    self.selected_product = p
                    self.price_display.setText(f"{fmt_da(p['selling_price'], 2)}")
                    self.stock_display.setText(str(p['stock_quantity']))
                    self.update_total()
                    
                    # Ne pas fermer - l'utilisateur clique sur "Ajouter" quand il veut
                    return
            QMessageBox.warning(self, "Erreur", "Impossible de créer le produit.")

    def display_products(self, products):
        from currency import fmt_da
        self.product_table.setRowCount(0)
        for p in products:
            row = self.product_table.rowCount()
            self.product_table.insertRow(row)
            self.product_table.setRowHeight(row, 40)
            name_item = QTableWidgetItem(p['name'])
            name_item.setData(Qt.ItemDataRole.UserRole, p)
            name_item.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            self.product_table.setItem(row, 0, name_item)
            price_item = QTableWidgetItem(fmt_da(p['selling_price']))
            price_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            price_item.setForeground(QColor(C['amber']))
            self.product_table.setItem(row, 1, price_item)
            stock_item = QTableWidgetItem(str(p['stock_quantity']))
            stock_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            stock_item.setForeground(QColor(C['teal']))
            self.product_table.setItem(row, 2, stock_item)

    def filter_products(self, text):
        t = text.lower().strip()
        self.display_products(
            self.all_products if not t
            else [p for p in self.all_products if p['name'].lower().startswith(t)])

    def on_product_selected_from_table(self):
        """Quand un produit est sélectionné dans la table"""
        selected_row = self.product_table.currentRow()

        if selected_row >= 0:
            item = self.product_table.item(selected_row, 0)
            if item:
                product = item.data(Qt.ItemDataRole.UserRole)
                
                # Réinitialiser qté/remise SEULEMENT si c'est un nouveau produit différent
                ancien_id = self.selected_product.get('id') if self.selected_product else None
                nouveau_id = product.get('id')
                
                # Ne réinitialiser QUE si c'est un produit différent
                if ancien_id != nouveau_id:
                    # Ne pas écraser si on vient de créer un nouveau produit
                    if not self._just_created:
                        self.quantity.setText("1")
                        self.discount.setText("0")
                    # Réinitialiser le flag après usage
                    self._just_created = False

                self.selected_product = product
                self.price_display.setText(f"{fmt_da(product['selling_price'], 2)}")
                self.stock_display.setText(str(product['stock_quantity']))
                self.update_total()
        else:
            self.selected_product = None
            self.price_display.setText("0 DA")
            self.stock_display.setText("0")

    def update_total(self):
        from currency import fmt_da
        if self.selected_product:
            try:
                qty = int(self.quantity.text() or 1)
                price = self.selected_product['selling_price']
                disc = float(self.discount.text() or 0)
                total = qty * price * (1 - disc / 100)
                self.total_display.setText(fmt_da(total))
            except ValueError:
                self.total_display.setText("0 DA")

    def validate_and_accept(self):
        if not self.selected_product:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un produit!")
            return
        try:
            qty = int(self.quantity.text() or 1)
        except ValueError:
            QMessageBox.warning(self, "Erreur", "La quantité doit être un nombre!")
            return
        if qty > self.selected_product['stock_quantity']:
            reply = QMessageBox.question(
                self, "Stock insuffisant",
                "La quantité demandée dépasse le stock disponible. Continuer et vendre quand même ?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply != QMessageBox.StandardButton.Yes:
                return
        self.accept()


class SalesPage(QWidget):
    sale_saved = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.db = get_database()
        self.cart_items = []
        self.vat_rate = self._get_vat_rate()

        self.setStyleSheet(f"background-color:{C['bg']};")
        root = QVBoxLayout(self)
        root.setContentsMargins(22, 20, 22, 20)
        root.setSpacing(14)
        layout = root

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
        t = QLabel("Point de Vente")
        t.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        t.setStyleSheet(f"color:{C['txt']}; background:transparent;")
        titles.addWidget(t)
        s = QLabel("Gestion des ventes et facturation")
        s.setFont(QFont("Segoe UI", 11))
        s.setStyleSheet(f"color:{C['txt_dim']}; background:transparent;")
        titles.addWidget(s)
        hdr.addLayout(titles)
        hdr.addStretch()
        layout.addLayout(hdr)

        # ── Sélection client ──
        client_card = QFrame()
        client_card.setStyleSheet(f"""
            QFrame {{
                background:{C['bg_card']}; border-radius:10px; border:1px solid {C['border']};
            }}
        """)
        cl = QHBoxLayout(client_card)
        cl.setContentsMargins(16, 12, 16, 12)
        cl.setSpacing(12)

        client_lbl = QLabel("👤  Client *")
        client_lbl.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        client_lbl.setStyleSheet(f"color:{C['amber']}; border:none;")

        self.client_required_label = QLabel("⚠  Champ obligatoire")
        self.client_required_label.setFont(QFont("Segoe UI", 10))
        self.client_required_label.setStyleSheet(f"color:{C['coral']}; border:none;")
        self.client_required_label.setVisible(False)

        self.client_combo = QComboBox()
        self.client_combo.setStyleSheet(INPUT_STYLE)
        self.client_combo.setMinimumHeight(40)
        self.client_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.client_combo.currentIndexChanged.connect(self._on_client_changed)
        self.load_clients()

        self.add_item_btn = QPushButton("＋  Ajouter Article")
        self.add_item_btn.setStyleSheet(BTN['primary'])
        self.add_item_btn.setMinimumHeight(40)
        self.add_item_btn.setFixedWidth(180)
        self.add_item_btn.clicked.connect(self.add_item)
        self.add_item_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        info_col = QVBoxLayout()
        info_col.setSpacing(2)
        info_col.addWidget(client_lbl)
        info_col.addWidget(self.client_required_label)
        cl.addLayout(info_col)
        cl.addWidget(self.client_combo)
        cl.addStretch()
        cl.addWidget(self.add_item_btn)
        layout.addWidget(client_card)

        # ── Tableau panier ──
        tbl_card = QFrame()
        tbl_card.setStyleSheet(f"""
            QFrame {{ background:{C['bg_card']}; border-radius:12px; border:1px solid {C['border']}; }}
        """)
        tcl = QVBoxLayout(tbl_card)
        tcl.setContentsMargins(14, 12, 14, 12)
        tcl.setSpacing(8)

        tbl_title_row = QHBoxLayout()
        tbl_title = QLabel("🛒  Panier")
        tbl_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        tbl_title.setStyleSheet(f"color:{C['txt']}; border:none;")
        tbl_title_row.addWidget(tbl_title)
        tbl_title_row.addStretch()
        tcl.addLayout(tbl_title_row)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(
            ["Produit", "Quantité", "Prix Unit.", "Remise", "Total", ""])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for i, w in [(1, 100), (2, 120), (3, 100), (4, 120), (5, 80)]:
            self.table.horizontalHeader().setSectionResizeMode(
                i, QHeaderView.ResizeMode.Fixed)
            self.table.setColumnWidth(i, w)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setMinimumHeight(120)
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.table.setShowGrid(False)
        self.table.setStyleSheet(TABLE_STYLE)
        tcl.addWidget(self.table)
        layout.addWidget(tbl_card)

        # ── Résumé ──
        summary_card = QFrame()
        summary_card.setObjectName("summaryCard")
        summary_card.setStyleSheet(f"""
            QFrame#summaryCard {{
                background:{C['bg_card']}; border-radius:12px;
                border:2px solid rgba(245,166,35,0.35);
            }}
        """)
        sl = QVBoxLayout(summary_card)
        sl.setContentsMargins(20, 16, 20, 16)
        sl.setSpacing(10)

        # Titre + client badge
        top_row = QHBoxLayout()
        sum_title = QLabel("💰  Résumé de la Vente")
        sum_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        sum_title.setStyleSheet(f"color:{C['txt']}; background:transparent;")
        top_row.addWidget(sum_title)
        top_row.addStretch()

        badge_frame = QFrame()
        badge_frame.setStyleSheet(f"""
            QFrame {{ background:rgba(245,166,35,0.10); border-radius:7px;
                     border:1px solid rgba(245,166,35,0.30); }}
        """)
        bfl = QHBoxLayout(badge_frame)
        bfl.setContentsMargins(10, 5, 10, 5)
        bfl.setSpacing(6)
        icon_lbl = QLabel("👤")
        icon_lbl.setFont(QFont("Segoe UI", 12))
        icon_lbl.setStyleSheet("border:none; background:transparent;")
        bfl.addWidget(icon_lbl)
        self.client_name_label = QLabel("—")
        self.client_name_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.client_name_label.setStyleSheet(f"color:{C['amber']}; border:none;")
        bfl.addWidget(self.client_name_label)
        top_row.addWidget(badge_frame)
        sl.addLayout(top_row)

        # ── Grille infos ──
        info_row = QHBoxLayout()
        info_row.setSpacing(20)

        def mk_row_label(text, color=None):
            l = QLabel(text)
            l.setFont(QFont("Segoe UI", 11))
            l.setStyleSheet(f"color:{C['txt_sec']}; background:transparent;")
            return l

        def mk_val_label(text="—", color=None):
            l = QLabel(text)
            l.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            l.setStyleSheet(f"color:{color or C['txt']}; background:transparent;")
            l.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            l.setMinimumWidth(120)
            return l

        left = QVBoxLayout()
        left.setSpacing(5)

        def add_info_row(parent_layout, label_text, color_val=None):
            h = QHBoxLayout()
            h.setSpacing(8)
            h.addWidget(mk_row_label(label_text), 1)
            v = mk_val_label(color=color_val)
            h.addWidget(v)
            parent_layout.addLayout(h)
            return v

        self.nb_articles_label = add_info_row(left, "📦  Articles :", C['amber'])
        self.qty_total_label = add_info_row(left, "🔢  Quantité :", C['amber'])
        self.discount_total_label = add_info_row(left, "🏷️  Remise :", C['coral'])

        right = QVBoxLayout()
        right.setSpacing(5)
        self.subtotal_label = add_info_row(right, "Sous-total HT :", C['txt'])

        tax_row = QHBoxLayout()
        tax_row.setSpacing(8)
        self.vat_percent = float(self.db.get_setting('vat', '19'))
        self.tax_header_label = QLabel(f"TVA ({self.vat_percent:.0f}%) :")
        self.tax_header_label.setFont(QFont("Segoe UI", 11))
        self.tax_header_label.setStyleSheet(f"color:{C['txt_sec']}; background:transparent;")
        self.tax_label = QLabel("—")
        self.tax_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.tax_label.setStyleSheet(f"color:{C['yellow']}; background:transparent;")
        self.tax_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.tax_label.setMinimumWidth(120)
        tax_row.addWidget(self.tax_header_label, 1)
        tax_row.addWidget(self.tax_label)
        right.addLayout(tax_row)

        info_row.addLayout(left, 1)
        vsep = QFrame()
        vsep.setFrameShape(QFrame.Shape.VLine)
        vsep.setFixedWidth(1)
        vsep.setStyleSheet(f"background:{C['border']};")
        info_row.addWidget(vsep)
        info_row.addLayout(right, 1)
        sl.addLayout(info_row)

        # Séparateur
        hsep = QFrame()
        hsep.setFrameShape(QFrame.Shape.HLine)
        hsep.setFixedHeight(1)
        hsep.setStyleSheet(f"background:rgba(245,166,35,0.30); border:none;")
        sl.addWidget(hsep)

        # Total TTC
        ttc_row = QHBoxLayout()
        ttc_lbl = QLabel("TOTAL TTC :")
        ttc_lbl.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        ttc_lbl.setStyleSheet(f"color:{C['txt']}; background:transparent;")
        self.total_label = QLabel("0 DA")
        self.total_label.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        self.total_label.setStyleSheet(f"color:{C['amber']}; background:transparent;")
        self.total_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        ttc_row.addWidget(ttc_lbl)
        ttc_row.addStretch()
        ttc_row.addWidget(self.total_label)
        sl.addLayout(ttc_row)

        # Boutons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        self.clear_btn = QPushButton("🗑  Vider le Panier")
        self.clear_btn.setStyleSheet(BTN['secondary'])
        self.clear_btn.setMinimumHeight(44)
        self.clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clear_btn.clicked.connect(self.clear_cart)
        self.save_btn = QPushButton("✦  Enregistrer la Vente")
        self.save_btn.setStyleSheet(BTN['success'])
        self.save_btn.setMinimumHeight(44)
        self.save_btn.setMinimumWidth(230)
        self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_btn.clicked.connect(self.save_sale)
        btn_row.addWidget(self.clear_btn)
        btn_row.addStretch()
        btn_row.addWidget(self.save_btn)
        sl.addLayout(btn_row)
        layout.addWidget(summary_card)

        self.update_totals()

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_page()

    def refresh_page(self):
        self.load_clients()
        self.cart_items = []
        self.table.setRowCount(0)
        self.update_totals()

    def load_clients(self):
        self.client_combo.clear()
        self.client_combo.addItem("Client Anonyme", None)
        for client in self.db.get_all_clients():
            self.client_combo.addItem(client['name'], client['id'])

    def add_item(self):
        dialog = AddProductDialog()
        if dialog.exec() and dialog.selected_product:
            from currency import fmt_da
            p = dialog.selected_product
            
            # Utiliser la quantité préservée si elle existe, sinon celle du champ
            if dialog._preserved_quantity is not None:
                qty = dialog._preserved_quantity
                # Nettoyer pour éviter réutilisation accidentelle
                dialog._preserved_quantity = None
            else:
                try:
                    qty = int(dialog.quantity.text() or 1)
                except Exception:
                    qty = 1
            
            disc = float(dialog.discount.text() or 0)
            unit_price = p['selling_price']
            total = qty * unit_price * (1 - disc / 100)
            
            self.cart_items.append({
                'product_id': p['id'], 'product_name': p['name'],
                'quantity': qty, 'unit_price': unit_price,
                'discount': disc, 'total': total
            })
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setRowHeight(row, 44)

            product_item = QTableWidgetItem(p['name'])
            product_item.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            self.table.setItem(row, 0, product_item)

            def mk_center(text, color=None):
                it = QTableWidgetItem(text)
                it.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if color:
                    it.setForeground(QColor(color))
                return it

            def mk_right(text, color=None):
                it = QTableWidgetItem(text)
                it.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                if color:
                    it.setForeground(QColor(color))
                return it

            self.table.setItem(row, 1, mk_center(str(qty)))
            self.table.setItem(row, 2, mk_right(f"{unit_price:,}", C['txt_sec']))
            self.table.setItem(row, 3, mk_center(f"{disc:,}%", C['yellow']))
            total_it = mk_right(f"{total:,}", C['amber'])
            total_it.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            self.table.setItem(row, 4, total_it)

            rm_btn = QPushButton("✕")
            rm_btn.setFont(QFont("Segoe UI", 13))
            rm_btn.setStyleSheet(f"""
                QPushButton {{ background:transparent; color:{C['coral']}; border:none; }}
                QPushButton:hover {{
                    background:{C['coral']}; color:white; border-radius:4px;
                }}
            """)
            rm_btn.clicked.connect(lambda _, r=row: self.remove_item(r))
            rm_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.table.setCellWidget(row, 5, rm_btn)
            self.update_totals()

    def remove_item(self, row):
        if row < len(self.cart_items):
            del self.cart_items[row]
        self.table.removeRow(row)
        self.update_totals()

    def clear_cart(self):
        reply = QMessageBox.question(self, "Confirmation",
            "Voulez-vous vraiment vider le panier?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.cart_items = []
            self.table.setRowCount(0)
            self.update_totals()

    def _get_vat_rate(self):
        try:
            return float(self.db.get_setting('vat', '19')) / 100.0
        except:
            return 0.19

    def update_totals(self):
        from currency import fmt_da
        subtotal = sum(item['total'] for item in self.cart_items)
        self.vat_rate = self._get_vat_rate()
        self.vat_percent = self.vat_rate * 100
        self.tax_header_label.setText(f"TVA ({self.vat_percent:.0f}%) :")
        tax = subtotal * self.vat_rate
        total = subtotal + tax
        nb = len(self.cart_items)
        qty_total = sum(item['quantity'] for item in self.cart_items)
        total_sans_remise = sum(
            item['quantity'] * item['unit_price'] for item in self.cart_items)
        remise_total = total_sans_remise - subtotal
        self.nb_articles_label.setText(f"{nb} article(s)")
        self.qty_total_label.setText(f"{qty_total} unité(s)")
        self.discount_total_label.setText(f"-{fmt_da(remise_total)}")
        self.subtotal_label.setText(fmt_da(subtotal))
        self.tax_label.setText(fmt_da(tax))
        self.total_label.setText(fmt_da(total))

    def _on_client_changed(self, index):
        if not hasattr(self, 'client_name_label'):
            return
        if index > 0:
            self.client_combo.setStyleSheet(INPUT_STYLE)
            self.client_required_label.setVisible(False)
            self.client_name_label.setText(self.client_combo.currentText())
        else:
            self.client_name_label.setText("—")

    def save_sale(self):
        from currency import fmt_da
        if not self.cart_items:
            QMessageBox.warning(self, "Attention", "Le panier est vide!")
            return
        if self.client_combo.currentIndex() == 0:
            self.client_combo.setStyleSheet(INPUT_STYLE + f"""
                QComboBox {{ border: 2px solid {C['coral']};
                             background-color: rgba(255,107,107,0.10); }}
            """)
            self.client_required_label.setVisible(True)
            self.client_combo.setFocus()
            QMessageBox.warning(self, "Client obligatoire",
                "⚠ Veuillez sélectionner un client avant d'enregistrer la facture.")
            return
        subtotal = sum(item['total'] for item in self.cart_items)
        self.vat_rate = self._get_vat_rate()
        tax = subtotal * self.vat_rate
        total_ttc = subtotal + tax
        invoice_number = self.db.generate_invoice_number()
        client_name = self.client_combo.currentText()
        payment_data = show_payment_dialog(
            total_amount=total_ttc, invoice_number=invoice_number,
            cart_items=self.cart_items, client_name=client_name, parent=self)
        if not payment_data:
            QMessageBox.information(self, "Paiement annulé", "La vente n'a pas été enregistrée.")
            return
        client_id = self.client_combo.currentData()
        items = [{
            'product_id': item['product_id'],
            'quantity': item['quantity'],
            'unit_price': item['unit_price'],
            'discount': item['discount']
        } for item in self.cart_items]
        self.db.create_sale(
            invoice_number=invoice_number, client_id=client_id,
            items=items, payment_method=payment_data['method'], discount=0)
        self.sale_saved.emit()
        self.cart_items = []
        self.table.setRowCount(0)
        self.update_totals()
        self.client_combo.setCurrentIndex(0)

    def get_payment_method_name(self, method_code):
        return {
            'cash': '💵 Espèces', 'card': '💳 Carte bancaire',
            'check': '📝 Chèque', 'transfer': '🏦 Virement',
            'mobile': '📱 Mobile Money', 'credit': '🔄 Crédit'
        }.get(method_code, method_code)

    def format_payment_details(self, payment_data):
        return ""


from currency import fmt_da, fmt, currency_manager