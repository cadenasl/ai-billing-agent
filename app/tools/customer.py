import json
from langchain_core.tools import tool


@tool
def get_customer(customer_id: str) -> dict | None:
    """Look up a customer by customer ID."""
    try:
        with open("data/customers.json", "r") as file:
            customers = json.load(file)
    except (OSError, json.JSONDecodeError):
        return None

    for customer in customers:
        if customer["customer_id"] == customer_id:
            return customer

    return None