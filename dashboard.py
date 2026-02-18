from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame, QGridLayout
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from styles import COLORS, get_kpi_card_style
from db_manager import get_database


class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()
        
        # Connexion à la base de données
        self.db = get_database()

        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # ------------------- HEADER -------------------
        title = QLabel("📊 Tableau de Bord")
        title.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']}; margin-bottom: 5px;")
        layout.addWidget(title)

        subtitle = QLabel("Vue d'ensemble de votre système")
        subtitle.setFont(QFont("Segoe UI", 14))
        subtitle.setStyleSheet(f"color: {COLORS['text_tertiary']}; margin-bottom: 15px;")
        layout.addWidget(subtitle)

        # ------------------- KPI CARDS GRID -------------------
        self.cards_grid = QGridLayout()
        self.cards_grid.setSpacing(15)
        layout.addLayout(self.cards_grid)

        # Charger les statistiques
        self.load_statistics()

        # ------------------- ACTIVITÉS RÉCENTES -------------------
        activity_title = QLabel("📋 Activités Récentes")
        activity_title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        activity_title.setStyleSheet(f"color: {COLORS['text_primary']}; margin-top: 20px;")
        layout.addWidget(activity_title)

        # Conteneur d'activités
        activities_container = QFrame()
        activities_container.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {COLORS['bg_card']}, stop:1 #242424);
                border-radius: 12px;
                border: 1px solid {COLORS['border']};
                padding: 15px;
            }}
        """)
        activities_layout = QVBoxLayout()
        activities_container.setLayout(activities_layout)
        activities_layout.setSpacing(10)

        # Charger les activités récentes
        self.load_recent_activities(activities_layout)

        layout.addWidget(activities_container)

        # ------------------- Spacer -------------------
        layout.addStretch()

    def load_statistics(self):
        """Charge les statistiques depuis la base de données"""
        # Récupérer les stats
        stats = self.db.get_statistics()
        
        # Calculer les pourcentages (exemple simplifié)
        # Dans une vraie app, vous compareriez avec le mois précédent
        sales_change = "+12.5%" if stats['total_sales'] > 0 else "0%"
        purchases_change = "-5.2%" if stats['total_purchases'] > 0 else "0%"
        
        # Calculer le bénéfice
        profit = stats['profit']
        profit_change = "+18.3%" if profit > 0 else "0%"
        
        # Première ligne
        self.cards_grid.addWidget(
            self.build_kpi_card(
                "💰 Ventes Totales",
                f"{stats['sales_total']:,.0f} DA",
                sales_change,
                "par rapport au mois dernier",
                COLORS['primary']
            ), 0, 0
        )
        self.cards_grid.addWidget(
            self.build_kpi_card(
                "🛒 Achats",
                f"{stats['purchases_total']:,.0f} DA",
                purchases_change,
                "réduction des coûts",
                COLORS['warning']
            ), 0, 1
        )
        
        # Deuxième ligne
        self.cards_grid.addWidget(
            self.build_kpi_card(
                "📈 Bénéfice Net",
                f"{profit:,.0f} DA",
                profit_change,
                "croissance mensuelle",
                COLORS['success']
            ), 1, 0
        )
        self.cards_grid.addWidget(
            self.build_kpi_card(
                "👥 Clients",
                str(stats['total_clients']),
                f"+{stats['total_clients']}",
                "clients enregistrés",
                COLORS['secondary']
            ), 1, 1
        )

    def load_recent_activities(self, layout):
        """Charge les activités récentes depuis la base de données"""
        # Récupérer les dernières ventes
        recent_sales = self.db.get_all_sales(limit=3)
        
        if recent_sales:
            for sale in recent_sales:
                activity_item = self.build_activity_item(
                    "✅",
                    "Nouvelle vente enregistrée",
                    f"Facture: {sale['invoice_number']} - {sale['total']:,.0f} DA",
                    "Récent"
                )
                layout.addWidget(activity_item)
        
        # Récupérer les derniers achats
        recent_purchases = self.db.get_all_purchases(limit=2)
        
        if recent_purchases:
            for purchase in recent_purchases:
                activity_item = self.build_activity_item(
                    "🛒",
                    "Achat effectué",
                    f"id: {purchase['id']} - {purchase['total']:,.0f} DA",
                    "Récent"
                )
                layout.addWidget(activity_item)
        
        # Si aucune activité
        if not recent_sales and not recent_purchases:
            no_activity = QLabel("Aucune activité récente")
            no_activity.setFont(QFont("Segoe UI", 12))
            no_activity.setStyleSheet(f"color: {COLORS['text_tertiary']}; padding: 20px;")
            no_activity.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(no_activity)

    def build_kpi_card(self, title, value, change, change_desc, color):
        """Construit une carte KPI améliorée"""
        card = QFrame()
        card.setStyleSheet(get_kpi_card_style(color))
        card.setMinimumHeight(160)

        card_layout = QVBoxLayout()
        card.setLayout(card_layout)
        card_layout.setSpacing(10)
        card_layout.setContentsMargins(20, 20, 20, 20)

        # Titre
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 13))
        title_label.setStyleSheet(f"color: {COLORS['text_tertiary']}; border: none;")
        card_layout.addWidget(title_label)

        # Valeur principale
        value_label = QLabel(value)
        value_label.setFont(QFont("Segoe UI", 32, QFont.Weight.Bold))
        value_label.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        card_layout.addWidget(value_label)

        # Changement
        change_layout = QHBoxLayout()
        change_layout.setSpacing(8)
        
        change_label = QLabel(change)
        change_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        
        # Couleur selon le signe
        change_color = COLORS['success'] if change.startswith('+') else COLORS['danger']
        if change == "0%":
            change_color = COLORS['text_tertiary']
        change_label.setStyleSheet(f"color: {change_color}; border: none;")
        
        change_desc_label = QLabel(change_desc)
        change_desc_label.setFont(QFont("Segoe UI", 11))
        change_desc_label.setStyleSheet(f"color: {COLORS['text_tertiary']}; border: none;")
        
        change_layout.addWidget(change_label)
        change_layout.addWidget(change_desc_label)
        change_layout.addStretch()
        
        card_layout.addLayout(change_layout)
        card_layout.addStretch()

        return card

    def build_activity_item(self, icon, title, description, time):
        """Construit un élément d'activité"""
        item = QFrame()
        item.setStyleSheet(f"""
            QFrame {{
                background: transparent;
                border: none;
                border-bottom: 1px solid {COLORS['border']};
                padding: 10px 0px;
            }}
            QFrame:hover {{
                background: rgba(255, 255, 255, 0.03);
                border-radius: 8px;
            }}
        """)
        item.setMinimumHeight(60)

        item_layout = QHBoxLayout()
        item.setLayout(item_layout)
        item_layout.setSpacing(15)

        # Icône
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI", 24))
        icon_label.setFixedSize(40, 40)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet(f"""
            background: {COLORS['bg_light']};
            border-radius: 20px;
            border: none;
        """)
        item_layout.addWidget(icon_label)

        # Contenu
        content_layout = QVBoxLayout()
        content_layout.setSpacing(4)

        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        content_layout.addWidget(title_label)

        desc_label = QLabel(description)
        desc_label.setFont(QFont("Segoe UI", 11))
        desc_label.setStyleSheet(f"color: {COLORS['text_tertiary']}; border: none;")
        content_layout.addWidget(desc_label)

        item_layout.addLayout(content_layout)
        item_layout.addStretch()

        # Temps
        time_label = QLabel(time)
        time_label.setFont(QFont("Segoe UI", 10))
        time_label.setStyleSheet(f"color: {COLORS['text_tertiary']}; border: none;")
        time_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        item_layout.addWidget(time_label)

        return item
    
    def refresh(self):
        """Rafraîchit le tableau de bord"""
        # Effacer les anciennes cartes
        while self.cards_grid.count():
            child = self.cards_grid.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Recharger les statistiques
        self.load_statistics()