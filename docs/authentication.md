# Authentication Architecture & Token Management

This documentation details the JWT authentication flow and the automated database lifecycle management for blocklisted tokens.

## Token Lifecycle & Logout Flow
1. **Login:** User authenticates, receiving an `access_token` valid for 1 hour.
2. **Protected Request:** Client sends token in the `Authentication: Bearer <token>` header.
3. **Logout:** The token's unique ID (`jti`) is saved to the `TokenBlockList` database table. The token is now dead.

## Automated Database Pruning
To prevent the SQLite database (`chat.db`) from bloating with thousends of old, useless logged-out tokens, a cleanup script runs daily.

### Mantenance Logic
* **Trigger:** Runs via a time-checked background condition (or `before_request` hook).
* **Interval:** Once every 24 hours.
* **Action:** Wipes rows where `created_at` timestamp is older than the maximum token lifetime.

```sql
-- Conceptual cleanup query executed by SQLAlchemy
DELETE FROM token_blocklist WHERE created_at < DATETIME('now', '-1 day');
```