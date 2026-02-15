"""
============================================================================
SCRIPT DE NETTOYAGE - MODULE PRODUITS PyQt6
============================================================================

Ce script vide toutes les données du module products.py (PyQt6)
Les données sont stockées dans products_data (liste Python)
============================================================================
"""

import json
import os
from datetime import datetime
import shutil


class ProductsDataCleaner:
    """Classe pour nettoyer les données du module produits PyQt6"""
    
    def __init__(self, data_file='products_data.json'):
        self.data_file = data_file
        self.backup_path = None
    
    def create_backup(self):
        """
        Crée une sauvegarde du fichier de données
        """
        if not os.path.exists(self.data_file):
            print(f"ℹ️  Fichier '{self.data_file}' introuvable (pas encore de données)")
            return True
        
        # Créer un dossier de sauvegarde
        backup_folder = 'backups'
        if not os.path.exists(backup_folder):
            os.makedirs(backup_folder)
        
        # Nom du fichier de sauvegarde
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.backup_path = os.path.join(backup_folder, f'products_backup_{timestamp}.json')
        
        try:
            shutil.copy2(self.data_file, self.backup_path)
            print(f"✅ Sauvegarde créée : {self.backup_path}")
            return True
        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde : {e}")
            return False
    
    def display_current_data(self):
        """
        Affiche les données actuelles des produits
        """
        print("\n" + "="*70)
        print("📦 DONNÉES ACTUELLES DES PRODUITS (PyQt6)")
        print("="*70)
        
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                print(f"\n📊 Nombre de produits : {len(data)}")
                
                if data:
                    print("\n" + "-"*70)
                    print(f"{'ID':<5} {'Nom':<30} {'Quantité':<10} {'Prix':<15}")
                    print("-"*70)
                    
                    for product in data[:10]:  # Afficher les 10 premiers
                        print(f"{product['id']:<5} {product['name']:<30} "
                              f"{product['quantity']:<10} {product['price']:<15.2f}")
                    
                    if len(data) > 10:
                        print(f"... et {len(data) - 10} autres produits")
                    
                    print("-"*70)
                    
                    # Statistiques
                    total_quantity = sum(p['quantity'] for p in data)
                    total_value = sum(p['quantity'] * p['price'] for p in data)
                    
                    print(f"\n📊 STATISTIQUES:")
                    print(f"   Total produits : {len(data)}")
                    print(f"   Stock total : {total_quantity:,}")
                    print(f"   Valeur totale : {total_value:,.2f} DA")
                else:
                    print("\nℹ️  Aucun produit enregistré")
            else:
                print("\nℹ️  Aucun fichier de données trouvé")
        
        except Exception as e:
            print(f"\n❌ Erreur lors de la lecture : {e}")
        
        print("="*70)
    
    def clean_all_products(self):
        """
        Vide toutes les données des produits
        """
        print("\n" + "="*70)
        print("🗑️  NETTOYAGE DES DONNÉES PRODUITS")
        print("="*70)
        
        try:
            if os.path.exists(self.data_file):
                # Lire d'abord pour afficher le nombre
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                count = len(data)
                
                # Vider le fichier (liste vide)
                with open(self.data_file, 'w', encoding='utf-8') as f:
                    json.dump([], f, ensure_ascii=False, indent=2)
                
                print(f"✅ {count} produits supprimés")
                print("✅ Fichier de données réinitialisé")
            else:
                print("ℹ️  Aucun fichier de données à nettoyer")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors du nettoyage : {e}")
            return False
    
    def run_full_cleanup(self):
        """
        Exécute le nettoyage complet
        """
        print("\n" + "="*70)
        print("🧹 NETTOYAGE COMPLET DES PRODUITS PyQt6")
        print("="*70)
        
        # Afficher l'état actuel
        self.display_current_data()
        
        # Demander confirmation
        print("\n⚠️  ATTENTION : Cette action va supprimer TOUS les produits !")
        response = input("\n❓ Voulez-vous continuer ? (tapez 'OUI' en majuscules) : ")
        
        if response != "OUI":
            print("\n❌ Nettoyage annulé.")
            return False
        
        # Créer une sauvegarde
        print("\n📦 Création d'une sauvegarde...")
        self.create_backup()
        
        # Nettoyer
        if self.clean_all_products():
            print("\n✅ NETTOYAGE TERMINÉ !")
            
            if self.backup_path:
                print(f"💾 Sauvegarde : {self.backup_path}")
            
            return True
        else:
            print("\n❌ Le nettoyage a échoué.")
            return False


