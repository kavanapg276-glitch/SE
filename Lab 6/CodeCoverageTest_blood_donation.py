import pytest
from blood_donation_screening import process_donor_cohort, verify_storage_centrifuge


def make_cohort(donors, registered=True, ctype="standard", fast_track=False):
    """Helper that builds a cohort dictionary."""
    return {
        "clinic_registered": registered,
        "type": ctype,
        "fast_track": fast_track,
        "donors": donors,
    }


GOOD_DONOR = {"age": 25, "weight_kg": 65, "hb": 14.0}


# ---------- process_donor_cohort ----------

def test_single_accepted_donor():
    cohorts = [make_cohort([GOOD_DONOR])]
    result = process_donor_cohort(cohorts, 450)
    assert result["collected_ml"] == 450
    assert result["status"] == "ACCEPTED"


def test_invalid_cohorts_not_a_list():
    with pytest.raises(ValueError):
        process_donor_cohort("not a list", 450)


def test_invalid_volume_zero():
    with pytest.raises(ValueError):
        process_donor_cohort([make_cohort([GOOD_DONOR])], 0)


def test_unregistered_cohort_is_skipped():
    result = process_donor_cohort([make_cohort([GOOD_DONOR], registered=False)], 450)
    assert result == {"collected_ml": 0, "status": "ZERO_YIELD"}


def test_underage_donor_deferred():
    donor = {"age": 16, "weight_kg": 70, "hb": 14.0}
    result = process_donor_cohort([make_cohort([donor])], 450)
    assert result == {"collected_ml": 0, "status": "ZERO_YIELD"}


def test_high_hemoglobin_deferred():
    donor = {"age": 30, "weight_kg": 70, "hb": 18.5}
    result = process_donor_cohort([make_cohort([donor])], 450)
    assert result == {"collected_ml": 0, "status": "ZERO_YIELD"}


def test_low_hemoglobin_high_altitude_resets_total_and_stops():
    low_hb = {"age": 30, "weight_kg": 70, "hb": 11.0}
    cohort = make_cohort([GOOD_DONOR, low_hb, GOOD_DONOR], ctype="high_altitude")
    result = process_donor_cohort([cohort], 450)
    assert result == {"collected_ml": 0, "status": "ZERO_YIELD"}


def test_fast_track_adds_bonus():
    result = process_donor_cohort([make_cohort([GOOD_DONOR], fast_track=True)], 450)
    assert result == {"collected_ml": 500, "status": "ACCEPTED"}


def test_high_deferral_status():
    bad = {"age": 10, "weight_kg": 30, "hb": 10.0}
    result = process_donor_cohort([make_cohort([bad] * 5)], 450)
    assert result == {"collected_ml": 0, "status": "HIGH_DEFERRAL"}


# ---------- verify_storage_centrifuge ----------

def test_centrifuge_no_data():
    assert verify_storage_centrifuge([]) == "NO_DATA"


def test_centrifuge_stable():
    assert verify_storage_centrifuge([[3500, 3200], [3100]]) == "STABLE"


def test_centrifuge_abort_spin():
    assert verify_storage_centrifuge([[3500, 2900, 2800]]) == "ABORT_SPIN"