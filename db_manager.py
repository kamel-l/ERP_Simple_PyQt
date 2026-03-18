"""
Module de gestion de la base de données SQLite
Gère toutes les opérations CRUD pour l'application ERP
"""

import sqlite3
from config import config
from datetime import datetime
from pathlib import Path
import json


class Database:
    """Classe principale pour gérer la base de données SQLite"""
    
    def __init__(self, db_path=None):
        """
        Initialise la connexion à la base de données
        
        Args:
            db_path: Chemin vers le fichier de base de données
        """
        self.db_path = db_path or config.db_path
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        """Établit la connexion à la base de données"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row  # Pour accéder aux colonnes par nom
            self.cursor = self.conn.cursor()
            print(f"✅ Connexion à la base de données établie: {self.db_path}")
        except sqlite3.Error as e:
            print(f"❌ Erreur de connexion à la base de données: {e}")
            raise
    
    def disconnect(self):
        """Ferme la connexion à la base de données"""
        if self.conn:
            self.conn.close()
            print("✅ Connexion à la base de données fermée")
    
    def create_tables(self):
        """Crée toutes les tables nécessaires si elles n'existent pas"""
        
        # Table des clients
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                address TEXT,
                nif TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Table des catégories de produits
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Table des produits
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                category_id INTEGER,
                purchase_price REAL DEFAULT 0,
                selling_price REAL NOT NULL,
                stock_quantity INTEGER DEFAULT 0,
                min_stock INTEGER DEFAULT 0,
                barcode TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories(id)
            )
        """)
        
        # Table des fournisseurs
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS suppliers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                address TEXT,
                nif TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Table des ventes
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_number TEXT UNIQUE NOT NULL,
                client_id INTEGER,
                sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                subtotal REAL NOT NULL,
                tax_rate REAL DEFAULT 19.0,
                tax_amount REAL NOT NULL,
                discount REAL DEFAULT 0,
                total REAL NOT NULL,
                payment_method TEXT,
                payment_status TEXT DEFAULT 'paid',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (client_id) REFERENCES clients(id)
            )
        """)
        
        # Table des détails de ventes (lignes de facturation)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS sale_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sale_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                unit_price REAL NOT NULL,
                discount REAL DEFAULT 0,
                total REAL NOT NULL,
                FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        """)
        
        # Table des achats
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS purchases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                supplier_id INTEGER,
                purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                subtotal REAL NOT NULL,
                tax_rate REAL DEFAULT 10.0,
                tax_amount REAL NOT NULL,
                total REAL NOT NULL,
                payment_method TEXT,
                payment_status TEXT DEFAULT 'paid',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
            )
        """)
        
        # Table des détails d'achats
        # Structure corrigée : product_id (INTEGER, clé étrangère correcte)
        # ET product_name (TEXT, pour affichage rapide sans JOIN)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS purchase_items (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                purchase_id  INTEGER NOT NULL,
                product_id   INTEGER,
                product_name TEXT,
                quantity     INTEGER NOT NULL,
                unit_price   REAL    NOT NULL,
                total        REAL    NOT NULL,
                created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (purchase_id) REFERENCES purchases(id) ON DELETE CASCADE,
                FOREIGN KEY (product_id)  REFERENCES products(id)
            )
        """)
        # Migration transparente pour les bases existantes
        self._migrate_purchase_items()
        
        # Table des mouvements de stock
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS stock_movements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                movement_type TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        """)
        
        # Table des paramètres de l'application
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Table des utilisateurs
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT,
                role TEXT DEFAULT 'user',
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        """)
        
            # Table des retours/avoirs
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS returns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                return_number TEXT UNIQUE NOT NULL,
                original_sale_id INTEGER NOT NULL,
                return_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                client_id INTEGER,
                client_name TEXT,
                total REAL NOT NULL,
                motif TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (original_sale_id) REFERENCES sales(id) ON DELETE CASCADE,
                FOREIGN KEY (client_id) REFERENCES clients(id)
            )
        """)
        
        # Table des articles retournés
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS return_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                return_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                unit_price REAL NOT NULL,
                total REAL NOT NULL,
                FOREIGN KEY (return_id) REFERENCES returns(id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        """)
        
        self.conn.commit()
        print("✅ Tables créées avec succès")

    def _migrate_purchase_items(self):
        """
        Migration robuste de purchase_items pour les bases existantes.
        Gère tous les cas :
          - Ancienne base : product_name TEXT seulement → ajoute product_id
          - Base migrée Bug2 : product_id seulement, product_name manquante → rajoute product_name
          - Base déjà complète : les deux colonnes existent → ne fait rien
        """
        try:
            self.cursor.execute("PRAGMA table_info(purchase_items)")
            cols = {row[1] for row in self.cursor.fetchall()}

            # Ajouter product_id si manquant
            if 'product_id' not in cols:
                self.cursor.execute(
                    "ALTER TABLE purchase_items ADD COLUMN product_id INTEGER")
                # Remplir product_id depuis le nom via JOIN products
                self.cursor.execute("""
                    UPDATE purchase_items
                    SET product_id = (
                        SELECT id FROM products WHERE name = purchase_items.product_name
                    )
                    WHERE product_id IS NULL
                """)
                self.conn.commit()
                print("🔧 Migration : colonne product_id ajoutée à purchase_items")

            # Rajouter product_name si elle a été supprimée par la correction Bug2
            if 'product_name' not in cols:
                self.cursor.execute(
                    "ALTER TABLE purchase_items ADD COLUMN product_name TEXT")
                # Remplir depuis le nom du produit via product_id
                self.cursor.execute("""
                    UPDATE purchase_items
                    SET product_name = (
                        SELECT name FROM products WHERE id = purchase_items.product_id
                    )
                    WHERE product_name IS NULL
                """)
                self.conn.commit()
                print("🔧 Migration : colonne product_name restaurée dans purchase_items")

        except Exception as e:
            print(f"⚠️  Migration purchase_items (non bloquant) : {e}")

    def get_best_days(self):
        """
        Retourne les 2 meilleurs jours avec détails :
        - best_sales_day : jour avec le plus de ventes (nombre)
        - sales_count : nombre de ventes ce jour
        - best_revenue_day : jour avec la plus grande recette (montant)
        - revenue_amount : montant total de la recette ce jour
        """
        JOURS = {
            '0': 'Dimanche', '1': 'Lundi',    '2': 'Mardi',
            '3': 'Mercredi', '4': 'Jeudi',    '5': 'Vendredi',
            '6': 'Samedi',
        }
        result = {
            "sales_day": "—", 
            "sales_count": 0,
            "revenue_day": "—",
            "revenue_amount": 0
        }
        
        try:
            # Meilleur jour par nombre de ventes
            self.cursor.execute("""
                SELECT
                    CAST(strftime('%w', sale_date) AS TEXT) AS day_num,
                    COUNT(*) AS nb_ventes
                FROM sales
                WHERE sale_date IS NOT NULL
                GROUP BY CAST(strftime('%w', sale_date) AS TEXT)
                ORDER BY nb_ventes DESC
                LIMIT 1
            """)
            row = self.cursor.fetchone()
            if row and row['day_num']:
                day_key = str(row['day_num']).strip()
                result["sales_day"] = JOURS.get(day_key, "—")
                result["sales_count"] = int(row['nb_ventes'])
            
            # Meilleur jour par recette (montant total)
            self.cursor.execute("""
                SELECT
                    CAST(strftime('%w', sale_date) AS TEXT) AS day_num,
                    SUM(total) AS total_da
                FROM sales
                WHERE sale_date IS NOT NULL
                GROUP BY CAST(strftime('%w', sale_date) AS TEXT)
                ORDER BY total_da DESC
                LIMIT 1
            """)
            row = self.cursor.fetchone()
            if row and row['day_num']:
                day_key = str(row['day_num']).strip()
                result["revenue_day"] = JOURS.get(day_key, "—")
                result["revenue_amount"] = float(row['total_da'] or 0)
                
        except Exception as e:
            print(f"⚠️  get_best_days : {e}")
        
        return result

    # ==================== CLIENTS ====================
    
    def add_client(self, name, phone="", email="", address="", nif=""):
        """Ajoute un nouveau client"""
        try:
            self.cursor.execute("""
                INSERT INTO clients (name, phone, email, address, nif)
                VALUES (?, ?, ?, ?, ?)
            """, (name, phone, email, address, nif))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"❌ Erreur lors de l'ajout du client: {e}")
            return None
    
    def get_all_clients(self, limit=None, offset=0):
        """Récupère les clients (pagination via limit/offset)."""
        query = "SELECT * FROM clients ORDER BY name"
        if limit is not None:
            query += f" LIMIT {limit} OFFSET {offset}"
        self.cursor.execute(query)
        return [dict(row) for row in self.cursor.fetchall()]

    def count_clients(self, search=None):
        """Retourne le nombre total de clients."""
        if search:
            self.cursor.execute(
                "SELECT COUNT(*) FROM clients WHERE name LIKE ? OR email LIKE ?",
                (f"%{search}%", f"%{search}%"))
        else:
            self.cursor.execute("SELECT COUNT(*) FROM clients")
        return self.cursor.fetchone()[0]
    
    def get_client_by_id(self, client_id):
        """Récupère un client par son ID"""
        self.cursor.execute("SELECT * FROM clients WHERE id = ?", (client_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def update_client(self, client_id, name, phone="", email="", address="", nif=""):
        """Met à jour les informations d'un client"""
        try:
            self.cursor.execute("""
                UPDATE clients 
                SET name = ?, phone = ?, email = ?, address = ?, nif = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (name, phone, email, address, nif, client_id))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"❌ Erreur lors de la mise à jour du client: {e}")
            return False
    
    def delete_client(self, client_id):
        """Supprime un client"""
        try:
            self.cursor.execute("DELETE FROM clients WHERE id = ?", (client_id,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"❌ Erreur lors de la suppression du client: {e}")
            return False
    
    def search_clients(self, search_term):
        """Recherche des clients par nom ou email"""
        self.cursor.execute("""
            SELECT * FROM clients 
            WHERE name LIKE ? OR email LIKE ?
            ORDER BY name
        """, (f"%{search_term}%", f"%{search_term}%"))
        return [dict(row) for row in self.cursor.fetchall()]
    
    
    def search_clients_by_first_letter(self, letter):
        """
        Recherche les clients dont le nom commence par une lettre spécifique
        """
        self.cursor.execute("""
            SELECT * FROM clients 
            WHERE name LIKE ? OR name LIKE ?
            ORDER BY name
        """, (
            f"{letter}%",          # Lettre minuscule
            f"{letter.upper()}%"    # Lettre majuscule (au cas où)
        ))
        return [dict(row) for row in self.cursor.fetchall()]
    
    
    def get_invoices_by_client(self, client_id):
        """Récupère toutes les factures d'un client"""
        self.cursor.execute("""
            SELECT 
                id,
                invoice_number,
                client_id,
                sale_date as created_at,
                subtotal,
                tax_amount,
                total as total_amount,
                payment_method,
                payment_status as status
            FROM sales 
            WHERE client_id = ?
            ORDER BY sale_date DESC
        """, (client_id,))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def generate_invoice_number(self):
        """
        Génère le prochain numéro de facture séquentiel
        Format: FAC-1000, FAC-1001, FAC-1002, etc.
        La première facture sera FAC-1000
        Gère la migration depuis ancien format FAC-timestamp
        
        Les nouveau format séquentiel: 1000-99999
        Les anciens timestamps (> 100000) sont ignorés
        """
        try:
            # Récupérer tous les numéros de facture existants
            self.cursor.execute("""
                SELECT invoice_number FROM sales 
                WHERE invoice_number LIKE 'FAC-%'
            """)
            results = self.cursor.fetchall()
            
            next_number = 1000  # Valeur par défaut pour première facture
            sequential_invoices = []
            
            if results:
                # Parcourir toutes les factures et extraire les numéros valides
                for row in results:
                    last_invoice = row['invoice_number']
                    try:
                        # Tenter d'extraire le numéro après "FAC-"
                        number_part = last_invoice.replace("FAC-", "").strip()
                        
                        # Vérifier si c'est un nombre valide
                        if number_part.isdigit():
                            number = int(number_part)
                            # Garder seulement les numéros séquentiels (1000-99999)
                            # Les nombres > 100000 sont des anciens timestamps
                            if 1000 <= number <= 99999:
                                sequential_invoices.append(number)
                    except (ValueError, AttributeError):
                        # Ignorer les formats invalides
                        continue
                
                # Si on a trouvé des factures séquentielles, prendre la plus grande
                if sequential_invoices:
                    next_number = max(sequential_invoices) + 1
            
            return f"FAC-{next_number}"
        
        except Exception as e:
            print(f"⚠️  Erreur lors de la génération du numéro de facture: {e}")
            # Fallback: utiliser timestamp
            from datetime import datetime
            return f"FAC-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # ==================== CATÉGORIES ====================
    
    def add_category(self, name, description=""):
        """Ajoute une nouvelle catégorie"""
        try:
            self.cursor.execute("""
                INSERT INTO categories (name, description)
                VALUES (?, ?)
            """, (name, description))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"❌ Erreur lors de l'ajout de la catégorie: {e}")
            return None
    
    def get_all_categories(self):
        """Récupère toutes les catégories"""
        self.cursor.execute("SELECT * FROM categories ORDER BY name")
        return [dict(row) for row in self.cursor.fetchall()]
    
    # ==================== PRODUITS ====================
    
    def add_product(self, name, selling_price, category_id=None, 
                    description="", purchase_price=0, stock_quantity=0, 
                    min_stock=0, barcode=""):
        """Ajoute un nouveau produit"""
        try:
            self.cursor.execute("""
                INSERT INTO products 
                (name, description, category_id, purchase_price, 
                 selling_price, stock_quantity, min_stock, barcode)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, description, category_id, purchase_price,
                  selling_price, stock_quantity, min_stock, barcode))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"❌ Erreur lors de l'ajout du produit: {e}")
            return None
    
    def get_all_products(self, limit=None, offset=0):
        """Récupère les produits avec leurs catégories (pagination via limit/offset)."""
        query = """
            SELECT p.*, c.name as category_name
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            ORDER BY p.name
        """
        if limit is not None:
            query += f" LIMIT {limit} OFFSET {offset}"
        self.cursor.execute(query)
        return [dict(row) for row in self.cursor.fetchall()]

    def count_products(self, search=None):
        """Retourne le nombre total de produits."""
        if search:
            self.cursor.execute(
                "SELECT COUNT(*) FROM products WHERE name LIKE ? OR barcode LIKE ?",
                (f"%{search}%", f"%{search}%"))
        else:
            self.cursor.execute("SELECT COUNT(*) FROM products")
        return self.cursor.fetchone()[0]
    
    def get_product_by_id(self, product_id):
        """Récupère un produit par son ID"""
        self.cursor.execute("""
            SELECT p.*, c.name as category_name
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE p.id = ?
        """, (product_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    

    def update_product(self, product_id, name, selling_price, 
                      category_id=None, description="", purchase_price=0, 
                      stock_quantity=0, min_stock=0, barcode=""):
        """Met à jour un produit"""
        try:
            self.cursor.execute("""
                UPDATE products 
                SET name = ?, description = ?, category_id = ?,
                    purchase_price = ?, selling_price = ?, stock_quantity = ?,
                    min_stock = ?, barcode = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (name, description, category_id, purchase_price,
                  selling_price, stock_quantity, min_stock, barcode, product_id))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"❌ Erreur lors de la mise à jour du produit: {e}")
            return False
    
    def delete_product(self, product_id):
        """Supprime un produit"""
        try:
            self.cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"❌ Erreur lors de la suppression du produit: {e}")
            return False
    
    def update_stock(self, product_id, quantity, movement_type, notes=""):
        """
        Met à jour le stock d'un produit
        
        Args:
            product_id: ID du produit
            quantity: Quantité (positive ou négative)
            movement_type: 'sale', 'purchase', 'adjustment', 'return'
            notes: Notes additionnelles
        """
        try:
            # Mettre à jour la quantité en stock
            self.cursor.execute("""
                UPDATE products 
                SET stock_quantity = stock_quantity + ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (quantity, product_id))
            
            # Enregistrer le mouvement de stock
            self.cursor.execute("""
                INSERT INTO stock_movements 
                (product_id, movement_type, quantity, notes)
                VALUES (?, ?, ?, ?)
            """, (product_id, movement_type, quantity, notes))
            
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"❌ Erreur lors de la mise à jour du stock: {e}")
            self.conn.rollback()
            return False
    
        # Dans db_manager.py - modifier la méthode search_products
    def search_products(self, search_term, starts_with=False):
        """
        Recherche des produits par nom
        
        Args:
            search_term: Terme de recherche
            starts_with: Si True, recherche les noms qui commencent par le terme
        """
        if starts_with:
            # Recherche les noms qui commencent par le terme
            self.cursor.execute("""
                SELECT p.*, c.name as category_name
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.id
                WHERE p.name LIKE ?
                ORDER BY p.name
            """, (f"{search_term}%",))  # Note: pas de % au début
        else:
            # Recherche les noms qui contiennent le terme (comportement original)
            self.cursor.execute("""
                SELECT p.*, c.name as category_name
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.id
                WHERE p.name LIKE ?
                ORDER BY p.name
            """, (f"%{search_term}%",))
        
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_low_stock_products(self):
        """Récupère les produits avec un stock faible"""
        self.cursor.execute("""
            SELECT p.*, c.name as category_name
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE p.stock_quantity <= p.min_stock
            ORDER BY p.stock_quantity
        """)
        return [dict(row) for row in self.cursor.fetchall()]
    
    # ==================== FOURNISSEURS ====================
    
    def add_supplier(self, name, phone="", email="", address="", nif=""):
        """Ajoute un nouveau fournisseur"""
        try:
            self.cursor.execute("""
                INSERT INTO suppliers (name, phone, email, address, nif)
                VALUES (?, ?, ?, ?, ?)
            """, (name, phone, email, address, nif))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"❌ Erreur lors de l'ajout du fournisseur: {e}")
            return None
    
    def get_all_suppliers(self):
        """Récupère tous les fournisseurs"""
        self.cursor.execute("SELECT * FROM suppliers ORDER BY name")
        return [dict(row) for row in self.cursor.fetchall()]
    
    # ==================== VENTES ====================
    
    def create_sale(self, invoice_number, client_id, items, payment_method="cash",
                   tax_rate=None, discount=0, notes="", sale_date=None):
        """
        Crée une nouvelle vente avec ses articles
        
        Args:
            invoice_number: Numéro de facture
            client_id: ID du client
            items: Liste de dict avec 'product_id', 'quantity', 'unit_price', 'discount'
            payment_method: Mode de paiement
            tax_rate: Taux de TVA (si None, récupère depuis les settings)
            discount: Remise globale
            notes: Notes
        """
        try:
            # Si tax_rate n'est pas spécifié, récupérer depuis les settings
            if tax_rate is None:
                tax_rates = self.get_tax_rates()
                tax_rate = tax_rates["sales_tax"]
                print(f"✅ create_sale() - TVA récupérée des settings: {tax_rate}%")
            else:
                print(f"✅ create_sale() - TVA spécifiée: {tax_rate}%")
            
            # Calculer les totaux
            subtotal = sum(item['quantity'] * item['unit_price'] * 
                          (1 - item.get('discount', 0) / 100) for item in items)
            tax_amount = subtotal * (tax_rate / 100)
            total = subtotal + tax_amount - discount
            
            # Créer la vente
            if sale_date:
                self.cursor.execute("""
                    INSERT INTO sales 
                    (invoice_number, client_id, subtotal, tax_rate, tax_amount, 
                     discount, total, payment_method, notes, sale_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (invoice_number, client_id, subtotal, tax_rate, tax_amount,
                      discount, total, payment_method, notes, sale_date))
            else:
                self.cursor.execute("""
                    INSERT INTO sales 
                    (invoice_number, client_id, subtotal, tax_rate, tax_amount, 
                     discount, total, payment_method, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (invoice_number, client_id, subtotal, tax_rate, tax_amount,
                      discount, total, payment_method, notes))
            
            sale_id = self.cursor.lastrowid
            
            # Ajouter les articles
            for item in items:
                item_total = (item['quantity'] * item['unit_price'] * 
                             (1 - item.get('discount', 0) / 100))
                
                self.cursor.execute("""
                    INSERT INTO sale_items 
                    (sale_id, product_id, quantity, unit_price, discount, total)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (sale_id, item['product_id'], item['quantity'], 
                      item['unit_price'], item.get('discount', 0), item_total))
                
                # Diminuer le stock
                self.update_stock(
                    item['product_id'], 
                    -item['quantity'],
                    'sale',
                    f"Vente #{invoice_number}"
                )
            
            self.conn.commit()
            return sale_id
            
        except sqlite3.Error as e:
            print(f"❌ Erreur lors de la création de la vente: {e}")
            self.conn.rollback()
            return None
    
    def get_all_sales(self, limit=None, offset=0):
        """Récupère toutes les ventes avec le nombre d'articles par vente (items_count)."""
        query = """
            SELECT s.*, c.name as client_name,
                   COUNT(si.id) AS items_count
            FROM sales s
            LEFT JOIN clients c ON s.client_id = c.id
            LEFT JOIN sale_items si ON si.sale_id = s.id
            GROUP BY s.id
            ORDER BY s.sale_date DESC
        """
        if limit is not None:
            query += f" LIMIT {limit} OFFSET {offset}"
        
        self.cursor.execute(query)
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_sale_by_id(self, sale_id):
        """Récupère une vente avec ses détails"""
        # Vente principale
        self.cursor.execute("""
            SELECT s.*, c.name as client_name, c.phone as client_phone,
                   c.email as client_email, c.address as client_address
            FROM sales s
            LEFT JOIN clients c ON s.client_id = c.id
            WHERE s.id = ?
        """, (sale_id,))
        
        sale = self.cursor.fetchone()
        if not sale:
            return None
        
        sale_dict = dict(sale)
        
        # Articles de la vente
        self.cursor.execute("""
            SELECT
                si.id,
                si.sale_id,
                si.product_id,
                si.quantity,
                si.unit_price,
                si.discount,
                si.total,
                COALESCE(p.name, 'Produit supprimé') AS product_name,
                COALESCE(p.description, '')               AS product_reference
            FROM sale_items si
            LEFT JOIN products p ON si.product_id = p.id
            WHERE si.sale_id = ?
        """, (sale_id,))
        
        sale_dict['items'] = [dict(row) for row in self.cursor.fetchall()]
    
        
        return sale_dict
    
    def get_sale_items(self, sale_id):
        """Récupère les articles d'une vente"""
        self.cursor.execute("""
            SELECT
                si.id,
                si.sale_id,
                si.product_id,
                si.quantity,
                si.unit_price,
                si.discount,
                si.total,
                COALESCE(p.name, 'Produit supprimé') AS product_name,
                COALESCE(p.barcode, '')               AS product_reference
            FROM sale_items si
            LEFT JOIN products p ON si.product_id = p.id
            WHERE si.sale_id = ?
            ORDER BY si.id
        """, (sale_id,))
        
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_sales_by_date_range(self, start_date, end_date):
        """Récupère les ventes dans une période"""
        self.cursor.execute("""
            SELECT s.*, c.name as client_name
            FROM sales s
            LEFT JOIN clients c ON s.client_id = c.id
            WHERE DATE(s.sale_date) BETWEEN ? AND ?
            ORDER BY s.sale_date DESC
        """, (start_date, end_date))
        return [dict(row) for row in self.cursor.fetchall()]
    
    # ==================== ACHATS ====================
    
    def create_purchase(self, reference, supplier_id, items, payment_method="cash",
                   tax_rate=None, notes=""):
        """Crée un nouvel achat avec ses articles"""
        try:
            # Si tax_rate n'est pas spécifié, récupérer depuis les settings
            if tax_rate is None:
                tax_rates = self.get_tax_rates()
                tax_rate = tax_rates["purchase_tax"]
                print(f"✅ create_purchase() - TVA Achats récupérée des settings: {tax_rate}%")
            else:
                print(f"✅ create_purchase() - TVA Achats spécifiée: {tax_rate}%")
            
            # Calculer les totaux
            subtotal = sum(item['quantity'] * item['unit_price'] for item in items)
            tax_amount = subtotal * (tax_rate / 100)
            total = subtotal + tax_amount
            
            # Créer l'achat
            self.cursor.execute("""
                INSERT INTO purchases 
                (supplier_id, subtotal, tax_rate, tax_amount, 
                total, payment_method, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (supplier_id, subtotal, tax_rate, tax_amount,
                total, payment_method, notes))
            
            purchase_id = self.cursor.lastrowid
            
            # Ajouter les articles
            for item in items:
                item_total = item['quantity'] * item['unit_price']
                
                # Insérer product_id ET product_name pour cohérence et affichage
                self.cursor.execute("""
                    INSERT INTO purchase_items
                    (purchase_id, product_id, product_name, quantity, unit_price, total)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (purchase_id, item['product_id'], item['product_name'],
                    item['quantity'], item['unit_price'], item_total))
                
                # Augmenter le stock avec l'ID du produit
                self.update_stock(
                    item['product_id'],  # Maintenant c'est l'ID
                    item['quantity'],
                    'purchase',
                    f"Achat #{reference}"
                )
            
            self.conn.commit()
            return purchase_id
            
        except sqlite3.Error as e:
            print(f"❌ Erreur lors de la création de l'achat: {e}")
            self.conn.rollback()
            return None
    
    def get_all_purchases(self, limit=None):
        """
        Récupère tous les achats avec le nom du produit et du fournisseur.
        - product_name vient directement de purchase_items (stocké à l'insertion)
        - JOIN purchases pour accéder à supplier_id
        - JOIN suppliers pour le nom du fournisseur
        """
        query = """
            SELECT
                pi.id,
                pi.purchase_id,
                pi.product_id,
                pi.product_name,
                pi.quantity,
                pi.unit_price,
                pi.total,
                pi.created_at,
                pu.payment_method,
                s.name AS supplier_name
            FROM purchase_items pi
            JOIN  purchases pu ON pi.purchase_id = pu.id
            LEFT JOIN suppliers s  ON pu.supplier_id = s.id
            ORDER BY pi.created_at DESC
        """
        if limit:
            query += f" LIMIT {limit}"
        self.cursor.execute(query)
        return [dict(row) for row in self.cursor.fetchall()]
    
    # ==================== STATISTIQUES ====================
    
    def get_statistics(self, year=None):
        """Récupère les statistiques globales, filtrées par année si précisée"""
        stats = {}
        yr = str(year) if year else str(datetime.now().year)

        # Nombre de clients (global)
        self.cursor.execute("SELECT COUNT(*) as count FROM clients")
        stats['total_clients'] = self.cursor.fetchone()['count']

        # Nombre de produits (global)
        self.cursor.execute("SELECT COUNT(*) as count FROM products")
        stats['total_products'] = self.cursor.fetchone()['count']

        # Nombre de ventes de l'année
        self.cursor.execute("""
            SELECT COUNT(*) as count FROM sales
            WHERE strftime('%Y', sale_date) = ?
        """, (yr,))
        stats['total_sales'] = self.cursor.fetchone()['count']

        # Nombre d'achats de l'année
        self.cursor.execute("""
            SELECT COUNT(*) as count FROM purchases
            WHERE strftime('%Y', purchase_date) = ?
        """, (yr,))
        stats['total_purchases'] = self.cursor.fetchone()['count']

        # Total des ventes de l'année
        self.cursor.execute("""
            SELECT COALESCE(SUM(total), 0) as total FROM sales
            WHERE strftime('%Y', sale_date) = ?
        """, (yr,))
        stats['sales_total'] = self.cursor.fetchone()['total']

        # Total des achats de l'année
        self.cursor.execute("""
            SELECT COALESCE(SUM(total), 0) as total FROM purchases
            WHERE strftime('%Y', purchase_date) = ?
        """, (yr,))
        stats['purchases_total'] = self.cursor.fetchone()['total']

        # Bénéfice
        stats['profit'] = stats['sales_total'] - stats['purchases_total']

        # Valeur du stock (global)
        self.cursor.execute("""
            SELECT COALESCE(SUM(stock_quantity * selling_price), 0) as total
            FROM products
        """)
        stats['stock_value'] = self.cursor.fetchone()['total']

        # Produits en rupture de stock (global)
        self.cursor.execute("""
            SELECT COUNT(*) as count FROM products
            WHERE stock_quantity <= min_stock
        """)
        stats['low_stock_count'] = self.cursor.fetchone()['count']

        # Ventes d'aujourd'hui
        today = datetime.now().strftime('%Y-%m-%d')
        self.cursor.execute("""
            SELECT COALESCE(SUM(total), 0) as total FROM sales
            WHERE DATE(sale_date) = ?
        """, (today,))
        stats['sales_today'] = self.cursor.fetchone()['total']

        stats['best_month'] = self.get_best_month(int(yr))
        stats['growth_rate'] = self.get_growth_rate(int(yr))

        return stats
        
        
    
    def get_sales_by_month(self, year):
        """Récupère les ventes par mois pour une année"""
        self.cursor.execute("""
            SELECT 
                strftime('%m', sale_date) as month,
                COUNT(*) as count,
                SUM(total) as total
            FROM sales
            WHERE strftime('%Y', sale_date) = ?
            GROUP BY month
            ORDER BY month
        """, (str(year),))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_top_products(self, limit=10, year=None):
        """Récupère les produits les plus vendus, filtrés par année si précisée"""
        if year:
            self.cursor.execute("""
                SELECT
                    p.name,
                    SUM(si.quantity) as total_quantity,
                    SUM(si.total) as total_sales
                FROM sale_items si
                JOIN products p ON si.product_id = p.id
                JOIN sales s ON si.sale_id = s.id
                WHERE strftime('%Y', s.sale_date) = ?
                GROUP BY si.product_id
                ORDER BY total_quantity DESC
                LIMIT ?
            """, (str(year), limit))
        else:
            self.cursor.execute("""
                SELECT
                    p.name,
                    SUM(si.quantity) as total_quantity,
                    SUM(si.total) as total_sales
                FROM sale_items si
                JOIN products p ON si.product_id = p.id
                GROUP BY si.product_id
                ORDER BY total_quantity DESC
                LIMIT ?
            """, (limit,))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_top_clients(self, limit=10, year=None):
        """Récupère les meilleurs clients, filtrés par année si précisée"""
        if year:
            self.cursor.execute("""
                SELECT
                    c.name,
                    COUNT(s.id) as sale_count,
                    SUM(s.total) as total_amount
                FROM sales s
                JOIN clients c ON s.client_id = c.id
                WHERE strftime('%Y', s.sale_date) = ?
                GROUP BY s.client_id
                ORDER BY total_amount DESC
                LIMIT ?
            """, (str(year), limit))
        else:
            self.cursor.execute("""
                SELECT
                    c.name,
                    COUNT(s.id) as sale_count,
                    SUM(s.total) as total_amount
                FROM sales s
                JOIN clients c ON s.client_id = c.id
                GROUP BY s.client_id
                ORDER BY total_amount DESC
                LIMIT ?
            """, (limit,))
        return [dict(row) for row in self.cursor.fetchall()]
    

    def get_profit_by_month(self, year):
        """Récupère le profit par mois"""
        self.cursor.execute("""
            SELECT 
                strftime('%m', s.sale_date) as month,
                COALESCE(SUM(s.total), 0) -
                COALESCE((
                    SELECT SUM(p.total)
                    FROM purchases p
                    WHERE strftime('%Y', p.purchase_date) = ?
                    AND strftime('%m', p.purchase_date) = strftime('%m', s.sale_date)
                ), 0) as profit
            FROM sales s
            WHERE strftime('%Y', s.sale_date) = ?
            GROUP BY month
            ORDER BY month
        """, (str(year), str(year)))

        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_best_month(self, year):
        """Retourne le meilleur mois en ventes"""
        self.cursor.execute("""
            SELECT 
                strftime('%m', sale_date) as month,
                SUM(total) as total
            FROM sales
            WHERE strftime('%Y', sale_date) = ?
            GROUP BY month
            ORDER BY total DESC
            LIMIT 1
        """, (str(year),))

        row = self.cursor.fetchone()
        return row['month'] if row else "-"
    
    def get_growth_rate(self, year):
        """Calcule la croissance entre les deux derniers mois"""
        self.cursor.execute("""
            SELECT 
                strftime('%m', sale_date) as month,
                SUM(total) as total
            FROM sales
            WHERE strftime('%Y', sale_date) = ?
            GROUP BY month
            ORDER BY month DESC
            LIMIT 2
        """, (str(year),))

        rows = self.cursor.fetchall()

        if len(rows) < 2:
            return 0

        last, previous = rows[0]['total'], rows[1]['total']

        if previous == 0:
            return 0

        return ((last - previous) / previous) * 100


    # ==================== PARAMÈTRES ====================
    
    def set_setting(self, key, value):
        """Définit un paramètre"""
        try:
            self.cursor.execute("""
                INSERT INTO settings (key, value)
                VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET 
                    value = excluded.value,
                    updated_at = CURRENT_TIMESTAMP
            """, (key, value))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"❌ Erreur lors de la définition du paramètre: {e}")
            return False
    
    def get_setting(self, key, default=None):
        """Récupère un paramètre"""
        self.cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = self.cursor.fetchone()
        return row['value'] if row else default
    
    def get_tax_rates(self):
        """
        Retourne les taux de TVA pour ventes et achats
        Récupère depuis les settings ou utilise les valeurs par défaut
        Returns: {"sales_tax": 19.0, "purchase_tax": 10.0}
        """
        try:
            # Récupérer les valeurs stockées (peuvent être des strings)
            vat_value = self.get_setting('vat', None)
            purchase_vat_value = self.get_setting('purchase_vat', None)
            
            # Convertir en float avec gestion des None/empty
            sales_tax = float(vat_value) if vat_value else 19.0
            purchase_tax = float(purchase_vat_value) if purchase_vat_value else 10.0
            
            print(f"📊 TVA Récupérée - Ventes: {sales_tax}%, Achats: {purchase_tax}%")
            
            return {"sales_tax": sales_tax, "purchase_tax": purchase_tax}
        except Exception as e:
            print(f"❌ Erreur get_tax_rates: {e}")
            return {"sales_tax": 19.0, "purchase_tax": 10.0}
    
    # ==================== BACKUP & RESTORE ====================
    
    def backup_database(self, backup_path):
        """Crée une sauvegarde de la base de données"""
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            print(f"✅ Sauvegarde créée: {backup_path}")
            return True
        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde: {e}")
            return False
    
    def restore_database(self, backup_path):
        """Restaure une sauvegarde"""
        try:
            import shutil
            self.disconnect()
            shutil.copy2(backup_path, self.db_path)
            self.connect()
            print(f"✅ Base de données restaurée depuis: {backup_path}")
            return True
        except Exception as e:
            print(f"❌ Erreur lors de la restauration: {e}")
            return False
    
    def clear_all_data(self):
        """Supprime toutes les données (pour nettoyage)"""
        try:
            # Supprimer dans l'ordre inverse des dépendances
            tables = [
                'stock_movements',
                'purchase_items',
                'purchases',
                'sale_items',
                'sales',
                'products',
                'categories',
                'suppliers',
                'clients',
                'settings'
            ]
            
            for table in tables:
                self.cursor.execute(f"DELETE FROM {table}")
            
            self.conn.commit()
            print("✅ Toutes les données ont été supprimées")
            return True
            
        except sqlite3.Error as e:
            print(f"❌ Erreur lors du nettoyage: {e}")
            self.conn.rollback()
            return False
    
    # ==================== GÉNÉRATION DE DONNÉES DE TEST ====================
    
    def populate_test_data(self):
        """Remplit la base avec des données de test"""
        print("📝 Création de données de test...")
        
        # Catégories
        categories = [
            ("Électronique", "Appareils électroniques"),
            ("Informatique", "Matériel informatique"),
            ("Mobilier", "Meubles de bureau"),
            ("Fournitures", "Fournitures de bureau")
        ]
        
        for name, desc in categories:
            self.add_category(name, desc)
        
        # Clients
        clients = [
            ("John Doe", "0555123456", "john@example.com", "123 Rue Example, Alger", ""),
            ("Alice Smith", "0555987654", "alice@example.com", "456 Avenue Commerce, Oran", ""),
            ("Entreprise X", "0555001122", "contact@companyx.com", "789 Boulevard Business, Constantine", "123456789012345"),
            ("Bob Martin", "0555445566", "bob@example.com", "321 Rue Test, Annaba", ""),
            ("Marie Dupont", "0555778899", "marie@example.com", "654 Avenue Principal, Sétif", ""),
        ]
        
        for name, phone, email, address, nif in clients:
            self.add_client(name, phone, email, address, nif)
        
        # Fournisseurs
        suppliers = [
            ("Fournisseur A", "0555111222", "fournisseurA@example.com", "Adresse A", "111222333444555"),
            ("Fournisseur B", "0555333444", "fournisseurB@example.com", "Adresse B", "555444333222111"),
        ]
        
        for name, phone, email, address, nif in suppliers:
            self.add_supplier(name, phone, email, address, nif)
        
        # Produits
        products = [
            ("Ordinateur Portable HP ProBook", 75000, 2, "Laptop professionnel", 60000, 10, 2, ""),
            ("Souris Sans Fil Logitech", 1500, 2, "Souris ergonomique", 1000, 50, 10, ""),
            ("Écran Samsung 24 pouces", 25000, 1, "Écran Full HD", 18000, 15, 3, ""),
            ("Bureau Professionnel", 35000, 3, "Bureau en bois", 25000, 5, 1, ""),
            ("Chaise de Bureau", 15000, 3, "Chaise ergonomique", 10000, 20, 5, ""),
        ]
        
        for name, price, cat, desc, p_price, stock, min_s, barcode in products:
            self.add_product(name, price, cat, desc, p_price, stock, min_s, barcode)
        
        print("✅ Données de test créées avec succès!")
        
        
    # ==================== NOUVEAUX KPI AVANCÉS ====================

    def get_average_cart_value(self):
        """
        Calcule la valeur moyenne du panier (total des ventes / nombre de ventes)
        """
        try:
            self.cursor.execute("""
                SELECT 
                    COALESCE(AVG(total), 0) as avg_cart,
                    COALESCE(SUM(total), 0) as total_sales,
                    COUNT(*) as total_orders
                FROM sales
            """)
            result = dict(self.cursor.fetchone())
            return {
                'avg_cart_value': result['avg_cart'],
                'total_sales': result['total_sales'],
                'total_orders': result['total_orders']
            }
        except Exception as e:
            print(f"❌ Erreur get_average_cart_value: {e}")
            return {'avg_cart_value': 0, 'total_sales': 0, 'total_orders': 0}

    def get_cart_value_by_period(self, days=30):
        """
        Calcule la valeur moyenne du panier sur une période donnée
        """
        try:
            from datetime import datetime, timedelta
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            self.cursor.execute("""
                SELECT 
                    COALESCE(AVG(total), 0) as avg_cart,
                    COUNT(*) as num_sales
                FROM sales
                WHERE DATE(sale_date) >= ?
            """, (start_date,))
            
            result = self.cursor.fetchone()
            return {
                'avg_cart': result['avg_cart'] if result else 0,
                'num_sales': result['num_sales'] if result else 0,
                'period_days': days
            }
        except Exception as e:
            print(f"❌ Erreur get_cart_value_by_period: {e}")
            return {'avg_cart': 0, 'num_sales': 0, 'period_days': days}

    def get_most_profitable_products(self, limit=10, year=None):
        """
        Récupère les produits avec la meilleure marge brute, filtrés par année si précisée
        Marge = (Prix vente - Prix achat) * Quantité vendue
        """
        try:
            if year:
                self.cursor.execute("""
                    SELECT
                        p.id,
                        p.name,
                        p.purchase_price,
                        p.selling_price,
                        COALESCE(SUM(si.quantity), 0) as quantity_sold,
                        COALESCE(SUM(si.total), 0) as total_revenue,
                        COALESCE(SUM(si.quantity * (p.selling_price - p.purchase_price)), 0) as gross_margin,
                        CASE
                            WHEN SUM(si.total) > 0
                            THEN (SUM(si.quantity * (p.selling_price - p.purchase_price)) * 100.0 / SUM(si.total))
                            ELSE 0
                        END as margin_percentage
                    FROM products p
                    LEFT JOIN sale_items si ON p.id = si.product_id
                    LEFT JOIN sales s ON si.sale_id = s.id
                    WHERE strftime('%Y', s.sale_date) = ?
                    GROUP BY p.id
                    HAVING quantity_sold > 0
                    ORDER BY gross_margin DESC
                    LIMIT ?
                """, (str(year), limit))
            else:
                self.cursor.execute("""
                    SELECT
                        p.id,
                        p.name,
                        p.purchase_price,
                        p.selling_price,
                        COALESCE(SUM(si.quantity), 0) as quantity_sold,
                        COALESCE(SUM(si.total), 0) as total_revenue,
                        COALESCE(SUM(si.quantity * (p.selling_price - p.purchase_price)), 0) as gross_margin,
                        CASE
                            WHEN SUM(si.total) > 0
                            THEN (SUM(si.quantity * (p.selling_price - p.purchase_price)) * 100.0 / SUM(si.total))
                            ELSE 0
                        END as margin_percentage
                    FROM products p
                    LEFT JOIN sale_items si ON p.id = si.product_id
                    GROUP BY p.id
                    HAVING quantity_sold > 0
                    ORDER BY gross_margin DESC
                    LIMIT ?
                """, (limit,))
            return [dict(row) for row in self.cursor.fetchall()]
        except Exception as e:
            print(f"❌ Erreur get_most_profitable_products: {e}")
            return []

    def get_product_profit_details(self, product_id):
        """
        Récupère les détails de profit pour un produit spécifique
        """
        try:
            self.cursor.execute("""
                SELECT 
                    p.name,
                    p.purchase_price,
                    p.selling_price,
                    (p.selling_price - p.purchase_price) as unit_margin,
                    ((p.selling_price - p.purchase_price) * 100.0 / p.purchase_price) as margin_percentage,
                    COALESCE(SUM(si.quantity), 0) as total_sold,
                    COALESCE(SUM(si.quantity * (p.selling_price - p.purchase_price)), 0) as total_margin
                FROM products p
                LEFT JOIN sale_items si ON p.id = si.product_id
                WHERE p.id = ?
                GROUP BY p.id
            """, (product_id,))
            
            return dict(self.cursor.fetchone()) if self.cursor.fetchone() else None
        except Exception as e:
            print(f"❌ Erreur get_product_profit_details: {e}")
            return None

    def get_conversion_rate(self, start_date=None, end_date=None):
        """
        Calcule le taux de transformation
        Nécessite une table 'visits' ou similaire - version simplifiée
        """
        try:
            from datetime import datetime, timedelta
            
            if not start_date:
                start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d')
            
            # Compter les ventes uniques (par client)
            self.cursor.execute("""
                SELECT 
                    COUNT(DISTINCT client_id) as unique_buyers,
                    COUNT(*) as total_sales,
                    COALESCE(SUM(total), 0) as revenue
                FROM sales
                WHERE DATE(sale_date) BETWEEN ? AND ?
            """, (start_date, end_date))
            
            sales_data = dict(self.cursor.fetchone())
            
            # Si vous avez une table de visites, vous pourriez faire :
            # self.cursor.execute("SELECT COUNT(DISTINCT visitor_id) FROM visits WHERE date BETWEEN ? AND ?", ...)
            # visitors = ...
            
            # Version simplifiée : on utilise le nombre total de clients comme base
            self.cursor.execute("SELECT COUNT(*) as total_clients FROM clients")
            total_clients = dict(self.cursor.fetchone())['total_clients']
            
            conversion_rate = (sales_data['unique_buyers'] / total_clients * 100) if total_clients > 0 else 0
            
            return {
                'conversion_rate': conversion_rate,
                'unique_buyers': sales_data['unique_buyers'],
                'total_clients': total_clients,
                'total_sales': sales_data['total_sales'],
                'revenue': sales_data['revenue'],
                'period': f"{start_date} to {end_date}"
            }
        except Exception as e:
            print(f"❌ Erreur get_conversion_rate: {e}")
            return {'conversion_rate': 0, 'unique_buyers': 0, 'total_clients': 0}

    def get_inventory_turnover(self):
        """
        Calcule la rotation du stock
        Rotation = Coût des marchandises vendues / Stock moyen
        """
        try:
            # Coût des marchandises vendues (CMV)
            self.cursor.execute("""
                SELECT COALESCE(SUM(purchase_price * quantity), 0) as cogs
                FROM sale_items si
                JOIN products p ON si.product_id = p.id
            """)
            cogs = dict(self.cursor.fetchone())['cogs']
            
            # Stock moyen (simplifié : moyenne du stock actuel)
            self.cursor.execute("""
                SELECT 
                    COALESCE(AVG(purchase_price * stock_quantity), 0) as avg_stock_value,
                    COALESCE(SUM(purchase_price * stock_quantity), 0) as total_stock_value
                FROM products
            """)
            stock_data = dict(self.cursor.fetchone())
            
            turnover = cogs / stock_data['avg_stock_value'] if stock_data['avg_stock_value'] > 0 else 0
            
            return {
                'turnover_rate': turnover,
                'cogs': cogs,
                'avg_stock_value': stock_data['avg_stock_value'],
                'total_stock_value': stock_data['total_stock_value']
            }
        except Exception as e:
            print(f"❌ Erreur get_inventory_turnover: {e}")
            return {'turnover_rate': 0, 'cogs': 0, 'avg_stock_value': 0}

    def get_customer_lifetime_value(self):
        """
        Calcule la valeur moyenne à vie d'un client
        CLV = (Valeur moyenne du panier * Fréquence d'achat * Durée de vie)
        """
        try:
            # Valeur moyenne du panier
            cart_data = self.get_average_cart_value()
            
            # Fréquence d'achat moyenne (ventes par client)
            self.cursor.execute("""
                SELECT 
                    COUNT(DISTINCT client_id) as active_clients,
                    COUNT(*) as total_sales,
                    COUNT(*) * 1.0 / NULLIF(COUNT(DISTINCT client_id), 0) as purchase_frequency
                FROM sales
                WHERE client_id IS NOT NULL
            """)
            freq_data = dict(self.cursor.fetchone())
            
            # Durée de vie moyenne estimée (en mois) - simplifié
            self.cursor.execute("""
                SELECT 
                    JULIANDAY(MAX(sale_date)) - JULIANDAY(MIN(sale_date)) as customer_lifespan_days,
                    COUNT(DISTINCT client_id) as clients_with_history
                FROM sales
                WHERE client_id IS NOT NULL
                GROUP BY client_id
                HAVING customer_lifespan_days > 0
            """)
            
            lifespan_rows = self.cursor.fetchall()
            if lifespan_rows:
                avg_lifespan_days = sum(row['customer_lifespan_days'] for row in lifespan_rows) / len(lifespan_rows)
                avg_lifespan_months = avg_lifespan_days / 30.44  # mois moyen
            else:
                avg_lifespan_months = 12  # valeur par défaut
            
            clv = cart_data['avg_cart_value'] * freq_data['purchase_frequency'] * avg_lifespan_months
            
            return {
                'clv': clv,
                'avg_cart_value': cart_data['avg_cart_value'],
                'purchase_frequency': freq_data['purchase_frequency'],
                'avg_lifespan_months': avg_lifespan_months,
                'active_clients': freq_data['active_clients']
            }
        except Exception as e:
            print(f"❌ Erreur get_customer_lifetime_value: {e}")
            return {'clv': 0, 'active_clients': 0}

    def get_return_rate(self):
        """
        Calcule le taux de retour des produits
        """
        try:
            # Vérifier si la table returns existe
            self.cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='returns'
            """)
            
            if not self.cursor.fetchone():
                return {'return_rate': 0, 'total_returns': 0, 'total_sales': 0}
            
            self.cursor.execute("""
                SELECT 
                    COALESCE(COUNT(*), 0) as total_returns,
                    COALESCE(SUM(total), 0) as returned_amount
                FROM returns
            """)
            returns_data = dict(self.cursor.fetchone())
            
            self.cursor.execute("SELECT COUNT(*) as total_sales FROM sales")
            sales_count = dict(self.cursor.fetchone())['total_sales']
            
            return_rate = (returns_data['total_returns'] / sales_count * 100) if sales_count > 0 else 0
            
            return {
                'return_rate': return_rate,
                'total_returns': returns_data['total_returns'],
                'returned_amount': returns_data['returned_amount'],
                'total_sales': sales_count
            }
        except Exception as e:
            print(f"❌ Erreur get_return_rate: {e}")
            return {'return_rate': 0, 'total_returns': 0, 'returned_amount': 0}

    def get_profit_margin_evolution(self, months=6):
        """
        Récupère l'évolution de la marge sur plusieurs mois
        """
        try:
            from datetime import datetime, timedelta
            
            margins = []
            for i in range(months):
                month_date = datetime.now() - timedelta(days=30*i)
                month_str = month_date.strftime('%Y-%m')
                
                self.cursor.execute("""
                    SELECT 
                        COALESCE(SUM(s.total), 0) as revenue,
                        COALESCE(SUM(p.purchase_price * si.quantity), 0) as cost
                    FROM sales s
                    JOIN sale_items si ON s.id = si.sale_id
                    JOIN products p ON si.product_id = p.id
                    WHERE strftime('%Y-%m', s.sale_date) = ?
                """, (month_str,))
                
                data = self.cursor.fetchone()
                revenue = data['revenue'] if data else 0
                cost = data['cost'] if data else 0
                profit = revenue - cost
                margin_pct = (profit / revenue * 100) if revenue > 0 else 0
                
                margins.insert(0, {
                    'month': month_date.strftime('%Y-%m'),
                    'revenue': revenue,
                    'cost': cost,
                    'profit': profit,
                    'margin_percentage': margin_pct
                })
            
            return margins
        except Exception as e:
            print(f"❌ Erreur get_profit_margin_evolution: {e}")
            return []    



    def create_return(self, original_sale_id, items, motif="", notes=""):
        """
        Crée un avoir/retour pour une vente
        
        Args:
            original_sale_id: ID de la vente originale
            items: Liste de dict avec 'product_id', 'quantity', 'unit_price', 'total'
            motif: Motif du retour
            notes: Notes complémentaires
        
        Returns:
            dict: Données de l'avoir créé ou None si erreur
        """
        try:
            # Récupérer les infos de la vente originale
            sale = self.get_sale_by_id(original_sale_id)
            if not sale:
                raise ValueError(f"Vente {original_sale_id} introuvable")
            
            # Générer un numéro d'avoir
            return_number = self.generate_return_number()
            
            # Calculer le total
            total = sum(item['total'] for item in items)
            
            # Insérer l'avoir
            self.cursor.execute("""
                INSERT INTO returns 
                (return_number, original_sale_id, client_id, client_name, total, motif, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                return_number,
                original_sale_id,
                sale.get('client_id'),
                sale.get('client_name', 'Client Anonyme'),
                total,
                motif,
                notes
            ))
            
            return_id = self.cursor.lastrowid
            
            # Insérer les articles retournés et remettre en stock
            for item in items:
                self.cursor.execute("""
                    INSERT INTO return_items
                    (return_id, product_id, quantity, unit_price, total)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    return_id,
                    item['product_id'],
                    item['quantity'],
                    item['unit_price'],
                    item['total']
                ))
                
                # Remettre en stock (quantité positive)
                self.update_stock(
                    item['product_id'],
                    item['quantity'],  # Quantité positive pour retour en stock
                    'return',
                    f"Retour #{return_number}"
                )
            
            self.conn.commit()
            
            return {
                'return_id': return_id,
                'return_number': return_number,
                'total': total
            }
            
        except Exception as e:
            print(f"❌ Erreur lors de la création de l'avoir: {e}")
            self.conn.rollback()
            return None

    def generate_return_number(self):
        """Génère un numéro d'avoir séquentiel"""
        try:
            self.cursor.execute("""
                SELECT return_number FROM returns 
                WHERE return_number LIKE 'AVOIR-%'
            """)
            results = self.cursor.fetchall()
            
            next_number = 1000  # Valeur par défaut
            
            if results:
                numbers = []
                for row in results:
                    try:
                        num_part = row['return_number'].replace("AVOIR-", "").strip()
                        if num_part.isdigit():
                            num = int(num_part)
                            if 1000 <= num <= 99999:
                                numbers.append(num)
                    except:
                        continue
                
                if numbers:
                    next_number = max(numbers) + 1
            
            return f"AVOIR-{next_number}"
            
        except Exception as e:
            print(f"⚠️ Erreur génération numéro avoir: {e}")
            from datetime import datetime
            return f"AVOIR-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    def get_all_returns(self):
        """Récupère tous les avoirs"""
        try:
            self.cursor.execute("""
                SELECT r.*, s.invoice_number
                FROM returns r
                LEFT JOIN sales s ON r.original_sale_id = s.id
                ORDER BY r.return_date DESC
            """)
            return [dict(row) for row in self.cursor.fetchall()]
        except Exception as e:
            print(f"❌ Erreur get_all_returns: {e}")
            return []


# ==================== SINGLETON ====================

_db_instance = None

def get_database(db_path=None):
    """Retourne l'instance unique de la base de données"""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database(db_path or config.db_path)
    return _db_instance


# ==================== EXEMPLE D'UTILISATION ====================

if __name__ == "__main__":
    # Créer/ouvrir la base de données
    db = Database("test_erp.db")
    
    # Remplir avec des données de test
    db.populate_test_data()
    
    # Exemples d'utilisation
    print("\n" + "="*60)
    print("📊 STATISTIQUES")
    print("="*60)
    stats = db.get_statistics()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    print("\n" + "="*60)
    print("👥 CLIENTS")
    print("="*60)
    clients = db.get_all_clients()
    for client in clients:
        print(f"- {client['name']} ({client['email']})")
    
    print("\n" + "="*60)
    print("📦 PRODUITS")
    print("="*60)
    products = db.get_all_products()
    for product in products:
        print(f"- {product['name']} - {product['selling_price']} DA (Stock: {product['stock_quantity']})")
    
    # Fermer la connexion
    db.disconnect()