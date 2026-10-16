from app.tools.customer import get_customer
from app.tools.billing import get_billing_info
from app.tools.usage import get_usage_info
from app.tools.rate_plan import get_rate_plan


print("CUSTOMER")
print(get_customer.invoke({"customer_id": "C001"}))

# print("\nBILL")
# print(get_billing_info.invoke({"customer_id": "C001", "billing_date": "2026-07"}))

# print("\nUSAGE")
# print(get_usage_info.invoke({"customer_id": "C001", "usage_date": "2026-07"}))
# print("\nGET RATE PLAN")
# print(get_rate_plan.invoke({"customer_id": "C001"}))
print(get_customer.name)
print(get_customer.description)
print(get_customer.args)