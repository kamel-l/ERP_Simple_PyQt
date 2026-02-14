from .db import Database

db = Database()

# ------------------ Products ------------------
class ProductModel:
    @staticmethod
    def all():
        return db.fetchall("SELECT id, name, quantity, price FROM products")

    @staticmethod
    def create(name, quantity, price):
        db.execute("INSERT INTO products (name, quantity, price) VALUES (?, ?, ?)", (name, quantity, price))

    @staticmethod
    def update(product_id, name, quantity, price):
        db.execute("UPDATE products SET name=?, quantity=?, price=? WHERE id=?", (name, quantity, price, product_id))

    @staticmethod
    def delete(product_id):
        db.execute("DELETE FROM products WHERE id=?", (product_id,))

# ------------------ Clients ------------------
class ClientModel:
    @staticmethod
    def all():
        return db.fetchall("SELECT id, name, phone, email FROM clients")

    @staticmethod
    def create(name, phone, email):
        db.execute("INSERT INTO clients (name, phone, email) VALUES (?, ?, ?)", (name, phone, email))

    @staticmethod
    def update(client_id, name, phone, email):
        db.execute("UPDATE clients SET name=?, phone=?, email=? WHERE id=?", (name, phone, email, client_id))

    @staticmethod
    def delete(client_id):
        db.execute("DELETE FROM clients WHERE id=?", (client_id,))

# ------------------ Sales ------------------
class SaleModel:
    @staticmethod
    def create(client_id, date, total):
        db.execute("INSERT INTO sales (client_id, date, total) VALUES (?, ?, ?)", (client_id, date, total))
        return db.cursor.lastrowid

class SaleItemModel:
    @staticmethod
    def create(sale_id, product_id, quantity, price, total):
        db.execute(
            "INSERT INTO sales_items (sale_id, product_id, quantity, price, total) VALUES (?, ?, ?, ?, ?)",
            (sale_id, product_id, quantity, price, total)
        )

# ------------------ Purchases ------------------
class PurchaseModel:
    @staticmethod
    def create(supplier_id, date, total):
        db.execute("INSERT INTO purchases (supplier_id, date, total) VALUES (?, ?, ?)", (supplier_id, date, total))
        return db.cursor.lastrowid

class PurchaseItemModel:
    @staticmethod
    def create(purchase_id, product_id, quantity, price, total):
        db.execute(
            "INSERT INTO purchase_items (purchase_id, product_id, quantity, price, total) VALUES (?, ?, ?, ?, ?)",
            (purchase_id, product_id, quantity, price, total)
        )
