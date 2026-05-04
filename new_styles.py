"""
new_styles.py — Thème "Midnight Amber" 
Style: Luxe industriel — fond charbon, accents ambre/or, typographie forte
"""

# ══════════════════════════════════════════════════════════
#  PALETTE  — Charbon + Ambre/Or + Corail
# ══════════════════════════════════════════════════════════
NEW_COLORS = {
    # Fonds
    'bg_dark':    '#0D0D0F',   # charbon presque noir
    'bg_medium':  '#141418',   # fond principal
    'bg_light':   '#1C1C23',   # cartes
    'bg_card':    '#1C1C23',
    'bg_input':   '#12121A',   # champs de saisie
    'bg_deep':    '#0A0A0E',

    # Accents
    'primary':       '#F5A623',   # ambre chaud
    'primary_dark':  '#C4841A',
    'primary_light': '#FFD080',
    'secondary':     '#FF6B6B',   # corail
    'secondary_dark':'#CC4444',
    'success':       '#4ECDC4',   # turquoise
    'warning':       '#FFE66D',   # jaune citron
    'danger':        '#FF6B6B',   # corail
    'info':          '#A8EDEA',   # menthe

    # Textes
    'text_primary':   '#F0EDE8',   # blanc cassé chaud
    'text_secondary': '#B0A99A',   # beige grisé
    'text_tertiary':  '#6B6460',   # brun foncé

    # Bordures
    'border':       '#2A2A35',
    'border_light': '#F5A62333',   # ambre translucide
    'border_glow':  '#F5A62366',

    # Aliases uppercase (compatibilité)
    'BG_PAGE':   '#0D0D0F',
    'BG_CARD':   '#1C1C23',
    'BG_DEEP':   '#0A0A0E',
    'BORDER':    'rgba(245,166,35,0.12)',
    'TXT_PRI':   '#F0EDE8',
    'TXT_SEC':   'rgba(176,169,154,0.85)',
    'TXT_MUTED': 'rgba(107,100,96,0.50)',
}

# ══════════════════════════════════════════════════════════
#  BOUTONS
# ══════════════════════════════════════════════════════════
NEW_BUTTON_STYLES = {
    'primary': f"""
        QPushButton {{
            background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                stop:0 #F5A623, stop:1 #C4841A);
            color: #0D0D0F;
            border: none;
            border-radius: 6px;
            padding: 10px 20px;
            font-size: 13px;
            font-weight: bold;
            min-height: 36px;
            letter-spacing: 0.5px;
        }}
        QPushButton:hover {{
            background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                stop:0 #FFD080, stop:1 #F5A623);
        }}
        QPushButton:pressed {{
            background: #C4841A;
        }}
        QPushButton:disabled {{
            background: #2A2A35;
            color: #4A4450;
        }}
    """,
    'success': f"""
        QPushButton {{
            background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                stop:0 #4ECDC4, stop:1 #3AAA9F);
            color: #0D0D0F;
            border: none;
            border-radius: 6px;
            padding: 10px 20px;
            font-size: 13px;
            font-weight: bold;
            min-height: 36px;
        }}
        QPushButton:hover {{
            background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                stop:0 #7EDBD5, stop:1 #4ECDC4);
        }}
        QPushButton:pressed {{ background: #3AAA9F; }}
    """,
    'danger': f"""
        QPushButton {{
            background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                stop:0 #FF6B6B, stop:1 #CC4444);
            color: #F0EDE8;
            border: none;
            border-radius: 6px;
            padding: 10px 20px;
            font-size: 13px;
            font-weight: bold;
            min-height: 36px;
        }}
        QPushButton:hover {{
            background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                stop:0 #FF9090, stop:1 #FF6B6B);
        }}
        QPushButton:pressed {{ background: #CC4444; }}
    """,
    'secondary': f"""
        QPushButton {{
            background: transparent;
            color: #F5A623;
            border: 1.5px solid #F5A62366;
            border-radius: 6px;
            padding: 10px 20px;
            font-size: 13px;
            font-weight: bold;
            min-height: 36px;
        }}
        QPushButton:hover {{
            background: rgba(245,166,35,0.10);
            border-color: #F5A623;
        }}
        QPushButton:pressed {{
            background: rgba(245,166,35,0.20);
        }}
    """,
    'warning': f"""
        QPushButton {{
            background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                stop:0 #FFE66D, stop:1 #DDBB44);
            color: #0D0D0F;
            border: none;
            border-radius: 6px;
            padding: 10px 20px;
            font-size: 13px;
            font-weight: bold;
            min-height: 36px;
        }}
        QPushButton:hover {{
            background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                stop:0 #FFF0A0, stop:1 #FFE66D);
        }}
        QPushButton:pressed {{ background: #DDBB44; }}
    """,
    # Alias pour compatibilité
    'info': f"""
        QPushButton {{
            background: transparent;
            color: #A8EDEA;
            border: 1.5px solid rgba(168,237,234,0.4);
            border-radius: 6px;
            padding: 10px 20px;
            font-size: 13px;
            font-weight: bold;
            min-height: 36px;
        }}
        QPushButton:hover {{ background: rgba(168,237,234,0.08); }}
    """,
}

