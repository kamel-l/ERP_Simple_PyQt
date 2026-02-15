from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QHBoxLayout, QFrame, QComboBox, QLineEdit, QMessageBox
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from styles import COLORS, BUTTON_STYLES, INPUT_STYLE, TABLE_STYLE
from db_manager import get_database
from datetime import datetime, timedelta


class SalesHistoryPage(QWidget):
    def __init__(self):
        super().__init__()
        
        self.db = get_database()

        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        title = QLabel("📊 Historique des Ventes")
        title.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']}; margin-bottom: 5px;")
        layout.addWidget(title)

        subtitle = QLabel("Consultez l'historique complet de vos ventes")
        subtitle.setFont(QFont("Segoe UI", 14))
        subtitle.setStyleSheet(f"color: {COLORS['text_tertiary']}; margin-bottom: 15px;")
        layout.addWidget(subtitle)

        # Statistics Cards
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)
        layout.addLayout(stats_layout)
        
        self.update_statistics()
        stats_layout.addStretch()

        # Filters Bar
        filters_card = QFrame()
        filters_card.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {COLORS['bg_card']}, stop:1 #242424);
                border-radius: 12px;
                border: 1px solid {COLORS['border']};
                padding: 20px;
            }}
        """)
        filters_layout = QHBoxLayout()
        filters_card.setLayout(filters_layout)
        filters_layout.setSpacing(15)

        # Filtre période
        period_label = QLabel("📅 Période:")
        period_label.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        period_label.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")

        self.period_combo = QComboBox()
        self.period_combo.addItems([
            "Aujourd'hui",
            "Cette semaine",
            "Ce mois",
            "3 derniers mois",
            "Cette année",
            "Tout"
        ])
        self.period_combo.setStyleSheet(INPUT_STYLE)
        self.period_combo.setMinimumHeight(45)
        self.period_combo.currentIndexChanged.connect(self.apply_filters)

        # Barre de recherche
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Rechercher par numéro de facture ou client...")
        self.search_input.setStyleSheet(INPUT_STYLE)
        self.search_input.textChanged.connect(self.apply_filters)
        self.search_input.setMinimumHeight(45)

        # Bouton rafraîchir
        refresh_btn = QPushButton("🔄 Actualiser")
        refresh_btn.setStyleSheet(BUTTON_STYLES['secondary'])
        refresh_btn.setMinimumHeight(45)
        refresh_btn.setFixedWidth(150)
        refresh_btn.clicked.connect(self.load_sales)
        refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        filters_layout.addWidget(period_label)
        filters_layout.addWidget(self.period_combo)
        filters_layout.addWidget(self.search_input)
        filters_layout.addWidget(refresh_btn)

        layout.addWidget(filters_card)

        # Table
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

        table_title = QLabel("📋 Liste des Ventes")
        table_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        table_title.setStyleSheet(f"color: {COLORS['text_primary']}; border: none; margin-bottom: 10px;")
        table_layout.addWidget(table_title)

        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels([
            "N° Facture", "Date", "Client", "Articles", 
            "Sous-total", "TVA", "Total TTC"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setStyleSheet(TABLE_STYLE)
        self.table.verticalHeader().setVisible(False)
        
        table_layout.addWidget(self.table)
        layout.addWidget(table_container)

        # Action Buttons
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(10)
        layout.addLayout(actions_layout)

        self.view_btn = QPushButton("👁️ Voir Détails")
        self.view_btn.setStyleSheet(BUTTON_STYLES['primary'])
        self.view_btn.clicked.connect(self.view_sale_details)
        self.view_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.view_btn.setMinimumHeight(40)

        actions_layout.addStretch()
        actions_layout.addWidget(self.view_btn)

        # Charger les données
        self.load_sales()

    def build_stat_card(self, title, value, color):
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
        card.setFixedHeight(80)
        card.setMinimumWidth(200)

        card_layout = QVBoxLayout()
        card.setLayout(card_layout)
        card_layout.setSpacing(5)
        card_layout.setContentsMargins(15, 10, 15, 10)

        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 11))
        title_label.setStyleSheet(f"color: {COLORS['text_tertiary']}; border: none;")
        card_layout.addWidget(title_label)

        value_label = QLabel(str(value))
        value_label.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        value_label.setStyleSheet(f"color: {color}; border: none;")
        card_layout.addWidget(value_label)

        return card

    def update_statistics(self):
        """Met à jour les statistiques"""
        # Effacer les anciennes cartes
        stats_layout = self.layout().itemAt(2)
        while stats_layout.count() > 1:
            child = stats_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Récupérer les stats
        stats = self.db.get_statistics()
        
        # Aujourd'hui
        today = datetime.now().strftime("%Y-%m-%d")
        today_sales = self.db.get_sales_by_date_range(today, today)
        today_total = sum(sale['total'] for sale in today_sales)
        
        # Cette semaine
        week_start = (datetime.now() - timedelta(days=datetime.now().weekday())).strftime("%Y-%m-%d")
        week_end = datetime.now().strftime("%Y-%m-%d")
        week_sales = self.db.get_sales_by_date_range(week_start, week_end)
        week_total = sum(sale['total'] for sale in week_sales)
        
        # Ajouter les cartes
        stats_layout.insertWidget(0, self.build_stat_card(
            "Ventes Aujourd'hui", f"{today_total:,.0f} DA", COLORS['primary']
        ))
        stats_layout.insertWidget(1, self.build_stat_card(
            "Ventes Cette Semaine", f"{week_total:,.0f} DA", COLORS['success']
        ))
        stats_layout.insertWidget(2, self.build_stat_card(
            "Total Ventes", f"{stats['sales_total']:,.0f} DA", COLORS['secondary']
        ))

    def load_sales(self):
        """Charge toutes les ventes"""
        self.table.setRowCount(0)
        sales = self.db.get_all_sales()
        
        for sale in sales:
            self.add_sale_to_table(sale)
        
        self.update_statistics()

    def add_sale_to_table(self, sale):
        """Ajoute une vente au tableau"""
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        # N° Facture
        invoice_item = QTableWidgetItem(sale['invoice_number'])
        invoice_item.setData(Qt.ItemDataRole.UserRole, sale['id'])
        invoice_item.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.table.setItem(row, 0, invoice_item)
        
        # Date
        sale_date = datetime.fromisoformat(sale['sale_date'])
        date_item = QTableWidgetItem(sale_date.strftime("%d/%m/%Y %H:%M"))
        self.table.setItem(row, 1, date_item)
        
        # Client
        client_item = QTableWidgetItem(sale.get('client_name', 'Anonyme'))
        self.table.setItem(row, 2, client_item)
        
        # Nombre d'articles (nécessite une requête supplémentaire)
        sale_details = self.db.get_sale_by_id(sale['id'])
        items_count = len(sale_details['items']) if sale_details else 0
        items_item = QTableWidgetItem(f"{items_count} article(s)")
        items_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(row, 3, items_item)
        
        # Sous-total
        subtotal_item = QTableWidgetItem(f"{sale['subtotal']:,.2f} DA")
        subtotal_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
        self.table.setItem(row, 4, subtotal_item)
        
        # TVA
        tax_item = QTableWidgetItem(f"{sale['tax_amount']:,.2f} DA")
        tax_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
        self.table.setItem(row, 5, tax_item)
        
        # Total
        total_item = QTableWidgetItem(f"{sale['total']:,.2f} DA")
        total_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
        total_item.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        total_item.setForeground(Qt.GlobalColor.green)
        self.table.setItem(row, 6, total_item)

    def apply_filters(self):
        """Applique les filtres"""
        period = self.period_combo.currentText()
        search_text = self.search_input.text().lower()
        
        # Calculer les dates selon la période
        end_date = datetime.now().strftime("%Y-%m-%d")
        
        if period == "Aujourd'hui":
            start_date = end_date
        elif period == "Cette semaine":
            start_date = (datetime.now() - timedelta(days=datetime.now().weekday())).strftime("%Y-%m-%d")
        elif period == "Ce mois":
            start_date = datetime.now().replace(day=1).strftime("%Y-%m-%d")
        elif period == "3 derniers mois":
            start_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
        elif period == "Cette année":
            start_date = datetime.now().replace(month=1, day=1).strftime("%Y-%m-%d")
        else:  # Tout
            # Charger toutes les ventes
            self.table.setRowCount(0)
            sales = self.db.get_all_sales()
            
            for sale in sales:
                if not search_text or \
                   search_text in sale['invoice_number'].lower() or \
                   search_text in (sale.get('client_name', 'anonyme')).lower():
                    self.add_sale_to_table(sale)
            return
        
        # Charger les ventes de la période
        self.table.setRowCount(0)
        sales = self.db.get_sales_by_date_range(start_date, end_date)
        
        for sale in sales:
            if not search_text or \
               search_text in sale['invoice_number'].lower() or \
               search_text in (sale.get('client_name', 'anonyme')).lower():
                self.add_sale_to_table(sale)

    def view_sale_details(self):
        """Affiche les détails d'une vente"""
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(
                self,
                "Attention",
                "Veuillez sélectionner une vente!"
            )
            return
        
        sale_id = self.table.item(selected, 0).data(Qt.ItemDataRole.UserRole)
        sale = self.db.get_sale_by_id(sale_id)
        
        if not sale:
            QMessageBox.critical(self, "Erreur", "Vente introuvable!")
            return
        
        # Créer le message de détails
        details = f"""
<h2 style='color: {COLORS['primary']};'>📄 Facture {sale['invoice_number']}</h2>

<h3>📅 Informations Générales</h3>
<table style='width: 100%; border-collapse: collapse;'>
<tr><td><b>Date:</b></td><td>{datetime.fromisoformat(sale['sale_date']).strftime('%d/%m/%Y %H:%M')}</td></tr>
<tr><td><b>Client:</b></td><td>{sale.get('client_name', 'Client Anonyme')}</td></tr>
<tr><td><b>Mode de paiement:</b></td><td>{sale.get('payment_method', 'cash').upper()}</td></tr>
</table>

<h3>🛒 Articles</h3>
<table style='width: 100%; border: 1px solid #ccc;'>
<tr style='background: #f0f0f0;'>
<th>Produit</th><th>Qté</th><th>P.U.</th><th>Remise</th><th>Total</th>
</tr>
"""
        
        for item in sale['items']:
            details += f"""
<tr>
<td>{item['product_name']}</td>
<td>{item['quantity']}</td>
<td>{item['unit_price']:,.2f} DA</td>
<td>{item['discount']:.2f}%</td>
<td><b>{item['total']:,.2f} DA</b></td>
</tr>
"""
        
        details += f"""
</table>

<h3>💰 Totaux</h3>
<table style='width: 100%;'>
<tr><td><b>Sous-total HT:</b></td><td style='text-align: right;'>{sale['subtotal']:,.2f} DA</td></tr>
<tr><td><b>TVA ({sale['tax_rate']}%):</b></td><td style='text-align: right;'>{sale['tax_amount']:,.2f} DA</td></tr>
<tr style='font-size: 18px; color: green;'><td><b>TOTAL TTC:</b></td><td style='text-align: right;'><b>{sale['total']:,.2f} DA</b></td></tr>
</table>
"""
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Détails de la Vente")
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText(details)
        msg.exec()