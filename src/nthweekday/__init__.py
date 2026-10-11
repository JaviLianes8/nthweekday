"""Find the nth weekday of a month and related calendar queries, zero dependencies."""

from __future__ import annotations

from ._weekday import (
    FRIDAY,
    MONDAY,
    SATURDAY,
    SUNDAY,
    THURSDAY,
    TUESDAY,
    WEDNESDAY,
    last_weekday,
    nth_weekday,
    week_of_month,
    weekdays_in_month,
)

__version__ = "0.1.0"

__all__ = [
    "FRIDAY",
    "MONDAY",
    "SATURDAY",
    "SUNDAY",
    "THURSDAY",
    "TUESDAY",
    "WEDNESDAY",
    "last_weekday",
    "nth_weekday",
    "week_of_month",
    "weekdays_in_month",
]
