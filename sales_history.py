from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QHBoxLayout, QFrame, QComboBox, QLineEdit, 
    QMessageBox, QDialog, QScrollArea
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from styles import COLORS, BUTTON_STYLES, INPUT_STYLE, TABLE_STYLE
from db_manager import get_database
from datetime import datetime, timedelta
from PyQt6.QtWidgets import QFileDialog


class InvoiceDetailsDialog(QDialog):
    """Dialogue moderne pour afficher les détails d'une facture"""
    
    def __init__(self, sale_data, parent=None):
        super().__init__(parent)
        
        self.sale = sale_data
        self.setWindowTitle(f"Facture {self.sale['invoice_number']}")
        self.setMinimumSize(900, 700)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['bg_medium']};
            }}
        """)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configure l'interface"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # ================= EN-TÊTE =================
        header = self.create_header()
        main_layout.addWidget(header)
        
        # ================= ZONE SCROLLABLE =================
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background-color: {COLORS['bg_dark']};
            }}
        """)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(20)
        scroll_layout.setContentsMargins(30, 30, 30, 30)
        
        # Informations générales
        info_section = self.create_info_section()
        scroll_layout.addWidget(info_section)
        
        # Articles
        items_section = self.create_items_section()
        scroll_layout.addWidget(items_section)
        
        # Totaux
        totals_section = self.create_totals_section()
        scroll_layout.addWidget(totals_section)
        
        scroll_layout.addStretch()
        
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)
        
        # ================= BOUTONS D'ACTION =================
        actions = self.create_actions()
        main_layout.addWidget(actions)
    
    def create_header(self):
        """Crée l'en-tête de la facture"""
        header = QFrame()
        header.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['primary']}, stop:1 {COLORS['secondary']});
                padding: 30px;
                border-bottom: 3px solid {COLORS['success']};
            }}
        """)
        
        header_layout = QVBoxLayout(header)
        header_layout.setSpacing(10)
        
        # Numéro de facture
        invoice_number = QLabel(f"📄 FACTURE N° {self.sale['invoice_number']}")
        invoice_number.setFont(QFont("Segoe UI", 32, QFont.Weight.Bold))
        invoice_number.setStyleSheet("color: white; border: none;")
        invoice_number.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(invoice_number)
        
        # Date
        sale_date = datetime.fromisoformat(self.sale['sale_date'])
        date_label = QLabel(f"📅 {sale_date.strftime('%d/%m/%Y à %H:%M')}")
        date_label.setFont(QFont("Segoe UI", 14))
        date_label.setStyleSheet("color: rgba(255, 255, 255, 0.9); border: none;")
        date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(date_label)
        
        return header
    
    def create_info_section(self):
        """Crée la section informations générales"""
        section = QFrame()
        section.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_card']};
                border-radius: 12px;
                border: 1px solid {COLORS['border']};
                padding: 20px;
            }}
        """)
        
        layout = QVBoxLayout(section)
        layout.setSpacing(15)
        
        # Titre
        title = QLabel("📋 Informations Générales")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        layout.addWidget(title)
        
        # Grille d'informations
        info_grid = QFrame()
        info_grid.setStyleSheet("border: none;")
        grid_layout = QVBoxLayout(info_grid)
        grid_layout.setSpacing(12)
        
        # Client
        client_row = self.create_info_row(
            "👤 Client:",
            self.sale.get('client_name', 'Client Anonyme')
        )
        grid_layout.addWidget(client_row)
        
        # Mode de paiement
        payment_method_display = {
            'cash': '💵 Espèces',
            'card': '💳 Carte Bancaire',
            'check': '📝 Chèque',
            'transfer': '🏦 Virement',
            'mobile': '📱 Mobile Money',
            'credit': '🔄 À Crédit'
        }
        payment_method = self.sale.get('payment_method', 'cash')
        payment_row = self.create_info_row(
            "💳 Mode de paiement:",
            payment_method_display.get(payment_method, payment_method)
        )
        grid_layout.addWidget(payment_row)
        
        # Date de vente
        sale_date = datetime.fromisoformat(self.sale['sale_date'])
        date_row = self.create_info_row(
            "📅 Date de vente:",
            sale_date.strftime('%A %d %B %Y à %H:%M')
        )
        grid_layout.addWidget(date_row)
        
        layout.addWidget(info_grid)
        
        return section
    
    def create_info_row(self, label_text, value_text):
        """Crée une ligne d'information"""
        row = QFrame()
        row.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_light']};
                border-radius: 8px;
                padding: 15px;
                border: none;
            }}
        """)
        
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(15, 10, 15, 10)
        
        label = QLabel(label_text)
        label.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        label.setStyleSheet(f"color: {COLORS['text_tertiary']}; border: none;")
        label.setMinimumWidth(200)
        
        value = QLabel(value_text)
        value.setFont(QFont("Segoe UI", 13))
        value.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        value.setWordWrap(True)
        
        row_layout.addWidget(label)
        row_layout.addWidget(value)
        row_layout.addStretch()
        
        return row
    
    def create_items_section(self):
        """Crée la section des articles"""
        section = QFrame()
        section.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_card']};
                border-radius: 12px;
                border: 1px solid {COLORS['border']};
                padding: 20px;
            }}
        """)
        
        layout = QVBoxLayout(section)
        layout.setSpacing(15)
        
        # Titre
        title = QLabel(f"🛒 Articles ({len(self.sale['items'])} article(s))")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        layout.addWidget(title)
        
        # Tableau des articles
        items_table = QTableWidget(0, 5)
        items_table.setHorizontalHeaderLabels([
            "Produit", "Quantité", "Prix Unit.", "Remise", "Total"
        ])
        items_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        items_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        items_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        items_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        items_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        items_table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        items_table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        items_table.verticalHeader().setVisible(False)
        items_table.setAlternatingRowColors(True)
        
        items_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {COLORS['bg_dark']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                gridline-color: {COLORS['border']};
            }}
            QTableWidget::item {{
                padding: 12px 8px;
                color: {COLORS['text_primary']};
                border: none;
            }}
            QTableWidget::item:alternate {{
                background-color: {COLORS['bg_light']};
            }}
            QHeaderView::section {{
                background-color: {COLORS['primary']};
                color: white;
                font-size: 13px;
                font-weight: bold;
                padding: 12px 8px;
                border: none;
                border-right: 1px solid rgba(255, 255, 255, 0.2);
            }}
            QHeaderView::section:last {{
                border-right: none;
            }}
        """)
        
        # Remplir le tableau
        for item in self.sale['items']:
            row = items_table.rowCount()
            items_table.insertRow(row)
            
            # Produit
            product_item = QTableWidgetItem(item['product_name'])
            product_item.setFont(QFont("Segoe UI", 11))
            items_table.setItem(row, 0, product_item)
            
            # Quantité
            qty_item = QTableWidgetItem(str(item['quantity']))
            qty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            qty_item.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            items_table.setItem(row, 1, qty_item)
            
            # Prix unitaire
            price_item = QTableWidgetItem(f"{item['unit_price']:,.2f} DA")
            price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            items_table.setItem(row, 2, price_item)
            
            # Remise
            discount_item = QTableWidgetItem(
                f"{item['discount']:.1f}%" if item['discount'] > 0 else "-"
            )
            discount_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if item['discount'] > 0:
                discount_item.setForeground(Qt.GlobalColor.red)
                discount_item.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            items_table.setItem(row, 3, discount_item)
            
            # Total
            total_item = QTableWidgetItem(f"{item['total']:,.2f} DA")
            total_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            total_item.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            total_item.setForeground(Qt.GlobalColor.green)
            items_table.setItem(row, 4, total_item)
        
        # Ajuster la hauteur
        items_table.setMaximumHeight(min(400, (len(self.sale['items']) + 1) * 50))
        
        layout.addWidget(items_table)
        
        return section
    
    def create_totals_section(self):
        """Crée la section des totaux"""
        section = QFrame()
        section.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['bg_card']}, stop:1 #242424);
                border-radius: 12px;
                border: 2px solid {COLORS['success']};
                padding: 25px;
            }}
        """)
        
        layout = QVBoxLayout(section)
        layout.setSpacing(15)
        
        # Titre
        title = QLabel("💰 Résumé Financier")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        layout.addWidget(title)
        
        # Sous-total
        subtotal_row = self.create_total_row(
            "Sous-total HT:",
            f"{self.sale['subtotal']:,.2f} DA",
            COLORS['text_primary']
        )
        layout.addWidget(subtotal_row)
        
        # TVA
        tax_row = self.create_total_row(
            f"TVA ({self.sale['tax_rate']}%):",
            f"{self.sale['tax_amount']:,.2f} DA",
            COLORS['warning']
        )
        layout.addWidget(tax_row)
        
        # Séparateur
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['border']};
                border: none;
                max-height: 2px;
                margin: 10px 0;
            }}
        """)
        layout.addWidget(separator)
        
        # Total TTC
        total_container = QFrame()
        total_container.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(48, 209, 88, 0.2), stop:1 rgba(10, 132, 255, 0.2));
                border-radius: 10px;
                padding: 20px;
                border: 2px solid {COLORS['success']};
            }}
        """)
        
        total_layout = QHBoxLayout(total_container)
        
        total_label = QLabel("TOTAL TTC:")
        total_label.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        total_label.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        
        total_value = QLabel(f"{self.sale['total']:,.2f} DA")
        total_value.setFont(QFont("Segoe UI", 32, QFont.Weight.Bold))
        total_value.setStyleSheet(f"color: {COLORS['success']}; border: none;")
        total_value.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        total_layout.addWidget(total_label)
        total_layout.addStretch()
        total_layout.addWidget(total_value)
        
        layout.addWidget(total_container)
        
        return section
    
    def create_total_row(self, label_text, value_text, color):
        """Crée une ligne de total"""
        row = QFrame()
        row.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_light']};
                border-radius: 8px;
                padding: 15px 20px;
                border: none;
            }}
        """)
        
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        
        label = QLabel(label_text)
        label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        label.setStyleSheet(f"color: {COLORS['text_tertiary']}; border: none;")
        
        value = QLabel(value_text)
        value.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        value.setStyleSheet(f"color: {color}; border: none;")
        value.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        row_layout.addWidget(label)
        row_layout.addStretch()
        row_layout.addWidget(value)
        
        return row
    
    def create_actions(self):
        """Crée les boutons d'action"""
        actions = QFrame()
        actions.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_medium']};
                border-top: 2px solid {COLORS['border']};
                padding: 20px 30px;
            }}
        """)
        
        actions_layout = QHBoxLayout(actions)
        actions_layout.setSpacing(15)
        
        # Bouton Export CSV
        csv_btn = QPushButton("📊 Exporter CSV")
        csv_btn.setStyleSheet(BUTTON_STYLES['secondary'])
        csv_btn.setMinimumHeight(50)
        csv_btn.setMinimumWidth(150)
        csv_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        csv_btn.clicked.connect(self.export_csv)
        
        # Bouton Exporter PDF (à implémenter)
        pdf_btn = QPushButton("📄 Exporter PDF")
        pdf_btn.setStyleSheet(BUTTON_STYLES['secondary'])
        pdf_btn.setMinimumHeight(50)
        pdf_btn.setMinimumWidth(150)
        pdf_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        pdf_btn.clicked.connect(self.export_pdf)
        
        # Bouton Fermer
        close_btn = QPushButton("✖️ Fermer")
        close_btn.setStyleSheet(BUTTON_STYLES['danger'])
        close_btn.setMinimumHeight(50)
        close_btn.setMinimumWidth(150)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(self.accept)
        
        actions_layout.addWidget(csv_btn)
        actions_layout.addWidget(pdf_btn)
        actions_layout.addStretch()
        actions_layout.addWidget(close_btn)
        
        return actions
    
    def export_csv(self):
            """Exporte la facture en CSV avec boîte de dialogue"""

            try:
                import csv

                # نافذة اختيار مكان الحفظ
                default_name = f"facture_{self.sale['invoice_number']}.csv"

                file_path, _ = QFileDialog.getSaveFileName(
                    self,
                    "Enregistrer la facture en CSV",
                    default_name,
                    "CSV Files (*.csv)"
                )

                # إذا المستخدم ضغط Annuler
                if not file_path:
                    return

                with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)

                    # Informations générales
                    writer.writerow(["Facture N°", self.sale['invoice_number']])
                    writer.writerow(["Date", self.sale['sale_date']])
                    writer.writerow(["Client", self.sale.get('client_name', 'Client Anonyme')])
                    writer.writerow([])

                    # Colonnes
                    writer.writerow(["Produit", "Quantité", "Prix Unitaire", "Remise (%)", "Total"])

                    # Articles
                    for item in self.sale['items']:
                        writer.writerow([
                            item['product_name'],
                            item['quantity'],
                            item['unit_price'],
                            item['discount'],
                            item['total']
                        ])

                    writer.writerow([])
                    writer.writerow(["Sous-total", self.sale['subtotal']])
                    writer.writerow(["TVA", self.sale['tax_amount']])
                    writer.writerow(["Total TTC", self.sale['total']])

                QMessageBox.information(
                    self,
                    "Export Réussi",
                    f"✅ Facture exportée avec succès !\n\n{file_path}"
                )

            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Erreur",
                    f"Erreur lors de l'export CSV:\n{str(e)}"
                )
    
    def export_pdf(self):
        """Exporte la facture en PDF"""
        try:
            from invoice_pdf import create_invoice_pdf
            
            # Préparer les données pour le PDF
            invoice_data = {
                'invoice_number': self.sale['invoice_number'],
                'date': datetime.fromisoformat(self.sale['sale_date']).strftime('%d/%m/%Y'),
                'company': {
                    'name': 'Ma Société SARL',
                    'address': '123 Rue Example, Alger',
                    'phone': '023 45 67 89',
                    'email': 'contact@masociete.dz',
                    'nif': '123456789012345',
                    'nis': '123456789012',
                    'rc': '12/34567890'
                },
                'customer': {
                    'name': self.sale.get('client_name', 'Client Anonyme'),
                    'address': '',
                    'phone': ''
                },
                'items': [
                    {
                        'product': item['product_name'],
                        'reference': '',
                        'quantity': item['quantity'],
                        'price': item['unit_price'],
                        'discount': item['discount'],
                        'total': item['total']
                    }
                    for item in self.sale['items']
                ],
                'subtotal': self.sale['subtotal'],
                'tax': self.sale['tax_amount'],
                'total': self.sale['total']
            }
            
            # Créer le PDF
            filename = f"facture_{self.sale['invoice_number']}.pdf"
            pdf_file = create_invoice_pdf(invoice_data, filename)
            
            QMessageBox.information(
                self,
                "PDF Créé",
                f"✅ La facture a été exportée avec succès !\n\n"
                f"Fichier: {pdf_file}"
            )
            
        except ImportError:
            QMessageBox.warning(
                self,
                "Module manquant",
                "Le module d'export PDF n'est pas disponible.\n\n"
                "Installez: pip install reportlab"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Erreur",
                f"Erreur lors de l'export PDF:\n{str(e)}"
            )


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
                padding: 0px;
            }}
        """)
        table_layout = QVBoxLayout()
        table_layout.setContentsMargins(15, 15, 15, 15)
        table_layout.setSpacing(10)
        table_container.setLayout(table_layout)

        table_title = QLabel("📋 Liste des Ventes")
        table_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        table_title.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        table_layout.addWidget(table_title)

        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels([
            "N° Facture", "Date", "Client", "Articles",
            "Sous-total", "TVA", "Total TTC"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.verticalHeader().setVisible(False)
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
        
        # Double-clic pour voir les détails
        self.table.doubleClicked.connect(self.view_sale_details)

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
        """Affiche les détails d'une vente dans un dialogue moderne"""
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
        
        # Ouvrir le dialogue moderne
        dialog = InvoiceDetailsDialog(sale, self)
        dialog.exec()
