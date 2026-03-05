from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QComboBox, QHBoxLayout, QFrame, QDialog,
    QFormLayout, QLineEdit, QSpinBox, QDoubleSpinBox, QMessageBox, QGridLayout,
    QScrollArea, QSizePolicy
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from styles import COLORS, BUTTON_STYLES, INPUT_STYLE, TABLE_STYLE
from db_manager import get_database
from datetime import datetime
from payment_module import show_payment_dialog  # ← AJOUTER CETTE LIGNE


class AddProductDialog(QDialog):
    """Dialogue pour ajouter un produit à la facture"""
    def __init__(self):
        super().__init__()
        
        self.db = get_database()
        self.selected_product = None
        
        self.setWindowTitle("🛒 Ajouter un Article à la Facture")
        self.setMinimumWidth(600)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['bg_medium']};
            }}
            QLabel {{
                color: {COLORS['text_primary']};
                font-size: 13px;
            }}
            {INPUT_STYLE}
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(25, 25, 25, 25)

        # En-tête
        header = QFrame()
        header.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['success']}, stop:1 {COLORS['primary']});
                border-radius: 10px;
                padding: 15px;
            }}
        """)
        header_layout = QVBoxLayout()
        header.setLayout(header_layout)

        title = QLabel("🛒 Ajouter un Article")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: white; margin-bottom: 5px; border: none;")
        header_layout.addWidget(title)

        subtitle = QLabel("Sélectionnez le produit et la quantité souhaitée")
        subtitle.setFont(QFont("Segoe UI", 11))
        subtitle.setStyleSheet("color: rgba(255, 255, 255, 0.8); border: none;")
        header_layout.addWidget(subtitle)

        main_layout.addWidget(header)

        # Formulaire
        form_container = QFrame()
        form_container.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_card']};
                border-radius: 10px;
                padding: 20px;
            }}
        """)
        form_layout = QFormLayout()
        form_container.setLayout(form_layout)
        form_layout.setSpacing(18)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        # Sélection du produit
        product_label = QLabel("Produit: *")
        product_label.setStyleSheet(f"color: {COLORS['text_primary']}; border: none; font-weight: bold;")
        
        self.product_combo = QComboBox()
        self.product_combo.setStyleSheet(INPUT_STYLE)
        self.product_combo.setMinimumHeight(45)
        
        # Charger les produits
        self.load_products()
        
        self.product_combo.currentIndexChanged.connect(self.on_product_selected)
        form_layout.addRow(product_label, self.product_combo)


        # Prix unitaire
        price_label = QLabel("Prix unitaire:")
        price_label.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        
        self.price_display = QLabel("0.00 DA")
        self.price_display.setStyleSheet(f"""
            color: {COLORS['success']}; 
            border: none;
            font-size: 18px;
            font-weight: bold;
            padding: 10px;
            background: {COLORS['bg_light']};
            border-radius: 5px;
        """)
        form_layout.addRow(price_label, self.price_display)

        # Stock disponible
        stock_label = QLabel("Stock disponible:")
        stock_label.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        
        self.stock_display = QLabel("0")
        self.stock_display.setStyleSheet(f"""
            color: {COLORS['warning']}; 
            border: none;
            font-size: 16px;
            font-weight: bold;
            padding: 10px;
            background: {COLORS['bg_light']};
            border-radius: 5px;
        """)
        form_layout.addRow(stock_label, self.stock_display)

        # Séparateur
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet(f"background-color: {COLORS['border']}; border: none; margin: 10px 0;")
        form_layout.addRow(separator)

        # Quantité
        qty_label = QLabel("Quantité: *")
        qty_label.setStyleSheet(f"color: {COLORS['text_primary']}; border: none; font-weight: bold;")
        
        self.quantity = QSpinBox()
        self.quantity.setMinimum(1)
        self.quantity.setMaximum(9999)
        self.quantity.setValue(1)
        self.quantity.setStyleSheet(INPUT_STYLE)
        self.quantity.setMinimumHeight(45)
        self.quantity.valueChanged.connect(self.update_total)
        form_layout.addRow(qty_label, self.quantity)

        # Remise
        discount_label = QLabel("Remise (%):")
        discount_label.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        
        self.discount = QDoubleSpinBox()
        self.discount.setMinimum(0.0)
        self.discount.setMaximum(100.0)
        self.discount.setDecimals(2)
        self.discount.setValue(0.0)
        self.discount.setStyleSheet(INPUT_STYLE)
        self.discount.setMinimumHeight(45)
        self.discount.setSuffix(" %")
        self.discount.valueChanged.connect(self.update_total)
        form_layout.addRow(discount_label, self.discount)

        main_layout.addWidget(form_container)

        # Résumé du total
        total_container = QFrame()
        total_container.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['bg_card']}, stop:1 #242424);
                border-radius: 10px;
                border: 2px solid {COLORS['primary']};
                padding: 15px;
            }}
        """)
        total_layout = QHBoxLayout()
        total_container.setLayout(total_layout)

        total_text = QLabel("TOTAL:")
        total_text.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        total_text.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        
        self.total_display = QLabel("0.00 DA")
        self.total_display.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        self.total_display.setStyleSheet(f"color: {COLORS['success']}; border: none;")
        self.total_display.setAlignment(Qt.AlignmentFlag.AlignRight)

        total_layout.addWidget(total_text)
        total_layout.addStretch()
        total_layout.addWidget(self.total_display)

        main_layout.addWidget(total_container)

        # Boutons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        cancel_btn = QPushButton("❌ Annuler")
        cancel_btn.setStyleSheet(BUTTON_STYLES['secondary'])
        cancel_btn.setMinimumHeight(50)
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        add_btn = QPushButton("✅ Ajouter")
        add_btn.setStyleSheet(BUTTON_STYLES['success'])
        add_btn.setMinimumHeight(50)
        add_btn.setFixedWidth(180)
        add_btn.clicked.connect(self.validate_and_accept)
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        btn_layout.addWidget(cancel_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(add_btn)
        
        main_layout.addLayout(btn_layout)

    def load_products(self):
        """Charge les produits depuis la base"""
        self.product_combo.clear()
        self.product_combo.addItem("-- Sélectionner un produit --", None)
        
        products = self.db.get_all_products()
        for product in products:
            if product['stock_quantity'] > 0:
                display_text = f"{product['name']}"
                self.product_combo.addItem(display_text, product)

    def on_product_selected(self, index):
        """Quand un produit est sélectionné"""
        product = self.product_combo.currentData()
        
        if product:
            self.selected_product = product
            self.price_display.setText(f"{product['selling_price']:,.2f} DA")
            self.stock_display.setText(str(product['stock_quantity']))
            self.quantity.setMaximum(product['stock_quantity'])
            self.update_total()
        else:
            self.selected_product = None
            self.price_display.setText("0.00 DA")
            self.stock_display.setText("0")

    def update_total(self):
        """Met à jour le total"""
        if self.selected_product:
            qty = self.quantity.value()
            price = self.selected_product['selling_price']
            discount = self.discount.value()
            
            total = qty * price * (1 - discount / 100)
            self.total_display.setText(f"{total:,.2f} DA")

    def validate_and_accept(self):
        """Valide et accepte"""
        if not self.selected_product:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un produit!")
            return
        
        if self.quantity.value() > self.selected_product['stock_quantity']:
            QMessageBox.warning(self, "Erreur", "Stock insuffisant!")
            return
        
        self.accept()


class SalesPage(QWidget):
    def __init__(self):
        super().__init__()
        
        self.db = get_database()
        self.cart_items = []  # Articles dans le panier
        
        # Layout racine sans marges
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ScrollArea pour éviter l'écrasement du résumé
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        scroll_container = QWidget()
        scroll_container.setStyleSheet("background: transparent;")

        layout = QVBoxLayout(scroll_container)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        scroll.setWidget(scroll_container)
        root_layout.addWidget(scroll)

        # Header
        title = QLabel("💰 Point de Vente")
        title.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']}; margin-bottom: 5px;")
        layout.addWidget(title)

        subtitle = QLabel("Gestion des ventes et facturation")
        subtitle.setFont(QFont("Segoe UI", 14))
        subtitle.setStyleSheet(f"color: {COLORS['text_tertiary']}; margin-bottom: 15px;")
        layout.addWidget(subtitle)

        # Client Selection
        client_card = QFrame()
        client_card.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {COLORS['bg_card']}, stop:1 #242424);
                border-radius: 12px;
                border: 1px solid {COLORS['border']};
                padding: 20px;
            }}
        """)
        client_layout = QHBoxLayout()
        client_card.setLayout(client_layout)
        client_layout.setSpacing(15)

        client_label = QLabel("👤 Client:")
        client_label.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        client_label.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")

        self.client_combo = QComboBox()
        self.client_combo.setStyleSheet(INPUT_STYLE)
        self.client_combo.setMinimumHeight(45)
        self.client_combo.setMinimumWidth(300)
        self.load_clients()
        self.client_combo.currentIndexChanged.connect(lambda _: self.update_totals())

        # Bouton ajouter article
        self.add_item_btn = QPushButton("➕ Ajouter Article")
        self.add_item_btn.setStyleSheet(BUTTON_STYLES['primary'])
        self.add_item_btn.setMinimumHeight(45)
        self.add_item_btn.setFixedWidth(180)
        self.add_item_btn.clicked.connect(self.add_item)
        self.add_item_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        client_layout.addWidget(client_label)
        client_layout.addWidget(self.client_combo)
        client_layout.addStretch()
        client_layout.addWidget(self.add_item_btn)

        layout.addWidget(client_card)

        # Cart Table
        table_container = QFrame()
        table_container.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_card']};
                border-radius: 12px;
                border: 1px solid {COLORS['border']};
                padding: 0px;
            }}
        """)
        table_layout = QVBoxLayout()
        table_layout.setContentsMargins(15, 15, 15, 15)
        table_layout.setSpacing(10)
        table_container.setLayout(table_layout)

        table_title = QLabel("🛒 Panier")
        table_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        table_title.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        table_layout.addWidget(table_title)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Produit", "Quantité", "Prix Unit.", "Remise", "Total", ""])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(1, 100)
        self.table.setColumnWidth(2, 120)
        self.table.setColumnWidth(3, 100)
        self.table.setColumnWidth(4, 120)
        self.table.setColumnWidth(5, 80)
        
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setMinimumHeight(220)
        self.table.setMaximumHeight(350)
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.table.setStyleSheet(TABLE_STYLE + f"""
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

        table_layout.addWidget(self.table)
        layout.addWidget(table_container)

        # ── Summary Section ──────────────────────────────────────────────
        summary_card = QFrame()
        summary_card.setObjectName("summaryCard")
        summary_card.setStyleSheet(f"""
            QFrame#summaryCard {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['bg_card']}, stop:1 #1a1a2e);
                border-radius: 12px;
                border: 2px solid {COLORS['success']};
            }}
        """)

        summary_main_layout = QVBoxLayout(summary_card)
        summary_main_layout.setContentsMargins(22, 16, 22, 16)
        summary_main_layout.setSpacing(10)

        # ── Ligne titre + client ──────────────────────────────────────────
        title_client_row = QHBoxLayout()

        summary_title = QLabel("💰 Résumé de la Vente")
        summary_title.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        summary_title.setStyleSheet(f"color: {COLORS['text_primary']};")
        title_client_row.addWidget(summary_title)
        title_client_row.addStretch()

        # Badge client
        client_badge_frame = QFrame()
        client_badge_frame.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['primary']}22;
                border-radius: 8px;
                border: 1px solid {COLORS['primary']};
            }}
        """)
        client_badge_layout = QHBoxLayout(client_badge_frame)
        client_badge_layout.setContentsMargins(10, 5, 10, 5)
        client_badge_layout.setSpacing(6)

        client_icon = QLabel("👤")
        client_icon.setFont(QFont("Segoe UI", 12))
        client_icon.setStyleSheet("border: none;")
        client_badge_layout.addWidget(client_icon)

        self.client_name_label = QLabel("—")
        self.client_name_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.client_name_label.setStyleSheet(f"color: {COLORS['primary']}; border: none;")
        client_badge_layout.addWidget(self.client_name_label)

        title_client_row.addWidget(client_badge_frame)
        summary_main_layout.addLayout(title_client_row)

        # ── Séparateur ────────────────────────────────────────────────────
        sep_top = QFrame()
        sep_top.setFrameShape(QFrame.Shape.HLine)
        sep_top.setFixedHeight(1)
        sep_top.setStyleSheet(f"background-color: {COLORS['border']}; border: none;")
        summary_main_layout.addWidget(sep_top)

        # ── 3 colonnes d'info ────────────────────────────────────────────
        cols_row = QHBoxLayout()
        cols_row.setSpacing(0)

        def _info_row(parent_layout, icon_text, color):
            h = QHBoxLayout()
            h.setSpacing(6)
            lbl = QLabel(icon_text)
            lbl.setFont(QFont("Segoe UI", 11))
            lbl.setStyleSheet(f"color: {COLORS['text_tertiary']}; border: none;")
            val = QLabel("—")
            val.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            val.setStyleSheet(f"color: {color}; border: none;")
            val.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            h.addWidget(lbl, 1)
            h.addWidget(val)
            parent_layout.addLayout(h)
            return val

        def _vsep():
            s = QFrame()
            s.setFrameShape(QFrame.Shape.VLine)
            s.setFixedWidth(1)
            s.setStyleSheet(f"background-color: {COLORS['border']}; border: none;")
            return s

        # -- Colonne 1 : articles & quantité --
        col1 = QVBoxLayout()
        col1.setSpacing(6)
        col1.setContentsMargins(0, 0, 16, 0)
        self.nb_articles_label    = _info_row(col1, "📦 Nombre d'articles :", COLORS['primary'])
        self.qty_total_label      = _info_row(col1, "🔢 Quantité totale :",    COLORS['primary'])
        self.discount_total_label = _info_row(col1, "🏷️  Remise totale :",     COLORS['danger'])
        cols_row.addLayout(col1, 1)
        cols_row.addWidget(_vsep())

        # -- Colonne 2 : montants --
        col2 = QVBoxLayout()
        col2.setSpacing(6)
        col2.setContentsMargins(16, 0, 16, 0)
        self.subtotal_label = _info_row(col2, "📊 Sous-total HT :", COLORS['text_primary'])
        self.tax_label      = _info_row(col2, "💹 TVA (19%) :",      COLORS.get('warning', '#F59E0B'))
        cols_row.addLayout(col2, 1)
        cols_row.addWidget(_vsep())

        # -- Colonne 3 : paiement --
        col3 = QVBoxLayout()
        col3.setSpacing(6)
        col3.setContentsMargins(16, 0, 0, 0)

        pay_lbl_top = QLabel("💳 Mode de paiement :")
        pay_lbl_top.setFont(QFont("Segoe UI", 11))
        pay_lbl_top.setStyleSheet(f"color: {COLORS['text_tertiary']}; border: none;")
        col3.addWidget(pay_lbl_top)

        self.payment_combo = QComboBox()
        self.payment_combo.addItems(["💵 Espèces", "💳 Carte bancaire", "🏦 Virement", "📱 Mobile", "📝 Chèque", "🔄 Crédit"])
        self.payment_combo.setStyleSheet(INPUT_STYLE)
        self.payment_combo.setMinimumHeight(36)
        col3.addWidget(self.payment_combo)
        col3.addStretch()

        cols_row.addLayout(col3, 1)
        summary_main_layout.addLayout(cols_row)

        # ── Séparateur vert ───────────────────────────────────────────────
        h_sep = QFrame()
        h_sep.setFrameShape(QFrame.Shape.HLine)
        h_sep.setFixedHeight(2)
        h_sep.setStyleSheet(f"background-color: {COLORS['success']}; border: none;")
        summary_main_layout.addWidget(h_sep)

        # ── TOTAL TTC + boutons ───────────────────────────────────────────
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(12)

        self.clear_btn = QPushButton("🗑️ Vider le Panier")
        self.clear_btn.setStyleSheet(BUTTON_STYLES['secondary'])
        self.clear_btn.setMinimumHeight(46)
        self.clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clear_btn.clicked.connect(self.clear_cart)
        bottom_row.addWidget(self.clear_btn)

        bottom_row.addStretch()

        total_lbl = QLabel("TOTAL TTC :")
        total_lbl.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        total_lbl.setStyleSheet(f"color: {COLORS['text_primary']};")
        total_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        bottom_row.addWidget(total_lbl)

        self.total_label = QLabel("0.00 DA")
        self.total_label.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
        self.total_label.setStyleSheet(f"color: {COLORS['success']};")
        self.total_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.total_label.setMinimumWidth(200)
        bottom_row.addWidget(self.total_label)

        self.save_btn = QPushButton("💾 Enregistrer la Vente")
        self.save_btn.setStyleSheet(BUTTON_STYLES['success'])
        self.save_btn.setMinimumHeight(46)
        self.save_btn.setMinimumWidth(220)
        self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_btn.clicked.connect(self.save_sale)
        bottom_row.addWidget(self.save_btn)

        summary_main_layout.addLayout(bottom_row)

        layout.addWidget(summary_card)

        # Initialiser l'affichage
        self.update_totals()


    def load_clients(self):
        """Charge les clients (peut être appelée depuis l'extérieur pour rafraîchir)"""
        self.client_combo.clear()
        self.client_combo.addItem("Client Anonyme", None)
        
        clients = self.db.get_all_clients()
        for client in clients:
            self.client_combo.addItem(client['name'], client['id'])

    def add_item(self):
        """Ajoute un article au panier"""
        dialog = AddProductDialog()
        if dialog.exec() and dialog.selected_product:
            product = dialog.selected_product
            quantity = dialog.quantity.value()
            discount = dialog.discount.value()
            unit_price = product['selling_price']
            total = quantity * unit_price * (1 - discount / 100)
            
            # Ajouter au panier
            self.cart_items.append({
                'product_id': product['id'],
                'product_name': product['name'],
                'quantity': quantity,
                'unit_price': unit_price,
                'discount': discount,
                'total': total
            })
            
            # Ajouter à la table
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # Produit
            product_item = QTableWidgetItem(product['name'])
            self.table.setItem(row, 0, product_item)
            
            # Quantité
            qty_item = QTableWidgetItem(str(quantity))
            qty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 1, qty_item)
            
            # Prix unitaire
            price_item = QTableWidgetItem(f"{unit_price:,.2f}")
            price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.table.setItem(row, 2, price_item)
            
            # Remise
            discount_item = QTableWidgetItem(f"{discount:.2f}%")
            discount_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 3, discount_item)
            
            # Total
            total_item = QTableWidgetItem(f"{total:,.2f}")
            total_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            total_item.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            self.table.setItem(row, 4, total_item)
            
            # Bouton supprimer
            remove_btn = QPushButton("🗑️")
            remove_btn.setFont(QFont("Segoe UI", 14))
            remove_btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    color: {COLORS['danger']};
                    border: none;
                }}
                QPushButton:hover {{
                    background: {COLORS['danger']};
                    color: white;
                    border-radius: 5px;
                }}
            """)
            remove_btn.clicked.connect(lambda _, r=row: self.remove_item(r))
            remove_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.table.setCellWidget(row, 5, remove_btn)
            
            self.update_totals()

    def remove_item(self, row):
        """Supprime un article"""
        if row < len(self.cart_items):
            del self.cart_items[row]
        self.table.removeRow(row)
        self.update_totals()

    def clear_cart(self):
        """Vide le panier"""
        reply = QMessageBox.question(
            self,
            "Confirmation",
            "Voulez-vous vraiment vider le panier?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.cart_items = []
            self.table.setRowCount(0)
            self.update_totals()

    def update_totals(self):
        """Met à jour les totaux et le nom du client"""
        subtotal = sum(item['total'] for item in self.cart_items)
        tax = subtotal * 0.19  # TVA 19%
        total = subtotal + tax

        nb_articles = len(self.cart_items)
        qty_total = sum(item['quantity'] for item in self.cart_items)

        total_sans_remise = sum(
            item['quantity'] * item['unit_price'] for item in self.cart_items
        )
        remise_total = total_sans_remise - subtotal

        self.nb_articles_label.setText(f"{nb_articles} article(s)")
        self.qty_total_label.setText(f"{qty_total} unité(s)")
        self.discount_total_label.setText(f"-{remise_total:,.2f} DA")
        self.subtotal_label.setText(f"{subtotal:,.2f} DA")
        self.tax_label.setText(f"{tax:,.2f} DA")
        self.total_label.setText(f"{total:,.2f} DA")

        # Mettre à jour le nom du client
        client_name = self.client_combo.currentText() or "Client Anonyme"
        self.client_name_label.setText(client_name)

    def save_sale(self):
        """Enregistre la vente avec gestion du paiement"""
        if not self.cart_items:
            QMessageBox.warning(self, "Attention", "Le panier est vide!")
            return
        
        # Calculer le total TTC
        subtotal = sum(item['total'] for item in self.cart_items)
        tax = subtotal * 0.19
        total_ttc = subtotal + tax
        
        # Générer un numéro de facture
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        invoice_number = f"FAC-{timestamp}"
        
        # 1. Afficher le dialogue de paiement
        payment_data = show_payment_dialog(
            total_amount=total_ttc,
            invoice_number=invoice_number,
            parent=self
        )
        
        # Si l'utilisateur a annulé le paiement
        if not payment_data:
            QMessageBox.information(
                self,
                "Paiement annulé",
                "La vente n'a pas été enregistrée."
            )
            return
        
        # 2. Si le paiement est validé, enregistrer la vente
        client_id = self.client_combo.currentData()
        
        # Préparer les articles
        items = []
        for item in self.cart_items:
            items.append({
                'product_id': item['product_id'],
                'quantity': item['quantity'],
                'unit_price': item['unit_price'],
                'discount': item['discount']
            })
        
        # Utiliser la méthode de paiement du dialogue
        payment_method = payment_data['method']
        
        # Enregistrer dans la base
        sale_id = self.db.create_sale(
            invoice_number=invoice_number,
            client_id=client_id,
            items=items,
            payment_method=payment_method,
            tax_rate=19.0,
            discount=0
        )
        
        if sale_id:
            # Afficher les détails du paiement dans le message
            payment_details = self.format_payment_details(payment_data)
            
            QMessageBox.information(
                self,
                "Succès",
                f"✅ Vente enregistrée avec succès!\n\n"
                f"📄 Facture N° {invoice_number}\n"
                f"💰 Montant: {total_ttc:,.2f} DA\n"
                f"💳 Paiement: {self.get_payment_method_name(payment_method)}\n"
                f"{payment_details}"
            )
            
            # Réinitialiser
            self.cart_items = []
            self.table.setRowCount(0)
            self.update_totals()
            self.client_combo.setCurrentIndex(0)
        else:
            QMessageBox.critical(
                self,
                "Erreur",
                "❌ Impossible d'enregistrer la vente!"
            )        

    def get_payment_method_name(self, method_code):
            """Convertit le code de paiement en nom affichable"""
            method_names = {
                'cash': '💵 Espèces',
                'card': '💳 Carte bancaire',
                'check': '📝 Chèque',
                'transfer': '🏦 Virement',
                'mobile': '📱 Mobile Money',
                'credit': '🔄 Crédit'
            }
            return method_names.get(method_code, method_code)

    def format_payment_details(self, payment_data):
            """Formate les détails du paiement pour l'affichage"""
            details = payment_data.get('details', {})
            method = payment_data['method']
            
            detail_text = ""
            
            if method == 'cash':
                if 'received' in details:
                    detail_text += f"   💵 Reçu: {details['received']:,.2f} DA\n"
                    if 'change' in details and details['change'] > 0:
                        detail_text += f"   💸 Monnaie rendue: {details['change']:,.2f} DA"
            
            elif method == 'card':
                if 'transaction' in details and details['transaction']:
                    detail_text += f"   🔢 Transaction: {details['transaction']}\n"
                if 'card_type' in details and details['card_type']:
                    detail_text += f"   💳 Carte: {details['card_type']}"
            
            elif method == 'check':
                if 'check_number' in details and details['check_number']:
                    detail_text += f"   📝 N° Chèque: {details['check_number']}\n"
                if 'bank' in details and details['bank']:
                    detail_text += f"   🏦 Banque: {details['bank']}"
            
            elif method == 'transfer':
                if 'reference' in details and details['reference']:
                    detail_text += f"   🔢 Référence: {details['reference']}"
            
            elif method == 'mobile':
                if 'operator' in details and details['operator']:
                    detail_text += f"   📱 Opérateur: {details['operator']}\n"
                if 'transaction' in details and details['transaction']:
                    detail_text += f"   🔢 Transaction: {details['transaction']}"
            
            elif method == 'credit':
                if 'due_date' in details and details['due_date']:
                    detail_text += f"   📅 Échéance: {details['due_date']}\n"
                detail_text += "   ⚠️ Paiement à crédit"
            
            if detail_text:
                return f"\n📋 Détails du paiement:\n{detail_text}"
            return ""