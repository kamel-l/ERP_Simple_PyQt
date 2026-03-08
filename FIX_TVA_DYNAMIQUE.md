# 🔧 Correction: TVA Dynamique dans les Ventes

## 🐛 Problème Identifié

Quand l'utilisateur changeait le taux de TVA dans **Paramètres > Système > Configuration Financière**, la valeur de la TVA n'était pas appliquée dans la page **Point de Vente**.

**Causes:**
1. Le label affichait toujours "TVA (19%) :" en dur
2. Les calculs utilisaient une constante `tax = subtotal * 0.19` 
3. Aucune récupération dynamique depuis les settings

---

## ✅ Solution Implémentée

### Dans `sales.py`:

#### 1. **Nouvelle méthode: `_get_vat_rate()`**
```python
def _get_vat_rate(self):
    """Récupère le taux de TVA depuis les settings"""
    try:
        vat_str = self.db.get_setting('vat', '19')
        return float(vat_str) / 100.0  # Convertir en décimal (ex: 19 -> 0.19)
    except:
        return 0.19  # Valeur par défaut
```
- Récupère la TVA stockée en settings
- Convertit le pourcentage en décimal
- Gère les erreurs avec une valeur par défaut

#### 2. **Initialisation dynamique du label TVA**
```python
# Avant (hardcoded):
self.tax_label = _row(right_col, "TVA (19%) :", COLORS['warning'])

# Après (dynamique):
self.vat_percent = float(self.db.get_setting('vat', '19'))
tax_row = QHBoxLayout()
# ... création manuelle du layout avec label modifiable
self.tax_header_label = QLabel(f"TVA ({self.vat_percent:.0f}%) :")
self.tax_label = QLabel("—")
```

#### 3. **Mise à jour automatique dans `update_totals()`**
```python
def update_totals(self):
    subtotal = sum(item['total'] for item in self.cart_items)
    self.vat_rate = self._get_vat_rate()
    self.vat_percent = self.vat_rate * 100  # Convertir en pourcentage
    # ✨ NOUVELLE LIGNE: Mettre à jour le label
    self.tax_header_label.setText(f"TVA ({self.vat_percent:.0f}%) :")
    tax = subtotal * self.vat_rate  # Utiliser la TVA dynamique
    total = subtotal + tax
    # ... reste du code
```

#### 4. **Calcul correct de la TVA dans `save_sale()`**
```python
# Avant:
tax = subtotal * 0.19

# Après:
self.vat_rate = self._get_vat_rate()
tax = subtotal * self.vat_rate
```

### Dans `db_manager.py`:
✅ Aucun changement nécessaire - la méthode `create_sale()` récupère déjà correctement la TVA via `get_tax_rates()`

---

## 🔄 Flux de Synchronisation

```
User change TVA dans Paramètres
    ↓
db.set_setting('vat', valeur)
    ↓
User revient à Point de Vente
    ↓
_get_vat_rate() récupère la nouvelle valeur
    ↓
update_totals() met à jour:
  - Label: "TVA (20%)" 
  - Calcul: tax = subtotal * 0.20
    ↓
Affichage et calculs corrects ✅
```

---

## 📝 Exemple Pratique

**Scénario:**
1. TVA initiale: 19%
2. Utilisateur ajoute article: 100 DA
   - TVA: 19 DA
   - Total: 119 DA ✅

3. Utilisateur change TVA à 20% dans Paramètres
4. Utilisateur revient à Ventes sans fermer
5. Interface affiche maintenant: "TVA (20%) :"
6. Si on ajoute un nouvel article de 100 DA:
   - TVA: 20 DA ✅
   - Total: 120 DA ✅

---

## 🔍 Code Modifié

### Avant:
```python
class SalesPage(QWidget):
    def __init__(self):
        self.db = get_database()
        self.cart_items = []
        # ... 
        self.tax_label = _row(right_col, "TVA (19%) :", COLORS['warning'])  # ❌ Dur

    def update_totals(self):
        tax = subtotal * 0.19  # ❌ Dur
        self.tax_label.setText(f"{tax:,.2f} DA")
```

### Après:
```python
class SalesPage(QWidget):
    def __init__(self):
        self.db = get_database()
        self.cart_items = []
        self.vat_rate = self._get_vat_rate()  # ✅ Dynamic
        # ...
        self.vat_percent = float(self.db.get_setting('vat', '19'))
        self.tax_header_label = QLabel(f"TVA ({self.vat_percent:.0f}%) :")
        self.tax_label = QLabel("—")

    def _get_vat_rate(self):  # ✅ Nouvelle métode
        vat_str = self.db.get_setting('vat', '19')
        return float(vat_str) / 100.0

    def update_totals(self):
        self.vat_rate = self._get_vat_rate()  # ✅ Récupère le taux
        self.vat_percent = self.vat_rate * 100
        self.tax_header_label.setText(f"TVA ({self.vat_percent:.0f}%) :")  # ✅ MAJ label
        tax = subtotal * self.vat_rate  # ✅ Taux dynamique
        self.tax_label.setText(f"{tax:,.2f} DA")
```

---

## ✨ Avantages

✅ TVA synchronisée en temps réel  
✅ Pas besoin de redémarrer l'app  
✅ Calculs corrects automatiquement  
✅ Label reflète la valeur actuelle  
✅ Cohérent avec settings de l'app  

---

## 🧪 Test

1. Ouvrir l'app → Point de Vente
2. Ajouter un article (affiche TVA 19%)
3. Aller à Paramètres → Système  
4. Changer TVA à 20% → Enregistrer
5. Revenir à Ventes
6. ✅ Label affiche "TVA (20%)"
7. Ajouter nouvel article → TVA calculée à 20%

---

**Date**: 8 Mars 2026  
**Fichiers modifiés**: `sales.py`  
**Impact**: Point de Vente, Facturation, Montants TVA
