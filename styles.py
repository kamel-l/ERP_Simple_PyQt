"""
Module de styles réutilisables pour l'application
Design moderne et professionnel
"""

# ==================== COULEURS ====================
COLORS = {
    'primary': '#A855F7',        # Violet améthyste
    'primary_dark': '#9333EA',
    'secondary': '#EC4899',      # Rose magenta
    'success': '#34D399',        # Vert menthe
    'warning': '#FBBF24',        # Or
    'danger': '#F472B6',         # Rose rouge
    'info': '#60A5FA',           # Bleu pervenche
    'bg_dark': '#415a77',        # Violet très sombre
    'bg_medium': '#2A1A33',
    'bg_light': '#3D2847',
    'bg_card': '#2A1A33',
    'text_primary': '#FAF5FF',
    'text_secondary': '#F3E8FF',
    'text_tertiary': '#D8B4FE',
    'border': '#4C2F5E',
    'border_light': '#5E3A73',
    'accent' : '#32D599' ,
    'accent_light' : '#60A5FA' ,
    'bg_card_hover' : '#A815F3' ,
    'bg_input' : '#F438B6' ,
    'BG_PAGE'   : "#0F1117",
    'BG_CARD'   : "#1A1D27",
    'BG_DEEP'   : "#13151F",
    'BORDER'    : "rgba(255,255,255,0.07)",
    'TXT_PRI'   : "#F1F5F9",
    'TXT_SEC'   : "rgba(255,255,255,0.45)",
    'TXT_MUTED' : "rgba(255,255,255,0.25)", 
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
        background-color: {COLORS['BG_CARD']};
        alternate-background-color: {COLORS['BG_CARD']};
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
    QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit {{
        background-color: {COLORS['bg_light']};
        border: 2px solid {COLORS['border']};
        border-radius: 8px;
        padding: 8px 12px;
        color: {COLORS['text_primary']};
        font-size: 14px;
        min-height: 36px;
    }}
    QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus, QTextEdit:focus {{
        border: 2px solid {COLORS['primary']};
        background-color: {COLORS['bg_medium']};
    }}
    QLineEdit:hover, QComboBox:hover, QSpinBox:hover, QDoubleSpinBox:hover, QTextEdit:hover {{
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
    QSpinBox::up-button, QDoubleSpinBox::up-button {{
        subcontrol-origin: border;
        subcontrol-position: top right;
        width: 20px;
        border-left: 1px solid {COLORS['border']};
        border-bottom: 1px solid {COLORS['border']};
        border-top-right-radius: 8px;
        background-color: {COLORS['bg_medium']};
    }}
    QSpinBox::down-button, QDoubleSpinBox::down-button {{
        subcontrol-origin: border;
        subcontrol-position: bottom right;
        width: 20px;
        border-left: 1px solid {COLORS['border']};
        border-bottom-right-radius: 8px;
        background-color: {COLORS['bg_medium']};
    }}
    QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
    QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{
        background-color: {COLORS['primary']};
    }}
"""

# ==================== STYLES DE BOUTONS RADIO ====================
RADIO_STYLE = f"""
    QRadioButton {{
        color: {COLORS['text_primary']};
        font-size: 14px;
        padding: 10px;
        spacing: 10px;
    }}
    QRadioButton::indicator {{
        width: 20px;
        height: 20px;
        border-radius: 10px;
        border: 2px solid {COLORS['border']};
        background-color: {COLORS['bg_light']};
    }}
    QRadioButton::indicator:checked {{
        background-color: {COLORS['primary']};
        border-color: {COLORS['primary']};
        image: url(:/icons/check.png);
    }}
    QRadioButton::indicator:hover {{
        border-color: {COLORS['primary']};
        background-color: {COLORS['bg_medium']};
    }}
"""

# ==================== STYLES DE DIALOGUES ====================
DIALOG_STYLE = f"""
    QDialog {{
        background-color: {COLORS['bg_medium']};
    }}
    QLabel {{
        color: {COLORS['text_primary']};
        font-size: 13px;
    }}
    QLabel#title {{
        font-size: 20px;
        font-weight: bold;
        color: white;
    }}
    QLabel#subtitle {{
        font-size: 11px;
        color: {COLORS['text_tertiary']};
    }}
    QFrame#header {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 {COLORS['success']}, stop:1 {COLORS['primary']});
        border-radius: 10px;
        padding: 20px;
    }}
    QFrame#amountFrame {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 {COLORS['bg_card']}, stop:1 #242424);
        border-radius: 12px;
        border: 3px solid {COLORS['success']};
        padding: 20px;
    }}
    QFrame#paymentFrame {{
        background: {COLORS['bg_card']};
        border-radius: 10px;
        padding: 20px;
    }}
    QFrame#detailsFrame {{
        background: {COLORS['bg_card']};
        border-radius: 8px;
        padding: 15px;
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


# ==================== STYLES SETTINGS (anciennement locaux à settings.py) ====================

# Couleurs palette sombre cohérente (dashboard / settings / statistics)
DARK_COLORS = {
    'bg_page':   "#0F1117",
    'bg_card':   "#1A1D27",
    'bg_deep':   "#13151F",
    'border':    "rgba(255,255,255,0.07)",
    'txt_pri':   "#F1F5F9",
    'txt_sec':   "rgba(255,255,255,0.45)",
    'txt_muted': "rgba(255,255,255,0.25)",
}

SETTINGS_CARD_STYLE = """
    QFrame {
        background: #1A1D27;
        border-radius: 14px;
        border: 1px solid rgba(255,255,255,0.07);
    }
"""

SETTINGS_INPUT_STYLE = """
    QLineEdit {
        background: #0F1117;
        color: #E2E8F0;
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 8px;
        padding: 10px 14px;
        font-size: 13px;
        selection-background-color: #3B82F6;
    }
    QLineEdit:focus {
        border: 1px solid #3B82F6;
        background: #111827;
    }
"""

SETTINGS_COMBO_STYLE = """
    QComboBox {
        background: #0F1117;
        color: #E2E8F0;
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 8px;
        padding: 10px 14px;
        font-size: 13px;
        min-height: 42px;
    }
    QComboBox:focus { border: 1px solid #3B82F6; }
    QComboBox::drop-down { border: none; width: 30px; }
    QComboBox QAbstractItemView {
        background: #1A1D27;
        color: #E2E8F0;
        selection-background-color: #3B82F6;
        border: 1px solid rgba(255,255,255,0.10);
    }
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
    {DIALOG_STYLE}
    {RADIO_STYLE}
"""