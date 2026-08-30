"""Optional Firebase inventory adapter.

The chatbot remains catalog-first for local development. When Firebase Admin
credentials and FIREBASE_DATABASE_URL are configured, this adapter can read
an `inventory` node and use those records as the live stock source.
"""

import json
import os
from typing import Any


_initialized = False


def _init_firebase() -> bool:
    global _initialized
    if _initialized:
        return True

    database_url = os.getenv("FIREBASE_DATABASE_URL")
    credentials_json = os.getenv("FIREBASE_CREDENTIALS_JSON")
    if not database_url or not credentials_json:
        return False

    try:
        import firebase_admin
        from firebase_admin import credentials

        if not firebase_admin._apps:
            credentials_dict = json.loads(credentials_json)
            firebase_admin.initialize_app(
                credentials.Certificate(credentials_dict),
                {"databaseURL": database_url},
            )
        _initialized = True
        return True
    except Exception:
        return False


def get_live_inventory() -> list[dict[str, Any]] | None:
    """Return normalized live inventory records, or None when Firebase is unavailable."""
    if not _init_firebase():
        return None

    try:
        from firebase_admin import db

        raw = db.reference(os.getenv("FIREBASE_INVENTORY_PATH", "inventory")).get()
        if raw is None:
            return []

        records = list(raw.values()) if isinstance(raw, dict) else raw
        normalized: list[dict[str, Any]] = []
        for item in records:
            if not isinstance(item, dict) or not item.get("id") or not item.get("name"):
                continue
            stock = int(item.get("stock", 0))
            status = item.get("status")
            if not status:
                status = "OUT_OF_STOCK" if stock <= 0 else "LOW_STOCK" if stock <= 10 else "IN_STOCK"
            normalized.append({**item, "stock": stock, "status": status})
        return normalized
    except Exception:
        return None
