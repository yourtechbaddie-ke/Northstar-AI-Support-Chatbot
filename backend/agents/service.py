import json
import os
import re
from pathlib import Path
from typing import Any

CATALOG = json.loads(
    (Path(__file__).resolve().parents[2] / "data" / "product_catalog.json").read_text(encoding="utf-8")
)

RETURN_POLICY = (
    "Northstar accepts eligible returns within 30 days. Items should be unused. "
    "FedEx drop-off is supported, refunds typically take 5–7 days, and exchanges are available."
)


def _find_products(message: str) -> list[dict[str, Any]]:
    q = message.lower()
    tokens = [t for t in re.findall(r"[a-z0-9]+", q) if len(t) > 2]
    scored: list[tuple[int, dict[str, Any]]] = []
    for product in CATALOG:
        haystack = " ".join(
            str(product.get(key, "")) for key in ("name", "category", "fabric", "sku")
        ).lower()
        score = sum(token in haystack for token in tokens)
        if score:
            scored.append((score, product))
    return [p for _, p in sorted(scored, key=lambda x: x[0], reverse=True)[:3]]


def _intent(message: str) -> str:
    q = message.lower()
    if any(k in q for k in ("return", "refund", "exchange")):
        return "return_request"
    if any(k in q for k in ("stock", "available", "availability", "in stock", "do you have", "do you carry")):
        return "stock_availability"
    if "@" in q or any(k in q for k in ("email me", "contact me", "email address")):
        return "contact_capture"
    return "escalation"


def _catalog_context(products: list[dict[str, Any]]) -> str:
    return json.dumps(products, ensure_ascii=False)


def _run_crewai(intent: str, message: str, products: list[dict[str, Any]]) -> str | None:
    """Use CrewAI when an LLM key is configured; keep a deterministic fallback for local demos."""
    if not os.getenv("OPENAI_API_KEY"):
        return None

    try:
        from crewai import Agent, Crew, LLM, Process, Task

        llm = LLM(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            api_key=os.environ["OPENAI_API_KEY"],
            temperature=0.2,
        )

        if intent == "stock_availability":
            agent = Agent(
                role="Northstar Luxury Inventory Specialist",
                goal="Answer availability questions using only the supplied catalog records.",
                backstory="A precise retail specialist who never invents stock, price, SKU, or product facts.",
                llm=llm,
                allow_delegation=False,
                verbose=False,
            )
            task = Task(
                description=(
                    "Answer the customer using only these matched catalog records. "
                    "If the records do not establish the answer, say so. Keep the response concise and warm.\n"
                    f"Customer: {message}\nRecords: {_catalog_context(products)}"
                ),
                expected_output="A concise customer-facing availability response.",
                agent=agent,
            )
        elif intent == "return_request":
            agent = Agent(
                role="Northstar Returns Policy Specialist",
                goal="Explain only the approved Northstar return policy.",
                backstory="A careful customer-care specialist who never invents exceptions.",
                llm=llm,
                allow_delegation=False,
                verbose=False,
            )
            task = Task(
                description=f"Answer this return question using only this policy: {RETURN_POLICY}\nCustomer: {message}",
                expected_output="A clear, concise return-policy response.",
                agent=agent,
            )
        else:
            agent = Agent(
                role="Northstar Customer Escalation Specialist",
                goal="Provide a transparent, warm handoff for requests outside the supported knowledge scope.",
                backstory="A calm support specialist who never fabricates answers.",
                llm=llm,
                allow_delegation=False,
                verbose=False,
            )
            task = Task(
                description=f"Write a helpful holding response for this request and direct the customer to human support: {message}",
                expected_output="A warm, transparent escalation response.",
                agent=agent,
            )

        crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=False)
        return str(crew.kickoff()).strip()
    except Exception:
        return None


def answer_customer(message: str) -> dict[str, Any]:
    intent = _intent(message)
    products = _find_products(message) if intent == "stock_availability" else []
    ai_response = _run_crewai(intent, message, products)

    if ai_response:
        return {"message": ai_response, "intent": intent, "products": products}

    if intent == "stock_availability":
        if not products:
            return {
                "message": "I couldn't find an exact product match in the Northstar catalog. Share the product name or category and I'll check again.",
                "intent": intent,
                "products": [],
            }
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
        return {
            "message": "I can help with that. Please share the email address you'd like Northstar Support to use for follow-up.",
            "intent": intent,
            "products": [],
        }

    return {
        "message": "I want to make sure you get the right answer. This request needs our human support team, and I can help route it to them.",
        "intent": intent,
        "products": [],
    }
