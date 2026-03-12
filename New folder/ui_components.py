# ─────────────────────────────────────────────────────────────
#  ui_components.py - Composants UI Centralisés
#  Module réutilisable pour toute l'application
# ─────────────────────────────────────────────────────────────

from PyQt6.QtWidgets import QLabel, QFrame
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QObject, pyqtProperty, QPropertyAnimation, QEasingCurve
import pyqtgraph as pg


# ═════════════════════════════════════════════════════════════
#  PALETTE DE COULEURS CENTRALISÉE
# ═════════════════════════════════════════════════════════════

class ThemeColors:
    """Palette de couleurs centralisée pour toute l'application"""
    
    # Arrière-plans
    BG_PAGE  = "#0F1117"
    BG_CARD  = "#1A1D27"
    BG_DEEP  = "#13151F"
    
    # Bordures et séparations
    BORDER   = "rgba(255,255,255,0.07)"
    BORDER_LIGHT = "rgba(255,255,255,0.12)"
    
    # Textes
    TXT_PRI  = "#F1F5F9"      # Texte primaire
    TXT_SEC  = "rgba(255,255,255,0.45)"   # Texte secondaire
    TXT_TER  = "rgba(255,255,255,0.25)"   # Texte tertiaire
    
    # Couleurs sémantiques
    C_BLUE   = "#3B82F6"      # Primaire
    C_GREEN  = "#10B981"      # Succès
    C_AMBER  = "#F59E0B"      # Avertissement
    C_VIOLET = "#8B5CF6"      # Info
    C_CYAN   = "#06B6D4"      # Accent
    C_RED    = "#EF4444"      # Danger
    
    @staticmethod
    def get_all_semantic_colors():
        """Retourne une liste de toutes les couleurs sémantiques"""
        return [
            ThemeColors.C_BLUE,
            ThemeColors.C_GREEN,
            ThemeColors.C_AMBER,
            ThemeColors.C_VIOLET,
            ThemeColors.C_CYAN,
            ThemeColors.C_RED
        ]


# Alias courtes pour rétro-compatibilité
BG_PAGE  = ThemeColors.BG_PAGE
BG_CARD  = ThemeColors.BG_CARD
BG_DEEP  = ThemeColors.BG_DEEP
BORDER   = ThemeColors.BORDER
BORDER_LIGHT = ThemeColors.BORDER_LIGHT
TXT_PRI  = ThemeColors.TXT_PRI
TXT_SEC  = ThemeColors.TXT_SEC
TXT_TER  = ThemeColors.TXT_TER
C_BLUE   = ThemeColors.C_BLUE
C_GREEN  = ThemeColors.C_GREEN
C_AMBER  = ThemeColors.C_AMBER
C_VIOLET = ThemeColors.C_VIOLET
C_CYAN   = ThemeColors.C_CYAN
C_RED    = ThemeColors.C_RED

CHART_COLORS = ThemeColors.get_all_semantic_colors()
MONTHS_FR = ['Jan','Fév','Mar','Avr','Mai','Jun','Jul','Aoû','Sep','Oct','Nov','Déc']


# ═════════════════════════════════════════════════════════════
#  CLASSES D'ANIMATION
# ═════════════════════════════════════════════════════════════

class KpiAnimator(QObject):
    """Animateur pour les compteurs KPI"""
    def __init__(self, label, suffix=""):
        super().__init__()
        self._value = 0
        self.label = label
        self.suffix = suffix

    def get_value(self):
        return self._value

    def set_value(self, v):
        self._value = v
        self.label.setText(f"{v:,.0f}{self.suffix}")

    value = pyqtProperty(float, fget=get_value, fset=set_value)


def animate_counter(label, target, suffix="", duration=700):
    """
    Anime un label avec un compte à rebours du chiffre
    
    Args:
        label: QLabel à animer
        target: Valeur finale
        suffix: Suffixe à ajouter (ex: " DA")
        duration: Durée de l'animation en ms
    """
    animator = KpiAnimator(label, suffix)
    anim = QPropertyAnimation(animator, b"value")
    anim.setDuration(duration)
    anim.setStartValue(0.0)
    anim.setEndValue(float(target))
    anim.setEasingCurve(QEasingCurve.Type.OutCubic)
    anim.start()
    # Conserver les références pour éviter la destruction
    label._anim_ref = anim
    label._anim_obj = animator


# ═════════════════════════════════════════════════════════════
#  FONCTIONS HELPER UI
# ═════════════════════════════════════════════════════════════

