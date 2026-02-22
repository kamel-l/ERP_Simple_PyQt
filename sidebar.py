from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QFrame, QSizePolicy
)
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt
from styles import COLORS


class SidebarButton(QPushButton):
    def __init__(self, text, icon_path=None):
        super().__init__()

        self.text = text
        self.icon_path = icon_path

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(48)
        self.setFont(QFont("Inter", 13, QFont.Weight.Medium))
        self.setStyleSheet(self.default_style())

        if icon_path:
            self.setIcon(QIcon(icon_path))
            self.setIconSize(Qt.QSize(22, 22))

        self.setText(f"   {text}")

    def default_style(self):
        return f"""
            QPushButton {{
                background: transparent;
                color: {COLORS['text_secondary']};
                text-align: left;
                padding-left: 14px;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background: {COLORS['bg_card_hover']};
                color: {COLORS['accent_light']};
            }}
        """

    def active_style(self):
        return f"""
            QPushButton {{
                background: {COLORS['bg_card']};
                color: {COLORS['accent']};
                border-left: 4px solid {COLORS['accent']};
                text-align: left;
                padding-left: 14px;
                border-radius: 0;
            }}
        """

    def set_active(self, active: bool):
        if active:
            self.setStyleSheet(self.active_style())
        else:
            self.setStyleSheet(self.default_style())


class Sidebar(QWidget):
    def __init__(self):
        super().__init__()

        self.setFixedWidth(220)
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['bg_card']};
                border-right: 1px solid {COLORS['border']};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 18, 12, 18)
        layout.setSpacing(14)

        # -------- Title --------
        app_title = QLabel("ERP System")
        app_title.setFont(QFont("Inter", 18, QFont.Weight.Bold))
        app_title.setStyleSheet(f"color: {COLORS['accent']}; padding: 8px;")
        app_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(app_title)

        layout.addSpacing(16)

        # -------- Buttons --------
        self.buttons = {}

        self.add_button(layout, "Dashboard", "icons/home.png")
        self.add_button(layout, "Produits", "icons/box.png")
        self.add_button(layout, "Clients", "icons/users.png")
        self.add_button(layout, "Ventes", "icons/cart.png")
        self.add_button(layout, "Achats", "icons/buy.png")
        self.add_button(layout, "Statistiques", "icons/stats.png")
        self.add_button(layout, "Paramètres", "icons/settings.png")

        layout.addStretch()

    def add_button(self, layout, name, icon_path):
        btn = SidebarButton(name, icon_path)
        layout.addWidget(btn)
        self.buttons[name] = btn

    def set_active(self, name):
        for key, btn in self.buttons.items():
            btn.set_active(key == name)