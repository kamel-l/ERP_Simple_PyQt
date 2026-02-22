import sqlite3
from datetime import datetime

DB_NAME = "erp_database.db"


# ============================================================
# 1)  Gestion de la base de données
# ============================================================
class Database:
    def __init__(self):
        self.connection = None
        self.cursor = None
        self.connect()

    def connect(self):
        self.connection = sqlite3.connect(DB_NAME)
        self.cursor = self.connection.cursor()

    def close(self):
        if self.connection:
            self.connection.close()

    def commit(self):
        if self.connection:
            self.connection.commit()

    # Clients CRUD
    def get_all_clients(self):
        self.cursor.execute("SELECT id, name, phone, address FROM clients ORDER BY name")
        rows = self.cursor.fetchall()
        return [{"id": r[0], "name": r[1], "phone": r[2], "address": r[3]} for r in rows]

    def add_client(self, name, phone, address):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute(
            "INSERT INTO clients (name, phone, address, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (name, phone, address, now, now)
        )
        self.commit()

    def update_client(self, client_id, name, phone, address):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute(
            "UPDATE clients SET name=?, phone=?, address=?, updated_at=? WHERE id=?",
            (name, phone, address, now, client_id)
        )
        self.commit()

    def delete_client(self, client_id):
        self.cursor.execute("DELETE FROM clients WHERE id=?", (client_id,))
        self.commit()

    def search_clients(self, text):
        self.cursor.execute(
            "SELECT id, name, phone, address FROM clients WHERE name LIKE ? ORDER BY name",
            (f"%{text}%",)
        )
        rows = self.cursor.fetchall()
        return [{"id": r[0], "name": r[1], "phone": r[2], "address": r[3]} for r in rows]

    # Products CRUD
    def get_all_products(self):
        self.cursor.execute("""
            SELECT id, name, category, selling_price, stock_quantity 
            FROM products
        """)
        rows = self.cursor.fetchall()
        return [{"id": r[0], "product_name": r[1], "category": r[2], "price": r[3], "Quantitee": r[4]} for r in rows]

    def add_product(self, name, category, price, quantity):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute(
            "INSERT INTO products (name, category, selling_price, stock_quantity, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
            (name, category, float(price), int(quantity), now, now)
        )
        self.commit()

    def update_product(self, product_id, name, category, price, quantity):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute(
            "UPDATE products SET name=?, category=?, selling_price=?, stock_quantity=?, updated_at=? WHERE id=?",
            (name, category, float(price), int(quantity), now, product_id)
        )
        self.commit()

    def delete_product(self, product_id):
        self.cursor.execute("DELETE FROM products WHERE id=?", (product_id,))
        self.commit()

    # Purchases CRUD methods
    def get_all_purchases(self):
        self.cursor.execute("""
            SELECT p.id, p.supplier, pr.name, pi.quantity, p.total_amount, p.created_at
            FROM purchases p
            LEFT JOIN purchase_items pi ON pi.purchase_id = p.id
            LEFT JOIN products pr ON pr.id = pi.product_id
            ORDER BY p.id DESC
        """)
        rows = self.cursor.fetchall()
        result = []
        for row in rows:
            result.append({
                "id": row[0],
                "supplier": row[1] or "",
                "product": row[2] or "",
                "quantity": row[3] or 0,
                "total": row[4] or 0,
                "date": row[5] or ""
            })
        return result

    def add_purchase(self, supplier, product, quantity, total):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("SELECT id FROM products WHERE name=?", (product,))
        product_result = self.cursor.fetchone()
        product_id = product_result[0] if product_result else None

        self.cursor.execute(
            "INSERT INTO purchases (supplier, total_amount, created_at) VALUES (?, ?, ?)",
            (supplier, float(total), now)
        )
        purchase_id = self.cursor.lastrowid

        if product_id:
            self.cursor.execute(
                """INSERT INTO purchase_items 
                   (purchase_id, product_id, quantity, unit_price, total_price) 
                   VALUES (?, ?, ?, ?, ?)""",
                (purchase_id, product_id, int(quantity),
                 float(total) / int(quantity) if int(quantity) > 0 else 0, float(total))
            )
            self.cursor.execute(
                "UPDATE products SET stock_quantity = stock_quantity + ? WHERE id = ?",
                (int(quantity), product_id)
            )

        self.commit()
        return purchase_id

    def update_purchase(self, purchase_id, supplier, product, quantity, total):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("""
            SELECT pi.product_id, pi.quantity 
            FROM purchase_items pi 
            WHERE pi.purchase_id = ?
        """, (purchase_id,))
        old_item = self.cursor.fetchone()

        self.cursor.execute(
            "UPDATE purchases SET supplier=?, total_amount=?, created_at=? WHERE id=?",
            (supplier, float(total), now, purchase_id)
        )

        if old_item:
            product_id = old_item[0]
            old_quantity = old_item[1]
            self.cursor.execute(
                "UPDATE products SET stock_quantity = stock_quantity - ? WHERE id = ?",
                (old_quantity, product_id)
            )
            self.cursor.execute(
                """UPDATE purchase_items 
                   SET quantity=?, unit_price=?, total_price=? 
                   WHERE purchase_id=?""",
                (int(quantity),
                 float(total) / int(quantity) if int(quantity) > 0 else 0,
                 float(total), purchase_id)
            )
            self.cursor.execute(
                "UPDATE products SET stock_quantity = stock_quantity + ? WHERE id = ?",
                (int(quantity), product_id)
            )

        self.commit()

    def delete_purchase(self, purchase_id):
        self.cursor.execute("SELECT product_id, quantity FROM purchase_items WHERE purchase_id=?", (purchase_id,))
        items = self.cursor.fetchall()
        for item in items:
            product_id, quantity = item
            self.cursor.execute(
                "UPDATE products SET stock_quantity = stock_quantity - ? WHERE id = ?",
                (quantity, product_id)
            )
        self.cursor.execute("DELETE FROM purchase_items WHERE purchase_id=?", (purchase_id,))
        self.cursor.execute("DELETE FROM purchases WHERE id=?", (purchase_id,))
        self.commit()

    def search_purchases(self, text):
        self.cursor.execute("""
            SELECT p.id, p.supplier, pr.name, pi.quantity, p.total_amount, p.created_at
            FROM purchases p
            LEFT JOIN purchase_items pi ON pi.purchase_id = p.id
            LEFT JOIN products pr ON pr.id = pi.product_id
            WHERE p.supplier LIKE ? OR pr.name LIKE ?
            ORDER BY p.id DESC
        """, (f"%{text}%", f"%{text}%"))
        rows = self.cursor.fetchall()
        result = []
        for row in rows:
            result.append({
                "id": row[0],
                "supplier": row[1] or "",
                "product": row[2] or "",
                "quantity": row[3] or 0,
                "total": row[4] or 0,
                "date": row[5] or ""
            })
        return result

    # Sales CRUD methods
    def get_all_sales(self):
        self.cursor.execute("""
            SELECT s.id, c.name, p.name, si.quantity, s.total_amount, s.created_at
            FROM sales s
            LEFT JOIN clients c ON c.id = s.client_id
            LEFT JOIN sale_items si ON si.sale_id = s.id
            LEFT JOIN products p ON p.id = si.product_id
            ORDER BY s.id DESC
        """)
        rows = self.cursor.fetchall()
        result = []
        for row in rows:
            result.append({
                "id": row[0],
                "client": row[1] or "",
                "product": row[2] or "",
                "quantity": row[3] or 0,
                "total": row[4] or 0,
                "date": row[5] or ""
            })
        return result

    def add_sale(self, client, product, quantity, total):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("SELECT id FROM clients WHERE name=?", (client,))
        client_result = self.cursor.fetchone()
        client_id = client_result[0] if client_result else None

        self.cursor.execute("SELECT id, stock_quantity FROM products WHERE name=?", (product,))
        product_result = self.cursor.fetchone()
        product_id = product_result[0] if product_result else None

        if not product_id:
            print(f"Produit non trouvé: {product}")
            return None

        self.cursor.execute(
            "INSERT INTO sales (client_id, total_amount, created_at) VALUES (?, ?, ?)",
            (client_id, float(total), now)
        )
        sale_id = self.cursor.lastrowid

        unit_price = float(total) / int(quantity) if int(quantity) > 0 else 0
        self.cursor.execute(
            """INSERT INTO sale_items 
               (sale_id, product_id, quantity, unit_price, total_price) 
               VALUES (?, ?, ?, ?, ?)""",
            (sale_id, product_id, int(quantity), unit_price, float(total))
        )
        self.cursor.execute(
            "UPDATE products SET stock_quantity = stock_quantity - ? WHERE id = ?",
            (int(quantity), product_id)
        )
        self.commit()
        return sale_id

    def update_sale(self, sale_id, client, product, quantity, total):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("""
            SELECT si.product_id, si.quantity 
            FROM sale_items si 
            WHERE si.sale_id = ?
        """, (sale_id,))
        old_item = self.cursor.fetchone()

        self.cursor.execute("SELECT id FROM clients WHERE name=?", (client,))
        client_result = self.cursor.fetchone()
        client_id = client_result[0] if client_result else None

        self.cursor.execute("SELECT id FROM products WHERE name=?", (product,))
        product_result = self.cursor.fetchone()
        product_id = product_result[0] if product_result else None

        self.cursor.execute(
            "UPDATE sales SET client_id=?, total_amount=?, created_at=? WHERE id=?",
            (client_id, float(total), now, sale_id)
        )

        if old_item and product_id:
            old_product_id, old_quantity = old_item
            self.cursor.execute(
                "UPDATE products SET stock_quantity = stock_quantity + ? WHERE id = ?",
                (old_quantity, old_product_id)
            )
            self.cursor.execute(
                """UPDATE sale_items 
                   SET product_id=?, quantity=?, unit_price=?, total_price=? 
                   WHERE sale_id=?""",
                (product_id, int(quantity),
                 float(total) / int(quantity) if int(quantity) > 0 else 0,
                 float(total), sale_id)
            )
            self.cursor.execute(
                "UPDATE products SET stock_quantity = stock_quantity - ? WHERE id = ?",
                (int(quantity), product_id)
            )

        self.commit()

    def delete_sale(self, sale_id):
        self.cursor.execute("SELECT product_id, quantity FROM sale_items WHERE sale_id=?", (sale_id,))
        items = self.cursor.fetchall()
        for item in items:
            product_id, quantity = item
            self.cursor.execute(
                "UPDATE products SET stock_quantity = stock_quantity + ? WHERE id = ?",
                (quantity, product_id)
            )
        self.cursor.execute("DELETE FROM sale_items WHERE sale_id=?", (sale_id,))
        self.cursor.execute("DELETE FROM sales WHERE id=?", (sale_id,))
        self.commit()

    def search_sales(self, text):
        self.cursor.execute("""
            SELECT s.id, c.name, p.name, si.quantity, s.total_amount, s.created_at
            FROM sales s
            LEFT JOIN clients c ON c.id = s.client_id
            LEFT JOIN sale_items si ON si.sale_id = s.id
            LEFT JOIN products p ON p.id = si.product_id
            WHERE c.name LIKE ? OR p.name LIKE ?
            ORDER BY s.id DESC
        """, (f"%{text}%", f"%{text}%"))
        rows = self.cursor.fetchall()
        result = []
        for row in rows:
            result.append({
                "id": row[0],
                "client": row[1] or "",
                "product": row[2] or "",
                "quantity": row[3] or 0,
                "total": row[4] or 0,
                "date": row[5] or ""
            })
        return result

    # Settings
    def get_settings(self):
        try:
            self.cursor.execute("SELECT key, value FROM settings")
            rows = self.cursor.fetchall()
            return {r[0]: r[1] for r in rows}
        except Exception:
            return {}

    def save_settings(self, app_name, company_name, currency):
        try:
            for key, value in [("app_name", app_name), ("company_name", company_name), ("currency", currency)]:
                self.cursor.execute(
                    "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value)
                )
            self.commit()
        except Exception as e:
            print(f"Erreur save_settings: {e}")

    def get_statistics(self):
        """Statistiques globales — retourne total_sales, total_purchases, sales_today ET sales_total
        (sales_total est un alias de total_sales, utilisé dans sales_history.py)"""
        self.cursor.execute("SELECT SUM(total_amount) FROM sales")
        total_sales = self.cursor.fetchone()[0] or 0
        self.cursor.execute("SELECT SUM(total_amount) FROM purchases")
        total_purchases = self.cursor.fetchone()[0] or 0
        self.cursor.execute(
            "SELECT SUM(total_amount) FROM sales WHERE created_at LIKE ?",
            (datetime.now().strftime("%Y-%m-%d") + '%',)
        )
        sales_today = self.cursor.fetchone()[0] or 0
        return {
            "total_sales": total_sales,
            "total_purchases": total_purchases,
            "sales_today": sales_today,
            "sales_total": total_sales,      # ✅ alias utilisé par sales_history.py
        }

    def get_sales_by_date_range(self, start_date, end_date):
        """Retourne les ventes entre start_date et end_date (format YYYY-MM-DD).
        Les enregistrements retournés contiennent les mêmes clés que get_all_sales()
        PLUS les champs attendus par sales_history.py :
        invoice_number, sale_date, client_name, subtotal, tax_rate, tax_amount, total, items."""
        self.cursor.execute("""
            SELECT s.id, s.total_amount, s.payment_method, s.created_at, c.name
            FROM sales s
            LEFT JOIN clients c ON c.id = s.client_id
            WHERE DATE(s.created_at) BETWEEN ? AND ?
            ORDER BY s.id DESC
        """, (start_date, end_date))
        rows = self.cursor.fetchall()
        result = []
        for row in rows:
            sale_id, total_amount, payment_method, created_at, client_name = row
            subtotal = round(total_amount / 1.19, 2)  # TVA 19 % par défaut
            tax_amount = round(total_amount - subtotal, 2)
            result.append({
                "id": sale_id,
                "invoice_number": f"FAC-{sale_id:05d}",
                "sale_date": created_at or datetime.now().isoformat(),
                "client_name": client_name or "Client Anonyme",
                "client": client_name or "",
                "payment_method": payment_method or "cash",
                "subtotal": subtotal,
                "tax_rate": 19,
                "tax_amount": tax_amount,
                "total": total_amount or 0,
                "items": [],   # chargé à la demande via get_sale_by_id
            })
        return result

    def get_sale_by_id(self, sale_id):
        """Retourne une vente complète avec ses articles (clé 'items').
        Chaque article contient : product_name, quantity, unit_price, discount, total."""
        self.cursor.execute("""
            SELECT s.id, s.total_amount, s.payment_method, s.created_at, c.name
            FROM sales s
            LEFT JOIN clients c ON c.id = s.client_id
            WHERE s.id = ?
        """, (sale_id,))
        row = self.cursor.fetchone()
        if not row:
            return None

        sale_id_db, total_amount, payment_method, created_at, client_name = row
        subtotal = round(total_amount / 1.19, 2)
        tax_amount = round(total_amount - subtotal, 2)

        # Récupérer les articles de la vente
        self.cursor.execute("""
            SELECT p.name, si.quantity, si.unit_price, si.total_price
            FROM sale_items si
            LEFT JOIN products p ON p.id = si.product_id
            WHERE si.sale_id = ?
        """, (sale_id,))
        items_rows = self.cursor.fetchall()
        items = []
        for item_row in items_rows:
            product_name, quantity, unit_price, total_price = item_row
            items.append({
                "product_name": product_name or "Produit inconnu",
                "quantity": quantity or 0,
                "unit_price": unit_price or 0,
                "discount": 0,   # remise non gérée dans le schéma actuel
                "total": total_price or 0,
            })

        return {
            "id": sale_id_db,
            "invoice_number": f"FAC-{sale_id_db:05d}",
            "sale_date": created_at or datetime.now().isoformat(),
            "client_name": client_name or "Client Anonyme",
            "payment_method": payment_method or "cash",
            "subtotal": subtotal,
            "tax_rate": 19,
            "tax_amount": tax_amount,
            "total": total_amount or 0,
            "items": items,
        }


