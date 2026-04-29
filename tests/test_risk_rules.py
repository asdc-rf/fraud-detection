from risk_rules import label_risk, score_transaction

# Minimal transaction with all signals at their lowest/neutral values.
# score_transaction(BASE_TX) should return 0.
BASE_TX = {
    "device_risk_score": 10,
    "is_international": 0,
    "amount_usd": 100,
    "velocity_24h": 1,
    "failed_logins_24h": 0,
    "prior_chargebacks": 0,
}


def tx(**overrides):
    return {**BASE_TX, **overrides}


# ---------------------------------------------------------------------------
# label_risk
# ---------------------------------------------------------------------------

def test_label_risk_low():
    assert label_risk(10) == "low"


def test_label_risk_medium():
    assert label_risk(35) == "medium"


def test_label_risk_high():
    assert label_risk(75) == "high"


def test_label_risk_boundary_medium():
    assert label_risk(30) == "medium"


def test_label_risk_boundary_high():
    assert label_risk(60) == "high"


# ---------------------------------------------------------------------------
# amount_usd
# ---------------------------------------------------------------------------

def test_large_amount_adds_risk():
    assert score_transaction(tx(amount_usd=1200)) >= 25


def test_mid_amount_adds_risk():
    assert score_transaction(tx(amount_usd=750)) > score_transaction(tx(amount_usd=100))


# ---------------------------------------------------------------------------
# device_risk_score
# ---------------------------------------------------------------------------

def test_high_device_risk_adds_risk():
    assert score_transaction(tx(device_risk_score=75)) > score_transaction(tx(device_risk_score=10))


def test_mid_device_risk_adds_risk():
    assert score_transaction(tx(device_risk_score=50)) > score_transaction(tx(device_risk_score=10))


# ---------------------------------------------------------------------------
# is_international
# ---------------------------------------------------------------------------

def test_international_adds_risk():
    assert score_transaction(tx(is_international=1)) > score_transaction(tx(is_international=0))


# ---------------------------------------------------------------------------
# velocity_24h
# ---------------------------------------------------------------------------

def test_high_velocity_adds_risk():
    assert score_transaction(tx(velocity_24h=8)) > score_transaction(tx(velocity_24h=1))


def test_moderate_velocity_adds_risk():
    assert score_transaction(tx(velocity_24h=4)) > score_transaction(tx(velocity_24h=1))


# ---------------------------------------------------------------------------
# failed_logins_24h
# ---------------------------------------------------------------------------

def test_many_failed_logins_adds_risk():
    assert score_transaction(tx(failed_logins_24h=6)) > score_transaction(tx(failed_logins_24h=0))


def test_some_failed_logins_adds_risk():
    assert score_transaction(tx(failed_logins_24h=3)) > score_transaction(tx(failed_logins_24h=0))


# ---------------------------------------------------------------------------
# prior_chargebacks
# ---------------------------------------------------------------------------

def test_two_prior_chargebacks_adds_risk():
    assert score_transaction(tx(prior_chargebacks=2)) > score_transaction(tx(prior_chargebacks=0))


def test_one_prior_chargeback_adds_risk():
    assert score_transaction(tx(prior_chargebacks=1)) > score_transaction(tx(prior_chargebacks=0))


# ---------------------------------------------------------------------------
# score clamping
# ---------------------------------------------------------------------------

def test_score_never_below_zero():
    assert score_transaction(BASE_TX) >= 0


def test_score_never_above_100():
    assert score_transaction(tx(
        device_risk_score=90,
        is_international=1,
        amount_usd=5000,
        velocity_24h=10,
        failed_logins_24h=10,
        prior_chargebacks=5,
    )) <= 100


# ---------------------------------------------------------------------------
# combined high-risk profile
# ---------------------------------------------------------------------------

def test_all_major_risk_signals_produce_high_label():
    score = score_transaction(tx(
        device_risk_score=80,
        is_international=1,
        amount_usd=1500,
        velocity_24h=8,
        failed_logins_24h=6,
        prior_chargebacks=2,
    ))
    assert label_risk(score) == "high"
