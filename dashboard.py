from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame,
    QGridLayout, QPushButton, QScrollArea, QHeaderView
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from styles import COLORS
from db_manager import get_database
from PyQt6.QtCore import QObject, pyqtProperty, QPropertyAnimation
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem


              #==================================Classe d’animation KPI (à ajouter en haut du fichier)===================================

class KpiAnimator(QObject):
    def __init__(self, label):
        super().__init__()
        self._value = 0
        self.label = label
        self.suffix = ""

    def getValue(self):
        return self._value

    def setValue(self, value):
        self._value = value
        formatted = f"{value:,.0f}{self.suffix}"
        self.label.setText(formatted)

    value = pyqtProperty(float, fget=getValue, fset=setValue)


class DashboardPage(QWidget):
    """Dashboard moderne avec grands widgets (version premium améliorée)"""

    def __init__(self):
        super().__init__()
        self.db = get_database()

        # ========== SCROLL GLOBAL ==========
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background: {COLORS['bg_dark']};
            }}
        """)

        # Conteneur principal
        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # ============================================================
        #                        HEADER
        # ============================================================

        header_layout = QHBoxLayout()

        title = QLabel("📊 Tableau de Bord")
        title.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']};")
        header_layout.addWidget(title)

        subtitle = QLabel("Vue d’ensemble de l’activité du système")
        subtitle.setFont(QFont("Segoe UI", 13))
        subtitle.setStyleSheet(f"color: {COLORS['text_tertiary']}; margin-left: 10px;")
        header_layout.addWidget(subtitle)

        header_layout.addStretch()

        refresh_btn = QPushButton("🔄 Actualiser")
        refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['primary']};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 25px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {COLORS['primary_dark']};
            }}
        """)
        refresh_btn.clicked.connect(self.refresh)
        refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        header_layout.addWidget(refresh_btn)

        main_layout.addLayout(header_layout)


        # ============================================================
        #                        KPI PREMIUM LARGE
        # ============================================================

        kpi_row = QHBoxLayout()
        kpi_row.setSpacing(25)

        self.kpi_sales = self.create_kpi_card_large(
            "💰", "Ventes Totales", "0 DA",
            "Total des ventes", COLORS['primary']
        )
        self.kpi_purchases = self.create_kpi_card_large(
            "🛒", "Achats", "0 DA",
            "Achats effectués", COLORS['warning']
        )
        self.kpi_profit = self.create_kpi_card_large(
            "📈", "Bénéfice Net", "0 DA",
            "Marge bénéficiaire", COLORS['success']
        )
        self.kpi_clients = self.create_kpi_card_large(
            "👥", "Clients", "0",
            "Clients enregistrés", COLORS['secondary']
        )

        kpi_row.addWidget(self.kpi_sales)
        kpi_row.addWidget(self.kpi_purchases)
        kpi_row.addWidget(self.kpi_profit)
        kpi_row.addWidget(self.kpi_clients)

        main_layout.addLayout(kpi_row)

        # ============================================================
        #                        ACTIVITÉS RÉCENTES
        # ============================================================

        activities_card = self.create_section_card("📋 Activités Récentes")

        activities_layout = QVBoxLayout()
        activities_layout.setSpacing(10)
        activities_layout.setContentsMargins(15, 10, 15, 15)

        activities_card.setLayout(activities_layout)
        self.activities_container = activities_layout
        main_layout.addWidget(activities_card)

        # ============================================================
        #                        INFO RAPIDE GRANDE TAILLE
        # ============================================================

        quick_row = QHBoxLayout()
        quick_row.setSpacing(20)

        self.info_sales_today = self.create_info_card(
            "📅", "Ventes Aujourd’hui", "0 DA", COLORS['info']
        )
        self.info_best_client = self.create_info_card(
            "🏆", "Top Client", "-", COLORS['success']
        )
        self.info_stock_low = self.create_info_card(
            "⚠️", "Stock Faible", "0 produits", COLORS['warning']
        )

        quick_row.addWidget(self.info_sales_today)
        quick_row.addWidget(self.info_best_client)
        quick_row.addWidget(self.info_stock_low)

        main_layout.addLayout(quick_row)

        main_layout.addStretch()

        scroll.setWidget(container)

        final_layout = QVBoxLayout(self)
        final_layout.setContentsMargins(0, 0, 0, 0)
        final_layout.addWidget(scroll)

        # Ajouter le tableau des factures (désormais un container complet avec titre)
        invoice_container = self.create_invoice_table()
        main_layout.addWidget(invoice_container)

        # Charger les données
        self.refresh()
    
    # =======================================================================================
    #                        Tableau des dernières factures (widget complet)
    # =======================================================================================


    def create_invoice_table(self):
        """Crée un tableau moderne des dernières factures"""
        # Container avec style moderne
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
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(0)
        table_container.setLayout(table_layout)
        
        # Titre de section
        title = QLabel("🧾 Dernières Factures")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']}; padding: 15px;")
        table_layout.addWidget(title)
        
        # Table
        table = QTableWidget(0, 5)
        table.setHorizontalHeaderLabels(["Facture", "Client", "Total", "Date", "Paiement"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.verticalHeader().setVisible(False)
        
        # Importer TABLE_STYLE et appliquer le style moderne
        from styles import TABLE_STYLE
        table.setStyleSheet(TABLE_STYLE + f"""
            QTableWidget {{
                background-color: {COLORS['bg_medium']};
                alternate-background-color: {COLORS['bg_light']};
            }}
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
            QHeaderView::section:first {{
                border-top-left-radius: 8px;
            }}
            QHeaderView::section:last {{
                border-top-right-radius: 8px;
                border-right: none;
            }}
        """)
        
        table.setMinimumHeight(300)
        table.setMaximumHeight(400)
        
        table_layout.addWidget(table)
        
        self.invoice_table = table
        return table_container    
    

    # =========================================================================
    #                          la fonction de chargement
    # =========================================================================
    
    def load_invoices_table(self):
        """Charge les dernières factures dans le tableau"""
        data = self.db.get_all_sales(limit=10)

        self.invoice_table.setRowCount(len(data))

        for row, sale in enumerate(data):
            # Facture
            self.invoice_table.setItem(row, 0, QTableWidgetItem(str(sale['invoice_number'])))
            
            # Client
            client_name = sale.get('client_name', sale.get('client', '—'))
            self.invoice_table.setItem(row, 1, QTableWidgetItem(client_name))
            
            # Total
            self.invoice_table.setItem(row, 2, QTableWidgetItem(f"{sale['total']:,.0f} DA"))
            
            # Date
            date_str = sale.get('sale_date', '—')
            if date_str and date_str != '—':
                # Extraire juste la date (sans l'heure si présente)
                date_str = str(date_str).split(' ')[0]
            self.invoice_table.setItem(row, 3, QTableWidgetItem(date_str))
            
            # Paiement
            payment = sale.get('payment_method', sale.get('payment_mode', '—'))
            self.invoice_table.setItem(row, 4, QTableWidgetItem(payment))
    # =========================================================================
    #                      Fonction pour animer un KPI
    # =========================================================================    
    

    def animate_kpi(self, label, target, suffix=""):
        anim = KpiAnimator(label)
        anim.suffix = suffix
        animation = QPropertyAnimation(anim, b"value")
        animation.setDuration(600)
        animation.setStartValue(0)
        animation.setEndValue(float(target))
        animation.start()
        label.animation = animation  # pour éviter le garbage collector
    # =====================================================================
    #                          CARTES KPI
    # =====================================================================

    def create_kpi_card_large(self, icon, title, value, subtitle, color):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {COLORS['bg_card']}, stop:1 #242424);
                border-radius: 14px;
                border: 1px solid {COLORS['border']};
                
            }}
        """)
        

        card.setMinimumHeight(180)
        card.setMaximumHeight(180)
        

        layout = QVBoxLayout(card)
        layout.setContentsMargins(8, 2, 8, 2)
        layout.setSpacing(8)

        header = QHBoxLayout()
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI", 46))
        header.addWidget(icon_label)

        header.addStretch()

        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 16))
        title_label.setStyleSheet(f"color: {COLORS['text_tertiary']};")
        header.addWidget(title_label)

        layout.addLayout(header)

        value_label = QLabel(value)
        value_label.setFont(QFont("Segoe UI", 40, QFont.Weight.Bold))
        value_label.setStyleSheet(f"color: {color};")
        layout.addWidget(value_label)

        subtitle_label = QLabel(subtitle)
        subtitle_label.setFont(QFont("Segoe UI", 14))
        subtitle_label.setStyleSheet(f"color: {COLORS['text_tertiary']};")
        layout.addWidget(subtitle_label)

        card.value_label = value_label

        return card

    # =====================================================================
    #                          SECTION CARD
    # =====================================================================

    def create_section_card(self, title):
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_card']};
                border-radius: 14px;
                border: 1px solid {COLORS['border']};
            }}
        """)
        frame.setMinimumHeight(250)

        title_label = QLabel(title, parent=frame)
        title_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {COLORS['text_primary']}; padding: 12px;")

        return frame

    # =====================================================================
    #                          INFO CARDS LARGE
    # =====================================================================

    def create_info_card(self, icon, title, value, color):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_card']};
                border-radius: 12px;
                border: 1px solid {COLORS['border']};
                
            }}
        """)
        card.setMinimumHeight(220)
        card.setMaximumHeight(220)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(5)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI", 25))
        layout.addWidget(icon_label)

        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 25))
        title_label.setStyleSheet(f"color: {COLORS['text_tertiary']};")
        layout.addWidget(title_label)

        value_label = QLabel(value)
        value_label.setFont(QFont("Segoe UI", 25, QFont.Weight.Bold))
        value_label.setStyleSheet(f"color: {color};")
        layout.addWidget(value_label)

        card.value_label = value_label

        return card

    # =====================================================================
    #                          FONCTIONS DE CHARGEMENT
    # =====================================================================

    def refresh(self):
        self.load_kpis()
        self.load_recent_activities()
        self.load_quick_info()
        self.load_invoices_table()

    def load_kpis(self):
        stats = self.db.get_statistics() or {}

        sales = float(stats.get("sales_total", 0))
        purchases = float(stats.get("purchases_total", 0))
        profit = sales - purchases
        clients = stats.get("total_clients", 0)

        self.kpi_sales.value_label.setText(f"{sales:,.0f} DA")
        self.kpi_purchases.value_label.setText(f"{purchases:,.0f} DA")
        self.kpi_profit.value_label.setText(f"{profit:,.0f} DA")
        self.kpi_clients.value_label.setText(str(clients))

    def load_recent_activities(self):
        # Nettoyage
        for i in reversed(range(self.activities_container.count())):
            widget = self.activities_container.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        sales = self.db.get_all_sales(limit=4)
        purchases = self.db.get_all_purchases(limit=2)

        if not sales and not purchases:
            empty = QLabel("Aucune activité récente")
            empty.setStyleSheet("font-size: 14px; color: gray; padding: 20px;")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.activities_container.addWidget(empty)
            return

        def add_item(icon, text):
            lbl = QLabel(f"{icon}  {text}")
            lbl.setStyleSheet("font-size: 15px; color: white; padding: 6px;")
            self.activities_container.addWidget(lbl)

        for s in sales:
            add_item("🟢", f"Vente : Facture {s['invoice_number']} - {s['total']:,.0f} DA")

        for p in purchases:
            add_item("🟡", f"Achat : id {p['id']} - {p['total']:,.0f} DA")

    def load_quick_info(self):
        stats = self.db.get_statistics() or {}

        sales_today = float(stats.get("sales_today", 0))
        self.info_sales_today.value_label.setText(f"{sales_today:,.0f} DA")

        top = self.db.get_top_clients(limit=1)
        if top:
            self.info_best_client.value_label.setText(top[0]["name"])
        else:
            self.info_best_client.value_label.setText("—")

        low_stock = self.db.get_low_stock_products() or []
        self.info_stock_low.value_label.setText(f"{len(low_stock)} produits")