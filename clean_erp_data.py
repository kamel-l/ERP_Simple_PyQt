"""
============================================================================
SCRIPT DE NETTOYAGE - VIDER TOUTES LES DONNÉES DU PROJET ERP
============================================================================

Ce script vide toutes les données du système ERP tout en conservant
la structure de la base de données (tables, colonnes, etc.)

⚠️ ATTENTION : Cette action est IRRÉVERSIBLE !
Toutes les données seront définitivement supprimées.
============================================================================
"""

import sqlite3
import os
from datetime import datetime
import shutil


class ERPDataCleaner:
    """Classe pour nettoyer toutes les données de l'ERP"""
    
    def __init__(self, db_path='erp_system.db'):
        self.db_path = db_path
        self.backup_path = None
        
    def create_backup(self):
        """
        Crée une sauvegarde de la base de données avant nettoyage
        """
        if not os.path.exists(self.db_path):
            print(f"❌ Base de données '{self.db_path}' introuvable.")
            return False
        
        # Créer un dossier de sauvegarde
        backup_folder = 'backups'
        if not os.path.exists(backup_folder):
            os.makedirs(backup_folder)
        
        # Nom du fichier de sauvegarde avec date et heure
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.backup_path = os.path.join(backup_folder, f'erp_backup_{timestamp}.db')
        
        try:
            # Copier la base de données
            shutil.copy2(self.db_path, self.backup_path)
            print(f"✅ Sauvegarde créée : {self.backup_path}")
            return True
        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde : {e}")
            return False
    
    def get_table_info(self):
        """
        Récupère les informations sur toutes les tables
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Récupérer la liste des tables
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' 
                AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """)
            
            tables = cursor.fetchall()
            
            # Compter les enregistrements dans chaque table
            table_info = {}
            for (table_name,) in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                table_info[table_name] = count
            
            conn.close()
            return table_info
            
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des infos : {e}")
            return {}
    
    def display_current_data(self):
        """
        Affiche un résumé des données actuelles
        """
        print("\n" + "="*70)
        print("📊 ÉTAT ACTUEL DE LA BASE DE DONNÉES")
        print("="*70)
        
        table_info = self.get_table_info()
        
        if not table_info:
            print("❌ Aucune donnée à afficher")
            return
        
        total_records = 0
        
        print(f"\n{'Table':<25} {'Nombre d\'enregistrements':>20}")
        print("-"*70)
        
        for table_name, count in sorted(table_info.items()):
            emoji = "📦" if "product" in table_name else \
                    "👥" if "customer" in table_name else \
                    "🏢" if "supplier" in table_name else \
                    "💰" if "sale" in table_name else \
                    "📋" if "inventory" in table_name else \
                    "💸" if "expense" in table_name else "📄"
            
            print(f"{emoji} {table_name:<23} {count:>20,}")
            total_records += count
        
        print("-"*70)
        print(f"{'TOTAL':<25} {total_records:>20,}")
        print("="*70)
    
    def clean_all_data(self):
        """
        Vide toutes les données de toutes les tables
        """
        print("\n" + "="*70)
        print("🗑️  NETTOYAGE DE TOUTES LES DONNÉES")
        print("="*70)
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Liste des tables à nettoyer
            tables_to_clean = [
                'sales_details',      # D'abord les détails (clés étrangères)
                'sales',              # Puis les ventes
                'inventory',          # Puis l'inventaire
                'products',           # Puis les produits
                'customers',          # Puis les clients
                'suppliers',          # Puis les fournisseurs
                'expenses'            # Enfin les dépenses
            ]
            
            cleaned_count = {}
            
            for table_name in tables_to_clean:
                try:
                    # Compter avant suppression
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count_before = cursor.fetchone()[0]
                    
                    # Supprimer toutes les données
                    cursor.execute(f"DELETE FROM {table_name}")
                    
                    # Réinitialiser l'auto-increment
                    cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table_name}'")
                    
                    cleaned_count[table_name] = count_before
                    
                    print(f"✅ {table_name:<25} {count_before:>10,} enregistrements supprimés")
                    
                except sqlite3.OperationalError as e:
                    if "no such table" in str(e):
                        print(f"⚠️  {table_name:<25} Table non trouvée (ignorée)")
                    else:
                        print(f"❌ {table_name:<25} Erreur : {e}")
            
            # Valider les changements
            conn.commit()
            conn.close()
            
            print("\n" + "="*70)
            print(f"✅ NETTOYAGE TERMINÉ - {sum(cleaned_count.values()):,} enregistrements supprimés")
            print("="*70)
            
            return True
            
        except Exception as e:
            print(f"\n❌ ERREUR lors du nettoyage : {e}")
            return False
    
    def verify_cleanup(self):
        """
        Vérifie que toutes les tables sont bien vides
        """
        print("\n" + "="*70)
        print("🔍 VÉRIFICATION POST-NETTOYAGE")
        print("="*70)
        
        table_info = self.get_table_info()
        
        all_empty = True
        for table_name, count in table_info.items():
            status = "✅ Vide" if count == 0 else f"❌ {count} enregistrements restants"
            print(f"{table_name:<25} {status}")
            if count > 0:
                all_empty = False
        
        print("="*70)
        
        if all_empty:
            print("✅ TOUTES LES TABLES SONT VIDES")
        else:
            print("⚠️  ATTENTION : Certaines tables contiennent encore des données")
        
        return all_empty
    
    def run_full_cleanup(self):
        """
        Exécute le nettoyage complet avec toutes les étapes
        """
        print("\n" + "="*70)
        print("🧹 NETTOYAGE COMPLET DE LA BASE DE DONNÉES ERP")
        print("="*70)
        print("\n⚠️  ATTENTION : Cette action va supprimer TOUTES les données !")
        print("⚠️  Les données supprimées seront IRRÉCUPÉRABLES !")
        
        # Afficher l'état actuel
        self.display_current_data()
        
        # Demander confirmation
        print("\n" + "="*70)
        response = input("\n❓ Voulez-vous continuer ? (tapez 'OUI' en majuscules) : ")
        
        if response != "OUI":
            print("\n❌ Nettoyage annulé par l'utilisateur.")
            return False
        
        # Créer une sauvegarde
        print("\n📦 Création d'une sauvegarde de sécurité...")
        if not self.create_backup():
            print("\n⚠️  La sauvegarde a échoué.")
            response = input("❓ Voulez-vous continuer sans sauvegarde ? (tapez 'OUI') : ")
            if response != "OUI":
                print("\n❌ Nettoyage annulé.")
                return False
        
        # Nettoyer les données
        if not self.clean_all_data():
            print("\n❌ Le nettoyage a échoué.")
            return False
        
        # Vérifier le résultat
        self.verify_cleanup()
        
        print("\n" + "="*70)
        print("✅ NETTOYAGE TERMINÉ AVEC SUCCÈS !")
        print("="*70)
        
        if self.backup_path:
            print(f"\n💾 Sauvegarde disponible : {self.backup_path}")
        
        return True


