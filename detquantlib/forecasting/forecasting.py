from datetime import datetime
import numpy as np
import pandas as pd


def forecast_knife_strategy(
    dates: list[datetime] | list[pd.Timestamp] | pd.DatetimeIndex,
    values: list | np.ndarray
):
    t1 = datetime.now()
    print(t1)

    # Make sure input dates are stored as pd.DatetimeIndex and values as np.array
    dates = pd.DatetimeIndex(dates)
    values = np.array(values)

    # Get times
    hours = dates.hour
    minutes = dates.minute
    seconds = dates.second

    # Get weekday types (1 = Mon-Fri, 2 = Sat, 3 = Sun)
    weekdays = dates.weekday
    day_types = np.zeros_like(weekdays)
    day_types[weekdays < 5] = 1
    day_types[weekdays == 5] = 2
    day_types[weekdays == 6] = 3

    fc_values = np.zeros_like(values)
    pairs = np.column_stack([hours, minutes, seconds, day_types])
    for hh, mm, ss, dt in np.unique(pairs, axis=0):
        idx = (hours == hh) & (minutes == mm) & (seconds == ss) & (day_types == dt)
        i_values = values[idx]
        fc_values[idx] = np.insert(i_values[:-1], 0, i_values[0])

    t2 = datetime.now()
    print(t2)
    print(t2 - t1)
    return fc_values


def forecast_knife_strategy1(
    dates: list[datetime] | list[pd.Timestamp] | pd.DatetimeIndex,
    values: list | np.ndarray
):
    t1 = datetime.now()
    print(t1)

    # Make sure input dates are stored as pd.DatetimeIndex and values as np.array
    dates = pd.DatetimeIndex(dates)
    values = np.array(values)

    # Get times
    seconds_since_midnight = dates.hour * 3600 + dates.minute * 60 + dates.second

    # hours = dates.hour
    # minutes = dates.minute
    # times = dates.time

    # Get weekday types (1 = Mon-Fri, 2 = Sat, 3 = Sun)
    weekdays = dates.weekday
    day_types = np.zeros_like(weekdays)
    day_types[weekdays < 5] = 1
    day_types[weekdays == 5] = 2
    day_types[weekdays == 6] = 3

    fc_values = np.zeros_like(values)
    pairs = np.column_stack([seconds_since_midnight, day_types])
    for sec, dt in np.unique(pairs, axis=0):
        idx = (seconds_since_midnight == sec) & (day_types == dt)
        i_values = values[idx]
        fc_values[idx] = np.insert(i_values[:-1], 0, i_values[0])

    t2 = datetime.now()
    print(t2)
    print(t2 - t1)
    return fc_values


def forecast_knife_strategy2(
    dates: list[datetime] | list[pd.Timestamp] | pd.DatetimeIndex,
    values: list | np.ndarray
):
    t1 = datetime.now()
    print(t1)

    times = dates.time
    weekdays = dates.weekday

    fc_values = np.zeros_like(values)
    for count, d in enumerate(dates):
        if weekdays[count] < 5:  # Weekday (Mon-Fri)
            idx = (dates < d) & (weekdays < 5) & (times == times[count])
        elif weekdays[count] == 5:  # Saturday
            idx = (dates < d) & (weekdays == 5) & (times == times[count])
        else:  # Sunday
            idx = (dates < d) & (weekdays == 6) & (times == times[count])

        prev_values = values[idx]
        if len(prev_values) > 0:
            fc_values[count] = prev_values[-1]
        else:
            fc_values[count] = values[count]

    t2 = datetime.now()
    print(t2)
    print(t2 - t1)
    return fc_values
