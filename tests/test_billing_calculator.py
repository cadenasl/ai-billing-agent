from decimal import Decimal

from app.billing_Calculator import calculate_bill


def test_c001_june_bill():
    total = calculate_bill(
        usage_kwh=840,
        base_charge=Decimal("20.00"),
        tier1_rate=Decimal("0.12"),
        tier2_rate=Decimal("0.16"),
        tier1_limit=1000,
    )

    assert total == Decimal("120.80")


def test_c001_july_bill():
    total = calculate_bill(
        usage_kwh=1240,
        base_charge=Decimal("20.00"),
        tier1_rate=Decimal("0.12"),
        tier2_rate=Decimal("0.16"),
        tier1_limit=1000,
    )

    assert total == Decimal("178.40")


def test_c001_bill_increase():
    june = calculate_bill(
        usage_kwh=840,
        base_charge=Decimal("20.00"),
        tier1_rate=Decimal("0.12"),
        tier2_rate=Decimal("0.16"),
        tier1_limit=1000,
    )

    july = calculate_bill(
        usage_kwh=1240,
        base_charge=Decimal("20.00"),
        tier1_rate=Decimal("0.12"),
        tier2_rate=Decimal("0.16"),
        tier1_limit=1000,
    )

    assert july - june == Decimal("57.60")