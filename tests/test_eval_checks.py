from evals.run_evals import check_expected_facts


def test_check_expected_facts_accepts_thousands_separator():
    assert check_expected_facts("Usage was 1,240 kWh.", ["1240"], [])


def test_check_expected_facts_accepts_alternative_phrasing():
    assert check_expected_facts(
        "The fee's cause cannot be determined from the records.",
        [],
        [["cannot determine", "cannot be determined", "not available"]],
    )


def test_check_expected_facts_rejects_missing_required_fact():
    assert not check_expected_facts(
        "The bill was $178.40.",
        ["57.60"],
        [],
    )
