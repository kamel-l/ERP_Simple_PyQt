"""
============================================================================
STYLES.PY - Fichier de styles pour le module PyQt6
============================================================================

Ce fichier contient tous les styles, couleurs et thèmes utilisés par
l'application ERP PyQt6.
"""

# ============================================================================
# PALETTE DE COULEURS
# ============================================================================

COLORS = {
    # Couleurs de fond
    'bg_dark': '#1a1a2e',
    'bg_medium': '#16213e',
    'bg_card': '#0f3460',
    'bg_light': '#533483',
    
    # Couleurs principales
    'primary': '#5d8aa8',
    'secondary': '#3498db',
    'success': '#27ae60',
    'warning': '#f39c12',
    'danger': '#e74c3c',
    'info': '#17a2b8',
    
    # Couleurs de texte
    'text_primary': '#ffffff',
    'text_secondary': '#e0e0e0',
    'text_tertiary': '#a0a0a0',
    'text_muted': '#6c757d',
    
    # Couleurs d'accentuation
    'accent_1': '#e94560',
    'accent_2': '#00adb5',
    'accent_3': '#f38181',
    
    # Couleurs de bordure
    'border_light': '#4a5568',
    'border_dark': '#2d3748',
}


# ============================================================================
# STYLES DES BOUTONS
# ============================================================================

BUTTON_STYLES = {
    'primary': f"""
        QPushButton {{
            background-color: {COLORS['primary']};
            color: {COLORS['text_primary']};
            border: none;
            border-radius: 8px;
            padding: 12px 24px;
            font-size: 14px;
            font-weight: bold;
            text-align: center;
        }}
        QPushButton:hover {{
            background-color: #34495e;
            border: 2px solid {COLORS['secondary']};
        }}
        QPushButton:pressed {{
            background-color: #1a252f;
        }}
        QPushButton:disabled {{
            background-color: #555555;
            color: #888888;
        }}
    """,
    
    'secondary': f"""
        QPushButton {{
            background-color: {COLORS['secondary']};
            color: {COLORS['text_primary']};
            border: none;
            border-radius: 8px;
            padding: 12px 24px;
            font-size: 14px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: #2980b9;
            border: 2px solid {COLORS['primary']};
        }}
        QPushButton:pressed {{
            background-color: #21618c;
        }}
        QPushButton:disabled {{
            background-color: #555555;
            color: #888888;
        }}
    """,
    
    'success': f"""
        QPushButton {{
            background-color: {COLORS['success']};
            color: {COLORS['text_primary']};
            border: none;
            border-radius: 8px;
            padding: 12px 24px;
            font-size: 14px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: #229954;
            border: 2px solid #1e8449;
        }}
        QPushButton:pressed {{
            background-color: #1e8449;
        }}
        QPushButton:disabled {{
            background-color: #555555;
            color: #888888;
        }}
    """,
    
    'warning': f"""
        QPushButton {{
            background-color: {COLORS['warning']};
            color: {COLORS['text_primary']};
            border: none;
            border-radius: 8px;
            padding: 12px 24px;
            font-size: 14px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: #e67e22;
            border: 2px solid #d35400;
        }}
        QPushButton:pressed {{
            background-color: #d35400;
        }}
        QPushButton:disabled {{
            background-color: #555555;
            color: #888888;
        }}
    """,
    
    'danger': f"""
        QPushButton {{
            background-color: {COLORS['danger']};
            color: {COLORS['text_primary']};
            border: none;
            border-radius: 8px;
            padding: 12px 24px;
            font-size: 14px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: #c0392b;
            border: 2px solid #a93226;
        }}
        QPushButton:pressed {{
            background-color: #a93226;
        }}
        QPushButton:disabled {{
            background-color: #555555;
            color: #888888;
        }}
    """,
    
    'info': f"""
        QPushButton {{
            background-color: {COLORS['info']};
            color: {COLORS['text_primary']};
            border: none;
            border-radius: 8px;
            padding: 12px 24px;
            font-size: 14px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: #138496;
            border: 2px solid #117a8b;
        }}
        QPushButton:pressed {{
            background-color: #117a8b;
        }}
        QPushButton:disabled {{
            background-color: #555555;
            color: #888888;
        }}
    """,
}


