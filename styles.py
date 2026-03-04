"""
Module de styles réutilisables pour l'application
Design moderne et vif — Palette Bleu Électrique + Cyan
"""

# ==================== COULEURS ====================
COLORS = {
    # Couleurs principales Blue & Purple
    'primary':        '#6366F1',        # Bleu indigo vif
    'primary_dark':   '#4F46E5',        # Bleu indigo foncé
    'primary_light':  '#818CF8',        # Bleu indigo clair
    'secondary':      '#A855F7',        # Purple éclatant
    'secondary_dark': '#9333EA',        # Purple foncé

    # Statuts
    'success':        '#10B981',        # Vert succès
    'warning':        '#F59E0B',        # Jaune vif
    'danger':         '#EF4444',        # Rouge vif
    'info':           '#06B6D4',        # Cyan info

    # Fonds bleu profond
    'bg_dark':        '#0F172A',        # Fond principal
    'bg_medium':      '#1E293B',        # Fond cartes
    'bg_light':       '#334155',        # Fond hover / inputs
    'bg_card':        '#1E293B',

    # Textes
    'text_primary':   '#F8FAFC',        # Blanc froid
    'text_secondary': '#CBD5E1',        # Gris-bleu doux
    'text_tertiary':  '#818CF8',        # Bleu indigo (accents texte)

    # Bordures
    'border':         'rgba(99,102,241,0.20)',        # Bordure bleu subtile
    'border_light':   '#A855F7',        # Bordure purple hover

    # Inputs
    'bg_input':       '#1E293B',

    # Alias uppercase
    'BG_PAGE':        '#0F172A',
    'BG_CARD':        '#1E293B',
    'BG_DEEP':        '#0A0F1F',
    'BORDER':         'rgba(99,102,241,0.20)',
    'TXT_PRI':        '#F8FAFC',
    'TXT_SEC':        'rgba(203,213,225,0.85)',
    'TXT_MUTED':      'rgba(126,139,141,0.50)',
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
                stop:0 {COLORS['primary_light']}, stop:1 {COLORS['primary']});
        }}
        QPushButton:pressed {{
            background: {COLORS['primary_dark']};
        }}
        QPushButton:disabled {{
            background: #1A7272;
            color: #555570;
        }}
    """,

    'success': f"""
        QPushButton {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {COLORS['success']}, stop:1 #059669);
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
                stop:0 #34D399, stop:1 {COLORS['success']});
        }}
        QPushButton:pressed {{
            background: #059669;
        }}
    """,

    'danger': f"""
        QPushButton {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {COLORS['danger']}, stop:1 #DC2626);
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
                stop:0 #F87171, stop:1 {COLORS['danger']});
        }}
        QPushButton:pressed {{
            background: #DC2626;
        }}
    """,

    'secondary': f"""
        QPushButton {{
            background: transparent;
            color: {COLORS['secondary']};
            border: 2px solid {COLORS['secondary']};
            border-radius: 8px;
            padding: 10px 20px;
            font-size: 14px;
            font-weight: bold;
            min-height: 36px;
        }}
        QPushButton:hover {{
            background: rgba(168,85,247,0.12);
            border-color: #D8B4FE;
            color: #D8B4FE;
        }}
        QPushButton:pressed {{
            background: rgba(168,85,247,0.25);
        }}
    """,
}

# ==================== STYLES DE CARTES ====================
CARD_STYLE = f"""
    QFrame {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 {COLORS['bg_card']}, stop:1 {COLORS['bg_dark']});
        border-radius: 12px;
        border: 1px solid {COLORS['border']};
    }}
    QFrame:hover {{
        border: 1px solid {COLORS['primary']};
    }}
