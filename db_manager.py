"""
Module de gestion de la base de données SQLite
Gère toutes les opérations CRUD pour l'application ERP
"""

import sqlite3
from datetime import datetime
from pathlib import Path
import json


class Database:
    """Classe principale pour gérer la base de données SQLite"""
    
    def __init__(self, db_path="erp_database.db"):
        """
        Initialise la connexion à la base de données
        
        Args:
            db_path: Chemin vers le fichier de base de données
        """
        self.db_path = db_path
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

    def get_best_day(self):
        """
        Calcule le meilleur jour de vente depuis la base de données.
        strftime('%w') : '0'=Dimanche, '1'=Lundi, ..., '6'=Samedi
        Retourne le nom du jour en français, ou '—' si aucune vente.
        """
        JOURS = {
            '0': 'Dimanche', '1': 'Lundi',    '2': 'Mardi',
            '3': 'Mercredi', '4': 'Jeudi',    '5': 'Vendredi',
            '6': 'Samedi',
        }
        try:
            self.cursor.execute("""
                SELECT
                    strftime('%w', sale_date) AS day_num,
                    COUNT(*)                  AS nb_ventes,
                    SUM(total)                AS total_da
                FROM sales
                GROUP BY day_num
                ORDER BY nb_ventes DESC, total_da DESC
                LIMIT 1
            """)
            row = self.cursor.fetchone()
            if row:
                return JOURS.get(row['day_num'], '—')
        except Exception as e:
            print(f"⚠️  get_best_day : {e}")
        return '—'

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
    
    def get_all_clients(self):
        """Récupère tous les clients"""
        self.cursor.execute("SELECT * FROM clients ORDER BY name")
        return [dict(row) for row in self.cursor.fetchall()]
    
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
    
    def get_all_products(self):
        """Récupère tous les produits avec leurs catégories"""
        self.cursor.execute("""
            SELECT p.*, c.name as category_name
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            ORDER BY p.name
        """)
        return [dict(row) for row in self.cursor.fetchall()]
    
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
    
    def search_products(self, search_term):
        """Recherche des produits par nom"""
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
                   tax_rate=19.0, discount=0, notes=""):
        """
        Crée une nouvelle vente avec ses articles
        
        Args:
            invoice_number: Numéro de facture
            client_id: ID du client
            items: Liste de dict avec 'product_id', 'quantity', 'unit_price', 'discount'
            payment_method: Mode de paiement
            tax_rate: Taux de TVA
            discount: Remise globale
            notes: Notes
        """
        try:
            # Calculer les totaux
            subtotal = sum(item['quantity'] * item['unit_price'] * 
                          (1 - item.get('discount', 0) / 100) for item in items)
            tax_amount = subtotal * (tax_rate / 100)
            total = subtotal + tax_amount - discount
            
            # Créer la vente
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
    
    def get_all_sales(self, limit=None):
        """Récupère toutes les ventes"""
        query = """
            SELECT s.*, c.name as client_name
            FROM sales s
            LEFT JOIN clients c ON s.client_id = c.id
            ORDER BY s.sale_date DESC
        """
        if limit:
            query += f" LIMIT {limit}"
        
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
            SELECT si.*, p.name as product_name
            FROM sale_items si
            JOIN products p ON si.product_id = p.id
            WHERE si.sale_id = ?
        """, (sale_id,))
        
        sale_dict['items'] = [dict(row) for row in self.cursor.fetchall()]
        
        return sale_dict
    
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
                   tax_rate=10.0, notes=""):
        """Crée un nouvel achat avec ses articles"""
        try:
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
    
    def get_statistics(self):
        """Récupère les statistiques globales"""
        stats = {}
        
        # Nombre de clients
        self.cursor.execute("SELECT COUNT(*) as count FROM clients")
        stats['total_clients'] = self.cursor.fetchone()['count']
        
        # Nombre de produits
        self.cursor.execute("SELECT COUNT(*) as count FROM products")
        stats['total_products'] = self.cursor.fetchone()['count']
        
        # Nombre de ventes
        self.cursor.execute("SELECT COUNT(*) as count FROM sales")
        stats['total_sales'] = self.cursor.fetchone()['count']
        
        # Nombre d'achats
        self.cursor.execute("SELECT COUNT(*) as count FROM purchases")
        stats['total_purchases'] = self.cursor.fetchone()['count']
        
        # Total des ventes
        self.cursor.execute("SELECT COALESCE(SUM(total), 0) as total FROM sales")
        stats['sales_total'] = self.cursor.fetchone()['total']
        
        # Total des achats
        self.cursor.execute("SELECT COALESCE(SUM(total), 0) as total FROM purchases")
        stats['purchases_total'] = self.cursor.fetchone()['total']
        
        # Bénéfice
        stats['profit'] = stats['sales_total'] - stats['purchases_total']
        
        # Valeur du stock
        self.cursor.execute("""
            SELECT COALESCE(SUM(stock_quantity * selling_price), 0) as total 
            FROM products
        """)
        stats['stock_value'] = self.cursor.fetchone()['total']
        
        # Produits en rupture de stock
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

        year = datetime.now().year
        stats['best_month'] = self.get_best_month(year)
        stats['growth_rate'] = self.get_growth_rate(year)
        
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
    
    def get_top_products(self, limit=10):
        """Récupère les produits les plus vendus"""
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
    
    def get_top_clients(self, limit=10):
        """Récupère les meilleurs clients"""
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


# ==================== SINGLETON ====================

_db_instance = None

def get_database(db_path="erp_database.db"):
    """Retourne l'instance unique de la base de données"""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database(db_path)
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