# ============================================================================
# STYLES DES CHAMPS DE SAISIE
# ============================================================================

INPUT_STYLE = f"""
    QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
        background-color: {COLORS['bg_medium']};
        color: {COLORS['text_primary']};
        border: 2px solid {COLORS['border_light']};
        border-radius: 6px;
        padding: 10px;
        font-size: 13px;
        selection-background-color: {COLORS['secondary']};
    }}
    
    QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{
        border: 2px solid {COLORS['secondary']};
        background-color: {COLORS['bg_card']};
    }}
    
    QLineEdit:hover, QSpinBox:hover, QDoubleSpinBox:hover, QComboBox:hover {{
        border: 2px solid {COLORS['primary']};
    }}
    
    QLineEdit:disabled, QSpinBox:disabled, QDoubleSpinBox:disabled, QComboBox:disabled {{
        background-color: #2a2a2a;
        color: #666666;
        border: 2px solid #444444;
    }}
    
    /* ComboBox dropdown */
    QComboBox::drop-down {{
        border: none;
        background-color: transparent;
        width: 30px;
    }}
    
    QComboBox::down-arrow {{
        image: none;
        border: 2px solid {COLORS['text_primary']};
        width: 8px;
        height: 8px;
        border-top: none;
        border-right: none;
        transform: rotate(-45deg);
    }}
    
    QComboBox QAbstractItemView {{
        background-color: {COLORS['bg_card']};
        color: {COLORS['text_primary']};
        selection-background-color: {COLORS['secondary']};
        border: 2px solid {COLORS['border_light']};
        border-radius: 4px;
        padding: 5px;
    }}
    
    /* SpinBox buttons */
    QSpinBox::up-button, QDoubleSpinBox::up-button {{
        background-color: {COLORS['bg_card']};
        border: none;
        border-left: 1px solid {COLORS['border_light']};
        width: 20px;
        border-top-right-radius: 6px;
    }}
    
    QSpinBox::down-button, QDoubleSpinBox::down-button {{
        background-color: {COLORS['bg_card']};
        border: none;
        border-left: 1px solid {COLORS['border_light']};
        width: 20px;
        border-bottom-right-radius: 6px;
    }}
    
    QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
    QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{
        background-color: {COLORS['secondary']};
    }}
"""


# ============================================================================
# STYLES DES TABLEAUX
# ============================================================================

TABLE_STYLE = f"""
    QTableWidget {{
        background-color: {COLORS['bg_dark']};
        alternate-background-color: {COLORS['bg_medium']};
        color: {COLORS['text_primary']};
        gridline-color: {COLORS['border_dark']};
        border: 2px solid {COLORS['border_light']};
        border-radius: 8px;
        selection-background-color: {COLORS['secondary']};
        selection-color: {COLORS['text_primary']};
        font-size: 13px;
    }}
    
    QTableWidget::item {{
        padding: 8px;
        border: none;
    }}
    
    QTableWidget::item:selected {{
        background-color: {COLORS['secondary']};
        color: {COLORS['text_primary']};
    }}
    
    QTableWidget::item:hover {{
        background-color: {COLORS['bg_card']};
    }}
    
    /* En-têtes de colonnes */
    QHeaderView::section {{
        background-color: {COLORS['primary']};
        color: {COLORS['text_primary']};
        padding: 12px;
        border: none;
        border-right: 1px solid {COLORS['border_dark']};
        font-weight: bold;
        font-size: 13px;
    }}
    
    QHeaderView::section:hover {{
        background-color: {COLORS['secondary']};
    }}
    
    QHeaderView::section:first {{
        border-top-left-radius: 8px;
    }}
    
    QHeaderView::section:last {{
        border-top-right-radius: 8px;
        border-right: none;
    }}
    
    /* Barre de défilement verticale */
    QScrollBar:vertical {{
        background-color: {COLORS['bg_dark']};
        width: 12px;
        border: none;
        border-radius: 6px;
    }}
    
    QScrollBar::handle:vertical {{
        background-color: {COLORS['border_light']};
        border-radius: 6px;
        min-height: 30px;
    }}
    
    QScrollBar::handle:vertical:hover {{
        background-color: {COLORS['secondary']};
    }}
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    
    /* Barre de défilement horizontale */
    QScrollBar:horizontal {{
        background-color: {COLORS['bg_dark']};
        height: 12px;
        border: none;
        border-radius: 6px;
    }}
    
    QScrollBar::handle:horizontal {{
        background-color: {COLORS['border_light']};
        border-radius: 6px;
        min-width: 30px;
    }}
    
    QScrollBar::handle:horizontal:hover {{
        background-color: {COLORS['secondary']};
    }}
    
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0px;
    }}
"""


