
import pytest
from water_utility_billing import (
    calculate_water_bill,
    check_meter_tampering,
)


# 1. Active residential account
def test_single_active_residential():
    accounts = [{
        "is_active": True,
        "is_commercial": False,
        "has_leak_waiver": False,
        "usage_blocks": [30],
    }]
    result = calculate_water_bill(accounts, 10.0)
    assert result == {"total_billed": 55.0, "status": "NORMAL"}


# 2. Invalid accounts input
def test_invalid_accounts():
    with pytest.raises(ValueError):
        calculate_water_bill("invalid", 10.0)


# 3. Negative base fee
def test_negative_base_fee():
    with pytest.raises(ValueError):
        calculate_water_bill([], -1.0)


# 4. Inactive account
def test_inactive_account():
    result = calculate_water_bill(
        [{"is_active": False, "usage_blocks": [30]}], 10.0
    )
    assert result["total_billed"] == 0.0
    assert result["status"] == "NO_ACTIVITY"


# 5. Empty accounts
def test_empty_accounts():
    result = calculate_water_bill([], 10.0)
    assert result["status"] == "NO_ACTIVITY"


# 6. Missing optional fields
def test_missing_optional_fields():
    result = calculate_water_bill([{"is_active": True}], 10.0)
    assert result["total_billed"] == 10.0


# 7. Zero and negative usage
def test_nonpositive_usage():
    result = calculate_water_bill(
        [{"is_active": True, "usage_blocks": [0, -5]}], 10.0
    )
    assert result["total_billed"] == 10.0


# 8. Low usage
def test_low_usage():
    result = calculate_water_bill(
        [{"is_active": True, "usage_blocks": [20, 50]}], 10.0
    )
    assert result["total_billed"] == 115.0


# 9. Medium usage
def test_medium_usage():
    result = calculate_water_bill(
        [{"is_active": True, "usage_blocks": [75]}], 10.0
    )
    assert result["total_billed"] == 197.5


# 10. Commercial usage greater than 100
def test_usage_over_100_commercial():
    result = calculate_water_bill(
        [{"is_active": True, "is_commercial": True,
          "usage_blocks": [120]}], 10.0
    )
    assert result["total_billed"] == 430.0


# 11. Residential usage greater than 100
def test_usage_over_100_residential():
    result = calculate_water_bill(
        [{"is_active": True, "is_commercial": False,
          "usage_blocks": [120, 20]}], 10.0
    )
    assert result["total_billed"] == 550.0


# 12. Commercial high usage continues to the next block
def test_commercial_high_usage_continues():
    result = calculate_water_bill(
        [{"is_active": True, "is_commercial": True,
          "usage_blocks": [120, 20]}], 10.0
    )
    assert result["total_billed"] == 460.0


# 13. Leak waiver applied when total exceeds 200
def test_waiver_applied():
    result = calculate_water_bill(
        [{"is_active": True, "has_leak_waiver": True,
          "usage_blocks": [120]}], 10.0
    )
    assert result["total_billed"] == 500.0


# 14. Leak waiver not applied when total equals 200
def test_waiver_not_applied_at_200():
    result = calculate_water_bill(
        [{"is_active": True, "has_leak_waiver": True,
          "usage_blocks": [50]}], 125.0
    )
    assert result["total_billed"] == 200.0


# 15. No leak waiver
def test_waiver_not_requested():
    result = calculate_water_bill(
        [{"is_active": True, "has_leak_waiver": False,
          "usage_blocks": [120]}], 10.0
    )
    assert result["total_billed"] == 550.0


# 16. Exactly five flags
def test_exactly_five_flags():
    result = calculate_water_bill(
        [{"is_active": True, "usage_blocks": [0, 0, 0, 0, 0]}], 10.0
    )
    assert result["status"] == "NORMAL"


# 17. More than five flags
def test_more_than_five_flags():
    result = calculate_water_bill(
        [{"is_active": True, "usage_blocks": [0, 0, 0, 0, 0, 0]}], 10.0
    )
    assert result["status"] == "EXCESSIVE_FLAGS"


# 18. Excessive flags take priority over no activity
def test_excessive_flags_priority():
    result = calculate_water_bill(
        [{"is_active": True, "usage_blocks": [0, 0, 0, 0, 0, 0]}], 0.0
    )
    assert result["status"] == "EXCESSIVE_FLAGS"


# 19. No meter data
def test_no_meter_data():
    assert check_meter_tampering([]) == "NO_DATA"


# 20. Clear meter readings
def test_clear_meter_readings():
    assert check_meter_tampering([[10, 20, 15], [5, 8, 12]]) == "CLEAR"


# 21. One negative reading
def test_one_negative_reading():
    assert check_meter_tampering([[10, -2, 5]]) == "CLEAR"


# 22. Two consecutive negative readings
def test_two_consecutive_negative_readings():
    assert check_meter_tampering([[10, -2, -3]]) == "TAMPER_SUSPECTED"


# 23. Negative counter resets after a nonnegative reading
def test_negative_counter_resets():
    assert check_meter_tampering([[-1, 10, -2]]) == "CLEAR"


# 24. Tampering in the second meter
def test_tampering_in_second_meter():
    assert check_meter_tampering([[10, -1], [5, -2, -3]]) == "TAMPER_SUSPECTED"


# 25. Empty meter row
def test_empty_meter_row():
    assert check_meter_tampering([[]]) == "CLEAR"
