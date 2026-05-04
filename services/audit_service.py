from __future__ import annotations

import json
import logging

logger = logging.getLogger(__name__)


class AuditService:
    """Journalisation applicative des actions sensibles."""

    def __init__(self, db):
        self.db = db

    def log_action(
        self,
        action: str,
        *,
        actor_id: int | None = None,
        actor_username: str | None = None,
        entity_type: str | None = None,
        entity_id: str | None = None,
        status: str = "success",
        details: dict | None = None,
        source_ip: str | None = None,
    ) -> None:
        try:
            payload = json.dumps(details or {}, ensure_ascii=False)
            self.db.cursor.execute(
                """
                INSERT INTO audit_log(
                    actor_id, actor_username, action, entity_type, entity_id,
                    status, details, source_ip
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    actor_id,
                    actor_username,
                    action,
                    entity_type,
                    entity_id,
                    status,
                    payload,
                    source_ip,
                ),
            )
            self.db.conn.commit()
        except Exception as exc:
            logger.warning("Audit log skipped: %s", exc)

