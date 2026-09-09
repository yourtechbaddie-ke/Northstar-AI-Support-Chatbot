import json
import os
import re
from pathlib import Path
from typing import Any

from openai import OpenAI

ROOT = Path(__file__).resolve().parents[2]
CATALOG_PATH = ROOT / "data" / "product_catalog.json"
IMAGE_DIR = ROOT / "public" / "images"
CATALOG = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
RETURN_POLICY = (
    "Northstar accepts eligible returns within 30 days. Items should be unused. "
    "FedEx drop-off is supported, refunds typically take 5–7 days, and exchanges are available."
)


def _normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def _image_map() -> dict[str, str]:
    if not IMAGE_DIR.exists():
        return {}
    return {
        _normalize(path.stem): f"/images/{path.name}"
        for path in IMAGE_DIR.iterdir()
        if path.is_file() and path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}
    }


def _attach_images(products: list[dict[str, Any]]) -> list[dict[str, Any]]:
    images = _image_map()
    return [{**product, "image_url": images.get(_normalize(str(product.get("name", ""))))} for product in products]


def _catalog() -> list[dict[str, Any]]:
    return CATALOG


def _find_products(message: str) -> list[dict[str, Any]]:
    tokens = [t for t in re.findall(r"[a-z0-9]+", message.lower()) if len(t) > 2]
    scored: list[tuple[int, dict[str, Any]]] = []
    for product in _catalog():
        haystack = " ".join(str(product.get(key, "")) for key in ("name", "category", "fabric", "sku")).lower()
        score = sum(token in haystack for token in tokens)
        if score:
            scored.append((score, product))
    return _attach_images([p for _, p in sorted(scored, key=lambda x: x[0], reverse=True)[:3]])


def _intent(message: str) -> str:
    q = message.lower()
    if any(k in q for k in ("return", "refund", "exchange")):
        return "return_request"
    if any(k in q for k in ("stock", "available", "availability", "in stock", "do you have", "do you carry")):
        return "stock_availability"
    if "@" in q or any(k in q for k in ("email me", "contact me", "email address")):
        return "contact_capture"
    return "general_support"


def _run_openai(intent: str, message: str, products: list[dict[str, Any]]) -> str | None:
    """Use OpenAI directly when configured; no agent framework is required."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    try:
        client = OpenAI(api_key=api_key)
        context = {"intent": intent, "customer_message": message, "matched_products": products, "return_policy": RETURN_POLICY}
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            temperature=0.2,
            messages=[
                {"role": "system", "content": "You are Northstar's luxury retail support concierge. Be warm, concise and precise. Use only supplied catalog and policy facts. Never invent prices, stock, products, delivery promises, discounts or policies. If the supplied information does not answer the question, say so clearly and recommend human support."},
                {"role": "user", "content": json.dumps(context, ensure_ascii=False)},
            ],
        )
        return (response.choices[0].message.content or "").strip() or None
    except Exception:
        return None


def answer_customer(message: str) -> dict[str, Any]:
    intent = _intent(message)
    products = _find_products(message) if intent == "stock_availability" else []
    ai_response = _run_openai(intent, message, products)
    if ai_response:
        return {"message": ai_response, "intent": intent, "products": products}
    if intent == "stock_availability":
        if not products:
            return {"message": "I couldn't find an exact product match in the Northstar catalog. Share the product name or category and I'll check again.", "intent": intent, "products": []}
        product = products[0]
        status = product.get("status", "")
        if status == "OUT_OF_STOCK":
            text = f"The {product['name']} is currently out of stock."
        elif status == "LOW_STOCK":
            text = f"The {product['name']} is available, with limited stock remaining."
        else:
            text = f"Yes — the {product['name']} is currently in stock."
        return {"message": text, "intent": intent, "products": products}
    if intent == "return_request":
        return {"message": RETURN_POLICY, "intent": intent, "products": []}
    if intent == "contact_capture":
        return {"message": "I can help with that. Please share the email address you'd like Northstar Support to use for follow-up.", "intent": intent, "products": []}
    return {"message": "I’m here to help with Northstar products, availability and support. Tell me what you’re looking for, and I’ll guide you from there.", "intent": intent, "products": []}
