from __future__ import annotations


class ProductService:
    """Regles metier de base pour les produits."""

    def __init__(self, repository, audit_service=None):
        self.repository = repository
        self.audit = audit_service

    def list_products(self) -> list[dict]:
        return self.repository.list_products()

    def search_products(self, query: str) -> list[dict]:
        return self.repository.search_products((query or "").strip(), starts_with=True)

    def get_product(self, product_id: int) -> dict | None:
        return self.repository.get_product(product_id)

    def resolve_category_id(self, category_name: str) -> int | None:
        name = (category_name or "").strip()
        if not name:
            return None
        categories = self.repository.list_categories()
        category = next((c for c in categories if c.get("name") == name), None)
        return category["id"] if category else self.repository.create_category(name)

    def create_product(self, actor: dict | None = None, **kwargs) -> int | None:
        product_id = self.repository.create_product(**kwargs)
        if self.audit:
            self.audit.log_action(
                "product.create",
                actor_id=(actor or {}).get("id"),
                actor_username=(actor or {}).get("username"),
                entity_type="product",
                entity_id=str(product_id) if product_id else None,
                status="success" if product_id else "failed",
                details={"name": kwargs.get("name")},
            )
        return product_id

    def update_product(self, actor: dict | None = None, **kwargs) -> bool:
        ok = self.repository.update_product(**kwargs)
        if self.audit:
            self.audit.log_action(
                "product.update",
                actor_id=(actor or {}).get("id"),
                actor_username=(actor or {}).get("username"),
                entity_type="product",
                entity_id=str(kwargs.get("product_id")),
                status="success" if ok else "failed",
                details={"name": kwargs.get("name")},
            )
        return ok

    def delete_product(self, product_id: int, actor: dict | None = None) -> bool:
        ok = self.repository.delete_product(product_id)
        if self.audit:
            self.audit.log_action(
                "product.delete",
                actor_id=(actor or {}).get("id"),
                actor_username=(actor or {}).get("username"),
                entity_type="product",
                entity_id=str(product_id),
                status="success" if ok else "failed",
            )
        return ok

