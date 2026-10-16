import json
from langchain_core.tools import tool


@tool
def get_usage_info(customer_id: str, usage_date: str) -> dict | None:
    """Get usage information for a customer and billing month."""
    try:
        with open("data/usage.json", "r") as file:
            usages = json.load(file)
    except (OSError, json.JSONDecodeError):
        return None

    for usage in usages:
        if usage["customer_id"] == customer_id and usage["billing_month"] == usage_date:
            return usage

    return None