from __future__ import annotations


class ProductRepository:
    """Acces SQL pour l'entite produit."""

    def __init__(self, db):
        self.db = db

    def list_products(self) -> list[dict]:
        return self.db.get_all_products() or []

    def search_products(self, query: str, starts_with: bool = True) -> list[dict]:
        return self.db.search_products(query, starts_with=starts_with) or []

    def get_product(self, product_id: int) -> dict | None:
        return self.db.get_product_by_id(product_id)

    def create_product(self, **kwargs) -> int | None:
        return self.db.add_product(**kwargs)

    def update_product(self, **kwargs) -> bool:
        return bool(self.db.update_product(**kwargs))

    def delete_product(self, product_id: int) -> bool:
        return bool(self.db.delete_product(product_id))

    def list_categories(self) -> list[dict]:
        return self.db.get_all_categories() or []

    def create_category(self, name: str) -> int | None:
        return self.db.add_category(name)

