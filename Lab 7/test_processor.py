
from hypothesis import given, strategies as st, example
from processor import sanitize_meter_id, parse_consumption_readings, format_billing_summary


# Test 1: Sanitize Meter ID
@example(None)
@given(st.text() | st.none())
def test_sanitize_meter_id_no_crash(s):
    try:
        sanitize_meter_id(s)
    except Exception as e:
        assert False, f"sanitize_meter_id crashed with: {e}"


# Test 2: Parse Consumption Readings
@example(None)
@example("1,,3")
@given(st.text() | st.none())
def test_parse_consumption_readings_safe(s):
    try:
        parse_consumption_readings(s)
    except Exception as e:
        assert False, f"parse_consumption_readings crashed with: {e}"


# Test 3: Format Billing Summary
@example(None)
@example("Navya")
@example("Navya:abc:Zone1")
@given(st.text() | st.none())
def test_format_billing_summary_safe(s):
    try:
        format_billing_summary(s)
    except Exception as e:
        assert False, f"format_billing_summary crashed with: {e}"
