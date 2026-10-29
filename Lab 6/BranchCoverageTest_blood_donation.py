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



# ================= EXTRA TESTS FOR BRANCH COVERAGE =================

# ---------- process_donor_cohort ----------

def test_invalid_volume_negative():
    with pytest.raises(ValueError):
        process_donor_cohort([make_cohort([GOOD_DONOR])], -10)


def test_empty_cohort_list():
    assert process_donor_cohort([], 450) == {"collected_ml": 0, "status": "ZERO_YIELD"}


def test_cohort_with_missing_keys_uses_defaults():
    # {} -> not registered by default, so it is skipped
    assert process_donor_cohort([{}], 450)["status"] == "ZERO_YIELD"
    # registered but no donors / type -> defaults used
    assert process_donor_cohort([{"clinic_registered": True}], 450)["status"] == "ZERO_YIELD"


def test_donor_with_missing_keys_is_deferred():
    cohort = make_cohort([{}])
    result = process_donor_cohort([cohort], 450)
    assert result == {"collected_ml": 0, "status": "ZERO_YIELD"}


def test_underweight_donor_deferred():
    donor = {"age": 30, "weight_kg": 49, "hb": 14.0}
    assert process_donor_cohort([make_cohort([donor])], 450)["collected_ml"] == 0


def test_boundary_age_17_and_weight_50_accepted():
    donor = {"age": 17, "weight_kg": 50, "hb": 14.0}
    assert process_donor_cohort([make_cohort([donor])], 450)["collected_ml"] == 450


def test_low_hemoglobin_standard_cohort_continues():
    low_hb = {"age": 30, "weight_kg": 70, "hb": 12.0}
    cohort = make_cohort([low_hb, GOOD_DONOR], ctype="standard")
    result = process_donor_cohort([cohort], 450)
    assert result == {"collected_ml": 450, "status": "ACCEPTED"}


def test_hemoglobin_boundaries_accepted():
    low_edge = {"age": 30, "weight_kg": 70, "hb": 12.5}
    high_edge = {"age": 30, "weight_kg": 70, "hb": 18.0}
    result = process_donor_cohort([make_cohort([low_edge, high_edge])], 450)
    assert result["collected_ml"] == 900


def test_high_altitude_cohort_all_good_donors():
    cohort = make_cohort([GOOD_DONOR, GOOD_DONOR], ctype="high_altitude")
    assert process_donor_cohort([cohort], 450)["collected_ml"] == 900


def test_fast_track_with_no_donors():
    result = process_donor_cohort([make_cohort([], fast_track=True)], 450)
    assert result == {"collected_ml": 50, "status": "ACCEPTED"}


def test_high_altitude_reset_then_fast_track_bonus():
    low_hb = {"age": 30, "weight_kg": 70, "hb": 11.0}
    cohort = make_cohort([GOOD_DONOR, low_hb], ctype="high_altitude", fast_track=True)
    assert process_donor_cohort([cohort], 450)["collected_ml"] == 50


def test_four_deferrals_is_not_high_deferral():
    bad = {"age": 10, "weight_kg": 30, "hb": 10.0}
    result = process_donor_cohort([make_cohort([bad] * 4 + [GOOD_DONOR])], 450)
    assert result == {"collected_ml": 450, "status": "ACCEPTED"}


def test_high_deferral_keeps_collected_volume():
    bad = {"age": 10, "weight_kg": 30, "hb": 10.0}
    result = process_donor_cohort([make_cohort([bad] * 5 + [GOOD_DONOR])], 450)
    assert result == {"collected_ml": 450, "status": "HIGH_DEFERRAL"}


def test_multiple_cohorts_mixed():
    c1 = make_cohort([GOOD_DONOR])
    c2 = make_cohort([GOOD_DONOR], registered=False)
    c3 = make_cohort([GOOD_DONOR], fast_track=True)
    assert process_donor_cohort([c1, c2, c3], 450) == {"collected_ml": 950, "status": "ACCEPTED"}


# ---------- verify_storage_centrifuge ----------

def test_centrifuge_none_input():
    assert verify_storage_centrifuge(None) == "NO_DATA"


def test_centrifuge_single_drop_is_stable():
    assert verify_storage_centrifuge([[3500, 2900, 3500]]) == "STABLE"


def test_centrifuge_non_consecutive_drops_reset_streak():
    assert verify_storage_centrifuge([[2900, 3500, 2900]]) == "STABLE"


def test_centrifuge_3000_is_not_a_drop():
    assert verify_storage_centrifuge([[3000, 3000, 3000]]) == "STABLE"


def test_centrifuge_abort_in_second_run():
    assert verify_storage_centrifuge([[3500, 3400], [2900, 2900]]) == "ABORT_SPIN"


def test_centrifuge_streak_resets_between_runs():
    assert verify_storage_centrifuge([[2900], [2900]]) == "STABLE"


def test_centrifuge_empty_run():
    assert verify_storage_centrifuge([[]]) == "STABLE"    