# ============================================================================
# STYLES DES LABELS
# ============================================================================

LABEL_STYLE = f"""
    QLabel {{
        color: {COLORS['text_primary']};
        font-size: 13px;
        padding: 5px;
    }}
"""


# ============================================================================
# STYLES DES GROUPBOX
# ============================================================================

GROUPBOX_STYLE = f"""
    QGroupBox {{
        background-color: {COLORS['bg_card']};
        border: 2px solid {COLORS['border_light']};
        border-radius: 8px;
        margin-top: 10px;
        padding: 15px;
        color: {COLORS['text_primary']};
        font-weight: bold;
        font-size: 14px;
    }}
    
    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 5px 10px;
        background-color: {COLORS['primary']};
        border-radius: 4px;
        color: {COLORS['text_primary']};
    }}
"""


# ============================================================================
# STYLES DES MESSAGEBOX
# ============================================================================

MESSAGEBOX_STYLE = f"""
    QMessageBox {{
        background-color: {COLORS['bg_medium']};
        color: {COLORS['text_primary']};
    }}
    
    QMessageBox QLabel {{
        color: {COLORS['text_primary']};
        font-size: 13px;
    }}
    
    QMessageBox QPushButton {{
        background-color: {COLORS['primary']};
        color: {COLORS['text_primary']};
        border: none;
        border-radius: 6px;
        padding: 10px 20px;
        font-size: 12px;
        min-width: 80px;
    }}
    
    QMessageBox QPushButton:hover {{
        background-color: {COLORS['secondary']};
    }}
"""


# ============================================================================
# STYLES DES CHECKBOX ET RADIOBUTTON
# ============================================================================

CHECKBOX_STYLE = f"""
    QCheckBox, QRadioButton {{
        color: {COLORS['text_primary']};
        font-size: 13px;
        spacing: 8px;
    }}
    
    QCheckBox::indicator, QRadioButton::indicator {{
        width: 20px;
        height: 20px;
        border: 2px solid {COLORS['border_light']};
        border-radius: 4px;
        background-color: {COLORS['bg_medium']};
    }}
    
    QCheckBox::indicator:checked, QRadioButton::indicator:checked {{
        background-color: {COLORS['success']};
        border-color: {COLORS['success']};
    }}
    
    QCheckBox::indicator:hover, QRadioButton::indicator:hover {{
        border-color: {COLORS['secondary']};
    }}
    
    QRadioButton::indicator {{
        border-radius: 10px;
    }}
"""


# ============================================================================
# STYLES DES PROGRESSBAR
# ============================================================================

PROGRESSBAR_STYLE = f"""
    QProgressBar {{
        background-color: {COLORS['bg_medium']};
        border: 2px solid {COLORS['border_light']};
        border-radius: 8px;
        text-align: center;
        color: {COLORS['text_primary']};
        font-weight: bold;
        height: 25px;
    }}
    
    QProgressBar::chunk {{
        background-color: {COLORS['success']};
        border-radius: 6px;
    }}
"""


# ============================================================================
# STYLES DES TABS
# ============================================================================

TAB_STYLE = f"""
    QTabWidget::pane {{
        background-color: {COLORS['bg_card']};
        border: 2px solid {COLORS['border_light']};
        border-radius: 8px;
        top: -2px;
    }}
    
    QTabBar::tab {{
        background-color: {COLORS['bg_medium']};
        color: {COLORS['text_secondary']};
        border: 2px solid {COLORS['border_light']};
        border-bottom: none;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        padding: 10px 20px;
        margin-right: 2px;
        font-size: 13px;
        font-weight: bold;
    }}
    
    QTabBar::tab:selected {{
        background-color: {COLORS['primary']};
        color: {COLORS['text_primary']};
        border-color: {COLORS['secondary']};
    }}
    
    QTabBar::tab:hover {{
        background-color: {COLORS['bg_card']};
        color: {COLORS['text_primary']};
    }}
"""