# ============================================================================
# SCRIPT PRINCIPAL
# ============================================================================

def main():
    """
    Fonction principale pour exécuter le nettoyage
    """
    print("\n" + "="*70)
    print("🧹 SCRIPT DE NETTOYAGE - SYSTÈME ERP")
    print("="*70)
    
    # Créer l'instance du nettoyeur
    cleaner = ERPDataCleaner('erp_system.db')
    
    # Exécuter le nettoyage complet
    cleaner.run_full_cleanup()


# ============================================================================
# FONCTIONS UTILITAIRES SUPPLÉMENTAIRES
# ============================================================================

def clean_specific_table(table_name, db_path='erp_system.db'):
    """
    Nettoie une table spécifique
    
    Usage:
        clean_specific_table('products')
        clean_specific_table('customers')
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Compter avant
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        
        if count == 0:
            print(f"ℹ️  La table '{table_name}' est déjà vide.")
            conn.close()
            return True
        
        # Demander confirmation
        print(f"\n⚠️  Vous allez supprimer {count} enregistrements de la table '{table_name}'")
        response = input("❓ Confirmer ? (oui/non) : ")
        
        if response.lower() != 'oui':
            print("❌ Annulé.")
            conn.close()
            return False
        
        # Supprimer
        cursor.execute(f"DELETE FROM {table_name}")
        cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table_name}'")
        conn.commit()
        conn.close()
        
        print(f"✅ Table '{table_name}' nettoyée ({count} enregistrements supprimés)")
        return True
        
    except Exception as e:
        print(f"❌ Erreur : {e}")
        return False


def restore_from_backup(backup_path, db_path='erp_system.db'):
    """
    Restaure la base de données depuis une sauvegarde
    
    Usage:
        restore_from_backup('backups/erp_backup_20260215_143022.db')
    """
    try:
        if not os.path.exists(backup_path):
            print(f"❌ Fichier de sauvegarde '{backup_path}' introuvable.")
            return False
        
        print(f"\n⚠️  Vous allez restaurer la base de données depuis : {backup_path}")
        print(f"⚠️  La base actuelle '{db_path}' sera remplacée !")
        response = input("❓ Confirmer ? (OUI en majuscules) : ")
        
        if response != "OUI":
            print("❌ Restauration annulée.")
            return False
        
        # Copier la sauvegarde
        shutil.copy2(backup_path, db_path)
        
        print(f"✅ Base de données restaurée depuis : {backup_path}")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la restauration : {e}")
        return False


def list_backups():
    """
    Liste toutes les sauvegardes disponibles
    """
    backup_folder = 'backups'
    
    if not os.path.exists(backup_folder):
        print("ℹ️  Aucune sauvegarde trouvée.")
        return []
    
    backups = [f for f in os.listdir(backup_folder) if f.endswith('.db')]
    
    if not backups:
        print("ℹ️  Aucune sauvegarde trouvée.")
        return []
    
    print("\n" + "="*70)
    print("💾 SAUVEGARDES DISPONIBLES")
    print("="*70)
    
    for i, backup in enumerate(sorted(backups, reverse=True), 1):
        path = os.path.join(backup_folder, backup)
        size = os.path.getsize(path) / 1024  # Ko
        mtime = datetime.fromtimestamp(os.path.getmtime(path))
        
        print(f"{i}. {backup}")
        print(f"   📅 Date: {mtime.strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"   📦 Taille: {size:.2f} Ko")
        print()
    
    return backups


# ============================================================================
# MENU INTERACTIF
# ============================================================================

def interactive_menu():
    """
    Menu interactif pour choisir l'action
    """
    while True:
        print("\n" + "="*70)
        print("🧹 MENU DE NETTOYAGE - SYSTÈME ERP")
        print("="*70)
        print("\n1. 🗑️  Nettoyer TOUTES les données (complet)")
        print("2. 📊 Afficher l'état actuel de la base")
        print("3. 🗂️  Nettoyer une table spécifique")
        print("4. 💾 Lister les sauvegardes disponibles")
        print("5. 🔄 Restaurer depuis une sauvegarde")
        print("6. 📦 Créer une sauvegarde manuelle")
        print("0. ❌ Quitter")
        print("="*70)
        
        choice = input("\n👉 Votre choix : ")
        
        if choice == "1":
            cleaner = ERPDataCleaner('erp_system.db')
            cleaner.run_full_cleanup()
            
        elif choice == "2":
            cleaner = ERPDataCleaner('erp_system.db')
            cleaner.display_current_data()
            
        elif choice == "3":
            print("\nTables disponibles :")
            print("  - customers")
            print("  - products")
            print("  - suppliers")
            print("  - sales")
            print("  - sales_details")
            print("  - inventory")
            print("  - expenses")
            table = input("\n📋 Nom de la table à nettoyer : ")
            clean_specific_table(table)
            
        elif choice == "4":
            list_backups()
            
        elif choice == "5":
            backups = list_backups()
            if backups:
                backup_name = input("\n📂 Nom du fichier de sauvegarde : ")
                backup_path = os.path.join('backups', backup_name)
                restore_from_backup(backup_path)
            
        elif choice == "6":
            cleaner = ERPDataCleaner('erp_system.db')
            cleaner.create_backup()
            
        elif choice == "0":
            print("\n👋 Au revoir !")
            break
            
        else:
            print("\n❌ Choix invalide. Veuillez réessayer.")


# ============================================================================
# EXÉCUTION
# ============================================================================
def run_full_cleanup():
    main()   # أو أي اسم الاستدعاء الرئيسي عندك


if __name__ == "__main__":
    # Vous pouvez choisir d'exécuter :
    
    # Option 1 : Menu interactif (recommandé)
    interactive_menu()
    
    # Option 2 : Nettoyage direct (décommenter pour utiliser)
    # main()
    
    # Option 3 : Nettoyer une table spécifique (décommenter pour utiliser)
    # clean_specific_table('products')
    
    # Option 4 : Lister les sauvegardes (décommenter pour utiliser)
    # list_backups()