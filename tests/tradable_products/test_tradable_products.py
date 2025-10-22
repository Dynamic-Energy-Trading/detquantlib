"""
Important notes:
- Pytest requires test modules to follow the naming convention "test_*.py"
- Pytest requires test functions to follow the naming convention "test_*()"
"""

# Python built-in packages
from datetime import datetime

# Internal modules
from detquantlib.tradable_products import convert_delivery_start_date_to_maturity, convert_maturity_to_delivery_start_date


def test_convert_delivery_start_date_to_maturity_year():
    trading_date = datetime(2025, 10, 22)
    delivery_start_date = datetime(2025, 1, 1)
    maturity = 0
    res = convert_delivery_start_date_to_maturity(trading_date, delivery_start_date, "year")
    assert res == maturity

    trading_date = datetime(2025, 10, 22)
    delivery_start_date = datetime(2027, 1, 1)
    maturity = 2
    res = convert_delivery_start_date_to_maturity(trading_date, delivery_start_date, "year")
    assert res == maturity


def test_convert_delivery_start_date_to_maturity_quarter():
    trading_date = datetime(2025, 12, 22)
    delivery_start_date = datetime(2025, 10, 1)
    maturity = 0
    res = convert_delivery_start_date_to_maturity(trading_date, delivery_start_date, "quarter")
    assert res == maturity

    trading_date = datetime(2025, 10, 22)
    delivery_start_date = datetime(2027, 1, 1)
    maturity = 5
    res = convert_delivery_start_date_to_maturity(trading_date, delivery_start_date, "quarter")
    assert res == maturity


def test_convert_delivery_start_date_to_maturity_month():
    trading_date = datetime(2025, 10, 22)
    delivery_start_date = datetime(2025, 10, 1)
    maturity = 0
    res = convert_delivery_start_date_to_maturity(trading_date, delivery_start_date, "month")
    assert res == maturity

    trading_date = datetime(2025, 10, 22)
    delivery_start_date = datetime(2027, 1, 1)
    maturity = 15
    res = convert_delivery_start_date_to_maturity(trading_date, delivery_start_date, "month")
    assert res == maturity


def test_convert_delivery_start_date_to_maturity_week():
    trading_date = datetime(2025, 10, 22)
    delivery_start_date = datetime(2025, 10, 20)
    maturity = 0
    res = convert_delivery_start_date_to_maturity(trading_date, delivery_start_date, "week")
    assert res == maturity

    trading_date = datetime(2025, 10, 22)
    delivery_start_date = datetime(2027, 1, 1)
    maturity = 63
    res = convert_delivery_start_date_to_maturity(trading_date, delivery_start_date, "week")
    assert res == maturity


def test_convert_delivery_start_date_to_maturity_weekend():
    trading_date = datetime(2025, 10, 26)
    delivery_start_date = datetime(2025, 10, 25)
    maturity = 0
    res = convert_delivery_start_date_to_maturity(trading_date, delivery_start_date, "weekend")
    assert res == maturity

    trading_date = datetime(2025, 10, 22)
    delivery_start_date = datetime(2027, 1, 1)
    maturity = 63
    res = convert_delivery_start_date_to_maturity(trading_date, delivery_start_date, "weekend")
    assert res == maturity


def test_convert_delivery_start_date_to_maturity_day():
    trading_date = datetime(2025, 10, 26)
    delivery_start_date = datetime(2025, 10, 26)
    maturity = 0
    res = convert_delivery_start_date_to_maturity(trading_date, delivery_start_date, "day")
    assert res == maturity

    trading_date = datetime(2025, 10, 22)
    delivery_start_date = datetime(2027, 1, 1)
    maturity = 436
    res = convert_delivery_start_date_to_maturity(trading_date, delivery_start_date, "day")
    assert res == maturity


def test_convert_maturity_to_delivery_start_date_year():
    trading_date = datetime(2025, 10, 26)
    delivery_start_date = datetime(2025, 10, 26)
    maturity = 0
    res = convert_maturity_to_delivery_start_date(trading_date, maturity, "year")
    assert res == delivery_start_date

    trading_date = datetime(2025, 10, 22)
    delivery_start_date = datetime(2027, 1, 1)
    maturity = 436
    res = convert_maturity_to_delivery_start_date(trading_date, maturity, "year")
    assert res == delivery_start_date


def test_convert_maturity_to_delivery_start_date_quarter():
    trading_date = datetime(2025, 12, 22)
    delivery_start_date = datetime(2025, 10, 1)
    maturity = 0
    res = convert_maturity_to_delivery_start_date(trading_date, maturity, "quarter")
    assert res == delivery_start_date

    trading_date = datetime(2025, 10, 22)
    delivery_start_date = datetime(2027, 1, 1)
    maturity = 5
    res = convert_maturity_to_delivery_start_date(trading_date, maturity, "quarter")
    assert res == delivery_start_date


def test_convert_maturity_to_delivery_start_date_month():
    trading_date = datetime(2025, 10, 22)
    delivery_start_date = datetime(2025, 10, 1)
    maturity = 0
    res = convert_maturity_to_delivery_start_date(trading_date, maturity, "month")
    assert res == delivery_start_date

    trading_date = datetime(2025, 10, 22)
    delivery_start_date = datetime(2027, 1, 1)
    maturity = 15
    res = convert_maturity_to_delivery_start_date(trading_date, maturity, "month")
    assert res == delivery_start_date
