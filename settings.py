from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton,
    QLineEdit, QScrollArea
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from styles import COLORS
from db_manager import get_database


class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()

        self.db = get_database()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(25)

        # ----------------------------------------------------------
        # HEADER
        # ----------------------------------------------------------
        header = QHBoxLayout()
        title = QLabel("⚙️ Paramètres")
        title.setFont(QFont("Inter", 32, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['accent']};")
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)

        # ----------------------------------------------------------
        # SETTINGS FORM
        # ----------------------------------------------------------
        form_card = QFrame()
        form_card.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_card']};
                border-radius: 12px;
                border: 1px solid {COLORS['border']};
            }}
        """)
        form_layout = QVBoxLayout(form_card)
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(12)

        form_title = QLabel("Paramètres de l'application")
        form_title.setFont(QFont("Inter", 18, QFont.Weight.Bold))
        form_title.setStyleSheet(f"color: {COLORS['accent']};")
        form_layout.addWidget(form_title)

        # Inputs
        self.input_app_name = QLineEdit()
        self.input_app_name.setPlaceholderText("Nom de l'application")
        form_layout.addWidget(self.input_app_name)

        self.input_company = QLineEdit()
        self.input_company.setPlaceholderText("Nom de la société")
        form_layout.addWidget(self.input_company)

        self.input_currency = QLineEdit()
        self.input_currency.setPlaceholderText("Devise (ex: DA)")
        form_layout.addWidget(self.input_currency)

        # Buttons row
        btn_row = QHBoxLayout()

        save_btn = QPushButton("💾 Enregistrer")
        save_btn.clicked.connect(self.save_settings)
        btn_row.addWidget(save_btn)

        reset_btn = QPushButton("♻️ Réinitialiser")
        reset_btn.clicked.connect(self.load_settings)
        reset_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['danger']};
                color: white;
                padding: 10px;
                border-radius: 6px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: #ff6b6b;
            }}
        """)
        btn_row.addWidget(reset_btn)

        form_layout.addLayout(btn_row)
        layout.addWidget(form_card)

        scroll.setWidget(container)
        page_layout = QVBoxLayout(self)
        page_layout.addWidget(scroll)

        self.load_settings()

    # ============================================================
    #                     DATA HANDLING
    # ============================================================
    def load_settings(self):
        settings = self.db.get_settings() or {}
        self.input_app_name.setText(settings.get("app_name", "ERP System"))
        self.input_company.setText(settings.get("company_name", "My Company"))
        self.input_currency.setText(settings.get("currency", "DA"))

    def save_settings(self):
        self.db.save_settings(
            app_name=self.input_app_name.text(),
            company_name=self.input_company.text(),
            currency=self.input_currency.text()
        )