"""
Module de styles réutilisables pour l'application
Design moderne et vif — Palette Bleu Électrique + Cyan
Fond anthracite #1E1E2E
"""

# ==================== COULEURS ====================
COLORS = {
    # Couleurs principales vives
    'primary':        '#00B4FF',        # Bleu électrique vif
    'primary_dark':   '#0090DD',        # Bleu électrique foncé
    'primary_light':  '#40CAFF',        # Bleu électrique clair
    'secondary':      '#00E5FF',        # Cyan éclatant
    'secondary_dark': '#00B8CC',        # Cyan foncé

    # Statuts
    'success':        '#00E676',        # Vert néon
    'warning':        '#FFD600',        # Jaune vif
    'danger':         '#FF1744',        # Rouge vif
    'info':           '#00B0FF',        # Bleu info

    # Fonds anthracite — plus clairs, respirants
    'bg_dark':        '#1E1E2E',        # Fond principal
    'bg_medium':      '#252535',        # Fond cartes
    'bg_light':       '#2E2E45',        # Fond hover / inputs
    'bg_card':        '#252535',

    # Textes
    'text_primary':   '#F0F4FF',        # Blanc bleuté
    'text_secondary': '#A0AACC',        # Gris-bleu doux
    'text_tertiary':  '#00E5FF',        # Cyan (accents texte)

    # Bordures
    'border':         "#F3F4F8",        # Bordure subtile
    'border_light':   '#00B4FF',        # Bordure hover bleu

    # Inputs — fond anthracite neutre (PLUS DE ROSE !)
    'bg_input':       '#252535',

    # Alias uppercase (utilisés dans TABLE_STYLE / INPUT_STYLE)
    'BG_PAGE':        '#1E1E2E',
    'BG_CARD':        '#252535',
    'BG_DEEP':        '#16161F',
    'BORDER':         'rgba(0,180,255,0.20)',
    'TXT_PRI':        '#F0F4FF',
    'TXT_SEC':        'rgba(160,170,204,0.85)',
    'TXT_MUTED':      'rgba(160,170,204,0.40)',

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
    'accent_dark':  "#1E5FA8",   # bleu foncé pressé,
    'accent':       "#4DA6FF",   # bleu néon vif
    'accent_light': "#99CCFF",   # bleu clair survol

}


# ==================== STYLES DE BOUTONS ====================
BUTTON_STYLES = {
    'primary': f"""
        QPushButton {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {COLORS['primary']}, stop:1 {COLORS['primary_dark']});
            color: #0A0A1A;
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
            background: #2E2E45;
            color: #555570;
        }}
    """,

    'success': f"""
        QPushButton {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {COLORS['success']}, stop:1 #00C853);
            color: #0A0A1A;
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            font-size: 14px;
            font-weight: bold;
            min-height: 36px;
        }}
        QPushButton:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #69FF99, stop:1 {COLORS['success']});
        }}
        QPushButton:pressed {{
            background: #00C853;
        }}
    """,

    'danger': f"""
        QPushButton {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {COLORS['danger']}, stop:1 #D50000);
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
                stop:0 #FF6E6E, stop:1 {COLORS['danger']});
        }}
        QPushButton:pressed {{
            background: #D50000;
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
            background: rgba(0, 229, 255, 0.12);
            border-color: #40F0FF;
            color: #40F0FF;
        }}
        QPushButton:pressed {{
            background: rgba(0, 229, 255, 0.25);
        }}
    """,

    'warning': f"""
        QPushButton {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {COLORS['warning']}, stop:1 #FFC200);
            color: #0A0A1A;
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            font-size: 14px;
            font-weight: bold;
            min-height: 36px;
        }}
        QPushButton:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #FFE033, stop:1 {COLORS['warning']});
        }}
        QPushButton:pressed {{
            background: #FFC200;
        }}
    """,
}

