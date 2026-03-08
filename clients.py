from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QHBoxLayout, QLineEdit, QDialog, QFormLayout, QFrame, QMessageBox
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, pyqtSignal
from styles import COLORS, BUTTON_STYLES, INPUT_STYLE, TABLE_STYLE
from db_manager import get_database
import re

# ------------------ DIALOG POUR AJOUTER / MODIFIER CLIENT ------------------
class ClientDialog(QDialog):
    def __init__(self, name="", phone="", email="", address="", client_id=None):
        super().__init__()

        self.client_id = client_id
        self.setWindowTitle("📝 Détails du Client") 
        self.setMinimumWidth(500)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['bg_card']};
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

        # Titre
        title_text = "Modifier le Client" if client_id else "Nouveau Client"
        title = QLabel(title_text)
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']}; margin-bottom: 10px;")
        main_layout.addWidget(title)

        # Formulaire
        form = QFormLayout()
        form.setSpacing(15)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.name_edit = QLineEdit(name)
        self.name_edit.setPlaceholderText("Entrez le nom du client")
        
        self.phone_edit = QLineEdit(phone)
        self.phone_edit.setPlaceholderText("Ex: 0555123456")
        
        self.email_edit = QLineEdit(email)
        self.email_edit.setPlaceholderText("email@exemple.com")
        
        self.address_edit = QLineEdit(address)
        self.address_edit.setPlaceholderText("Adresse du client")

        form.addRow("Nom:", self.name_edit)
        form.addRow("Téléphone:", self.phone_edit)
        form.addRow("Email:", self.email_edit)
        form.addRow("Adresse:", self.address_edit)

        main_layout.addLayout(form)

        # Boutons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        save_btn = QPushButton("💾 Enregistrer")
        save_btn.setStyleSheet(BUTTON_STYLES['success'])
        save_btn.clicked.connect(self.accept)
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        cancel_btn = QPushButton("❌ Annuler")
        cancel_btn.setStyleSheet(BUTTON_STYLES['secondary'])
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        
        main_layout.addLayout(btn_layout)

    def validate_email(self):
        email = self.email_edit.text()
        if email and not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            QMessageBox.warning(self, "Erreur", "Format d'email invalide.")
            return False
        return True
