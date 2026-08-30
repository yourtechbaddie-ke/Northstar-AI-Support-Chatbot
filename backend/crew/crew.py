import json
from pathlib import Path
from crewai import Crew, Process
from .agents import build_support_agents
from .tasks import inventory_task, returns_task, escalation_task

CATALOG = json.loads((Path(__file__).resolve().parents[2] / "data" / "product_catalog.json").read_text())


def run_crew(intent: str, customer_message: str) -> str:
    inventory, returns, escalation = build_support_agents()
    catalog_text = json.dumps(CATALOG, ensure_ascii=False)

    if intent == "stock_availability":
        task = inventory_task(inventory, customer_message, catalog_text)
        agent = inventory
    elif intent == "return_request":
        task = returns_task(returns, customer_message)
        agent = returns
    else:
        task = escalation_task(escalation, customer_message)
        agent = escalation

    crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=False)
    return str(crew.kickoff())