# ==================== STYLES DE CARTES ====================
CARD_STYLE = f"""
    QFrame {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 {COLORS['bg_medium']}, stop:1 {COLORS['bg_dark']});
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
        alternate-background-color: #222233;
        border: 1px solid {COLORS['border']};
        border-radius: 8px;
        gridline-color: #2A2A40;
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
            stop:0 #2A2A40, stop:1 {COLORS['bg_medium']});
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
        background-color: {COLORS['bg_input']};
        border: 2px solid {COLORS['border']};
        border-radius: 8px;
        padding: 8px 12px;
        color: {COLORS['text_primary']};
        font-size: 14px;
        min-height: 36px;
    }}
    QLineEdit:focus, QComboBox:focus, QSpinBox:focus,
    QDoubleSpinBox:focus, QTextEdit:focus {{
        border: 2px solid {COLORS['primary']};
        background-color: {COLORS['bg_light']};
    }}
    QLineEdit:hover, QComboBox:hover, QSpinBox:hover,
    QDoubleSpinBox:hover, QTextEdit:hover {{
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
                stop:0 {COLORS['bg_light']}, stop:1 {COLORS['bg_medium']});
        }}
    """


# ==================== STYLES SETTINGS ====================

DARK_COLORS = {
    'bg_page':   '#1E1E2E',
    'bg_card':   '#252535',
    'bg_deep':   '#16161F',
    'border':    'rgba(0,180,255,0.20)',
    'txt_pri':   '#F0F4FF',
    'txt_sec':   'rgba(160,170,204,0.85)',
    'txt_muted': 'rgba(160,170,204,0.40)',
}

SETTINGS_CARD_STYLE = """
    QFrame {
        background: #252535;
        border-radius: 14px;
        border: 1px solid rgba(0,180,255,0.20);
    }
"""

SETTINGS_INPUT_STYLE = """
    QLineEdit {
        background: #1E1E2E;
        color: #F0F4FF;
        border: 1px solid rgba(0,180,255,0.25);
        border-radius: 8px;
        padding: 10px 14px;
        font-size: 13px;
        selection-background-color: #00B4FF;
    }
    QLineEdit:focus {
        border: 1px solid #00B4FF;
        background: #252535;
    }
"""

SETTINGS_COMBO_STYLE = """
    QComboBox {
        background: #1E1E2E;
        color: #F0F4FF;
        border: 1px solid rgba(0,180,255,0.25);
        border-radius: 8px;
        padding: 10px 14px;
        font-size: 13px;
        min-height: 42px;
    }
    QComboBox:focus { border: 1px solid #00B4FF; }
    QComboBox::drop-down { border: none; width: 30px; }
    QComboBox QAbstractItemView {
        background: #252535;
        color: #F0F4FF;
        selection-background-color: #0090DD;
        border: 1px solid rgba(0,180,255,0.20);
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

# ==================== STYLE CHAMP OBLIGATOIRE ====================
REQUIRED_FIELD_STYLE = f"""
    QLineEdit {{
        background-color: {COLORS['bg_input']};
        border: 2px solid {COLORS['warning']};
        border-radius: 8px;
        padding: 8px 12px;
        color: {COLORS['text_primary']};
        font-size: 14px;
        min-height: 36px;
    }}
    QLineEdit:focus {{
        border: 2px solid {COLORS['primary']};
        background-color: {COLORS['bg_light']};
    }}
    QLineEdit:hover {{
        border: 2px solid {COLORS['border_light']};
    }}
"""

REQUIRED_ERROR_STYLE = f"""
    QLineEdit {{
        background-color: rgba(248, 113, 113, 0.10);
        border: 2px solid {COLORS['danger']};
        border-radius: 8px;
        padding: 8px 12px;
        color: {COLORS['text_primary']};
        font-size: 14px;
        min-height: 36px;
    }}
    QLineEdit:focus {{
        border: 2px solid {COLORS['danger']};
        background-color: rgba(248, 113, 113, 0.15);
    }}
"""

# Ajoutez ceci dans votre fichier styles.py ou dans le style principal

SCROLLBAR_STYLE = """
/* Scrollbar vertical */
QScrollBar:vertical {
    background: #1E1E2E;
    width: 8px;
    border-radius: 4px;
    margin: 2px 0px 2px 0px;
}

QScrollBar::handle:vertical {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #6366F1,
        stop:1 #A855F7);
    border-radius: 4px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #818CF8,
        stop:1 #C084FC);
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
    border: none;
}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: transparent;
}

/* Scrollbar horizontal */
QScrollBar:horizontal {
    background: #1E1E2E;
    height: 8px;
    border-radius: 4px;
    margin: 0px 2px 0px 2px;
}

QScrollBar::handle:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #6366F1,
        stop:1 #A855F7);
    border-radius: 4px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #818CF8,
        stop:1 #C084FC);
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
    border: none;
}

QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
    background: transparent;
}
"""