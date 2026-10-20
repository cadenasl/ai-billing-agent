from decimal import Decimal


def calculate_bill(
    usage_kwh: int,
    base_charge: Decimal,
    tier1_rate: Decimal,
    tier2_rate: Decimal,
    tier1_limit: int,
) -> Decimal:

    tier1_usage = min(usage_kwh, tier1_limit)
    tier2_usage = max(usage_kwh - tier1_limit, 0)

    total = (
        base_charge
        + Decimal(tier1_usage) * tier1_rate
        + Decimal(tier2_usage) * tier2_rate
    )

    return total.quantize(Decimal("0.01"))