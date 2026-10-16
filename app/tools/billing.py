import json
from langchain_core.tools import tool


@tool
def get_billing_info(customer_id: str,billing_date: str) -> dict | None:
    """Get billing information for a customer and billing month."""
    try:
        with open("data/billing.json", "r") as file:
            billings = json.load(file)
    except (OSError, json.JSONDecodeError):
        return None

    for bill in billings:
        if bill["customer_id"] == customer_id and bill["billing_month"] == billing_date:
            return bill

    return None