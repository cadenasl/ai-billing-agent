import json

import pytest

from app.tools.billing import get_billing_info
from app.tools.customer import get_customer
from app.tools.rate_plan import get_rate_plan
from app.tools.usage import get_usage_info


@pytest.fixture
def data_dir(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    directory = tmp_path / "data"
    directory.mkdir()
    return directory


def write_json(data_dir, filename, data):
    (data_dir / filename).write_text(json.dumps(data), encoding="utf-8")


def test_get_customer_returns_matching_customer(data_dir):
    customer = {
        "customer_id": "C001",
        "name": "Alex Example",
        "rate_plan": "RESIDENTIAL_STANDARD",
    }
    write_json(data_dir, "customers.json", [customer])

    assert get_customer.invoke({"customer_id": "C001"}) == customer


def test_get_customer_returns_none_for_unknown_customer(data_dir):
    write_json(data_dir, "customers.json", [])

    assert get_customer.invoke({"customer_id": "C999"}) is None


def test_get_billing_info_matches_customer_and_month(data_dir):
    bill = {
        "customer_id": "C001",
        "billing_month": "2026-07",
        "amount_due": 178.40,
    }
    write_json(data_dir, "billing.json", [bill])

    assert get_billing_info.invoke(
        {"customer_id": "C001", "billing_date": "2026-07"}
    ) == bill


def test_get_billing_info_returns_none_when_customer_or_month_does_not_match(
    data_dir,
):
    write_json(
        data_dir,
        "billing.json",
        [{"customer_id": "C001", "billing_month": "2026-07"}],
    )

    assert get_billing_info.invoke(
        {"customer_id": "C001", "billing_date": "2026-06"}
    ) is None
    assert get_billing_info.invoke(
        {"customer_id": "C002", "billing_date": "2026-07"}
    ) is None


def test_get_usage_info_matches_customer_and_month(data_dir):
    usage = {
        "customer_id": "C001",
        "billing_month": "2026-07",
        "usage_kwh": 1240,
    }
    write_json(data_dir, "usage.json", [usage])

    assert get_usage_info.invoke(
        {"customer_id": "C001", "usage_date": "2026-07"}
    ) == usage


def test_get_usage_info_returns_none_when_customer_or_month_does_not_match(
    data_dir,
):
    write_json(
        data_dir,
        "usage.json",
        [{"customer_id": "C001", "billing_month": "2026-07"}],
    )

    assert get_usage_info.invoke(
        {"customer_id": "C001", "usage_date": "2026-06"}
    ) is None
    assert get_usage_info.invoke(
        {"customer_id": "C002", "usage_date": "2026-07"}
    ) is None


def test_get_rate_plan_returns_plan_assigned_to_customer(data_dir):
    write_json(
        data_dir,
        "customers.json",
        [{"customer_id": "C001", "rate_plan": "RESIDENTIAL_STANDARD"}],
    )
    rate_plan = {
        "rate_plan": "RESIDENTIAL_STANDARD",
        "base_charge": 20.0,
    }
    write_json(data_dir, "rate_plans.json", [rate_plan])

    assert get_rate_plan.invoke({"customer_id": "C001"}) == rate_plan


def test_get_rate_plan_returns_none_for_unknown_customer(data_dir):
    write_json(data_dir, "customers.json", [])

    assert get_rate_plan.invoke({"customer_id": "C999"}) is None


def test_get_rate_plan_returns_none_when_customer_plan_is_not_defined(data_dir):
    write_json(
        data_dir,
        "customers.json",
        [{"customer_id": "C001", "rate_plan": "UNKNOWN_PLAN"}],
    )
    write_json(data_dir, "rate_plans.json", [])

    assert get_rate_plan.invoke({"customer_id": "C001"}) is None