# ══════════════════════════════════════════════════════════
#  CHAMPS DE SAISIE
# ══════════════════════════════════════════════════════════
NEW_INPUT_STYLE = """
    QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit {
        background-color: #12121A;
        border: 1.5px solid #2A2A35;
        border-radius: 6px;
        padding: 8px 12px;
        color: #F0EDE8;
        font-size: 13px;
        min-height: 36px;
        selection-background-color: #F5A62333;
    }
    QLineEdit:focus, QComboBox:focus, QSpinBox:focus,
    QDoubleSpinBox:focus, QTextEdit:focus {
        border: 1.5px solid #F5A623;
        background-color: #1C1C23;
    }
    QLineEdit:hover, QComboBox:hover, QSpinBox:hover,
    QDoubleSpinBox:hover, QTextEdit:hover {
        border: 1.5px solid rgba(245,166,35,0.40);
    }
    QComboBox::drop-down { border: none; width: 30px; }
    QComboBox::down-arrow {
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 5px solid #F5A623;
        margin-right: 10px;
    }
    QComboBox QAbstractItemView {
        background-color: #1C1C23;
        border: 1px solid #F5A62333;
        selection-background-color: rgba(245,166,35,0.20);
        color: #F0EDE8;
    }
    QSpinBox::up-button, QDoubleSpinBox::up-button,
    QSpinBox::down-button, QDoubleSpinBox::down-button {
        background-color: #1C1C23;
        border: none;
        width: 20px;
    }
    QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
    QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {
        background-color: #F5A623;
    }
"""

# ══════════════════════════════════════════════════════════
#  TABLEAUX
# ══════════════════════════════════════════════════════════
NEW_TABLE_STYLE = """
    QTableWidget {
        background-color: #1C1C23;
        alternate-background-color: #141418;
        border: 1px solid #2A2A35;
        border-radius: 8px;
        gridline-color: rgba(255,255,255,0.04);
        color: #F0EDE8;
        selection-background-color: rgba(245,166,35,0.18);
        font-size: 13px;
    }
    QTableWidget::item {
        padding: 10px 8px;
        border: none;
    }
    QTableWidget::item:selected {
        background-color: rgba(245,166,35,0.22);
        color: #F0EDE8;
    }
    QTableWidget::item:hover {
        background-color: rgba(245,166,35,0.08);
    }
    QHeaderView::section {
        background: #0D0D0F;
        color: #F5A623;
        padding: 10px 8px;
        border: none;
        border-bottom: 2px solid #F5A62344;
        font-weight: bold;
        font-size: 12px;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    QHeaderView::section:hover {
        background: #1C1C23;
        color: #FFD080;
    }
    QScrollBar:vertical {
        background: #0D0D0F;
        width: 8px;
        border-radius: 4px;
    }
    QScrollBar::handle:vertical {
        background: #F5A62344;
        border-radius: 4px;
    }
    QScrollBar::handle:vertical:hover {
        background: #F5A623;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height:0; }
"""
