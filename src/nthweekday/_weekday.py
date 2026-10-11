"""Nth-weekday-of-a-month queries built on the standard library only."""

from __future__ import annotations

import calendar
from datetime import date

MONDAY = 0
TUESDAY = 1
WEDNESDAY = 2
THURSDAY = 3
FRIDAY = 4
SATURDAY = 5
SUNDAY = 6

_ORDINALS = {1: "first", 2: "second", 3: "third", 4: "fourth", 5: "fifth"}


def _check(year: int, month: int, weekday: int) -> None:
    if not 1 <= month <= 12:
        raise ValueError(f"month must be in 1..12, got {month}")
    if not MONDAY <= weekday <= SUNDAY:
        raise ValueError(f"weekday must be in 0..6 (Monday=0), got {weekday}")
    date(year, 1, 1)  # reject a year outside the supported range early


def weekdays_in_month(year: int, month: int, weekday: int) -> list[date]:
    """Every date in the month that falls on ``weekday`` (Monday=0), in order."""
    _check(year, month, weekday)
    _, days = calendar.monthrange(year, month)
    return [d for day in range(1, days + 1) if (d := date(year, month, day)).weekday() == weekday]


def nth_weekday(year: int, month: int, weekday: int, n: int) -> date:
    """The ``n``-th ``weekday`` of the month (Monday=0).

    ``n`` is 1..5 counting from the start, or -1 for the last. Raises
    ``ValueError`` when the requested occurrence does not exist, such as a fifth
    one in a month that only has four.
    """
    occurrences = weekdays_in_month(year, month, weekday)
    if n == -1:
        return occurrences[-1]
    if not 1 <= n <= 5:
        raise ValueError(f"n must be in 1..5 or -1, got {n}")
    if n > len(occurrences):
        name = calendar.day_name[weekday]
        raise ValueError(f"{year}-{month:02d} has no {_ORDINALS[n]} {name}")
    return occurrences[n - 1]


def last_weekday(year: int, month: int, weekday: int) -> date:
    """The last ``weekday`` of the month (Monday=0)."""
    return weekdays_in_month(year, month, weekday)[-1]


def week_of_month(d: date) -> int:
    """Which week of its month ``d`` falls in, counting from 1.

    Weeks start on Monday: week 1 holds the first of the month through the first
    Sunday, matching ``calendar.monthcalendar`` rows.
    """
    first_weekday, _ = calendar.monthrange(d.year, d.month)
    return (first_weekday + d.day - 1) // 7 + 1