# ============================================================================
# GUIDE D'INTÉGRATION DANS products.py
# ============================================================================

INTEGRATION_CODE = """
# ============================================================================
# CODE À AJOUTER DANS products.py
# ============================================================================

import json
import os

class ProductsPage(QWidget):
    def __init__(self):
        super().__init__()
        
        # Fichier de sauvegarde des données
        self.data_file = 'products_data.json'
        
        # Charger les données depuis le fichier
        self.products_data = self.load_products_from_file()
        
        # ... reste du code ...
    
    def load_products_from_file(self):
        \"\"\"Charge les produits depuis le fichier JSON\"\"\"
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_products_to_file(self):
        \"\"\"Sauvegarde les produits dans le fichier JSON\"\"\"
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.products_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            QMessageBox.warning(self, "Erreur", f"Erreur de sauvegarde : {e}")
    
    def add_product(self):
        \"\"\"Ajoute un produit\"\"\"
        # ... code existant ...
        
        self.products_data.append(product_data)
        self.save_products_to_file()  # ← AJOUTER CETTE LIGNE
        
        # ... reste du code ...
    
    def edit_product(self):
        \"\"\"Modifie un produit\"\"\"
        # ... code existant ...
        
        self.products_data[selected] = updated_data
        self.save_products_to_file()  # ← AJOUTER CETTE LIGNE
        
        # ... reste du code ...
    
    def delete_product(self):
        \"\"\"Supprime un produit\"\"\"
        # ... code existant ...
        
        del self.products_data[selected]
        self.save_products_to_file()  # ← AJOUTER CETTE LIGNE
        
        # ... reste du code ...
"""


# ============================================================================
# SCRIPT PRINCIPAL
# ============================================================================

def main():
    """
    Fonction principale
    """
    print("\n" + "="*70)
    print("🧹 SCRIPT DE NETTOYAGE - MODULE PRODUITS PyQt6")
    print("="*70)
    
    cleaner = ProductsDataCleaner('products_data.json')
    cleaner.run_full_cleanup()


# ============================================================================
# MENU INTERACTIF
# ============================================================================

def interactive_menu():
    """
    Menu interactif
    """
    while True:
        print("\n" + "="*70)
        print("🧹 MENU - NETTOYAGE PRODUITS PyQt6")
        print("="*70)
        print("\n1. 📊 Afficher les données actuelles")
        print("2. 🗑️  Nettoyer tous les produits")
        print("3. 📦 Créer une sauvegarde")
        print("4. 💾 Lister les sauvegardes")
        print("5. ℹ️  Guide d'intégration")
        print("0. ❌ Quitter")
        print("="*70)
        
        choice = input("\n👉 Votre choix : ")
        
        cleaner = ProductsDataCleaner('products_data.json')
        
        if choice == "1":
            cleaner.display_current_data()
            
        elif choice == "2":
            cleaner.run_full_cleanup()
            
        elif choice == "3":
            cleaner.create_backup()
            
        elif choice == "4":
            list_backups()
            
        elif choice == "5":
            print("\n" + "="*70)
            print("📖 GUIDE D'INTÉGRATION")
            print("="*70)
            print(INTEGRATION_CODE)
            
        elif choice == "0":
            print("\n👋 Au revoir !")
            break
            
        else:
            print("\n❌ Choix invalide.")


def list_backups():
    """
    Liste les sauvegardes disponibles
    """
    backup_folder = 'backups'
    
    if not os.path.exists(backup_folder):
        print("\nℹ️  Aucune sauvegarde trouvée.")
        return
    
    backups = [f for f in os.listdir(backup_folder) 
               if f.startswith('products_backup_') and f.endswith('.json')]
    
    if not backups:
        print("\nℹ️  Aucune sauvegarde de produits trouvée.")
        return
    
    print("\n" + "="*70)
    print("💾 SAUVEGARDES DISPONIBLES")
    print("="*70)
    
    for i, backup in enumerate(sorted(backups, reverse=True), 1):
        path = os.path.join(backup_folder, backup)
        size = os.path.getsize(path) / 1024
        mtime = datetime.fromtimestamp(os.path.getmtime(path))
        
        print(f"\n{i}. {backup}")
        print(f"   📅 {mtime.strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"   📦 {size:.2f} Ko")


# ============================================================================
# EXÉCUTION
# ============================================================================

if __name__ == "__main__":
    # Menu interactif (recommandé)
    interactive_menu()
    
    # Ou nettoyage direct (décommenter pour utiliser)
    # main()