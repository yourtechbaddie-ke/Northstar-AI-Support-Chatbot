import json
from pathlib import Path

CATALOG_PATH = Path(__file__).resolve().parents[2] / "data" / "product_catalog.json"


def load_catalog() -> list[dict]:
    return json.loads(CATALOG_PATH.read_text())


def find_product(query: str) -> list[dict]:
    q = query.lower().strip()
    return [p for p in load_catalog() if q in p["name"].lower() or q in p["category"].lower() or q == p["id"].lower()]
