CREATE TABLE IF NOT EXISTS api_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    token_hash TEXT NOT NULL UNIQUE,
    issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    is_revoked INTEGER NOT NULL DEFAULT 0,
    created_by_user_id INTEGER
);

CREATE INDEX IF NOT EXISTS idx_api_tokens_expires_at ON api_tokens(expires_at);
CREATE INDEX IF NOT EXISTS idx_api_tokens_revoked ON api_tokens(is_revoked);

