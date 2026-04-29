import pandas as pd
import pytest

from analyze_fraud import summarize_results


def make_scored(rows):
    """rows: list of (transaction_id, account_id, amount_usd, risk_label)"""
    return pd.DataFrame(rows, columns=["transaction_id", "account_id", "amount_usd", "risk_label"])


def make_chargebacks(txn_ids):
    return pd.DataFrame({"transaction_id": txn_ids})


# ---------------------------------------------------------------------------
# chargeback_rate correctness
# ---------------------------------------------------------------------------

def test_chargeback_rate_is_zero_not_nan_for_clean_tiers():
    scored = make_scored([
        (1, "a", 100.0, "low"),
        (2, "a", 200.0, "medium"),
        (3, "a", 300.0, "high"),
    ])
    chargebacks = make_chargebacks([3])  # only the high-risk txn is a chargeback

    summary = summarize_results(scored, chargebacks)

    low_rate = summary.loc[summary["risk_label"] == "low", "chargeback_rate"].iloc[0]
    mid_rate = summary.loc[summary["risk_label"] == "medium", "chargeback_rate"].iloc[0]

    assert low_rate == 0.0, f"expected 0.0, got {low_rate}"
    assert mid_rate == 0.0, f"expected 0.0, got {mid_rate}"


def test_chargeback_rate_calculation():
    scored = make_scored([
        (1, "a", 100.0, "high"),
        (2, "a", 200.0, "high"),
        (3, "a", 300.0, "high"),
    ])
    chargebacks = make_chargebacks([1, 2])  # 2 of 3 are chargebacks

    summary = summarize_results(scored, chargebacks)
    rate = summary.loc[summary["risk_label"] == "high", "chargeback_rate"].iloc[0]

    assert rate == pytest.approx(2 / 3)


def test_chargeback_rate_all_fraud():
    scored = make_scored([
        (1, "a", 500.0, "high"),
        (2, "a", 500.0, "high"),
    ])
    chargebacks = make_chargebacks([1, 2])

    summary = summarize_results(scored, chargebacks)
    rate = summary.loc[summary["risk_label"] == "high", "chargeback_rate"].iloc[0]

    assert rate == pytest.approx(1.0)


def test_chargeback_rate_no_fraud():
    scored = make_scored([
        (1, "a", 100.0, "low"),
        (2, "a", 200.0, "low"),
    ])
    chargebacks = make_chargebacks([])

    summary = summarize_results(scored, chargebacks)
    rate = summary.loc[summary["risk_label"] == "low", "chargeback_rate"].iloc[0]

    assert rate == 0.0


# ---------------------------------------------------------------------------
# sort order
# ---------------------------------------------------------------------------

def test_risk_labels_sorted_low_to_high():
    scored = make_scored([
        (1, "a", 100.0, "high"),
        (2, "a", 200.0, "low"),
        (3, "a", 300.0, "medium"),
    ])
    chargebacks = make_chargebacks([])

    summary = summarize_results(scored, chargebacks)
    labels = summary["risk_label"].tolist()

    assert labels == ["low", "medium", "high"], f"expected low→medium→high, got {labels}"


# ---------------------------------------------------------------------------
# amount aggregation
# ---------------------------------------------------------------------------

def test_total_and_avg_amount():
    scored = make_scored([
        (1, "a", 100.0, "low"),
        (2, "a", 300.0, "low"),
    ])
    chargebacks = make_chargebacks([])

    summary = summarize_results(scored, chargebacks)
    row = summary.loc[summary["risk_label"] == "low"].iloc[0]

    assert row["transactions"] == 2
    assert row["total_amount_usd"] == pytest.approx(400.0)
    assert row["avg_amount_usd"] == pytest.approx(200.0)
