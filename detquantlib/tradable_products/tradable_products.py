# Python built-in packages
from datetime import datetime
from typing import Literal

# Third-party packages
import pandas as pd
from dateutil.relativedelta import *
from detquantlib.dates.dates import calc_months_diff


def convert_delivery_start_date_to_maturity(
    trading_date: datetime,
    delivery_start_date: datetime,
    product: Literal["month", "quarter", "year"],
) -> int:
    """
    Calculates the number of maturities between the input trading date and the input delivery
    date, based on the input product type.

    Args:
        trading_date: Trading date
        delivery_start_date: Delivery start date
        product: Product type (e.g. "month", "quarter", "year")

    Returns:
        Product maturity

    Raises:
        ValueError: Raises an error when the delivery start date is older than the trading date
        ValueError: Raises an error when the input product type is not recognized
    """
    # Make input product string lower case only
    product = product.lower()

    # Validate input dates
    if delivery_start_date < trading_date:
        raise ValueError(
            "Input argument 'delivery_start_date' cannot be smaller than input argument "
            "'trading_date'."
        )

    if product == "month":
        maturity = calc_months_diff(
            start_date=trading_date,
            end_date=delivery_start_date,
            diff_method="month",
        )

    elif product == "quarter":
        quarter = pd.Timestamp(trading_date).quarter
        year_start_date = datetime(trading_date.year, 1, 1)
        trading_quarter_start_date = year_start_date + relativedelta(months=((quarter - 1) * 3))

        quarter = pd.Timestamp(delivery_start_date).quarter
        year_start_date = datetime(delivery_start_date.year, 1, 1)
        delivery_quarter_start_date = year_start_date + relativedelta(months=((quarter - 1) * 3))

        months_diff = calc_months_diff(
            start_date=trading_quarter_start_date,
            end_date=delivery_quarter_start_date,
            diff_method="month",
        )
        maturity = months_diff / 3

    elif product == "year":
        maturity = delivery_start_date.year - trading_date.year

    else:
        raise ValueError("Invalid input product name.")

    return maturity


def convert_maturity_to_delivery_start_date(
    trading_date: datetime,
    maturity: int,
    product: Literal["month", "quarter", "year"],
) -> datetime:
    """
    Calculates the delivery start date of the input product, based on the input trading date
    and input maturity.

    Args:
        trading_date: Trading date
        maturity: Product maturity
        product: Product type (e.g. "month", "quarter", "year")

    Returns:
        Delivery start date

    Raises:
        ValueError: Raises an error when the input product type is not recognized
    """

    # Make input product string lower case only
    product = product.lower()

    if product == "month":
        month_start_date = datetime(trading_date.year, trading_date.month, 1)
        delivery_start_date = month_start_date + relativedelta(months=maturity)

    elif product == "quarter":
        quarter = pd.Timestamp(trading_date).quarter
        year_start_date = datetime(trading_date.year, 1, 1)
        quarter_start_date = year_start_date + relativedelta(months=((quarter - 1) * 3))
        delivery_start_date = quarter_start_date + relativedelta(months=(maturity * 3))

    elif product == "year":
        year_start_date = datetime(trading_date.year, 1, 1)
        delivery_start_date = year_start_date + relativedelta(years=maturity)

    else:
        raise ValueError("Invalid input product name.")

    return delivery_start_date
