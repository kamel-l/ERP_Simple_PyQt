# ============================
#   STYLES.PY - DARK PREMIUM
#   Theme: Dark SaaS 2025
#   Font: Inter
#   Accent: Cyan (#00BCD4)
# ============================

COLORS = {
    "accent": "#00BCD4",
    "accent_light": "#26D8F1",
    "accent_dark": "#0091A6",

    # Alias primary/secondary utilisés dans sales_history.py
    "primary": "#00BCD4",       # ✅ AJOUTÉ
    "secondary": "#0091A6",     # ✅ AJOUTÉ (remplace l'ancienne valeur purple)

    # Text
    "text_primary": "#FFFFFF",
    "text_secondary": "#BFC6D0",
    "text_tertiary": "#8A8F99",

    # Backgrounds
    "bg_dark": "#10141A",
    "bg_medium": "#13181F",     # ✅ AJOUTÉ — utilisé dans sales_history.py (QDialog)
    "bg_light": "#1E252E",      # ✅ AJOUTÉ — utilisé dans sales_history.py (info rows)
    "bg_card": "#161B22",
    "bg_card_hover": "#1E252E",
    "bg_input": "#1A1F26",

    # Borders
    "border": "#2A313C",
    "border_strong": "#3A424F",

    # KPI colors
    "success": "#4CAF50",
    "warning": "#FFC107",
    "danger": "#FF5252",
    "info": "#29B6F6",
    "purple": "#9C27B0",        # ✅ AJOUTÉ (ancienne valeur de secondary)
}

# =======================================
#      Global StyleSheet (Dark Premium)
# =======================================

GLOBAL_STYLE = f"""
    * {{
        font-family: Inter;
        color: {COLORS['text_primary']};
    }}

    QWidget {{
        background-color: {COLORS['bg_dark']};
    }}

    QFrame {{
        background-color: {COLORS['bg_card']};
        border: 1px solid {COLORS['border']};
        border-radius: 10px;
    }}

    QLabel {{
        color: {COLORS['text_primary']};
        font-size: 14px;
    }}

    QLineEdit, QComboBox {{
        background-color: {COLORS['bg_input']};
        border: 1px solid {COLORS['border_strong']};
        padding: 8px;
        border-radius: 6px;
        color: white;
    }}

    QPushButton {{
        background-color: {COLORS['accent']};
        color: white;
        padding: 10px;
        border-radius: 6px;
        font-size: 14px;
        font-weight: bold;
        border: none;
    }}

    QPushButton:hover {{
        background-color: {COLORS['accent_light']};
    }}

    QPushButton:pressed {{
        background-color: {COLORS['accent_dark']};
    }}

    QScrollArea {{
        background-color: transparent;
        border: none;
    }}

    /* Scrollbar */
    QScrollBar:vertical {{
        width: 10px;
        background: transparent;
        margin: 0px;
    }}
    QScrollBar::handle:vertical {{
        background: {COLORS['accent_dark']};
        border-radius: 5px;
        min-height: 30px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {COLORS['accent_light']};
    }}

    /* Table */
    QTableWidget {{
        background-color: {COLORS['bg_card']};
        alternate-background-color: {COLORS['bg_card_hover']};
        gridline-color: {COLORS['border']};
        border-radius: 8px;
    }}

    QHeaderView::section {{
        background-color: {COLORS['accent']};
        color: black;
        font-weight: bold;
        padding: 8px;
        border: none;
    }}

    QTableWidget::item:hover {{
        background-color: {COLORS['bg_card_hover']};
    }}
"""

# =======================================
#   BUTTON_STYLES — utilisé dans sales_history.py
# =======================================
BUTTON_STYLES = {
    "primary": f"""
        QPushButton {{
            background-color: {COLORS['accent']};
            color: black;
            padding: 10px 20px;
            border-radius: 8px;
            font-size: 13px;
            font-weight: bold;
            border: none;
        }}
        QPushButton:hover {{
            background-color: {COLORS['accent_light']};
        }}
        QPushButton:pressed {{
            background-color: {COLORS['accent_dark']};
        }}
    """,
    "secondary": f"""
        QPushButton {{
            background-color: {COLORS['bg_card']};
            color: {COLORS['text_primary']};
            padding: 10px 20px;
            border-radius: 8px;
            font-size: 13px;
            font-weight: bold;
            border: 1px solid {COLORS['border_strong']};
        }}
        QPushButton:hover {{
            background-color: {COLORS['bg_card_hover']};
            border-color: {COLORS['accent']};
            color: {COLORS['accent']};
        }}
        QPushButton:pressed {{
            background-color: {COLORS['bg_dark']};
        }}
    """,
    "danger": f"""
        QPushButton {{
            background-color: {COLORS['danger']};
            color: white;
            padding: 10px 20px;
            border-radius: 8px;
            font-size: 13px;
            font-weight: bold;
            border: none;
        }}
        QPushButton:hover {{
            background-color: #ff6b6b;
        }}
        QPushButton:pressed {{
            background-color: #cc0000;
        }}
    """,
    "success": f"""
        QPushButton {{
            background-color: {COLORS['success']};
            color: white;
            padding: 10px 20px;
            border-radius: 8px;
            font-size: 13px;
            font-weight: bold;
            border: none;
        }}
        QPushButton:hover {{
            background-color: #66BB6A;
        }}
        QPushButton:pressed {{
            background-color: #388E3C;
        }}
    """,
}

# =======================================
#   INPUT_STYLE — utilisé dans sales_history.py
# =======================================
INPUT_STYLE = f"""
    QLineEdit, QComboBox {{
        background-color: {COLORS['bg_input']};
        border: 1px solid {COLORS['border_strong']};
        border-radius: 8px;
        padding: 8px 12px;
        color: {COLORS['text_primary']};
        font-size: 13px;
        min-height: 20px;
    }}
    QLineEdit:focus, QComboBox:focus {{
        border: 1px solid {COLORS['accent']};
    }}
    QLineEdit::placeholder {{
        color: {COLORS['text_tertiary']};
    }}
    QComboBox::drop-down {{
        border: none;
        padding-right: 8px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {COLORS['bg_card']};
        border: 1px solid {COLORS['border']};
        selection-background-color: {COLORS['accent_dark']};
        color: {COLORS['text_primary']};
        padding: 4px;
    }}
"""

# =======================================
#   TABLE_STYLE — utilisé dans sales_history.py
# =======================================
TABLE_STYLE = f"""
    QTableWidget {{
        background-color: {COLORS['bg_card']};
        alternate-background-color: {COLORS['bg_light']};
        gridline-color: {COLORS['border']};
        border: none;
        border-radius: 8px;
        font-size: 13px;
        color: {COLORS['text_primary']};
        selection-background-color: {COLORS['accent_dark']};
    }}
    QTableWidget::item {{
        padding: 8px;
        border-bottom: 1px solid {COLORS['border']};
    }}
    QTableWidget::item:hover {{
        background-color: {COLORS['bg_card_hover']};
    }}
    QTableWidget::item:selected {{
        background-color: {COLORS['accent_dark']};
        color: white;
    }}
    QScrollBar:vertical {{
        width: 8px;
        background: transparent;
    }}
    QScrollBar::handle:vertical {{
        background: {COLORS['accent_dark']};
        border-radius: 4px;
        min-height: 20px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {COLORS['accent']};
    }}
"""