def create_card(bg=BG_CARD, border=BORDER, border_radius=14):
    """
    Crée une carte stylisée (QFrame)
    
    Args:
        bg: Couleur de fond
        border: Couleur de la bordure
        border_radius: Rayon de bordure
    
    Returns:
        QFrame stylisé
    """
    frame = QFrame()
    frame.setStyleSheet(f"""
        QFrame {{
            background: {bg};
            border-radius: {border_radius}px;
            border: 1px solid {border};
        }}
    """)
    return frame


def create_label(text, size=11, bold=False, color=TXT_PRI, transparent=True):
    """
    Crée un label stylisé
    
    Args:
        text: Contenu du label
        size: Taille de la police (par défaut 11)
        bold: Gras (par défaut False)
        color: Couleur du texte
        transparent: Fond transparent
    
    Returns:
        QLabel stylisé
    """
    label = QLabel(text)
    weight = QFont.Weight.Bold if bold else QFont.Weight.Normal
    label.setFont(QFont("Segoe UI", size, weight))
    bg = "transparent" if transparent else "none"
    label.setStyleSheet(f"color: {color}; background: {bg}; border: none;")
    return label


def create_separator(height=1, color=BORDER):
    """
    Crée une ligne de séparation
    
    Args:
        height: Hauteur de la ligne
        color: Couleur de la ligne
    
    Returns:
        QFrame (ligne horizontale)
    """
    separator = QFrame()
    separator.setFrameShape(QFrame.Shape.HLine)
    separator.setFixedHeight(height)
    separator.setStyleSheet(f"background: {color}; border: none;")
    return separator


def create_plot(bg=BG_DEEP, height=220, show_grid=True, show_buttons=True):
    """
    Crée un graphique pyqtgraph stylisé
    
    Args:
        bg: Couleur de fond
        height: Hauteur minimale du graphique
        show_grid: Afficher la grille
        show_buttons: Afficher les boutons de contrôle
    
    Returns:
        pg.PlotWidget stylisé
    """
    plot = pg.PlotWidget()
    plot.setBackground(bg)
    plot.setMinimumHeight(height)
    
    if show_grid:
        plot.showGrid(x=True, y=True, alpha=0.08)
    
    if not show_buttons:
        plot.hideButtons()
    
    plot.setMouseEnabled(x=False, y=False)
    
    # Styliser les axes
    axis_pen = pg.mkPen(color="#ffffff22", width=1)
    label_pen = pg.mkPen(color="#ffffff55")
    
    for axis_name in ("bottom", "left"):
        axis = plot.getAxis(axis_name)
        axis.setPen(axis_pen)
        axis.setTextPen(label_pen)
        axis.setStyle(tickFont=QFont("Segoe UI", 8))
    
    return plot


# ═════════════════════════════════════════════════════════════
#  ALIAS COURTES POUR RÉTRO-COMPATIBILITÉ
# ═════════════════════════════════════════════════════════════

# Anciennes fonctions - garder les alias pour la compatibilité
def _card():
    return create_card()

def _lbl(text, size, bold=False, color=TXT_PRI):
    return create_label(text, size, bold, color)

def _sep():
    return create_separator()

def _styled_plot(bg=BG_DEEP, height=220):
    return create_plot(bg, height)


# Classe d'animation avec ancien nom
class _KpiAnim(KpiAnimator):
    """Classe d'animation héritée pour compatibilité"""
    def __init__(self, label, suffix=""):
        super().__init__(label, suffix)
    
    def _get(self):
        return self.value
    
    def _set(self, v):
        self.set_value(v)


def count_up(label, target, suffix="", ms=700):
    """Fonction d'animation avec ancien nom pour compatibilité"""
    animate_counter(label, target, suffix, ms)


# ═════════════════════════════════════════════════════════════
#  CONSTANTES DE STYLE RÉUTILISABLES
# ═════════════════════════════════════════════════════════════

CARD_STYLE = f"""
    QFrame {{
        background: {BG_CARD};
        border-radius: 16px;
        border: 1px solid {BORDER};
    }}
"""

LIGHT_CARD_STYLE = f"""
    QFrame {{
        background: rgba(255,255,255,0.03);
        border-radius: 12px;
        border: 1px solid {BORDER_LIGHT};
    }}
"""

HOVER_CARD_STYLE = f"""
    QFrame {{
        background: {BG_CARD};
        border-radius: 14px;
        border: 1px solid {BORDER};
    }}
    QFrame:hover {{
        border: 1px solid {BORDER_LIGHT};
        background: rgba(255,255,255,0.02);
    }}
"""
