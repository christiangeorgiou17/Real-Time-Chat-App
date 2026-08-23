# Database Schema & Maintenance

This application uses **SQLite** for local development, managed entirely via **Flask-SQLAlchemny**.

## Blocklist Schema

### `TokenBlocklist` Table
Stores unique token identifiers to invalidate sessions upon logout.

| Column Name | Data Type | Modifiers | Description |
| :--- | :--- | :--- | :--- |
| `id` | Integer | Primary Key, Auto-Increment | Unique row identifier. |
| `jti` | String(36) | Unique, Nullable=False, Index | The unique JWT identifier string. |
| `created_at` | DateTime | Nullable=False, Default=Now | Timestamp of when the user logged out. |

---

## Automated 24-Hour Database Cleanup

To prevent the local SQLite databse file (`chat.db`) from bloating over time with useless, naturally expired tokens, an automated pruning function is implemented.

### How it works
* **Trigger:** Runs via a timestamp-checked loop attached to a Flask global hook (e.g. `before_request`).
* **Interval:** Executes exactly once every 24 hours.
* **Logic:** Calculates a cutoff threshold (Current Time minus 1 Day). Any blocklist row with a `created_at` timestamp older than this cutoff is safely deleted as the token would have naturally expired anyway.

### Conseptual SQLAlchemy Query
```python
# Cleans up old rows to keep local DB footprint small
cutoff_time = datetime.now(timezone.utc) - JWT_ACCESS_TOKEN_EXPIRES # JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)
deleted_count = db.session.query(TokenBlockList).filter(TokenBlockList.created_at < cutoff_time).delete()
db.session.commit()
```