# ============================================================
# 2)  Standalone functions (utilisant des connexions séparées)
# ============================================================

def get_statistics():
    """Fonction standalone pour le dashboard et les statistiques"""
    db = sqlite3.connect(DB_NAME)
    cursor = db.cursor()
    cursor.execute("SELECT SUM(total_amount) FROM sales")
    total_sales = cursor.fetchone()[0] or 0
    cursor.execute("SELECT SUM(total_amount) FROM purchases")
    total_purchases = cursor.fetchone()[0] or 0
    cursor.execute(
        "SELECT SUM(total_amount) FROM sales WHERE created_at LIKE ?",
        (datetime.now().strftime("%Y-%m-%d") + '%',)
    )
    sales_today = cursor.fetchone()[0] or 0
    db.close()
    return {"total_sales": total_sales, "total_purchases": total_purchases, "sales_today": sales_today}


def get_recent_sales(limit=10):
    db = sqlite3.connect(DB_NAME)
    cursor = db.cursor()
    cursor.execute("""
        SELECT sales.id, clients.name, sales.total_amount, sales.created_at
        FROM sales
        LEFT JOIN clients ON clients.id = sales.client_id
        ORDER BY sales.id DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    db.close()
    return [{"id": r[0], "client_name": r[1] or "Client supprimé", "total": r[2], "date": r[3]} for r in rows]


def get_recent_purchases(limit=5):
    db = sqlite3.connect(DB_NAME)
    cursor = db.cursor()
    cursor.execute("""
        SELECT id, supplier, total_amount, created_at
        FROM purchases
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    db.close()
    return [{"id": r[0], "supplier": r[1], "total": r[2], "date": r[3]} for r in rows]


def get_top_clients(limit=5):
    db = sqlite3.connect(DB_NAME)
    cursor = db.cursor()
    cursor.execute("""
        SELECT clients.name, SUM(sales.total_amount) as total_spent
        FROM sales
        LEFT JOIN clients ON clients.id = sales.client_id
        WHERE clients.id IS NOT NULL
        GROUP BY clients.id
        ORDER BY total_spent DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    db.close()
    return [{"name": r[0] or "Client inconnu", "total_spent": r[1] or 0} for r in rows]


def get_low_stock_products(limit=10):
    db = sqlite3.connect(DB_NAME)
    cursor = db.cursor()
    cursor.execute("""
        SELECT name, stock_quantity, min_stock
        FROM products
        WHERE stock_quantity <= min_stock
        ORDER BY stock_quantity ASC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    db.close()
    return [{"name": r[0], "stock": r[1], "min_stock": r[2]} for r in rows]


def get_top_products(limit=5):
    db = sqlite3.connect(DB_NAME)
    cursor = db.cursor()
    cursor.execute("""
        SELECT products.name, SUM(sale_items.quantity) as total_quantity,
               SUM(sale_items.total_price) as total_revenue
        FROM sale_items
        LEFT JOIN products ON products.id = sale_items.product_id
        GROUP BY sale_items.product_id
        ORDER BY total_quantity DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    db.close()
    return [{"name": r[0] or "Produit inconnu", "quantity": r[1] or 0, "total": r[2] or 0} for r in rows]


# ============================================================
# 3)  Global database instance
# ============================================================
_db_instance = None


def get_database():
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance


def init_database():
    db = sqlite3.connect(DB_NAME)
    cursor = db.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            address TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            purchase_price REAL,
            selling_price REAL,
            stock_quantity INTEGER DEFAULT 0,
            min_stock INTEGER DEFAULT 0,
            barcode TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER,
            total_amount REAL,
            payment_method TEXT,
            created_at TEXT,
            FOREIGN KEY(client_id) REFERENCES clients(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sale_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            unit_price REAL,
            total_price REAL,
            FOREIGN KEY(sale_id) REFERENCES sales(id),
            FOREIGN KEY(product_id) REFERENCES products(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            supplier TEXT,
            total_amount REAL,
            created_at TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS purchase_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            purchase_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            unit_price REAL,
            total_price REAL,
            FOREIGN KEY(purchase_id) REFERENCES purchases(id),
            FOREIGN KEY(product_id) REFERENCES products(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT UNIQUE,
            sales_total REAL DEFAULT 0,
            purchases_total REAL DEFAULT 0,
            nb_sales INTEGER DEFAULT 0,
            nb_purchases INTEGER DEFAULT 0
        )
    """)

    # ✅ CORRIGÉ : Table settings ajoutée (utilisée par SettingsPage)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    db.commit()
    db.close()