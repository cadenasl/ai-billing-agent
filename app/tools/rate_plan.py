from app.tools.customer import get_customer
import json
from langchain_core.tools import tool


@tool
def get_rate_plan(customer_id: str) -> dict | None:
    """Get the rate plan assigned to a customer."""
    customer = get_customer.invoke({"customer_id": customer_id})

    if customer is None:
        return None

    rate_plan_name = customer["rate_plan"]
    try:
        with open("data/rate_plans.json", "r") as file:
            rate_plans = json.load(file)
    except (OSError, json.JSONDecodeError):
        return None

    for rate_plan in rate_plans:
        if rate_plan["rate_plan"] == rate_plan_name:
            return rate_plan

    return None