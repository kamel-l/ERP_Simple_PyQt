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

    # Text
    "text_primary": "#FFFFFF",
    "text_secondary": "#BFC6D0",
    "text_tertiary": "#8A8F99",

    # Backgrounds
    "bg_dark": "#10141A",
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
    "secondary": "#9C27B0",
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