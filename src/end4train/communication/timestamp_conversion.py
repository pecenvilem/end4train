from __future__ import annotations

from typing import NamedTuple

import pandas as pd

TimestampTuple = NamedTuple("TimestampTuple", [("second", pd.Series), ("millisecond", pd.Series)])


def combine_timestamp(timestamp_tuple: TimestampTuple) -> pd.Series:
    timestamp_series = pd.to_datetime(timestamp_tuple.second, unit="s")
    return timestamp_series + pd.to_timedelta(timestamp_tuple.millisecond, unit="ms")


def separate_timestamp(timestamp: pd.Series) -> TimestampTuple:
    second = timestamp.astype(int) // 10 ** 9  # underlying np array stores nanoseconds
    millisecond = timestamp.dt.microsecond // 1000
    second.name = "second"
    millisecond.name = "millisecond"
    return TimestampTuple(second, millisecond)


def get_timestamp_as_columns(timestamp: pd.Series) -> pd.DataFrame:
    timestamp_tuple = separate_timestamp(timestamp)
    return pd.DataFrame({"second": timestamp_tuple.second, "millisecond": timestamp_tuple.millisecond})