"""

# ==================== STYLES DE TABLEAUX ====================
TABLE_STYLE = f"""
    QTableWidget {{
        background-color: {COLORS['BG_CARD']};
        alternate-background-color: #0F5252;
        border: 1px solid {COLORS['border']};
        border-radius: 8px;
        gridline-color: #1A6B6B;
        color: {COLORS['text_primary']};
        selection-background-color: {COLORS['primary_dark']};
    }}
    QTableWidget::item {{
        padding: 8px;
        border: none;
    }}
    QTableWidget::item:selected {{
        background-color: {COLORS['primary_dark']};
        color: white;
    }}
    QTableWidget::item:hover {{
        background-color: {COLORS['bg_light']};
    }}
    QHeaderView::section {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #0F5555, stop:1 {COLORS['bg_medium']});
        color: {COLORS['primary_light']};
        padding: 10px;
        border: none;
        border-bottom: 2px solid {COLORS['primary']};
        font-weight: bold;
        font-size: 13px;
    }}
    QHeaderView::section:hover {{
        background: {COLORS['bg_light']};
        color: {COLORS['secondary']};
    }}
"""

# ==================== STYLES DE CHAMPS DE SAISIE ====================
INPUT_STYLE = f"""
    QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit {{
        background-color: {COLORS['secondary_dark']};
        border: 2px solid {COLORS['border']};
        border-radius: 8px;
        padding: 8px 12px;
        color: {COLORS['text_primary']};
        font-size: 14px;
        min-height: 36px;
    }}
    QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus, QTextEdit:focus {{
        border: 2px solid {COLORS['primary']};
        background-color: {COLORS['bg_light']};
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
        border-top: 5px solid {COLORS['secondary']};
        margin-right: 10px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {COLORS['bg_light']};
        border: 1px solid {COLORS['border']};
        selection-background-color: {COLORS['primary_dark']};
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
        border-color: {COLORS['secondary']};
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
        color: {COLORS['secondary']};
    }}
    QFrame#header {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 {COLORS['primary_dark']}, stop:1 {COLORS['secondary_dark']});
        border-radius: 10px;
        padding: 20px;
    }}
    QFrame#amountFrame {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 {COLORS['bg_card']}, stop:1 {COLORS['bg_dark']});
        border-radius: 12px;
        border: 3px solid {COLORS['primary']};
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
        background: {COLORS['primary']};
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
        background: {COLORS['primary']};
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
                stop:0 {COLORS['bg_card']}, stop:1 {COLORS['bg_dark']});
            border-radius: 12px;
            border: 1px solid {COLORS['border']};
            border-left: 4px solid {color};
        }}
        QFrame:hover {{
            border: 1px solid {COLORS['primary']};
            border-left: 4px solid {color};
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {COLORS['bg_medium']}, stop:1 {COLORS['bg_dark']});
        }}
    """


# ==================== STYLES SETTINGS ====================

DARK_COLORS = {
    'bg_page':   '#0D4A4A',
    'bg_card':   '#155E5E',
    'bg_deep':   '#0A3A3A',
    'border':    'rgba(46,204,113,0.20)',
    'txt_pri':   '#FFFFFF',
    'txt_sec':   'rgba(213,232,232,0.85)',
    'txt_muted': 'rgba(168,213,213,0.50)',
}

SETTINGS_CARD_STYLE = """
    QFrame {
        background: #155E5E;
        border-radius: 14px;
        border: 1px solid rgba(46,204,113,0.20);
    }
"""

SETTINGS_INPUT_STYLE = """
    QLineEdit {
        background: #0D4A4A;
        color: #FFFFFF;
        border: 1px solid rgba(46,204,113,0.30);
        border-radius: 8px;
        padding: 10px 14px;
        font-size: 13px;
        selection-background-color: #2ECC71;
    }
    QLineEdit:focus {
        border: 1px solid #2ECC71;
        background: #155E5E;
    }
"""

SETTINGS_COMBO_STYLE = """
    QComboBox {
        background: #0D4A4A;
        color: #FFFFFF;
        border: 1px solid rgba(46,204,113,0.30);
        border-radius: 8px;
        padding: 10px 14px;
        font-size: 13px;
        min-height: 42px;
    }
    QComboBox:focus { border: 1px solid #2ECC71; }
    QComboBox::drop-down { border: none; width: 30px; }
    QComboBox QAbstractItemView {
        background: #155E5E;
        color: #FFFFFF;
        selection-background-color: #27AE60;
        border: 1px solid rgba(46,204,113,0.20);
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