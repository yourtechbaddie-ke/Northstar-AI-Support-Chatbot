import json
import re
from pathlib import Path
from typing import Any

CATALOG = json.loads((Path(__file__).resolve().parents[2] / "data" / "product_catalog.json").read_text())
RETURN_POLICY = "Northstar accepts eligible returns within 30 days. Items should be unused. FedEx drop-off is supported, refunds typically take 5–7 days, and exchanges are available."


def _find_products(message: str) -> list[dict[str, Any]]:
    q = message.lower()
    tokens = [t for t in re.findall(r"[a-z0-9]+", q) if len(t) > 2]
    scored = []
    for product in CATALOG:
        haystack = f"{product['name']} {product['category']} {product['fabric']}".lower()
        score = sum(token in haystack for token in tokens)
        if score:
            scored.append((score, product))
    return [p for _, p in sorted(scored, key=lambda x: x[0], reverse=True)[:3]]


def _intent(message: str) -> str:
    q = message.lower()
    if any(k in q for k in ["return", "refund", "exchange"]):
        return "return_request"
    if any(k in q for k in ["stock", "available", "availability", "have the", "do you carry", "in stock"]):
        return "stock_availability"
    if "@" in q or any(k in q for k in ["email me", "contact me", "email address"]):
        return "contact_capture"
    return "out_of_scope"


def answer_customer(message: str) -> dict[str, Any]:
    intent = _intent(message)
    products = _find_products(message) if intent == "stock_availability" else []

    if intent == "stock_availability":
        if not products:
            return {"message": "I couldn't find an exact product match in the Northstar catalog. If you share the product name or category, I can check again.", "intent": intent, "products": []}
        product = products[0]
        if product["status"] == "OUT_OF_STOCK":
            text = f"The {product['name']} is currently out of stock."
        elif product["status"] == "LOW_STOCK":
            text = f"The {product['name']} is available, with limited stock remaining."
        else:
            text = f"Yes — the {product['name']} is currently in stock."
        return {"message": text, "intent": intent, "products": products}

    if intent == "return_request":
        return {"message": RETURN_POLICY, "intent": intent, "products": []}

    if intent == "contact_capture":
        return {"message": "I can help with that. Please share the email address you'd like Northstar Support to use for follow-up.", "intent": intent, "products": []}

    return {"message": "Thanks for reaching out. I can help with Northstar product availability and returns, and I can route other requests to the support team.", "intent": intent, "products": []}
