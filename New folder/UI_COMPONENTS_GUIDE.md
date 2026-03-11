# 📦 ui_components.py - Composants UI Centralisés

## 🎯 Overview

Module centralisé contenant tous les composants UI réutilisables, les constantes de couleur et les fonctions helper pour toute l'application. Élimine la duplication de code et facilite la maintenance.

---

## ✨ Avantages

✅ **DRY (Don't Repeat Yourself)** - Une seule source de vérité  
✅ **Cohérence** - Même design partout  
✅ **Maintenabilité** - Mise à jour unique pour tous les fichiers  
✅ **Réutilisabilité** - Utiliser partout dans l'app  
✅ **Rétro-compatible** - Ancien code continue de fonctionner  

---

## 📚 API Reference

### 1. **Constantes de Couleur**

#### `ThemeColors` class
```python
from ui_components import ThemeColors

# Accès aux couleurs
print(ThemeColors.BG_PAGE)      # "#0F1117"
print(ThemeColors.C_BLUE)       # "#3B82F6"
print(ThemeColors.TXT_PRI)      # "#F1F5F9"
```

#### Alias courtes (recommandées)
```python
from ui_components import (
    BG_PAGE, BG_CARD, BG_DEEP, BORDER, BORDER_LIGHT,
    TXT_PRI, TXT_SEC, TXT_TER,
    C_BLUE, C_GREEN, C_AMBER, C_VIOLET, C_CYAN, C_RED,
    CHART_COLORS, MONTHS_FR
)

# Utilisation
print(BG_PAGE)        # "#0F1117"
print(CHART_COLORS)   # [Blue, Green, Amber, Violet, Cyan, Red]
```

---

### 2. **Animations**

#### `KpiAnimator` class (nouveau nom)
```python
from ui_components import KpiAnimator, animate_counter

# Créer un label à animer
label = QLabel("0")

# Animer de 0 à 1000 sur 1000ms
animate_counter(label, target=1000, suffix=" DA", duration=1000)
```

#### `count_up()` function (ancien nom, conservé)
```python
from ui_components import count_up

count_up(label, target=1500, suffix=" DA", ms=700)
```

---

### 3. **Fonctions Helper UI**

#### `create_card()` / `_card()` (alias)
```python
from ui_components import create_card, _card

# Créer une carte stylisée
card = create_card()
card.setMinimumHeight(200)

# Avec options personnalisées
card = create_card(
    bg="#1A1D27",
    border="rgba(255,255,255,0.07)",
    border_radius=14
)

# Ancien nom (toujours compatible)
card = _card()
```

#### `create_label()` / `_lbl()` (alias)
```python
from ui_components import create_label, _lbl, C_BLUE, TXT_SEC

# Créer un label stylisé
label = create_label("Mon Titre", size=16, bold=True, color=C_BLUE)

# Avec options complètes
label = create_label(
    text="Sous-titre",
    size=12,
    bold=False,
    color=TXT_SEC,
    transparent=True
)

# Ancien nom (toujours compatible)
label = _lbl("Texte", size=14, bold=True)
```

#### `create_separator()` / `_sep()` (alias)
```python
from ui_components import create_separator, _sep

# Créer une ligne horizontal
line = create_separator()

# Avec couleur personnalisée
line = create_separator(height=2, color=C_RED)

# Ancien nom
line = _sep()
```

#### `create_plot()` / `_styled_plot()` (alias)
```python
from ui_components import create_plot, _styled_plot, BG_DEEP

# Créer un graphique
plot = create_plot(bg=BG_DEEP, height=250)

# Avec options personnalisées
plot = create_plot(
    bg="#13151F",
    height=220,
    show_grid=True,
    show_buttons=False
)

# Ancien nom
plot = _styled_plot(bg=BG_DEEP, height=220)
```

---

### 4. **Constantes de Style**

```python
from ui_components import (
    CARD_STYLE, LIGHT_CARD_STYLE, HOVER_CARD_STYLE
)

# Utiliser dans setStyleSheet()
frame.setStyleSheet(CARD_STYLE)

# ou avec hover effect
frame.setStyleSheet(HOVER_CARD_STYLE)
```

---

## 💡 Exemples Pratiques

### Exemple 1: Créer une section avec titre et contenu

```python
from ui_components import create_card, create_label, create_separator, C_BLUE

# Card principale
card = create_card()
layout = QVBoxLayout(card)

# Titre
title = create_label("Mon Formulaire", size=16, bold=True, color=C_BLUE)
layout.addWidget(title)

# Séparation
layout.addWidget(create_separator())

# Contenu
content = create_label("Contenu ici", size=11)
layout.addWidget(content)
```

### Exemple 2: Créer un KPI animé

```python
from ui_components import create_label, animate_counter, C_GREEN

# Label KPI
kpi_label = create_label("0", size=24, bold=True, color=C_GREEN)

# Animer au chargement
animate_counter(kpi_label, target=15000, suffix=" DA", duration=800)

layout.addWidget(kpi_label)
```

### Exemple 3: Créer un graphique

```python
from ui_components import create_plot, create_card, create_label, BG_DEEP, C_BLUE
import pyqtgraph as pg

card = create_card()
layout = QVBoxLayout(card)

# Titre du graphique
title = create_label("Ventes Mensuelles", size=14, bold=True, color=C_BLUE)
layout.addWidget(title)

# Graphique
plot = create_plot(bg=BG_DEEP, height=250)
layout.addWidget(plot)

# Ajouter des données
values = [100, 200, 300, 400]
plot.plot(list(range(len(values))), values, pen=pg.mkPen('blue', width=2))
```

---

## 🔄 Migration du Code Existant

### Avant (hardcoded)
```python
# advanced_analytics_view.py
BG_PAGE  = "#0F1117"
BG_CARD  = "#1A1D27"
C_BLUE   = "#3B82F6"

def _card():
    f = QFrame()
    f.setStyleSheet(f"background:{BG_CARD};...")
    return f

def _lbl(text, size, bold=False, color=TXT_PRI):
    l = QLabel(text)
    l.setFont(QFont("Segoe UI", size, ...))
    return l
```

### Après (centralisé)
```python
# advanced_analytics_view.py
from ui_components import (
    BG_PAGE, BG_CARD, C_BLUE,
    _card, _lbl
)

# Utiliser directement!
card = _card()
label = _lbl("Texte", size=14, bold=True)
```

---

## 📋 Fichiers Modifiés

✅ **ui_components.py** - Nouveau module (créé)  
✅ **statistics_view.py** - Mise à jour des imports  
✅ **advanced_analytics_view.py** - Mise à jour des imports  

---

## 🚀 Prochaines Étapes

**Fichiers à migrer (potentiels):**
- `sales.py` - Utiliser les constantes de couleur
- `dashboard.py` - Utiliser les fonctions helper
- `purchases.py` - Utiliser les composants UI
- `clients.py` - Utiliser les animations

**Améliorations futures:**
- [ ] Créer `create_button()` pour les boutons stylisés
- [ ] Créer `create_dialog()` pour les dialogues
- [ ] Créer `create_table()` pour les tableaux stylisés
- [ ] Support des thèmes clairs/sombres
- [ ] Configuration de thème centralisée

---

## 📝 Notes

- ✅ **Rétro-compatibilité**: Les anciennes fonctions `_card()`, `_lbl()`, etc. continuent de fonctionner
- ✅ **Graduel**: Migrer le code existant progressive
- ✅ **DRY**: Une seule source de vérité pour les styles
- ✅ **Extensible**: Ajouter facilement de nouveaux composants

---

**Créé**: 8 Mars 2026  
**Version**: 1.0  
**Maintenance**: Centrale
