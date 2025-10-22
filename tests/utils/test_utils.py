"""
Important notes:
- Pytest requires test modules to follow the naming convention "test_*.py"
- Pytest requires test functions to follow the naming convention "test_*()"
"""

# Third-party packages
import numpy as np

# Internal modules
from detquantlib.utils import divide_with_nan


def test_divide_with_nan():
    numerator = np.array([10, 0, 10, 10, -10, 0, -0, 0])
    denominator = np.array([10, 10, 0, -0, 0, 0, 0, -0])

    expected = np.array([1, 0, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan])
    res = divide_with_nan(numerator, denominator)
    np.testing.assert_array_equal(res, expected)

    expected = np.array([1, 0, np.nan, np.nan, np.nan, -1, -1, -1])
    res = divide_with_nan(numerator, denominator, nan=-1)
    np.testing.assert_array_equal(res, expected)

    expected = np.array([1, 0, -1, -1, np.nan, np.nan, np.nan, np.nan])
    res = divide_with_nan(numerator, denominator, posinf=-1)
    np.testing.assert_array_equal(res, expected)

    expected = np.array([1, 0, np.nan, np.nan, -1, np.nan, np.nan, np.nan])
    res = divide_with_nan(numerator, denominator, neginf=-1)
    np.testing.assert_array_equal(res, expected)
