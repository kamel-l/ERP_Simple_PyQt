from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
    QFormLayout, QLineEdit, QComboBox, QFrame, QTabWidget
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
import qdarktheme
from styles import COLORS, BUTTON_STYLES, INPUT_STYLE


class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # ------------------- HEADER -------------------
        header_layout = QVBoxLayout()
        layout.addLayout(header_layout)

        title = QLabel("⚙️ Paramètres")
        title.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']}; margin-bottom: 5px;")
        header_layout.addWidget(title)

        subtitle = QLabel("Configuration de votre système")
        subtitle.setFont(QFont("Segoe UI", 14))
        subtitle.setStyleSheet(f"color: {COLORS['text_tertiary']}; margin-bottom: 15px;")
        header_layout.addWidget(subtitle)

        # ------------------- TABS -------------------
        tabs = QTabWidget()
        tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                background: {COLORS['bg_card']};
                padding: 15px;
            }}
            QTabBar::tab {{
                background: {COLORS['bg_medium']};
                color: {COLORS['text_tertiary']};
                padding: 12px 24px;
                margin-right: 5px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-size: 13px;
                font-weight: bold;
            }}
            QTabBar::tab:selected {{
                background: {COLORS['bg_card']};
                color: {COLORS['primary']};
                border-bottom: 3px solid {COLORS['primary']};
            }}
            QTabBar::tab:hover {{
                background: {COLORS['bg_light']};
            }}
        """)

        # ------------------- ONGLET SYSTÈME -------------------
        system_tab = QWidget()
        system_layout = QVBoxLayout()
        system_tab.setLayout(system_layout)
        system_layout.setSpacing(20)

        # Section Entreprise
        company_section = self.create_section(
            "🏢 Informations de l'Entreprise",
            [
                ("Nom de l'entreprise:", "My Company", "company_name"),
                ("Adresse:", "123 Rue Example, Alger", "address"),
                ("Téléphone:", "0555123456", "company_phone"),
                ("Email:", "contact@mycompany.dz", "company_email"),
            ]
        )
        system_layout.addWidget(company_section)

        # Section Devise et Taxes
        finance_section = self.create_section(
            "💰 Configuration Financière",
            [
                ("Devise:", "DA (Dinar Algérien)", "currency"),
                ("TVA (%):", "19", "vat"),
                ("Numéro de TVA:", "123456789012345", "vat_number"),
            ]
        )
        system_layout.addWidget(finance_section)

        system_layout.addStretch()
        tabs.addTab(system_tab, "🏢 Système")

        # ------------------- ONGLET APPARENCE -------------------
        appearance_tab = QWidget()
        appearance_layout = QVBoxLayout()
        appearance_tab.setLayout(appearance_layout)
        appearance_layout.setSpacing(20)

        # Section Thème
        theme_card = QFrame()
        theme_card.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {COLORS['bg_card']}, stop:1 #242424);
                border-radius: 12px;
                border: 1px solid {COLORS['border']};
                padding: 20px;
            }}
        """)
        theme_layout = QVBoxLayout()
        theme_card.setLayout(theme_layout)
        theme_layout.setSpacing(15)

        theme_title = QLabel("🎨 Thème de l'Application")
        theme_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        theme_title.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        theme_layout.addWidget(theme_title)

        theme_desc = QLabel("Choisissez le thème qui vous convient le mieux")
        theme_desc.setFont(QFont("Segoe UI", 12))
        theme_desc.setStyleSheet(f"color: {COLORS['text_tertiary']}; border: none;")
        theme_layout.addWidget(theme_desc)

        theme_select_layout = QHBoxLayout()
        theme_select_layout.setSpacing(15)

        theme_label = QLabel("Thème:")
        theme_label.setFont(QFont("Segoe UI", 13))
        theme_label.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["🌙 Mode Sombre", "☀️ Mode Clair"])
        self.theme_combo.setStyleSheet(INPUT_STYLE)
        self.theme_combo.setMinimumHeight(45)
        self.theme_combo.currentIndexChanged.connect(self.change_theme)

        theme_select_layout.addWidget(theme_label)
        theme_select_layout.addWidget(self.theme_combo)
        theme_select_layout.addStretch()

        theme_layout.addLayout(theme_select_layout)
        appearance_layout.addWidget(theme_card)

        # Section Police
        font_card = self.create_section(
            "🔤 Configuration de la Police",
            [
                ("Taille de police:", "14", "font_size"),
                ("Famille de police:", "Segoe UI", "font_family"),
            ]
        )
        appearance_layout.addWidget(font_card)

        appearance_layout.addStretch()
        tabs.addTab(appearance_tab, "🎨 Apparence")

        # ------------------- ONGLET UTILISATEUR -------------------
        user_tab = QWidget()
        user_layout = QVBoxLayout()
        user_tab.setLayout(user_layout)
        user_layout.setSpacing(20)

        # Section Compte
        account_section = self.create_section(
            "👤 Informations du Compte",
            [
                ("Nom d'utilisateur:", "admin", "username"),
                ("Email:", "admin@mycompany.dz", "user_email"),
                ("Rôle:", "Administrateur", "role"),
            ]
        )
        user_layout.addWidget(account_section)

        # Section Sécurité
        security_card = QFrame()
        security_card.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {COLORS['bg_card']}, stop:1 #242424);
                border-radius: 12px;
                border: 1px solid {COLORS['border']};
                padding: 20px;
            }}
        """)
        security_layout = QVBoxLayout()
        security_card.setLayout(security_layout)
        security_layout.setSpacing(15)

        security_title = QLabel("🔒 Sécurité")
        security_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        security_title.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        security_layout.addWidget(security_title)

        # Formulaire mot de passe
        password_form = QFormLayout()
        password_form.setSpacing(12)
        password_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.current_password = QLineEdit()
        self.current_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.current_password.setPlaceholderText("Mot de passe actuel")
        self.current_password.setStyleSheet(INPUT_STYLE)
        
        self.new_password = QLineEdit()
        self.new_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_password.setPlaceholderText("Nouveau mot de passe")
        self.new_password.setStyleSheet(INPUT_STYLE)
        
        self.confirm_password = QLineEdit()
        self.confirm_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password.setPlaceholderText("Confirmer le mot de passe")
        self.confirm_password.setStyleSheet(INPUT_STYLE)

        password_form.addRow("Mot de passe actuel:", self.current_password)
        password_form.addRow("Nouveau mot de passe:", self.new_password)
        password_form.addRow("Confirmation:", self.confirm_password)

        security_layout.addLayout(password_form)

        # Bouton changer mot de passe
        change_password_btn = QPushButton("🔑 Changer le Mot de Passe")
        change_password_btn.setStyleSheet(BUTTON_STYLES['primary'])
        change_password_btn.setMinimumHeight(45)
        change_password_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        security_layout.addWidget(change_password_btn)

        user_layout.addWidget(security_card)
        user_layout.addStretch()
        tabs.addTab(user_tab, "👤 Utilisateur")

        layout.addWidget(tabs)

        # ------------------- ACTION BUTTONS -------------------
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        layout.addLayout(btn_layout)

        self.reset_btn = QPushButton("♻️ Réinitialiser")
        self.reset_btn.setStyleSheet(BUTTON_STYLES['secondary'])
        self.reset_btn.setMinimumHeight(45)
        self.reset_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.save_btn = QPushButton("💾 Enregistrer les Paramètres")
        self.save_btn.setStyleSheet(BUTTON_STYLES['success'])
        self.save_btn.setMinimumHeight(45)
        self.save_btn.setFixedWidth(250)
        self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        btn_layout.addWidget(self.reset_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.save_btn)

    def create_section(self, title, fields):
        """Crée une section de paramètres avec des champs"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {COLORS['bg_card']}, stop:1 #242424);
                border-radius: 12px;
                border: 1px solid {COLORS['border']};
                padding: 20px;
            }}
        """)
        card_layout = QVBoxLayout()
        card.setLayout(card_layout)
        card_layout.setSpacing(15)

        # Titre de la section
        section_title = QLabel(title)
        section_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        section_title.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")
        card_layout.addWidget(section_title)

        # Formulaire
        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form.setFormAlignment(Qt.AlignmentFlag.AlignLeft)

        for label_text, default_value, field_name in fields:
            label = QLabel(label_text)
            label.setFont(QFont("Segoe UI", 12))
            label.setStyleSheet(f"color: {COLORS['text_tertiary']}; border: none;")
            
            field = QLineEdit(default_value)
            field.setStyleSheet(INPUT_STYLE)
            field.setMinimumHeight(40)
            setattr(self, field_name, field)
            
            form.addRow(label, field)

        card_layout.addLayout(form)
        return card

    # ------------------- CHANGER THÈME -------------------
    def change_theme(self, index):
        if index == 0:
            qdarktheme.setup_theme("dark")
        else:
            qdarktheme.setup_theme("light")