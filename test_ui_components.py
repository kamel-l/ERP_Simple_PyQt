#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_ui_components.py - Test du module ui_components centralisÃ©
Valide que tous les composants sont correctement importables
"""

def test_imports():
    """Test que tous les imports fonctionnent"""
    print("=" * 60)
    print("TEST: Imports depuis ui_components")
    print("=" * 60)
    
    try:
        # Test 1: Constantes de couleur
        print("\nâœ“ Test 1: Constantes de couleur")
        from ui_components import (
            BG_PAGE, BG_CARD, BG_DEEP, BORDER, BORDER_LIGHT,
            TXT_PRI, TXT_SEC, TXT_TER,
            C_BLUE, C_GREEN, C_AMBER, C_VIOLET, C_CYAN, C_RED,
            CHART_COLORS, MONTHS_FR, ThemeColors
        )
        print(f"   âœ… BG_PAGE: {BG_PAGE}")
        print(f"   âœ… C_BLUE: {C_BLUE}")
        print(f"   âœ… CHART_COLORS: {len(CHART_COLORS)} couleurs")
        print(f"   âœ… MONTHS_FR: {MONTHS_FR[:3]} ...")
        
        # Test 2: Classe d'animation
        print("\nâœ“ Test 2: Classes d'animation")
        from ui_components import KpiAnimator, animate_counter
        print(f"   âœ… KpiAnimator: {KpiAnimator.__name__}")
        print(f"   âœ… animate_counter: {animate_counter.__name__}")
        
        # Test 3: Fonctions helper (nouveaux noms)
        print("\nâœ“ Test 3: Fonctions helper (nouveaux noms)")
        from ui_components import (
            create_card, create_label, create_separator, create_plot
        )
        print(f"   âœ… create_card: {create_card.__name__}")
        print(f"   âœ… create_label: {create_label.__name__}")
        print(f"   âœ… create_separator: {create_separator.__name__}")
        print(f"   âœ… create_plot: {create_plot.__name__}")
        
        # Test 4: Fonctions helper (anciens noms - compatibilitÃ©)
        print("\nâœ“ Test 4: Fonctions helper (anciens noms)")
        from ui_components import (
            _card, _lbl, _sep, _styled_plot, _KpiAnim, count_up
        )
        print(f"   âœ… _card: {_card.__name__}")
        print(f"   âœ… _lbl: {_lbl.__name__}")
        print(f"   âœ… _sep: {_sep.__name__}")
        print(f"   âœ… _styled_plot: {_styled_plot.__name__}")
        print(f"   âœ… _KpiAnim: {_KpiAnim.__name__}")
        print(f"   âœ… count_up: {count_up.__name__}")
        
        # Test 5: Constantes de style
        print("\nâœ“ Test 5: Constantes de style")
        from ui_components import (
            CARD_STYLE, LIGHT_CARD_STYLE, HOVER_CARD_STYLE
        )
        print(f"   âœ… CARD_STYLE: {len(CARD_STYLE)} caractÃ¨res")
        print(f"   âœ… LIGHT_CARD_STYLE: {len(LIGHT_CARD_STYLE)} caractÃ¨res")
        print(f"   âœ… HOVER_CARD_STYLE: {len(HOVER_CARD_STYLE)} caractÃ¨res")
        
        print("\n" + "=" * 60)
        print("âœ… TOUS LES TESTS RÃ‰USSIS!")
        print("=" * 60)
                
    except ImportError as e:
        print(f"\nâŒ ERREUR D'IMPORT: {e}")
        assert False
    except Exception as e:
        print(f"\nâŒ ERREUR: {e}")
        assert False


def test_functionality():
    """Test que les composants fonctionnent correctement"""
    print("\n" + "=" * 60)
    print("TEST: FonctionnalitÃ© des composants")
    print("=" * 60)
    
    try:
        from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QFrame, QVBoxLayout
        from ui_components import (
            create_card, create_label, create_separator, create_plot,
            BG_PAGE, C_BLUE, TXT_SEC
        )
        
        # CrÃ©er une app PyQt minimale
        app = QApplication.instance() or QApplication([])
        
        # Test 1: CrÃ©er une carte
        print("\nâœ“ Test 1: create_card()")
        card = create_card()
        print(f"   âœ… Card crÃ©Ã©e: {type(card).__name__}")
        
        # Test 2: CrÃ©er un label
        print("\nâœ“ Test 2: create_label()")
        label = create_label("Test Label", size=14, bold=True, color=C_BLUE)
        print(f"   âœ… Label crÃ©Ã©: {label.text()}")
        
        # Test 3: CrÃ©er un sÃ©parateur
        print("\nâœ“ Test 3: create_separator()")
        sep = create_separator()
        print(f"   âœ… SÃ©parateur crÃ©Ã©: hauteur={sep.height()}")
        
        # Test 4: CrÃ©er un graphique
        print("\nâœ“ Test 4: create_plot()")
        plot = create_plot(height=300)
        print(f"   âœ… Graphique crÃ©Ã©: hauteur={plot.minimumHeight()}")
        
        print("\n" + "=" * 60)
        print("âœ… TOUS LES TESTS DE FONCTIONNALITÃ‰ RÃ‰USSIS!")
        print("=" * 60)
                
    except Exception as e:
        print(f"\nâŒ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        assert False


if __name__ == "__main__":
    success = True
    try:
        test_imports()
    except AssertionError:
        success = False

    # Test de fonctionnalitÃ© uniquement si les imports rÃ©ussissent
    if success:
        try:
            test_functionality()
        except ImportError:
            print("\nâš ï¸  PyQt6 non disponible - tests de fonctionnalitÃ© ignorÃ©s")
        except AssertionError:
            success = False

    exit(0 if success else 1)

