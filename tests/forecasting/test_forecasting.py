"""
Important notes:
- Pytest requires test modules to follow the naming convention "test_*.py"
- Pytest requires test functions to follow the naming convention "test_*()"
"""

# Python built-in packages
from pathlib import Path

# Internal modules
from detquantlib.forecasting import *

FOLDER_DIR = Path(__file__).parent
DATA_DIR = FOLDER_DIR.joinpath("_Data")


def test_forecast_knife_strategy_timezone_naive():
    # Load mock forecast data, with timezone-naive dates
    df = pd.read_csv(DATA_DIR.joinpath("forecast_knife_strategy_in.csv"))
    dates = pd.DatetimeIndex(pd.to_datetime(df["date"]))
    values = df["injection"].values

    # Load expected output
    expected = np.load(DATA_DIR.joinpath("forecast_knife_strategy_out.npy"))

    # Call function
    actual = forecast_knife_strategy(dates, values)

    # Assert
    np.testing.assert_array_equal(actual, expected)


def test_forecast_knife_strategy_timezone_aware():
    # Load mock forecast data, with timezone-aware dates
    df = pd.read_csv(DATA_DIR.joinpath("forecast_knife_strategy_in.csv"))
    dates = pd.DatetimeIndex(
        data=pd.to_datetime(df["date"]), tz="Europe/Amsterdam", ambiguous="infer"
    )
    values = df["injection"].values

    # Load expected output
    expected = np.load(DATA_DIR.joinpath("forecast_knife_strategy_out.npy"))

    # Call function
    actual = forecast_knife_strategy(dates, values)

    # Assert
    np.testing.assert_array_equal(actual, expected)
