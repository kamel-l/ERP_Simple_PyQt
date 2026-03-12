#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_ui_components.py - Test du module ui_components centralisé
Valide que tous les composants sont correctement importables
"""

def test_imports():
    """Test que tous les imports fonctionnent"""
    print("=" * 60)
    print("TEST: Imports depuis ui_components")
    print("=" * 60)
    
    try:
        # Test 1: Constantes de couleur
        print("\n✓ Test 1: Constantes de couleur")
        from ui_components import (
            BG_PAGE, BG_CARD, BG_DEEP, BORDER, BORDER_LIGHT,
            TXT_PRI, TXT_SEC, TXT_TER,
            C_BLUE, C_GREEN, C_AMBER, C_VIOLET, C_CYAN, C_RED,
            CHART_COLORS, MONTHS_FR, ThemeColors
        )
        print(f"   ✅ BG_PAGE: {BG_PAGE}")
        print(f"   ✅ C_BLUE: {C_BLUE}")
        print(f"   ✅ CHART_COLORS: {len(CHART_COLORS)} couleurs")
        print(f"   ✅ MONTHS_FR: {MONTHS_FR[:3]} ...")
        
        # Test 2: Classe d'animation
        print("\n✓ Test 2: Classes d'animation")
        from ui_components import KpiAnimator, animate_counter
        print(f"   ✅ KpiAnimator: {KpiAnimator.__name__}")
        print(f"   ✅ animate_counter: {animate_counter.__name__}")
        
        # Test 3: Fonctions helper (nouveaux noms)
        print("\n✓ Test 3: Fonctions helper (nouveaux noms)")
        from ui_components import (
            create_card, create_label, create_separator, create_plot
        )
        print(f"   ✅ create_card: {create_card.__name__}")
        print(f"   ✅ create_label: {create_label.__name__}")
        print(f"   ✅ create_separator: {create_separator.__name__}")
        print(f"   ✅ create_plot: {create_plot.__name__}")
        
        # Test 4: Fonctions helper (anciens noms - compatibilité)
        print("\n✓ Test 4: Fonctions helper (anciens noms)")
        from ui_components import (
            _card, _lbl, _sep, _styled_plot, _KpiAnim, count_up
        )
        print(f"   ✅ _card: {_card.__name__}")
        print(f"   ✅ _lbl: {_lbl.__name__}")
        print(f"   ✅ _sep: {_sep.__name__}")
        print(f"   ✅ _styled_plot: {_styled_plot.__name__}")
        print(f"   ✅ _KpiAnim: {_KpiAnim.__name__}")
        print(f"   ✅ count_up: {count_up.__name__}")
        
        # Test 5: Constantes de style
        print("\n✓ Test 5: Constantes de style")
        from ui_components import (
            CARD_STYLE, LIGHT_CARD_STYLE, HOVER_CARD_STYLE
        )
        print(f"   ✅ CARD_STYLE: {len(CARD_STYLE)} caractères")
        print(f"   ✅ LIGHT_CARD_STYLE: {len(LIGHT_CARD_STYLE)} caractères")
        print(f"   ✅ HOVER_CARD_STYLE: {len(HOVER_CARD_STYLE)} caractères")
        
        print("\n" + "=" * 60)
        print("✅ TOUS LES TESTS RÉUSSIS!")
        print("=" * 60)
        return True
        
    except ImportError as e:
        print(f"\n❌ ERREUR D'IMPORT: {e}")
        return False
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        return False


def test_functionality():
    """Test que les composants fonctionnent correctement"""
    print("\n" + "=" * 60)
    print("TEST: Fonctionnalité des composants")
    print("=" * 60)
    
    try:
        from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QFrame, QVBoxLayout
        from ui_components import (
            create_card, create_label, create_separator, create_plot,
            BG_PAGE, C_BLUE, TXT_SEC
        )
        
        # Créer une app PyQt minimale
        app = QApplication.instance() or QApplication([])
        
        # Test 1: Créer une carte
        print("\n✓ Test 1: create_card()")
        card = create_card()
        print(f"   ✅ Card créée: {type(card).__name__}")
        
        # Test 2: Créer un label
        print("\n✓ Test 2: create_label()")
        label = create_label("Test Label", size=14, bold=True, color=C_BLUE)
        print(f"   ✅ Label créé: {label.text()}")
        
        # Test 3: Créer un séparateur
        print("\n✓ Test 3: create_separator()")
        sep = create_separator()
        print(f"   ✅ Séparateur créé: hauteur={sep.height()}")
        
        # Test 4: Créer un graphique
        print("\n✓ Test 4: create_plot()")
        plot = create_plot(height=300)
        print(f"   ✅ Graphique créé: hauteur={plot.minimumHeight()}")
        
        print("\n" + "=" * 60)
        print("✅ TOUS LES TESTS DE FONCTIONNALITÉ RÉUSSIS!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_imports()
    
    # Test de fonctionnalité uniquement si les imports réussissent
    if success:
        try:
            success = test_functionality()
        except ImportError:
            print("\n⚠️  PyQt6 non disponible - tests de fonctionnalité ignorés")
    
    exit(0 if success else 1)