# ------------------ PAGE CLIENTS ------------------
class ClientsPage(QWidget):
    # Signal émis quand un client est ajouté ou modifié
    client_added = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        # Connexion à la base de données
        self.db = get_database()

        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # ------------------- HEADER -------------------
        title = QLabel("👥 Gestion des Clients")
        title.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']}; margin-bottom: 5px;")
        layout.addWidget(title)

        subtitle = QLabel("Gérez vos clients et leurs informations")
        subtitle.setFont(QFont("Segoe UI", 14))
        subtitle.setStyleSheet(f"color: {COLORS['text_tertiary']}; margin-bottom: 15px;")
        layout.addWidget(subtitle)

        # ------------------- STATISTICS CARDS -------------------
        self.stats_layout = QHBoxLayout()
        self.stats_layout.setSpacing(15)
        layout.addLayout(self.stats_layout)

        # Les cartes seront créées dans load_statistics()
        self.load_statistics()
        self.stats_layout.addStretch()

        # ------------------- SEARCH & ACTIONS BAR -------------------
        search_layout = QHBoxLayout()
        search_layout.setSpacing(15)
        layout.addLayout(search_layout)

        # Barre de recherche
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Rechercher par nom ou email...")
        self.search_input.setStyleSheet(INPUT_STYLE)
        self.search_input.textChanged.connect(self.filter_clients)
        self.search_input.setMinimumHeight(45)
        search_layout.addWidget(self.search_input)

        # Bouton Ajouter
        self.add_btn = QPushButton("➕ Nouveau Client")
        self.add_btn.setStyleSheet(BUTTON_STYLES['primary'])
        self.add_btn.setFixedWidth(180)
        self.add_btn.setMinimumHeight(45)
        self.add_btn.clicked.connect(self.add_client)
        self.add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        search_layout.addWidget(self.add_btn)

        # ------------------- CLIENT TABLE -------------------
        table_container = QFrame()
        table_container.setStyleSheet(f"QFrame#inv {{ background:{COLORS['BG_CARD']}; border-radius:16px; border:1px solid {COLORS['BORDER']}; }}")
        table_layout = QVBoxLayout()
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(0)
        table_container.setLayout(table_layout)
        
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["ID", "Nom", "Téléphone", "Email", "Adresse"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet(TABLE_STYLE + f"""
            QHeaderView::section {{
                background-color: {COLORS['BG_DEEP']};
                color: {COLORS['text_primary']};
                font-size: 13px;
                font-weight: bold;
                padding: 10px 8px;
                border: none;
                border-right: 1px solid {COLORS['BORDER']};
                border-bottom: 2px solid {COLORS['primary']};
            }}
            QHeaderView::section:last {{
                border-right: none;
            }}
        """)
        
        table_layout.addWidget(self.table)
        layout.addWidget(table_container)

        # ------------------- ACTIONS BUTTONS -------------------
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(10)
        layout.addLayout(actions_layout)

        self.invoice_btn = QPushButton("📄 Factures")
        self.invoice_btn.setStyleSheet(BUTTON_STYLES['primary'])
        self.invoice_btn.clicked.connect(self.show_invoices)
        self.invoice_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.invoice_btn.setMinimumHeight(40)

        self.edit_btn = QPushButton("✏️ Modifier")
        self.edit_btn.setStyleSheet(BUTTON_STYLES['secondary'])
        self.edit_btn.clicked.connect(self.edit_client)
        self.edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.edit_btn.setMinimumHeight(40)
        
        self.delete_btn = QPushButton("🗑️ Supprimer")
        self.delete_btn.setStyleSheet(BUTTON_STYLES['danger'])
        self.delete_btn.clicked.connect(self.delete_client)
        self.delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete_btn.setMinimumHeight(40)

        actions_layout.addStretch()
        actions_layout.addWidget(self.invoice_btn)
        actions_layout.addWidget(self.edit_btn)
        actions_layout.addWidget(self.delete_btn)

        # Charger les données
        self.load_clients()
        client_added = pyqtSignal()

    def build_stat_card(self, title, value, color):
        """Construit une petite carte de statistique"""
        card = QFrame()
        card.setObjectName("stat")
        card.setStyleSheet(f"""
            QFrame#stat {{
                background: {COLORS['BG_CARD']};
                border-radius: 12px;
                border: 1px solid {COLORS['BORDER']};
            }}
            QFrame#stat:hover {{
                border: 1px solid {COLORS['primary']};
            }}
        """)
        card.setFixedHeight(90)
        card.setMinimumWidth(160)

        card_layout = QVBoxLayout()
        card.setLayout(card_layout)
        card_layout.setSpacing(8)
        card_layout.setContentsMargins(16, 14, 16, 14)

        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 11))
        title_label.setStyleSheet(f"color: {COLORS['TXT_SEC']}; border: none;")
        card_layout.addWidget(title_label)

        value_label = QLabel(str(value))
        value_label.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        value_label.setStyleSheet(f"color: {color}; border: none;")
        card_layout.addWidget(value_label)

        return card

    def load_statistics(self):
        """Charge les statistiques depuis la base de données"""
        # Effacer les anciennes cartes
        while self.stats_layout.count():
            child = self.stats_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Récupérer les stats
        stats = self.db.get_statistics()
        
        # Créer les cartes
        self.stats_layout.addWidget(
            self.build_stat_card("Total Clients", stats['total_clients'], COLORS['primary'])
        )
        self.stats_layout.addWidget(
            self.build_stat_card("Clients actifs", stats['total_clients'], COLORS['success'])
        )

    # ------------------ CHARGEMENT DES DONNÉES ------------------
    def load_clients(self):
        """Charge tous les clients depuis la base de données"""
        self.table.setRowCount(0)
        clients = self.db.get_all_clients()
        
        for client in clients:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # ID
            id_item = QTableWidgetItem(str(client["id"]))
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            id_item.setData(Qt.ItemDataRole.UserRole, client["id"])  # Stocker l'ID
            
            # Nom
            name_item = QTableWidgetItem(client["name"])
            
            # Téléphone
            phone_item = QTableWidgetItem(client["phone"] or "")
            
            # Email
            email_item = QTableWidgetItem(client["email"] or "")
            
            # Adresse
            address_item = QTableWidgetItem(client["address"] or "")
            
            self.table.setItem(row, 0, id_item)
            self.table.setItem(row, 1, name_item)
            self.table.setItem(row, 2, phone_item)
            self.table.setItem(row, 3, email_item)
            self.table.setItem(row, 4, address_item)

    # ------------------ RECHERCHE ------------------
    def filter_clients(self, text):
        """Filtre les clients par nom ou email"""
        if not text:
            self.load_clients()
            return
        
        self.table.setRowCount(0)
        clients = self.db.search_clients(text)
        
        for client in clients:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            id_item = QTableWidgetItem(str(client["id"]))
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            id_item.setData(Qt.ItemDataRole.UserRole, client["id"])
            
            self.table.setItem(row, 0, id_item)
            self.table.setItem(row, 1, QTableWidgetItem(client["name"]))
            self.table.setItem(row, 2, QTableWidgetItem(client["phone"] or ""))
            self.table.setItem(row, 3, QTableWidgetItem(client["email"] or ""))
            self.table.setItem(row, 4, QTableWidgetItem(client["address"] or ""))

    # ------------------ AJOUTER CLIENT ------------------
    def add_client(self):
        """Ajoute un nouveau client"""
        dialog = ClientDialog()
        if dialog.exec():
            name = dialog.name_edit.text().strip()
            phone = dialog.phone_edit.text().strip()
            email = dialog.email_edit.text().strip()
            address = dialog.address_edit.text().strip()
            
            if not name:
                QMessageBox.warning(
                    self,
                    "Erreur",
                    "Le nom du client est obligatoire!"
                )
                return
            
            client_id = self.db.add_client(name, phone, email, address)
            
            if client_id:
                QMessageBox.information(
                    self,
                    "Succès",
                    f"Client '{name}' ajouté avec succès!"
                )
                self.load_clients()
                self.load_statistics()
                # Émettre le signal pour notifier les autres modules
                self.client_added.emit()
            else:
                QMessageBox.critical(
                    self,
                    "Erreur",
                    "Impossible d'ajouter le client!"
                )

        
    # ------------------ MODIFIER CLIENT ------------------
    def edit_client(self):
        """Modifie un client existant"""
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(
                self,
                "Attention",
                "Veuillez sélectionner un client à modifier!"
            )
            return
        
        # Récupérer l'ID du client
        client_id = self.table.item(selected, 0).data(Qt.ItemDataRole.UserRole)
        
        # Récupérer les données du client
        client = self.db.get_client_by_id(client_id)
        
        if not client:
            QMessageBox.critical(
                self,
                "Erreur",
                "Client introuvable!"
            )
            return
        
        # Ouvrir le dialogue avec les données existantes
        dialog = ClientDialog(
            name=client["name"],
            phone=client["phone"] or "",
            email=client["email"] or "",
            address=client["address"] or "",
            client_id=client_id
        )
        
        if dialog.exec():
            name = dialog.name_edit.text().strip()
            phone = dialog.phone_edit.text().strip()
            email = dialog.email_edit.text().strip()
            address = dialog.address_edit.text().strip()
            
            if not name:
                QMessageBox.warning(
                    self,
                    "Erreur",
                    "Le nom du client est obligatoire!"
                )
                return
            
            if self.db.update_client(client_id, name, phone, email, address):
                QMessageBox.information(
                    self,
                    "Succès",
                    f"Client '{name}' modifié avec succès!"
                )
                self.load_clients()
                # Émettre le signal pour notifier les autres modules
                self.client_added.emit()
            else:
                QMessageBox.critical(
                    self,
                    "Erreur",
                    "Impossible de modifier le client!"
                )

    # ------------------ SUPPRIMER CLIENT ------------------
    def delete_client(self):
        """Supprime un client"""
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(
                self,
                "Attention",
                "Veuillez sélectionner un client à supprimer!"
            )
            return
        
        # Récupérer l'ID et le nom du client
        client_id = self.table.item(selected, 0).data(Qt.ItemDataRole.UserRole)
        client_name = self.table.item(selected, 1).text()
        
        # Confirmation
        reply = QMessageBox.question(
            self,
            "Confirmation",
            f"Voulez-vous vraiment supprimer le client '{client_name}'?\n\n"
            "Cette action est irréversible!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.db.delete_client(client_id):
                QMessageBox.information(
                    self,
                    "Succès",
                    f"Client '{client_name}' supprimé avec succès!"
                )
                self.load_clients()
                self.load_statistics()
                # Émettre le signal pour notifier les autres modules
                self.client_added.emit()
            else:
                QMessageBox.critical(
                    self,
                    "Erreur",
                    "Impossible de supprimer le client!"
                )

    # ------------------ AFFICHER FACTURES ------------------
    def show_invoices(self):
        """Affiche les factures d'un client sélectionné"""
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(
                self,
                "Attention",
                "Veuillez sélectionner un client!"
            )
            return
        
        # Récupérer l'ID et le nom du client
        client_id = self.table.item(selected, 0).data(Qt.ItemDataRole.UserRole)
        client_name = self.table.item(selected, 1).text()
        
        # Récupérer les factures du client
        invoices = self.db.get_invoices_by_client(client_id)
        
        if not invoices:
            QMessageBox.information(
                self,
                "Aucune facture",
                f"Le client '{client_name}' n'a pas de factures."
            )
            return
        
        # Créer un dialogue pour afficher les factures
        dialog = QDialog(self)
        dialog.setWindowTitle(f"📄 Factures - {client_name}")
        dialog.setMinimumWidth(900)
        dialog.setMinimumHeight(500)
        dialog.setStyleSheet(f"QDialog {{ background-color: {COLORS['bg_medium']}; }}")
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Titre
        title = QLabel(f"📄 Factures de {client_name}")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']};")
        layout.addWidget(title)
        
        # Tableau des factures
        table = QTableWidget(0, 5)
        table.setHorizontalHeaderLabels(["N° Facture", "Date", "Montant Total", "Méthode de Paiement", "Statut"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setAlternatingRowColors(True)
        table.verticalHeader().setVisible(False)
        table.setStyleSheet(TABLE_STYLE + f"""
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
        
        # Ajouter les factures dans le tableau
        for invoice in invoices:
            row = table.rowCount()
            table.insertRow(row)
            
            invoice_num = QTableWidgetItem(str(invoice.get('invoice_number', 'N/A')))
            invoice_num.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            date_item = QTableWidgetItem(str(invoice.get('created_at', 'N/A')))
            date_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            amount = QTableWidgetItem(f"{invoice.get('total_amount', 0):,.2f} DA")
            amount.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            
            payment = QTableWidgetItem(str(invoice.get('payment_method', 'N/A')))
            payment.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            status = QTableWidgetItem(str(invoice.get('status', 'Complétée')))
            status.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            table.setItem(row, 0, invoice_num)
            table.setItem(row, 1, date_item)
            table.setItem(row, 2, amount)
            table.setItem(row, 3, payment)
            table.setItem(row, 4, status)
        
        layout.addWidget(table)
        
        # Boutons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        details_btn = QPushButton("📋 Voir les détails")
        details_btn.setStyleSheet(BUTTON_STYLES['primary'])
        details_btn.setMinimumHeight(40)
        details_btn.clicked.connect(lambda: self.show_invoice_details(table, invoices))
        
        close_btn = QPushButton("✕ Fermer")
        close_btn.setStyleSheet(BUTTON_STYLES['secondary'])
        close_btn.setMinimumHeight(40)
        close_btn.clicked.connect(dialog.close)
        
        btn_layout.addWidget(details_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)
        
        dialog.exec()

    def show_invoice_details(self, table, invoices):
        """Affiche les détails d'une facture sélectionnée"""
        selected = table.currentRow()
        if selected < 0:
            QMessageBox.warning(
                self,
                "Attention",
                "Veuillez sélectionner une facture!"
            )
            return
        
        # Récupérer la facture sélectionnée
        invoice = invoices[selected]
        invoice_id = invoice.get('id')
        invoice_number = invoice.get('invoice_number', 'N/A')
        
        # Récupérer les items de la facture
        items = self.db.get_sale_items(invoice_id)
        
        # Créer un dialogue pour afficher les détails
        dialog = QDialog(self)
        dialog.setWindowTitle(f"📋 Détails de la facture - {invoice_number}")
        dialog.setMinimumWidth(900)
        dialog.setMinimumHeight(600)
        dialog.setStyleSheet(f"QDialog {{ background-color: {COLORS['bg_medium']}; }}")
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Titre
        title = QLabel(f"📋 Facture N° {invoice_number}")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']};")
        layout.addWidget(title)
        
        # Infos facture
        info_layout = QHBoxLayout()
        info_layout.setSpacing(30)
        
        date_text = QLabel(f"📅 Date: {invoice.get('created_at', 'N/A')}")
        date_text.setFont(QFont("Segoe UI", 11))
        date_text.setStyleSheet(f"color: {COLORS['text_primary']};")
        
        payment_text = QLabel(f"💳 Paiement: {invoice.get('payment_method', 'N/A')}")
        payment_text.setFont(QFont("Segoe UI", 11))
        payment_text.setStyleSheet(f"color: {COLORS['text_primary']};")
        
        status_text = QLabel(f"📌 Statut: {invoice.get('status', 'Complétée')}")
        status_text.setFont(QFont("Segoe UI", 11))
        status_text.setStyleSheet(f"color: {COLORS['success']};")
        
        info_layout.addWidget(date_text)
        info_layout.addWidget(payment_text)
        info_layout.addWidget(status_text)
        info_layout.addStretch()
        layout.addLayout(info_layout)
        
        # Tableau des articles
        items_table = QTableWidget(0, 4)
        items_table.setHorizontalHeaderLabels(["Produit", "Quantité", "Prix Unitaire", "Total"])
        items_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        items_table.setAlternatingRowColors(True)
        items_table.verticalHeader().setVisible(False)
        items_table.setStyleSheet(TABLE_STYLE + f"""
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
        
        # Ajouter les articles
        for item in items:
            row = items_table.rowCount()
            items_table.insertRow(row)
            
            product_name = QTableWidgetItem(str(item.get('product_name', 'N/A')))
            qty_item = QTableWidgetItem(str(item.get('quantity', 0)))
            qty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            price_item = QTableWidgetItem(f"{item.get('unit_price', 0):,.2f} DA")
            price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            total_item = QTableWidgetItem(f"{item.get('total', 0):,.2f} DA")
            total_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            total_item.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            
            items_table.setItem(row, 0, product_name)
            items_table.setItem(row, 1, qty_item)
            items_table.setItem(row, 2, price_item)
            items_table.setItem(row, 3, total_item)
        
        layout.addWidget(items_table)
        
        # Résumé des montants
        summary_layout = QHBoxLayout()
        summary_layout.addStretch()
        
        subtotal_text = QLabel(f"Sous-total HT: {invoice.get('subtotal', 0):,.2f} DA")
        subtotal_text.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        subtotal_text.setStyleSheet(f"color: {COLORS['text_primary']};")
        
        tax_text = QLabel(f"TVA: {invoice.get('tax_amount', 0):,.2f} DA")
        tax_text.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        tax_text.setStyleSheet(f"color: {COLORS['warning']};")
        
        total_text = QLabel(f"Total TTC: {invoice.get('total_amount', 0):,.2f} DA")
        total_text.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        total_text.setStyleSheet(f"color: {COLORS['success']};")
        
        summary_layout.addWidget(subtotal_text)
        summary_layout.addWidget(tax_text)
        summary_layout.addWidget(total_text)
        layout.addLayout(summary_layout)
        
        # Bouton fermer
        close_btn = QPushButton("✕ Fermer")
        close_btn.setStyleSheet(BUTTON_STYLES['secondary'])
        close_btn.setMinimumHeight(40)
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)
        
        dialog.exec()