# ============================================================================
# THÈME GLOBAL DE L'APPLICATION
# ============================================================================

APPLICATION_STYLE = f"""
    QMainWindow, QWidget, QDialog {{
        background-color: {COLORS['bg_dark']};
        color: {COLORS['text_primary']};
        font-family: 'Segoe UI', Arial, sans-serif;
    }}
    
    QToolTip {{
        background-color: {COLORS['bg_card']};
        color: {COLORS['text_primary']};
        border: 2px solid {COLORS['border_light']};
        border-radius: 6px;
        padding: 5px;
        font-size: 12px;
    }}
    
    QMenuBar {{
        background-color: {COLORS['bg_medium']};
        color: {COLORS['text_primary']};
        border-bottom: 2px solid {COLORS['border_light']};
        padding: 5px;
    }}
    
    QMenuBar::item {{
        background-color: transparent;
        padding: 8px 12px;
        border-radius: 4px;
    }}
    
    QMenuBar::item:selected {{
        background-color: {COLORS['primary']};
    }}
    
    QMenu {{
        background-color: {COLORS['bg_card']};
        color: {COLORS['text_primary']};
        border: 2px solid {COLORS['border_light']};
        border-radius: 6px;
        padding: 5px;
    }}
    
    QMenu::item {{
        padding: 8px 30px 8px 30px;
        border-radius: 4px;
    }}
    
    QMenu::item:selected {{
        background-color: {COLORS['secondary']};
    }}
    
    QStatusBar {{
        background-color: {COLORS['bg_medium']};
        color: {COLORS['text_secondary']};
        border-top: 2px solid {COLORS['border_light']};
    }}
"""


# ============================================================================
# STYLES PAR CATÉGORIE (POUR FACILITER L'IMPORT)
# ============================================================================

STYLES = {
    'application': APPLICATION_STYLE,
    'button': BUTTON_STYLES,
    'input': INPUT_STYLE,
    'table': TABLE_STYLE,
    'label': LABEL_STYLE,
    'groupbox': GROUPBOX_STYLE,
    'messagebox': MESSAGEBOX_STYLE,
    'checkbox': CHECKBOX_STYLE,
    'progressbar': PROGRESSBAR_STYLE,
    'tab': TAB_STYLE,
}


# ============================================================================
# FONCTION UTILITAIRE POUR APPLIQUER UN THÈME
# ============================================================================

def apply_theme(app):
    """
    Applique le thème complet à l'application PyQt6
    
    Usage:
        from PyQt6.QtWidgets import QApplication
        from styles import apply_theme
        
        app = QApplication([])
        apply_theme(app)
    """
    app.setStyleSheet(APPLICATION_STYLE)


def get_color(color_name):
    """
    Retourne une couleur de la palette
    
    Usage:
        from styles import get_color
        color = get_color('primary')
    """
    return COLORS.get(color_name, '#ffffff')


def get_button_style(button_type='primary'):
    """
    Retourne le style d'un bouton
    
    Usage:
        from styles import get_button_style
        button.setStyleSheet(get_button_style('success'))
    """
    return BUTTON_STYLES.get(button_type, BUTTON_STYLES['primary'])


# ============================================================================
# EXEMPLES D'UTILISATION
# ============================================================================

if __name__ == "__main__":
    print("="*70)
    print("STYLES.PY - Fichier de styles pour ERP PyQt6")
    print("="*70)
    print("\nCouleurs disponibles:")
    for name, value in COLORS.items():
        print(f"  - {name:20s} : {value}")
    
    print("\nStyles de boutons disponibles:")
    for name in BUTTON_STYLES.keys():
        print(f"  - {name}")
    
    print("\n✅ Fichier styles.py chargé avec succès!")
    print("="*70)