"""
Module d'historique des ventes
Affiche toutes les ventes avec filtres et recherche avancée
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, 
    QTableWidgetItem, QHeaderView, QPushButton, QLineEdit,
    QComboBox, QDateEdit, QFrame, QMessageBox
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QDate
from styles import COLORS, BUTTON_STYLES, INPUT_STYLE, TABLE_STYLE
from datetime import datetime


class SalesHistoryPage(QWidget):
    """Page d'historique des ventes avec filtres avancés"""
    
    def __init__(self):
        super().__init__()
        
        self.setup_ui()
        self.load_sample_data()
        self.load_sales()
    
    def setup_ui(self):
        """Configure l'interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # En-tête
        header = self.create_header()
        layout.addLayout(header)
        
        # Statistiques
        stats = self.create_statistics()
        layout.addLayout(stats)
        
        # Filtres
        filters = self.create_filters()
        layout.addWidget(filters)
        
        # Tableau des ventes
        table = self.create_sales_table()
        layout.addWidget(table)
        
        # Boutons d'action
        actions = self.create_actions()
        layout.addLayout(actions)
    
    def create_header(self):
        """Crée l'en-tête de la page"""
        layout = QVBoxLayout()
        
        title = QLabel("📊 Historique des Ventes")
        title.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']};")
        layout.addWidget(title)
        
        subtitle = QLabel("Consultez et analysez vos ventes passées")
        subtitle.setFont(QFont("Segoe UI", 14))
        subtitle.setStyleSheet(f"color: {COLORS['text_tertiary']};")
        layout.addWidget(subtitle)
        
        return layout
    
    def create_statistics(self):
        """Crée les cartes de statistiques"""
        layout = QHBoxLayout()
        layout.setSpacing(15)
        
        self.total_sales_card = self.build_stat_card(
            "Ventes Totales", "0", "0 DA", COLORS['primary']
        )
        self.today_sales_card = self.build_stat_card(
            "Aujourd'hui", "0", "0 DA", COLORS['success']
        )
        self.month_sales_card = self.build_stat_card(
            "Ce Mois", "0", "0 DA", COLORS['warning']
        )
        self.avg_sale_card = self.build_stat_card(
            "Panier Moyen", "0 DA", "", COLORS['secondary']
        )
        
        layout.addWidget(self.total_sales_card)
        layout.addWidget(self.today_sales_card)
        layout.addWidget(self.month_sales_card)
        layout.addWidget(self.avg_sale_card)
        layout.addStretch()
        
        return layout
    
    def build_stat_card(self, title, value1, value2, color):
        """Construit une carte de statistique"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {COLORS['bg_card']}, stop:1 #242424);
                border-radius: 10px;
                border: 1px solid {COLORS['border']};
                border-left: 4px solid {color};
            }}
        """)
        card.setFixedHeight(110)
        card.setMinimumWidth(180)
        
        card_layout = QVBoxLayout()
        card.setLayout(card_layout)
        card_layout.setSpacing(5)
        card_layout.setContentsMargins(15, 12, 15, 12)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 11))
        title_label.setStyleSheet(f"color: {COLORS['text_tertiary']}; border: none;")
        card_layout.addWidget(title_label)
        
        value1_label = QLabel(value1)
        value1_label.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        value1_label.setStyleSheet(f"color: {color}; border: none;")
        card_layout.addWidget(value1_label)
        
        if value2:
            value2_label = QLabel(value2)
            value2_label.setFont(QFont("Segoe UI", 12))
            value2_label.setStyleSheet(f"color: {COLORS['text_tertiary']}; border: none;")
            card_layout.addWidget(value2_label)
        
        return card
    
    def create_filters(self):
        """Crée la section de filtres"""
        container = QFrame()
        container.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_card']};
                border-radius: 12px;
                border: 1px solid {COLORS['border']};
                padding: 20px;
            }}
        """)
        
        layout = QVBoxLayout(container)
        layout.setSpacing(15)
        
        # Titre
        title = QLabel("🔍 Filtres de Recherche")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        layout.addWidget(title)
        
        # Ligne 1 : Recherche et période
        row1 = QHBoxLayout()
        row1.setSpacing(15)
        
        # Recherche textuelle
        search_label = QLabel("Recherche:")
        search_label.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        row1.addWidget(search_label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("N° facture, client, produit...")
        self.search_input.setStyleSheet(INPUT_STYLE)
        self.search_input.setMinimumHeight(40)
        self.search_input.textChanged.connect(self.apply_filters)
        row1.addWidget(self.search_input)
        
        # Date début
        date_from_label = QLabel("Du:")
        date_from_label.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        row1.addWidget(date_from_label)
        
        self.date_from = QDateEdit()
        self.date_from.setDate(QDate.currentDate().addMonths(-1))
        self.date_from.setCalendarPopup(True)
        self.date_from.setStyleSheet(INPUT_STYLE)
        self.date_from.setMinimumHeight(40)
        self.date_from.dateChanged.connect(self.apply_filters)
        row1.addWidget(self.date_from)
        
        # Date fin
        date_to_label = QLabel("Au:")
        date_to_label.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        row1.addWidget(date_to_label)
        
        self.date_to = QDateEdit()
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setCalendarPopup(True)
        self.date_to.setStyleSheet(INPUT_STYLE)
        self.date_to.setMinimumHeight(40)
        self.date_to.dateChanged.connect(self.apply_filters)
        row1.addWidget(self.date_to)
        
        layout.addLayout(row1)
        
        # Ligne 2 : Statut et client
        row2 = QHBoxLayout()
        row2.setSpacing(15)
        
        # Statut de paiement
        status_label = QLabel("Statut:")
        status_label.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        row2.addWidget(status_label)
        
        self.status_filter = QComboBox()
        self.status_filter.addItems([
            "Tous les statuts",
            "Payée",
            "En attente",
            "Annulée"
        ])
        self.status_filter.setStyleSheet(INPUT_STYLE)
        self.status_filter.setMinimumHeight(40)
        self.status_filter.currentIndexChanged.connect(self.apply_filters)
        row2.addWidget(self.status_filter)
        
        # Filtre client
        client_label = QLabel("Client:")
        client_label.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        row2.addWidget(client_label)
        
        self.client_filter = QComboBox()
        self.client_filter.addItems([
            "Tous les clients",
            "John Doe",
            "Alice Smith",
            "Entreprise X",
            "Bob Martin"
        ])
        self.client_filter.setStyleSheet(INPUT_STYLE)
        self.client_filter.setMinimumHeight(40)
        self.client_filter.currentIndexChanged.connect(self.apply_filters)
        row2.addWidget(self.client_filter)
        
        # Bouton réinitialiser
        reset_btn = QPushButton("🔄 Réinitialiser")
        reset_btn.setStyleSheet(BUTTON_STYLES['secondary'])
        reset_btn.setMinimumHeight(40)
        reset_btn.clicked.connect(self.reset_filters)
        reset_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        row2.addWidget(reset_btn)
        
        layout.addLayout(row2)
        
        return container
    
    def create_sales_table(self):
        """Crée le tableau des ventes"""
        container = QFrame()
        container.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_card']};
                border-radius: 12px;
                border: 1px solid {COLORS['border']};
                padding: 15px;
            }}
        """)
        
        layout = QVBoxLayout(container)
        
        # Titre
        title = QLabel("📋 Liste des Ventes")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        layout.addWidget(title)
        
        # Tableau
        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels([
            "N° Facture", "Date", "Client", "Articles", 
            "Montant HT", "TVA", "Total TTC", "Statut"
        ])
        
        # Configurer les colonnes
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)
        
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet(TABLE_STYLE)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        # Double-clic pour voir les détails
        self.table.doubleClicked.connect(self.view_sale_details)
        
        layout.addWidget(self.table)
        
        return container
    
    def create_actions(self):
        """Crée les boutons d'action"""
        layout = QHBoxLayout()
        layout.setSpacing(10)
        
        # Bouton exporter
        export_btn = QPushButton("📤 Exporter Excel")
        export_btn.setStyleSheet(BUTTON_STYLES['secondary'])
        export_btn.setMinimumHeight(45)
        export_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Bouton imprimer
        print_btn = QPushButton("🖨️ Imprimer")
        print_btn.setStyleSheet(BUTTON_STYLES['secondary'])
        print_btn.setMinimumHeight(45)
        print_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Bouton voir détails
        details_btn = QPushButton("👁️ Voir Détails")
        details_btn.setStyleSheet(BUTTON_STYLES['primary'])
        details_btn.setMinimumHeight(45)
        details_btn.clicked.connect(self.view_sale_details)
        details_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        layout.addWidget(export_btn)
        layout.addWidget(print_btn)
        layout.addStretch()
        layout.addWidget(details_btn)
        
        return layout
    
    def load_sample_data(self):
        """Charge des données exemple"""
        self.sales_data = [
            {
                'invoice': 'FAC-2026-001',
                'date': '14/02/2026',
                'client': 'Entreprise X',
                'items': 5,
                'subtotal': 352500.00,
                'tax': 66975.00,
                'total': 419475.00,
                'status': 'Payée'
            },
            {
                'invoice': 'FAC-2026-002',
                'date': '13/02/2026',
                'client': 'John Doe',
                'items': 2,
                'subtotal': 76500.00,
                'tax': 14535.00,
                'total': 91035.00,
                'status': 'Payée'
            },
            {
                'invoice': 'FAC-2026-003',
                'date': '12/02/2026',
                'client': 'Alice Smith',
                'items': 3,
                'subtotal': 125000.00,
                'tax': 23750.00,
                'total': 148750.00,
                'status': 'En attente'
            },
        ]
    
    def load_sales(self, filtered_data=None):
        """Charge les ventes dans le tableau"""
        data = filtered_data if filtered_data is not None else self.sales_data
        
        self.table.setRowCount(0)
        
        for sale in data:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # N° Facture
            invoice_item = QTableWidgetItem(sale['invoice'])
            invoice_item.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            self.table.setItem(row, 0, invoice_item)
            
            # Date
            date_item = QTableWidgetItem(sale['date'])
            self.table.setItem(row, 1, date_item)
            
            # Client
            client_item = QTableWidgetItem(sale['client'])
            self.table.setItem(row, 2, client_item)
            
            # Articles
            items_item = QTableWidgetItem(str(sale['items']))
            items_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 3, items_item)
            
            # Montant HT
            subtotal_item = QTableWidgetItem(f"{sale['subtotal']:,.2f}")
            subtotal_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.table.setItem(row, 4, subtotal_item)
            
            # TVA
            tax_item = QTableWidgetItem(f"{sale['tax']:,.2f}")
            tax_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.table.setItem(row, 5, tax_item)
            
            # Total TTC
            total_item = QTableWidgetItem(f"{sale['total']:,.2f}")
            total_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            total_item.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            self.table.setItem(row, 6, total_item)
            
            # Statut
            status_item = QTableWidgetItem(sale['status'])
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Couleur selon le statut
            if sale['status'] == 'Payée':
                status_item.setForeground(Qt.GlobalColor.green)
            elif sale['status'] == 'En attente':
                status_item.setForeground(Qt.GlobalColor.yellow)
            elif sale['status'] == 'Annulée':
                status_item.setForeground(Qt.GlobalColor.red)
            
            self.table.setItem(row, 7, status_item)
        
        # Mettre à jour les statistiques
        self.update_statistics(data)
    
    def update_statistics(self, data):
        """Met à jour les cartes de statistiques"""
        total_sales = len(data)
        total_amount = sum(s['total'] for s in data)
        
        # Calculer aujourd'hui et ce mois (simplifié)
        today_sales = len([s for s in data if s['date'] == '14/02/2026'])
        today_amount = sum(s['total'] for s in data if s['date'] == '14/02/2026')
        
        month_sales = len(data)  # Simplifié pour l'exemple
        month_amount = total_amount
        
        avg_sale = total_amount / total_sales if total_sales > 0 else 0
        
        # Mettre à jour les cartes
        self.total_sales_card.findChildren(QLabel)[1].setText(str(total_sales))
        self.total_sales_card.findChildren(QLabel)[2].setText(f"{total_amount:,.0f} DA")
        
        self.today_sales_card.findChildren(QLabel)[1].setText(str(today_sales))
        self.today_sales_card.findChildren(QLabel)[2].setText(f"{today_amount:,.0f} DA")
        
        self.month_sales_card.findChildren(QLabel)[1].setText(str(month_sales))
        self.month_sales_card.findChildren(QLabel)[2].setText(f"{month_amount:,.0f} DA")
        
        self.avg_sale_card.findChildren(QLabel)[1].setText(f"{avg_sale:,.0f} DA")
    
    def apply_filters(self):
        """Applique les filtres sur les données"""
        filtered = self.sales_data.copy()
        
        # Filtre de recherche
        search_text = self.search_input.text().lower()
        if search_text:
            filtered = [
                s for s in filtered 
                if search_text in s['invoice'].lower() 
                or search_text in s['client'].lower()
            ]
        
        # Filtre de statut
        status = self.status_filter.currentText()
        if status != "Tous les statuts":
            filtered = [s for s in filtered if s['status'] == status]
        
        # Filtre de client
        client = self.client_filter.currentText()
        if client != "Tous les clients":
            filtered = [s for s in filtered if s['client'] == client]
        
        self.load_sales(filtered)
    
    def reset_filters(self):
        """Réinitialise tous les filtres"""
        self.search_input.clear()
        self.status_filter.setCurrentIndex(0)
        self.client_filter.setCurrentIndex(0)
        self.date_from.setDate(QDate.currentDate().addMonths(-1))
        self.date_to.setDate(QDate.currentDate())
        self.load_sales()
    
    def view_sale_details(self):
        """Affiche les détails d'une vente"""
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Aucune sélection",
                              "Veuillez sélectionner une vente !")
            return
        
        invoice = self.table.item(selected, 0).text()
        QMessageBox.information(self, "Détails de la vente",
                              f"Affichage des détails de la facture {invoice}\n\n"
                              "Cette fonctionnalité sera implémentée prochainement.")