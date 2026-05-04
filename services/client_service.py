from __future__ import annotations


class ClientService:
    """Regles metier de base pour les clients."""

    def __init__(self, repository, audit_service=None):
        self.repository = repository
        self.audit = audit_service

    def list_clients(self) -> list[dict]:
        clients = self.repository.list_clients()
        clients.sort(key=lambda c: (c.get("name") or "").lower())
        return clients

    def get_client(self, client_id: int) -> dict | None:
        return self.repository.get_client(client_id)

    def create_client(self, name: str, phone: str = "", email: str = "", address: str = "", actor: dict | None = None) -> int | None:
        clean_name = (name or "").strip()
        if not clean_name:
            return None
        client_id = self.repository.create_client(clean_name, (phone or "").strip(), (email or "").strip(), (address or "").strip())
        if self.audit:
            self.audit.log_action(
                "client.create",
                actor_id=(actor or {}).get("id"),
                actor_username=(actor or {}).get("username"),
                entity_type="client",
                entity_id=str(client_id) if client_id else None,
                status="success" if client_id else "failed",
                details={"name": clean_name},
            )
        return client_id

    def update_client(self, client_id: int, name: str, phone: str = "", email: str = "", address: str = "", actor: dict | None = None) -> bool:
        clean_name = (name or "").strip()
        if not clean_name:
            return False
        ok = self.repository.update_client(client_id, clean_name, (phone or "").strip(), (email or "").strip(), (address or "").strip())
        if self.audit:
            self.audit.log_action(
                "client.update",
                actor_id=(actor or {}).get("id"),
                actor_username=(actor or {}).get("username"),
                entity_type="client",
                entity_id=str(client_id),
                status="success" if ok else "failed",
                details={"name": clean_name},
            )
        return ok

    def delete_client(self, client_id: int, actor: dict | None = None) -> bool:
        ok = self.repository.delete_client(client_id)
        if self.audit:
            self.audit.log_action(
                "client.delete",
                actor_id=(actor or {}).get("id"),
                actor_username=(actor or {}).get("username"),
                entity_type="client",
                entity_id=str(client_id),
                status="success" if ok else "failed",
            )
        return ok
