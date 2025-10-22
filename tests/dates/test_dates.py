"""
Important notes:
- Pytest requires test modules to follow the naming convention "test_*.py"
- Pytest requires test functions to follow the naming convention "test_*()"
"""

# Python built-in packages
from datetime import datetime

# Internal modules
from detquantlib.dates import calc_months_diff, count_delivery_periods, datetime_to_month_code


def test_datetime_to_month_code():
    res = datetime_to_month_code(datetime(2025, 10, 22))
    assert res == 1510


def test_count_delivery_periods_day_freq_day():
    freq = "D"
    start_date = datetime(2025, 10, 1, 15, 0, 0)
    end_date = datetime(2027, 6, 1)

    res = count_delivery_periods(start_date, end_date, freq)
    assert res == 608

    res = count_delivery_periods(start_date, end_date, freq, True)
    assert res == 607

    res = count_delivery_periods(start_date, end_date, freq, timezone="Europe/Amsterdam")
    assert res == 608


def test_count_delivery_periods_day_freq_day_leap_year():
    freq = "D"
    start_date = datetime(2024, 1, 1, 15, 0, 0)
    end_date = datetime(2024, 5, 1)

    res = count_delivery_periods(start_date, end_date, freq)
    assert res == 121

    res = count_delivery_periods(start_date, end_date, freq, True)
    assert res == 120

    res = count_delivery_periods(start_date, end_date, freq, timezone="Europe/Amsterdam")
    assert res == 121


def test_count_delivery_periods_day_freq_15min():
    freq = "15min"
    start_date = datetime(2025, 6, 1, 15, 10, 0)
    end_date = datetime(2025, 9, 1)

    res = count_delivery_periods(start_date, end_date, freq)
    assert res == 8772

    res = count_delivery_periods(start_date, end_date, freq, True)
    assert res == 8771


def test_count_delivery_periods_day_freq_15min_dst_mar():
    freq = "15min"
    start_date = datetime(2025, 2, 1, 15, 10, 0)
    end_date = datetime(2025, 4, 1)

    res = count_delivery_periods(start_date, end_date, freq)
    assert res == 5604

    res = count_delivery_periods(start_date, end_date, freq, timezone="Europe/Amsterdam")
    assert res == 5600

    res = count_delivery_periods(start_date, end_date, freq, True, timezone="Europe/Amsterdam")
    assert res == 5599


def test_count_delivery_periods_day_freq_15min_dst_oct():
    freq = "15min"
    start_date = datetime(2025, 10, 1, 15, 10, 0)
    end_date = datetime(2026, 1, 1)

    res = count_delivery_periods(start_date, end_date, freq)
    assert res == 8772

    res = count_delivery_periods(start_date, end_date, freq, timezone="Europe/Amsterdam")
    assert res == 8776

    res = count_delivery_periods(start_date, end_date, freq, True, timezone="Europe/Amsterdam")
    assert res == 8775


def test_calc_months_diff_month():
    start_date = datetime(2025, 4, 1)
    end_date = datetime(2026, 9, 1)
    res = calc_months_diff(start_date, end_date, "month")
    assert res == 17

    start_date = datetime(2025, 4, 1)
    end_date = datetime(2026, 9, 30)
    res = calc_months_diff(start_date, end_date, "month")
    assert res == 17

    start_date = datetime(2025, 4, 30)
    end_date = datetime(2026, 9, 30)
    res = calc_months_diff(start_date, end_date, "month")
    assert res == 17

    start_date = datetime(2025, 4, 10)
    end_date = datetime(2026, 9, 20)
    res = calc_months_diff(start_date, end_date, "month")
    assert res == 17

    start_date = datetime(2025, 4, 20)
    end_date = datetime(2026, 9, 10)
    res = calc_months_diff(start_date, end_date, "month")
    assert res == 17


def test_calc_months_diff_time():
    start_date = datetime(2025, 4, 1)
    end_date = datetime(2026, 9, 1)
    res = calc_months_diff(start_date, end_date, "time")
    assert res == 17

    start_date = datetime(2025, 4, 1)
    end_date = datetime(2026, 9, 30)
    res = calc_months_diff(start_date, end_date, "time")
    assert res == 17

    start_date = datetime(2025, 4, 30)
    end_date = datetime(2026, 9, 30)
    res = calc_months_diff(start_date, end_date, "time")
    assert res == 17

    start_date = datetime(2025, 4, 10)
    end_date = datetime(2026, 9, 20)
    res = calc_months_diff(start_date, end_date, "time")
    assert res == 17

    start_date = datetime(2025, 4, 20)
    end_date = datetime(2026, 9, 10)
    res = calc_months_diff(start_date, end_date, "time")
    assert res == 16

    start_date = datetime(2025, 4, 14)
    end_date = datetime(2026, 9, 15)
    res = calc_months_diff(start_date, end_date, "time")
    assert res == 17

    start_date = datetime(2025, 4, 15)
    end_date = datetime(2026, 9, 15)
    res = calc_months_diff(start_date, end_date, "time")
    assert res == 17

    start_date = datetime(2025, 4, 15)
    end_date = datetime(2026, 9, 14)
    res = calc_months_diff(start_date, end_date, "time")
    assert res == 16


def test_calc_months_diff_full_months_only():
    start_date = datetime(2025, 4, 1)
    end_date = datetime(2026, 9, 1)
    res = calc_months_diff(start_date, end_date, "full_months_only")
    assert res == 17

    start_date = datetime(2025, 4, 1)
    end_date = datetime(2026, 9, 30)
    res = calc_months_diff(start_date, end_date, "full_months_only")
    assert res == 17

    start_date = datetime(2025, 4, 30)
    end_date = datetime(2026, 9, 30)
    res = calc_months_diff(start_date, end_date, "full_months_only")
    assert res == 16

    start_date = datetime(2025, 4, 10)
    end_date = datetime(2026, 9, 20)
    res = calc_months_diff(start_date, end_date, "full_months_only")
    assert res == 16

    start_date = datetime(2025, 4, 20)
    end_date = datetime(2026, 9, 10)
    res = calc_months_diff(start_date, end_date, "full_months_only")
    assert res == 16
