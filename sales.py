

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QComboBox, QHBoxLayout, QFrame, QDialog,
    QFormLayout, QLineEdit, QSpinBox, QDoubleSpinBox, QMessageBox, QGridLayout,
    QScrollArea, QSizePolicy
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, pyqtSignal
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
        self.all_products = []
        
        self.setWindowTitle("🛒 Ajouter un Article à la Facture")
        self.setFixedWidth(700)
        self.setFixedHeight(920)
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
        main_layout.setSpacing(6)
        main_layout.setContentsMargins(12, 12, 12, 12)

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

        subtitle = QLabel("Recherchez et sélectionnez le produit souhaité")
        subtitle.setFont(QFont("Segoe UI", 11))
        subtitle.setStyleSheet("color: rgba(255, 255, 255, 0.8); border: none;")
        header_layout.addWidget(subtitle)

        main_layout.addWidget(header)

        # ScrollArea pour le contenu principal
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        scroll_widget = QWidget()
        scroll_widget.setStyleSheet("background: transparent;")
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(5)
        scroll_layout.setContentsMargins(0, 0, 0, 0)

        # Containers de recherche et tableau
        search_container = QFrame()
        search_container.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_card']};
                border-radius: 10px;
                padding: 8px;
            }}
        """)
        search_layout = QVBoxLayout()
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setSpacing(4)
        search_container.setLayout(search_layout)

        # Champ de recherche
        product_label = QLabel("🔍 Rechercher un produit: *")
        product_label.setStyleSheet(f"color: {COLORS['text_primary']}; border: none; font-weight: bold; font-size: 14px;")
        search_layout.addWidget(product_label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Tapez le nom du produit...")
        self.search_input.setStyleSheet(INPUT_STYLE)
        self.search_input.setMinimumHeight(32)
        self.search_input.textChanged.connect(self.filter_products)
        search_layout.addWidget(self.search_input)

        # Table des produits
        self.product_table = QTableWidget(0, 3)
        self.product_table.setHorizontalHeaderLabels(["Produit", "Prix Unit.", "Stock Disponible"])
        self.product_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.product_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.product_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.product_table.setColumnWidth(1, 120)
        self.product_table.setColumnWidth(2, 140)
        self.product_table.verticalHeader().setVisible(False)
        self.product_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.product_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.product_table.setMinimumHeight(160)
        self.product_table.setMaximumHeight(180)
        self.product_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.product_table.itemSelectionChanged.connect(self.on_product_selected_from_table)
        self.product_table.setStyleSheet(TABLE_STYLE + f"""
            QHeaderView::section {{
                background-color: {COLORS['bg_light']};
                color: {COLORS['text_primary']};
                font-size: 12px;
                font-weight: bold;
                padding: 10px 8px;
                border: none;
                border-right: 1px solid {COLORS['border']};
                border-bottom: 2px solid {COLORS['primary']};
            }}
        """)
        search_layout.addWidget(self.product_table)

        scroll_layout.addWidget(search_container)

        # Formulaire pour quantité et remise
        form_container = QFrame()
        form_container.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_card']};
                border-radius: 10px;
                padding: 10px;
            }}
        """)
        form_layout = QFormLayout()
        form_container.setLayout(form_layout)
        form_layout.setSpacing(6)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        # Prix unitaire
        price_label = QLabel("Prix unitaire:")
        price_label.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        
        self.price_display = QLabel("0 DA")
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
        
        self.quantity = QLineEdit()
        self.quantity.setText("1")
        self.quantity.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.quantity.setStyleSheet(INPUT_STYLE)
        self.quantity.setMinimumHeight(32)
        self.quantity.textChanged.connect(self.update_total)
        
        form_layout.addRow(qty_label, self.quantity)

        # Remise
        discount_label = QLabel("Remise (%)")
        discount_label.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        
        self.discount = QLineEdit()
        self.discount.setText("0")
        self.discount.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.discount.setStyleSheet(INPUT_STYLE)
        self.discount.setMinimumHeight(32)
        self.discount.textChanged.connect(self.update_total)
        
        form_layout.addRow(discount_label, self.discount)

        scroll_layout.addWidget(form_container)

        # Résumé du total
        total_container = QFrame()
        total_container.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['bg_card']}, stop:1 #242424);
                border-radius: 10px;
                border: 2px solid {COLORS['primary']};
                padding: 8px;
            }}
        """)
        total_layout = QHBoxLayout()
        total_container.setLayout(total_layout)
        total_layout.setContentsMargins(11, 10, 16, 13)

        total_text = QLabel("TOTAL:")
        total_text.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        total_text.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        
        self.total_display = QLabel("0 DA")
        self.total_display.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.total_display.setStyleSheet(f"color: {COLORS['success']}; border: none;")
        self.total_display.setMinimumWidth(150)
        self.total_display.setAlignment(Qt.AlignmentFlag.AlignRight)

        total_layout.addWidget(total_text)
        total_layout.addStretch()
        total_layout.addWidget(self.total_display)

        scroll_layout.addWidget(total_container)

        scroll.setWidget(scroll_widget)
        main_layout.addWidget(scroll)

        # Boutons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        cancel_btn = QPushButton("❌ Annuler")
        cancel_btn.setStyleSheet(BUTTON_STYLES['secondary'])
        cancel_btn.setMinimumHeight(40)
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        add_btn = QPushButton("✅ Ajouter")
        add_btn.setStyleSheet(BUTTON_STYLES['success'])
        add_btn.setMinimumHeight(40)
        add_btn.setFixedWidth(180)
        add_btn.clicked.connect(self.validate_and_accept)
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        btn_layout.addWidget(cancel_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(add_btn)
        
        main_layout.addLayout(btn_layout)

        # Charger les produits
        self.load_products()

    def load_products(self):
        """Charge les produits depuis la base"""
        self.all_products = []
        self.product_table.setRowCount(0)
        
        products = self.db.get_all_products()
        for product in products:
            if product['stock_quantity'] > 0:
                self.all_products.append(product)
        
        # Afficher tous les produits initialement
        self.display_products(self.all_products)

    def display_products(self, products):
        """Affiche les produits dans la table"""
        self.product_table.setRowCount(0)
        
        for product in products:
            row = self.product_table.rowCount()
            self.product_table.insertRow(row)
            
            # Nom du produit
            name_item = QTableWidgetItem(product['name'])
            name_item.setData(Qt.ItemDataRole.UserRole, product)
            self.product_table.setItem(row, 0, name_item)
            
            # Prix unitaire
            price_item = QTableWidgetItem(f"{fmt_da(product['selling_price'], 2)}")
            price_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.product_table.setItem(row, 1, price_item)
            
            # Stock
            stock_item = QTableWidgetItem(str(product['stock_quantity']))
            stock_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.product_table.setItem(row, 2, stock_item)

    def filter_products(self, text):
        """Filtre les produits selon le texte de recherche"""
        search_text = text.lower().strip()
        
        if not search_text:
            self.display_products(self.all_products)
        else:
            filtered = [p for p in self.all_products if search_text in p['name'].lower()]
            self.display_products(filtered)

    def on_product_selected_from_table(self):
        """Quand un produit est sélectionné dans la table"""
        selected_row = self.product_table.currentRow()
        
        if selected_row >= 0:
            item = self.product_table.item(selected_row, 0)
            if item:
                product = item.data(Qt.ItemDataRole.UserRole)
                self.selected_product = product
                self.price_display.setText(f"{fmt_da(product['selling_price'], 2)}")
                self.stock_display.setText(str(product['stock_quantity']))
                self.quantity.setText("1")
                self.discount.setText("0")
                self.update_total()
        else:
            self.selected_product = None
            self.price_display.setText("0 DA")
            self.stock_display.setText("0")

    def update_total(self):
        """Met à jour le total"""
        if self.selected_product:
            try:
                qty = int(self.quantity.text() or 1)
                price = self.selected_product['selling_price']
                discount = float(self.discount.text() or 0)
                
                total = qty * price * (1 - discount / 100)
                self.total_display.setText(f"{fmt_da(total, 2)}")
            except ValueError:
                self.total_display.setText("0 DA")

    def validate_and_accept(self):
        """Valide et accepte"""
        if not self.selected_product:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un produit!")
            return
        
        try:
            qty = int(self.quantity.text() or 1)
        except ValueError:
            QMessageBox.warning(self, "Erreur", "La quantité doit être un nombre!")
            return
        
        if qty > self.selected_product['stock_quantity']:
            QMessageBox.warning(self, "Erreur", "Stock insuffisant!")
            return
        
        self.accept()


class SalesPage(QWidget):
    # Émis après chaque vente enregistrée
    sale_saved = pyqtSignal()

    def __init__(self):
        super().__init__()
        # self.showEvent = self.refresh  # Rafraîchir à chaque affichage
        self.db = get_database()
        self.cart_items = []  # Articles dans le panier
        self.vat_rate = self._get_vat_rate()  # Récupérer la TVA depuis les settings
        
        # Layout racine sans marges
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(12, 12, 12, 12)
        root_layout.setSpacing(8)

        layout = root_layout

        # Header
        title = QLabel("💰 Point de Vente")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']};")
        layout.addWidget(title)

        subtitle = QLabel("Gestion des ventes et facturation")
        subtitle.setFont(QFont("Segoe UI", 11))
        subtitle.setStyleSheet(f"color: {COLORS['text_tertiary']};")
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
        client_layout.setSpacing(10)

        client_label = QLabel("👤 Client:")
        client_label.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        client_label.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")

        self.client_combo = QComboBox()
        self.client_combo.setStyleSheet(INPUT_STYLE)
        self.client_combo.setMinimumHeight(32)
        self.client_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.load_clients()

        # Bouton ajouter article
        self.add_item_btn = QPushButton("➕ Ajouter Article")
        self.add_item_btn.setStyleSheet(BUTTON_STYLES['primary'])
        self.add_item_btn.setMinimumHeight(32)
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
        table_layout.setContentsMargins(10, 10, 10, 10)
        table_layout.setSpacing(8)
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
        self.table.setMinimumHeight(80)
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
                    stop:0 {COLORS['bg_card']}, stop:1 #242424);
                border-radius: 12px;
                border: 2px solid {COLORS['success']};
            }}
        """)

        # summary_card.setMinimumHeight(260)
        summary_main_layout = QVBoxLayout(summary_card)
        summary_main_layout.setContentsMargins(16, 12, 16, 12)
        summary_main_layout.setSpacing(8)

        # ── Ligne titre + client ──────────────────────────────────────────
        title_client_row = QHBoxLayout()

        # Titre
        summary_title = QLabel("💰 Résumé de la Vente")
        summary_title.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        summary_title.setStyleSheet(f"color: {COLORS['text_primary']};")
        # summary_main_layout.addWidget(summary_title)
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

        # ── Grille principale en 2 colonnes ──────────────────────────────
        info_row = QHBoxLayout()
        info_row.setSpacing(25)

        # helper pour créer une ligne label + valeur
        def _row(parent_layout, icon_text, color):
            h = QHBoxLayout()
            h.setSpacing(8)
            lbl = QLabel(icon_text)
            lbl.setFont(QFont("Segoe UI", 12))
            lbl.setStyleSheet(f"color: {COLORS['text_tertiary']};")
            val = QLabel("—")
            val.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
            val.setStyleSheet(f"color: {color};")
            val.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            val.setMinimumWidth(120)
            h.addWidget(lbl, 1)
            h.addWidget(val)
            parent_layout.addLayout(h)
            return val

        # Colonne gauche
        left_col = QVBoxLayout()
        left_col.setSpacing(4)
        self.nb_articles_label   = _row(left_col, "📦 Articles :", COLORS['primary'])
        self.qty_total_label     = _row(left_col, "🔢 Quantité :",   COLORS['primary'])
        self.discount_total_label= _row(left_col, "🏷️  Remise :",    COLORS['danger'])

        # Colonne droite
        right_col = QVBoxLayout()
        right_col.setSpacing(4)
        self.subtotal_label = _row(right_col, "Sous-total HT :", COLORS['text_primary'])
        
        # Créer la ligne TVA de manière dynamique pour pouvoir la mettre à jour
        self.vat_percent = float(self.db.get_setting('vat', '19'))
        tax_row = QHBoxLayout()
        tax_row.setSpacing(8)
        self.tax_header_label = QLabel(f"TVA ({self.vat_percent:.0f}%) :")
        self.tax_header_label.setFont(QFont("Segoe UI", 12))
        self.tax_header_label.setStyleSheet(f"color: {COLORS['text_tertiary']};")
        self.tax_label = QLabel("—")
        self.tax_label.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        self.tax_label.setStyleSheet(f"color: {COLORS['warning']};")
        self.tax_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.tax_label.setMinimumWidth(120)
        tax_row.addWidget(self.tax_header_label, 1)
        tax_row.addWidget(self.tax_label)
        right_col.addLayout(tax_row)

        info_row.addLayout(left_col, 1)

        v_sep = QFrame()
        v_sep.setFrameShape(QFrame.Shape.VLine)
        v_sep.setFixedWidth(1)
        v_sep.setStyleSheet(f"background-color: {COLORS['border']};")
        info_row.addWidget(v_sep)

        info_row.addLayout(right_col, 1)
        summary_main_layout.addLayout(info_row)

        # ── Séparateur vert ──────────────────────────────────────────────
        h_sep = QFrame()
        h_sep.setFrameShape(QFrame.Shape.HLine)
        h_sep.setFixedHeight(1)
        h_sep.setStyleSheet(f"background-color: {COLORS['success']};")
        summary_main_layout.addWidget(h_sep)

        # ── TOTAL TTC ────────────────────────────────────────────────────
        total_row = QHBoxLayout()
        total_lbl = QLabel("TOTAL TTC :")
        total_lbl.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        total_lbl.setStyleSheet(f"color: {COLORS['text_primary']};")
        self.total_label = QLabel("0 DA")
        self.total_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        self.total_label.setStyleSheet(f"color: {COLORS['success']};")
        self.total_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        total_row.addWidget(total_lbl)
        total_row.addStretch()
        total_row.addWidget(self.total_label)
        summary_main_layout.addLayout(total_row)

        # ── Boutons ──────────────────────────────────────────────────────
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.clear_btn = QPushButton("🗑️ Vider le Panier")
        self.clear_btn.setStyleSheet(BUTTON_STYLES['secondary'])
        self.clear_btn.setMinimumHeight(40)
        self.clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clear_btn.clicked.connect(self.clear_cart)

        self.save_btn = QPushButton("💾 Enregistrer la Vente")
        self.save_btn.setStyleSheet(BUTTON_STYLES['success'])
        self.save_btn.setMinimumHeight(40)
        self.save_btn.setMinimumWidth(220)
        self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_btn.clicked.connect(self.save_sale)

        button_layout.addWidget(self.clear_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.save_btn)
        summary_main_layout.addLayout(button_layout)

        layout.addWidget(summary_card)

        # Initialiser l'affichage
        self.update_totals()
        self.showEvent = self.refresh_page()  # Rafraîchir à chaque affichage
    
    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_page()
        
        
    def refresh_page(self):
        """Rafraîchit les données de la page (clients, produits, etc.)"""
        self.load_clients()
        self.cart_items = []
        self.table.setRowCount(0)
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
            quantity = int(dialog.quantity.text() or 1)
            discount = float(dialog.discount.text() or 0)
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
            price_item = QTableWidgetItem(f"{unit_price:,}")
            price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.table.setItem(row, 2, price_item)
            
            # Remise
            discount_item = QTableWidgetItem(f"{discount:,}%")
            discount_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 3, discount_item)
            
            # Total
            total_item = QTableWidgetItem(f"{total:,}")
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

    def _get_vat_rate(self):
        """Récupère le taux de TVA depuis les settings"""
        try:
            vat_str = self.db.get_setting('vat', '19')
            return float(vat_str) / 100.0  # Convertir en décimal (ex: 19 -> 0.19)
        except:
            return 0.19  # Valeur par défaut

    def update_totals(self):
        """Met à jour les totaux"""
        subtotal = sum(item['total'] for item in self.cart_items)
        self.vat_rate = self._get_vat_rate()
        self.vat_percent = self.vat_rate * 100  # Convertir en pourcentage pour l'affichage
        # Mettre à jour le label de TVA avec le nouveau pourcentage
        self.tax_header_label.setText(f"TVA ({self.vat_percent:}%) :")
        tax = subtotal * self.vat_rate
        total = subtotal + tax

        # Calcul du nombre d'articles et de la quantité totale
        nb_articles = len(self.cart_items)
        qty_total = sum(item['quantity'] for item in self.cart_items)

        # Calcul de la remise totale (prix sans remise - prix avec remise)
        total_sans_remise = sum(
            item['quantity'] * item['unit_price'] for item in self.cart_items
        )
        remise_total = total_sans_remise - subtotal

        self.nb_articles_label.setText(f"{nb_articles} article(s)")
        self.qty_total_label.setText(f"{qty_total} unité(s)")
        self.discount_total_label.setText(f"-{fmt_da(remise_total, 2)}")
        self.subtotal_label.setText(f"{fmt_da(subtotal, 2)}")
        self.tax_label.setText(f"{fmt_da(tax, 2)}")
        self.total_label.setText(f"{fmt_da(total, 2)}")

    def save_sale(self):
        """Enregistre la vente avec gestion du paiement"""
        if not self.cart_items:
            QMessageBox.warning(self, "Attention", "Le panier est vide!")
            return
        
        # Calculer le total TTC
        subtotal = sum(item['total'] for item in self.cart_items)
        self.vat_rate = self._get_vat_rate()
        tax = subtotal * self.vat_rate
        total_ttc = subtotal + tax
        
        # Générer un numéro de facture séquentiel (FAC-1000, FAC-1001, etc.)
        invoice_number = self.db.generate_invoice_number()
        
        # 1. Afficher le dialogue de paiement avec tous les détails
        client_name = self.client_combo.currentText() or "Client Anonyme"
        payment_data = show_payment_dialog(
            total_amount=total_ttc,
            invoice_number=invoice_number,
            cart_items=self.cart_items,
            client_name=client_name,
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
        # La TVA sera récupérée automatiquement depuis les settings
        sale_id = self.db.create_sale(
            invoice_number=invoice_number,
            client_id=client_id,
            items=items,
            payment_method=payment_method,
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
                f"💰 Montant: {fmt_da(total_ttc, 0)}\n"
                f"💳 Paiement: {self.get_payment_method_name(payment_method)}\n"
                f"{payment_details}"
            )
            
            # Notifier les autres pages (dashboard, historique, stats)
            self.sale_saved.emit()

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
                    detail_text += f"   💵 Reçu: {fmt_da(details['received'], 0)}\n"
                    if 'change' in details and details['change'] > 0:
                        detail_text += f"   💸 Monnaie rendue: {fmt_da(details['change'], 0)}"
            
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
from currency import fmt_da, fmt, currency_manager