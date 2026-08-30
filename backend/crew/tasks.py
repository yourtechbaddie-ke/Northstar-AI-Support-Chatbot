from crewai import Task


def inventory_task(agent, customer_message: str, catalog_text: str):
    return Task(
        description=(
            f"Answer this customer question using only the catalog below. "
            f"Customer: {customer_message}\nCatalog: {catalog_text}\n"
            "If the product or fact is absent, say that it is unknown."
        ),
        expected_output="A concise, factual customer-support response.",
        agent=agent,
    )


def returns_task(agent, customer_message: str):
    return Task(
        description=(
            f"Explain the documented Northstar return policy for this request: {customer_message}. "
            "Do not invent exceptions or eligibility decisions."
        ),
        expected_output="Clear return instructions grounded in the supplied policy.",
        agent=agent,
    )


def escalation_task(agent, customer_message: str):
    return Task(
        description=f"Write a warm holding response for this unsupported request: {customer_message}.",
        expected_output="A transparent response that directs the customer to human support.",
        agent=agent,
    )
