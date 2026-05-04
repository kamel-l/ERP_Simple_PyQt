from __future__ import annotations


class ClientRepository:
    """Acces SQL pour l'entite client."""

    def __init__(self, db):
        self.db = db

    def list_clients(self) -> list[dict]:
        return self.db.get_all_clients() or []

    def get_client(self, client_id: int) -> dict | None:
        return self.db.get_client_by_id(client_id)

    def create_client(self, name: str, phone: str, email: str, address: str) -> int | None:
        return self.db.add_client(name, phone, email, address)

    def update_client(self, client_id: int, name: str, phone: str, email: str, address: str) -> bool:
        return bool(self.db.update_client(client_id, name, phone, email, address))

    def delete_client(self, client_id: int) -> bool:
        return bool(self.db.delete_client(client_id))

