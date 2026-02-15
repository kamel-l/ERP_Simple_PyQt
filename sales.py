from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QComboBox, QHBoxLayout, QFrame, QDialog,
    QFormLayout, QLineEdit, QSpinBox, QDoubleSpinBox, QMessageBox
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from styles import COLORS, BUTTON_STYLES, INPUT_STYLE, TABLE_STYLE


class AddProductDialog(QDialog):
    """Dialogue pour ajouter un produit à la facture"""
    def __init__(self, available_products=None):
        super().__init__()
        
        self.available_products = available_products or []
        
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
        
        # Remplir la combo avec les produits
        self.product_combo.addItem("-- Sélectionner un produit --", None)
        for product in self.available_products:
            display_text = f"{product['name']} - {product['price']:,.2f} DA (Stock: {product['quantity']})"
            self.product_combo.addItem(display_text, product)
        
        self.product_combo.currentIndexChanged.connect(self.on_product_selected)
        form_layout.addRow(product_label, self.product_combo)

        # Référence (affichage seulement)
        ref_label = QLabel("Référence:")
        ref_label.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        
        self.reference_display = QLabel("-")
        self.reference_display.setStyleSheet(f"""
            color: {COLORS['text_tertiary']}; 
            border: none;
            font-size: 14px;
            padding: 10px;
            background: {COLORS['bg_light']};
            border-radius: 5px;
        """)
        form_layout.addRow(ref_label, self.reference_display)

        # Prix unitaire (affichage seulement)
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

        # Stock disponible (affichage)
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

        # Remise (optionnel)
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

        # Note
        note = QLabel("* Champs obligatoires")
        note.setFont(QFont("Segoe UI", 10))
        note.setStyleSheet(f"color: {COLORS['text_tertiary']};")
        main_layout.addWidget(note)

        # Boutons d'action
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        cancel_btn = QPushButton("❌ Annuler")
        cancel_btn.setStyleSheet(BUTTON_STYLES['secondary'])
        cancel_btn.setMinimumHeight(50)
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        add_btn = QPushButton("➕ Ajouter à la Facture")
        add_btn.setStyleSheet(BUTTON_STYLES['success'])
        add_btn.setMinimumHeight(50)
        add_btn.setFixedWidth(220)
        add_btn.clicked.connect(self.validate_and_accept)
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        btn_layout.addWidget(cancel_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(add_btn)
        
        main_layout.addLayout(btn_layout)

    def on_product_selected(self, index):
        """Met à jour l'affichage quand un produit est sélectionné"""
        product = self.product_combo.currentData()
        
        if product:
            # Afficher les informations du produit
            self.reference_display.setText(product.get('reference', '-'))
            self.price_display.setText(f"{product['price']:,.2f} DA")
            self.stock_display.setText(str(product['quantity']))
            
            # Limiter la quantité au stock disponible
            self.quantity.setMaximum(product['quantity'])
            
            # Colorer le stock en rouge si faible
            if product['quantity'] < 10:
                self.stock_display.setStyleSheet(f"""
                    color: {COLORS['danger']}; 
                    border: none;
                    font-size: 16px;
                    font-weight: bold;
                    padding: 10px;
                    background: {COLORS['bg_light']};
                    border-radius: 5px;
                """)
            else:
                self.stock_display.setStyleSheet(f"""
                    color: {COLORS['success']}; 
                    border: none;
                    font-size: 16px;
                    font-weight: bold;
                    padding: 10px;
                    background: {COLORS['bg_light']};
                    border-radius: 5px;
                """)
            
            # Mettre à jour le total
            self.update_total()
        else:
            # Réinitialiser l'affichage
            self.reference_display.setText("-")
            self.price_display.setText("0.00 DA")
            self.stock_display.setText("0")
            self.quantity.setMaximum(9999)
            self.total_display.setText("0.00 DA")

    def update_total(self):
        """Calcule et affiche le total"""
        product = self.product_combo.currentData()
        
        if product:
            qty = self.quantity.value()
            price = product['price']
            discount = self.discount.value()
            
            subtotal = qty * price
            discount_amount = subtotal * (discount / 100)
            total = subtotal - discount_amount
            
            self.total_display.setText(f"{total:,.2f} DA")
        else:
            self.total_display.setText("0.00 DA")

    def validate_and_accept(self):
        """Valide les données avant d'accepter"""
        product = self.product_combo.currentData()
        
        if not product:
            QMessageBox.warning(self, "Sélection requise", 
                              "Veuillez sélectionner un produit !")
            self.product_combo.setFocus()
            return
        
        qty = self.quantity.value()
        if qty > product['quantity']:
            QMessageBox.warning(self, "Stock insuffisant", 
                              f"Stock disponible: {product['quantity']}\n"
                              f"Quantité demandée: {qty}")
            self.quantity.setFocus()
            return
        
        if qty <= 0:
            QMessageBox.warning(self, "Quantité invalide", 
                              "La quantité doit être supérieure à 0 !")
            self.quantity.setFocus()
            return

        self.accept()

    def get_item_data(self):
        """Retourne les données de l'article"""
        product = self.product_combo.currentData()
        qty = self.quantity.value()
        discount = self.discount.value()
        
        price = product['price']
        subtotal = qty * price
        discount_amount = subtotal * (discount / 100)
        total = subtotal - discount_amount
        
        return {
            "product_id": product['id'],
            "product_name": product['name'],
            "reference": product.get('reference', ''),
            "quantity": qty,
            "price": price,
            "discount": discount,
            "total": total
        }


class SalesPage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # ------------------- HEADER -------------------
        title = QLabel("💰 Point de Vente")
        title.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']}; margin-bottom: 5px;")
        layout.addWidget(title)

        subtitle = QLabel("Créez et gérez vos factures de vente")
        subtitle.setFont(QFont("Segoe UI", 14))
        subtitle.setStyleSheet(f"color: {COLORS['text_tertiary']}; margin-bottom: 15px;")
        layout.addWidget(subtitle)

        # ------------------- CUSTOMER SELECTION CARD -------------------
        customer_card = QFrame()
        customer_card.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {COLORS['bg_card']}, stop:1 #242424);
                border-radius: 12px;
                border: 1px solid {COLORS['border']};
                padding: 20px;
            }}
        """)
        customer_layout = QHBoxLayout()
        customer_card.setLayout(customer_layout)
        customer_layout.setSpacing(15)

        cust_label = QLabel("👤 Client:")
        cust_label.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        cust_label.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        
        self.customer_combo = QComboBox()
        self.customer_combo.addItems([
            "Sélectionner un client", 
            "John Doe", 
            "Alice Smith", 
            "Entreprise X",
            "Bob Martin",
            "Client Comptant"
        ])
        self.customer_combo.setStyleSheet(INPUT_STYLE)
        self.customer_combo.setMinimumHeight(45)
        self.customer_combo.setMinimumWidth(300)

        # Bouton ajouter article
        self.add_item_btn = QPushButton("➕ Ajouter Article")
        self.add_item_btn.setStyleSheet(BUTTON_STYLES['primary'])
        self.add_item_btn.setMinimumHeight(45)
        self.add_item_btn.setFixedWidth(180)
        self.add_item_btn.clicked.connect(self.add_item)
        self.add_item_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        customer_layout.addWidget(cust_label)
        customer_layout.addWidget(self.customer_combo)
        customer_layout.addStretch()
        customer_layout.addWidget(self.add_item_btn)

        layout.addWidget(customer_card)

        # ------------------- INVOICE TABLE -------------------
        table_container = QFrame()
        table_container.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_card']};
                border-radius: 12px;
                border: 1px solid {COLORS['border']};
                padding: 15px;
            }}
        """)
        table_layout = QVBoxLayout()
        table_container.setLayout(table_layout)

        table_title = QLabel("📋 Articles de la Facture")
        table_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        table_title.setStyleSheet(f"color: {COLORS['text_primary']}; border: none; margin-bottom: 10px;")
        table_layout.addWidget(table_title)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels([
            "Produit", "Référence", "Quantité", "Prix Unit.", "Remise", "Total"
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet(TABLE_STYLE)
        self.table.verticalHeader().setVisible(False)
        self.table.setMinimumHeight(300)

        table_layout.addWidget(self.table)
        
        # Boutons d'action sur le tableau
        table_actions = QHBoxLayout()
        
        remove_btn = QPushButton("🗑️ Supprimer la ligne")
        remove_btn.setStyleSheet(BUTTON_STYLES['danger'])
        remove_btn.setMinimumHeight(40)
        remove_btn.clicked.connect(self.remove_selected_item)
        remove_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        clear_btn = QPushButton("🧹 Vider la facture")
        clear_btn.setStyleSheet(BUTTON_STYLES['secondary'])
        clear_btn.setMinimumHeight(40)
        clear_btn.clicked.connect(self.clear_invoice)
        clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        table_actions.addStretch()
        table_actions.addWidget(clear_btn)
        table_actions.addWidget(remove_btn)
        
        table_layout.addLayout(table_actions)
        
        layout.addWidget(table_container)

        # ------------------- SUMMARY CARD -------------------
        summary_card = QFrame()
        summary_card.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['bg_card']}, stop:1 #242424);
                border-radius: 12px;
                border: 2px solid {COLORS['primary']};
                padding: 20px;
            }}
        """)
        summary_layout = QHBoxLayout()
        summary_card.setLayout(summary_layout)
        summary_layout.setSpacing(30)

        # Informations à gauche
        info_layout = QVBoxLayout()
        info_layout.setSpacing(8)
        
        self.items_count_label = QLabel("Articles: 0")
        self.items_count_label.setFont(QFont("Segoe UI", 12))
        self.items_count_label.setStyleSheet(f"color: {COLORS['text_tertiary']}; border: none;")
        
        date_label = QLabel("📅 Date: 14/02/2026")
        date_label.setFont(QFont("Segoe UI", 12))
        date_label.setStyleSheet(f"color: {COLORS['text_tertiary']}; border: none;")
        
        info_layout.addWidget(self.items_count_label)
        info_layout.addWidget(date_label)
        summary_layout.addLayout(info_layout)

        summary_layout.addStretch()

        # Total à droite
        total_container = QVBoxLayout()
        total_container.setSpacing(5)
        
        total_title = QLabel("TOTAL À PAYER")
        total_title.setFont(QFont("Segoe UI", 12))
        total_title.setStyleSheet(f"color: {COLORS['text_tertiary']}; border: none;")
        total_title.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        self.total_label = QLabel("0.00 DA")
        self.total_label.setFont(QFont("Segoe UI", 32, QFont.Weight.Bold))
        self.total_label.setStyleSheet(f"color: {COLORS['success']}; border: none;")
        self.total_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        total_container.addWidget(total_title)
        total_container.addWidget(self.total_label)
        
        summary_layout.addLayout(total_container)

        # Bouton sauvegarder
        self.save_btn = QPushButton("💾 Enregistrer\nFacture")
        self.save_btn.setStyleSheet(BUTTON_STYLES['success'])
        self.save_btn.setFixedSize(150, 80)
        self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_btn.clicked.connect(self.save_invoice)
        summary_layout.addWidget(self.save_btn)

        layout.addWidget(summary_card)

        # ------------------- PRODUITS DISPONIBLES (Données exemple) -------------------
        self.available_products = [
            {"id": 1, "name": "Ordinateur Portable HP", "reference": "HP-001", "quantity": 15, "price": 75000.00},
            {"id": 2, "name": "Souris Sans Fil Logitech", "reference": "LOG-MS-100", "quantity": 50, "price": 1500.00},
            {"id": 3, "name": "Clavier Mécanique RGB", "reference": "KB-RGB-001", "quantity": 30, "price": 5000.00},
            {"id": 4, "name": "Écran Dell 24 pouces", "reference": "DELL-002", "quantity": 25, "price": 35000.00},
            {"id": 5, "name": "Webcam HD Logitech", "reference": "CAM-001", "quantity": 8, "price": 8000.00},
            {"id": 6, "name": "Casque Audio Gaming", "reference": "AUDIO-001", "quantity": 20, "price": 6500.00},
            {"id": 7, "name": "Tapis de Souris XXL", "reference": "PAD-001", "quantity": 45, "price": 2000.00},
            {"id": 8, "name": "Hub USB 3.0", "reference": "USB-HUB-001", "quantity": 35, "price": 3500.00},
        ]

    # ------------------ AJOUTER ARTICLE ------------------
    def add_item(self):
        """Ouvre le dialogue pour ajouter un article"""
        dialog = AddProductDialog(self.available_products)
        
        if dialog.exec():
            item_data = dialog.get_item_data()
            
            # Ajouter l'article au tableau
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # Produit
            product_item = QTableWidgetItem(item_data['product_name'])
            self.table.setItem(row, 0, product_item)
            
            # Référence
            ref_item = QTableWidgetItem(item_data['reference'])
            self.table.setItem(row, 1, ref_item)
            
            # Quantité
            qty_item = QTableWidgetItem(str(item_data['quantity']))
            qty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 2, qty_item)
            
            # Prix unitaire
            price_item = QTableWidgetItem(f"{item_data['price']:,.2f}")
            price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.table.setItem(row, 3, price_item)
            
            # Remise
            discount_item = QTableWidgetItem(f"{item_data['discount']:.1f}%")
            discount_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 4, discount_item)
            
            # Total
            total_item = QTableWidgetItem(f"{item_data['total']:,.2f}")
            total_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            total_item.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            self.table.setItem(row, 5, total_item)
            
            # Mettre à jour le total
            self.update_total()

    # ------------------ SUPPRIMER ARTICLE ------------------
    def remove_selected_item(self):
        """Supprime l'article sélectionné"""
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Aucune sélection", 
                              "Veuillez sélectionner une ligne à supprimer !")
            return
        
        # Confirmation
        product_name = self.table.item(selected, 0).text()
        reply = QMessageBox.question(
            self, 
            "Confirmation", 
            f"Supprimer '{product_name}' de la facture ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.table.removeRow(selected)
            self.update_total()

    # ------------------ VIDER FACTURE ------------------
    def clear_invoice(self):
        """Vide toute la facture"""
        if self.table.rowCount() == 0:
            return
        
        reply = QMessageBox.question(
            self, 
            "Confirmation", 
            "Voulez-vous vraiment vider toute la facture ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.table.setRowCount(0)
            self.update_total()

    # ------------------ METTRE À JOUR TOTAL ------------------
    def update_total(self):
        """Calcule et affiche le total de la facture"""
        total = 0
        items_count = self.table.rowCount()
        
        for row in range(items_count):
            try:
                total_item = self.table.item(row, 5)
                if total_item:
                    # Enlever les virgules et convertir
                    total_text = total_item.text().replace(',', '')
                    total += float(total_text)
            except:
                pass
        
        self.total_label.setText(f"{total:,.2f} DA")
        self.items_count_label.setText(f"Articles: {items_count}")

    # ------------------ SAUVEGARDER FACTURE ------------------
    def save_invoice(self):
        """Sauvegarde la facture"""
        if self.table.rowCount() == 0:
            QMessageBox.warning(self, "Facture vide", 
                              "Ajoutez au moins un article avant d'enregistrer !")
            return
        
        if self.customer_combo.currentIndex() == 0:
            QMessageBox.warning(self, "Client requis", 
                              "Veuillez sélectionner un client !")
            return
        
        # Ici vous pourriez sauvegarder dans la base de données
        # Pour l'instant, on affiche juste un message de confirmation
        
        customer = self.customer_combo.currentText()
        items_count = self.table.rowCount()
        total = self.total_label.text()
        
        message = f"""
        ✅ Facture enregistrée avec succès !
        
        Client: {customer}
        Nombre d'articles: {items_count}
        Total: {total}
        
        La facture a été ajoutée au système.
        """
        
        QMessageBox.information(self, "Succès", message)
        
        # Demander si on veut créer une nouvelle facture
        reply = QMessageBox.question(
            self,
            "Nouvelle facture ?",
            "Voulez-vous créer une nouvelle facture ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.table.setRowCount(0)
            self.customer_combo.setCurrentIndex(0)
            self.update_total()