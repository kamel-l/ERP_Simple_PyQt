"""
Module de styles réutilisables pour l'application
Design moderne et professionnel
"""

# ==================== COULEURS ====================
COLORS = {
    'primary': '#3B82F6',        # Bleu royal
    'primary_dark': '#2563EB',
    'secondary': '#A855F7',      # Violet pourpre
    'success': '#22C55E',        # Vert
    'warning': '#FBBF24',        # Jaune or
    'danger': '#F87171',         # Rouge doux
    'info': '#38BDF8',           # Bleu ciel
    'bg_dark': '#0A0E1A',        # Bleu nuit profond
    'bg_medium': '#141B2D',
    'bg_light': '#1E2A42',
    'bg_card': '#141B2D',
    'text_primary': '#F8FAFC',
    'text_secondary': '#E2E8F0',
    'text_tertiary': '#94A3B8',
    'border': '#2D3A54',
    'border_light': '#3B4B68',
}

# ==================== STYLES DE BOUTONS ====================
BUTTON_STYLES = {
    'primary': f"""
        QPushButton {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {COLORS['primary']}, stop:1 {COLORS['primary_dark']});
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            font-size: 14px;
            font-weight: bold;
            min-height: 36px;
        }}
        QPushButton:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #1A94FF, stop:1 #0A84FF);
        }}
        QPushButton:pressed {{
            background: {COLORS['primary_dark']};
        }}
        QPushButton:disabled {{
            background: #3A3A3C;
            color: #8E8E93;
        }}
    """,
    
    'success': f"""
        QPushButton {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {COLORS['success']}, stop:1 #28C248);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            font-size: 14px;
            font-weight: bold;
            min-height: 36px;
        }}
        QPushButton:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #40E168, stop:1 {COLORS['success']});
        }}
        QPushButton:pressed {{
            background: #28C248;
        }}
    """,
    
    'danger': f"""
        QPushButton {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {COLORS['danger']}, stop:1 #D93D32);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            font-size: 14px;
            font-weight: bold;
            min-height: 36px;
        }}
        QPushButton:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #FF5549, stop:1 {COLORS['danger']});
        }}
        QPushButton:pressed {{
            background: #D93D32;
        }}
    """,
    
    'secondary': f"""
        QPushButton {{
            background: transparent;
            color: {COLORS['primary']};
            border: 2px solid {COLORS['primary']};
            border-radius: 8px;
            padding: 10px 20px;
            font-size: 14px;
            font-weight: bold;
            min-height: 36px;
        }}
        QPushButton:hover {{
            background: rgba(10, 132, 255, 0.1);
            border-color: #1A94FF;
        }}
        QPushButton:pressed {{
            background: rgba(10, 132, 255, 0.2);
        }}
    """,
}

# ==================== STYLES DE CARTES ====================
CARD_STYLE = f"""
    QFrame {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 {COLORS['bg_card']}, stop:1 #242424);
        border-radius: 12px;
        border: 1px solid {COLORS['border']};
    }}
    QFrame:hover {{
        border: 1px solid {COLORS['border_light']};
    }}
"""

# ==================== STYLES DE TABLEAUX ====================
TABLE_STYLE = f"""
    QTableWidget {{
        background-color: {COLORS['bg_medium']};
        alternate-background-color: {COLORS['bg_light']};
        border: 1px solid {COLORS['border']};
        border-radius: 8px;
        gridline-color: {COLORS['border']};
        color: {COLORS['text_primary']};
        selection-background-color: {COLORS['primary']};
    }}
    QTableWidget::item {{
        padding: 8px;
        border: none;
    }}
    QTableWidget::item:selected {{
        background-color: {COLORS['primary']};
        color: white;
    }}
    QTableWidget::item:hover {{
        background-color: {COLORS['bg_light']};
    }}
    QHeaderView::section {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 {COLORS['bg_light']}, stop:1 {COLORS['bg_medium']});
        color: {COLORS['text_primary']};
        padding: 10px;
        border: none;
        border-bottom: 2px solid {COLORS['primary']};
        font-weight: bold;
        font-size: 13px;
    }}
    QHeaderView::section:hover {{
        background: {COLORS['bg_light']};
    }}
"""

# ==================== STYLES DE CHAMPS DE SAISIE ====================
INPUT_STYLE = f"""
    QLineEdit, QComboBox {{
        background-color: {COLORS['bg_light']};
        border: 2px solid {COLORS['border']};
        border-radius: 8px;
        padding: 8px 12px;
        color: {COLORS['text_primary']};
        font-size: 14px;
        min-height: 36px;
    }}
    QLineEdit:focus, QComboBox:focus {{
        border: 2px solid {COLORS['primary']};
        background-color: {COLORS['bg_medium']};
    }}
    QLineEdit:hover, QComboBox:hover {{
        border: 2px solid {COLORS['border_light']};
    }}
    QComboBox::drop-down {{
        border: none;
        width: 30px;
    }}
    QComboBox::down-arrow {{
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 5px solid {COLORS['text_tertiary']};
        margin-right: 10px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {COLORS['bg_light']};
        border: 1px solid {COLORS['border']};
        selection-background-color: {COLORS['primary']};
        color: {COLORS['text_primary']};
    }}
"""

# ==================== STYLES DE DIALOGUES ====================
DIALOG_STYLE = f"""
    QDialog {{
        background-color: {COLORS['bg_medium']};
    }}
    QLabel {{
        color: {COLORS['text_primary']};
    }}
"""

# ==================== STYLES DE SCROLLBAR ====================
SCROLLBAR_STYLE = f"""
    QScrollBar:vertical {{
        border: none;
        background: {COLORS['bg_medium']};
        width: 10px;
        margin: 0px;
    }}
    QScrollBar::handle:vertical {{
        background: {COLORS['bg_light']};
        border-radius: 5px;
        min-height: 20px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {COLORS['border_light']};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    QScrollBar:horizontal {{
        border: none;
        background: {COLORS['bg_medium']};
        height: 10px;
        margin: 0px;
    }}
    QScrollBar::handle:horizontal {{
        background: {COLORS['bg_light']};
        border-radius: 5px;
        min-width: 20px;
    }}
    QScrollBar::handle:horizontal:hover {{
        background: {COLORS['border_light']};
    }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0px;
    }}
"""

# ==================== FONCTION POUR CRÉER UNE CARTE KPI ====================
def get_kpi_card_style(color):
    """Retourne le style pour une carte KPI avec la couleur spécifiée"""
    return f"""
        QFrame {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {COLORS['bg_card']}, stop:1 #242424);
            border-radius: 12px;
            border: 1px solid {COLORS['border']};
            border-left: 4px solid {color};
        }}
        QFrame:hover {{
            border: 1px solid {COLORS['border_light']};
            border-left: 4px solid {color};
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #323232, stop:1 #2A2A2A);
        }}
    """

# ==================== STYLES GLOBAUX ====================
GLOBAL_STYLE = f"""
    QWidget {{
        background-color: {COLORS['bg_dark']};
        color: {COLORS['text_primary']};
        font-family: 'Segoe UI', Arial, sans-serif;
    }}
    
    {INPUT_STYLE}
    {TABLE_STYLE}
    {SCROLLBAR_STYLE}
"""