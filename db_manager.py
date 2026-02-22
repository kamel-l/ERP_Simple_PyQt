import sqlite3
from datetime import datetime

DB_NAME = "erp_database.db"


# ============================================================
# 1)  Gestion de la base de données
# ============================================================
def get_database():
    return sqlite3.connect(DB_NAME)


def init_database():
    db = get_database()
    cursor = db.cursor()

    # ------------------------------------------------------------
    # TABLE: Clients
    # ------------------------------------------------------------
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

    # ------------------------------------------------------------
    # TABLE: Products
    # ------------------------------------------------------------
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

    # ------------------------------------------------------------
    # TABLE: Sales
    # ------------------------------------------------------------
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

    # ------------------------------------------------------------
    # TABLE: Sale Items
    # ------------------------------------------------------------
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

    # ------------------------------------------------------------
    # TABLE: Purchases
    # ------------------------------------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            supplier TEXT,
            total_amount REAL,
            created_at TEXT
        )
    """)

    # ------------------------------------------------------------
    # TABLE: Purchase Items
    # ------------------------------------------------------------
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

    # ------------------------------------------------------------
    # TABLE: Daily Stats (for Dashboard)
    # ------------------------------------------------------------
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

    db.commit()
    db.close()


# ============================================================
# 2)  CRUD: Products
# ============================================================
def get_all_products():
    db = get_database()
    cursor = db.cursor()
    cursor.execute("""
        SELECT id, name, category, purchase_price, selling_price,
               stock_quantity, min_stock, barcode
        FROM products
    """)
    rows = cursor.fetchall()
    db.close()

    products = []
    for row in rows:
        products.append({
            "id": row[0],
            "name": row[1],
            "category": row[2],
            "purchase_price": row[3],
            "selling_price": row[4],
            "stock_quantity": row[5],
            "min_stock": row[6],
            "barcode": row[7],
        })
    return products


# ============================================================
# 3)  Dashboard Queries
# ============================================================
def get_total_sales():
    db = get_database()
    cursor = db.cursor()
    cursor.execute("SELECT SUM(total_amount) FROM sales")
    result = cursor.fetchone()[0]
    db.close()
    return result if result else 0


def get_total_purchases():
    db = get_database()
    cursor = db.cursor()
    cursor.execute("SELECT SUM(total_amount) FROM purchases")
    result = cursor.fetchone()[0]
    db.close()
    return result if result else 0


def get_sales_today():
    today = datetime.now().strftime("%Y-%m-%d")
    db = get_database()
    cursor = db.cursor()
    cursor.execute("""
        SELECT SUM(total_amount)
        FROM sales
        WHERE created_at LIKE ?
    """, (today + "%",))
    result = cursor.fetchone()[0]
    db.close()
    return result if result else 0


def get_recent_sales(limit=10):
    db = get_database()
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

    invoices = []
    for row in rows:
        invoices.append({
            "id": row[0],
            "client_name": row[1] if row[1] else "Client supprimé",
            "total": row[2],
            "date": row[3]
        })
    return invoices


def get_top_products(limit=5):
    db = get_database()
    cursor = db.cursor()
    cursor.execute("""
        SELECT products.name, SUM(sale_items.quantity) AS total_sold
        FROM sale_items
        LEFT JOIN products ON products.id = sale_items.product_id
        GROUP BY product_id
        ORDER BY total_sold DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    db.close()

    result = []
    for row in rows:
        result.append({"name": row[0], "sold": row[1]})
    return result

def get_statistics():
    """Retourne un dictionnaire contenant tous les KPIs du Dashboard"""
    stats = {}

    # Total sales
    stats["total_sales"] = get_total_sales()

    # Total purchases
    stats["total_purchases"] = get_total_purchases()

    # Sales today
    stats["sales_today"] = get_sales_today()

    return stats

def get_recent_purchases(limit=5):
    db = get_database()
    cursor = db.cursor()
    cursor.execute("""
        SELECT id, supplier, total_amount, created_at
        FROM purchases
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    db.close()

    return [
        {"id": r[0], "supplier": r[1], "total": r[2], "date": r[3]}
        for r in rows
    ]
    
def get_top_clients(limit=5):
    db = get_database()
    cursor = db.cursor()
    cursor.execute("""
        SELECT clients.name, SUM(sales.total_amount) AS total_spent
        FROM sales
        LEFT JOIN clients ON clients.id = sales.client_id
        GROUP BY clients.id
        ORDER BY total_spent DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    db.close()

    return [
        {"name": r[0], "total_spent": r[1]}
        for r in rows
    ]
    
def get_low_stock_products(limit=10):
    db = get_database()
    cursor = db.cursor()
    cursor.execute("""
        SELECT name, stock_quantity
        FROM products
        WHERE stock_quantity <= min_stock
        ORDER BY stock_quantity ASC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    db.close()

    return [
        {"name": r[0], "stock": r[1]}
        for r in rows
    ]        

def get_all_clients(self):
        """Récupère tous les clients"""
        self.cursor.execute("SELECT * FROM clients ORDER BY name")
        return [dict(row) for row in self.cursor.fetchall()]    