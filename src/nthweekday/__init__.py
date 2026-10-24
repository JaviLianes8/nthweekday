"""Find the nth weekday of a month (third Thursday, last Friday) and read RFC 5545 BYDAY values."""

from __future__ import annotations

from ._byday import ByDay, byday_dates, parse_byday
from ._month import (
    NoSuchDayError,
    last_weekday,
    nth_weekday,
    nth_weekday_in_year,
    weekdays_in_month,
)
from ._relative import next_weekday, ordinal_of, previous_weekday, week_of_month
from ._weekday import Weekday

MONDAY = Weekday.MONDAY
TUESDAY = Weekday.TUESDAY
WEDNESDAY = Weekday.WEDNESDAY
THURSDAY = Weekday.THURSDAY
FRIDAY = Weekday.FRIDAY
SATURDAY = Weekday.SATURDAY
SUNDAY = Weekday.SUNDAY

__version__ = "1.0.0"

# Public names show and pickle as nthweekday.<name>, so a pickle never depends on the
# private module that defines them, and doctest finds every example from the package.
for _obj in (
    ByDay,
    NoSuchDayError,
    Weekday,
    byday_dates,
    last_weekday,
    next_weekday,
    nth_weekday,
    nth_weekday_in_year,
    ordinal_of,
    parse_byday,
    previous_weekday,
    week_of_month,
    weekdays_in_month,
):
    _obj.__module__ = __name__
    for _member in vars(_obj).values() if isinstance(_obj, type) else ():
        _func = getattr(_member, "__func__", _member)
        if callable(_func) and str(getattr(_func, "__module__", "")).startswith(f"{__name__}._"):
            _func.__module__ = __name__
del _obj, _member, _func

__all__ = [
    "FRIDAY",
    "MONDAY",
    "SATURDAY",
    "SUNDAY",
    "THURSDAY",
    "TUESDAY",
    "WEDNESDAY",
    "ByDay",
    "NoSuchDayError",
    "Weekday",
    "byday_dates",
    "last_weekday",
    "next_weekday",
    "nth_weekday",
    "nth_weekday_in_year",
    "ordinal_of",
    "parse_byday",
    "previous_weekday",
    "week_of_month",
    "weekdays_in_month",
]
