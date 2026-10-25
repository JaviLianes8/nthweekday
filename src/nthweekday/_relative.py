"""Questions about a given date: its ordinal, its week, the nearest weekday."""

from __future__ import annotations

import calendar
from datetime import date, timedelta
from typing import SupportsIndex

from ._month import NoSuchDayError
from ._weekday import Weekday, _is_bool, check_date, check_weekday


def _flag(name: str, value: object) -> bool:
    # Read by truth value, from_end="no" would count from the end; refuse it as the integer
    # arguments refuse True. numpy's bool scalar counts as a bool here too.
    if not _is_bool(value):
        raise TypeError(f"{name} must be a bool, got {type(value).__name__}")
    return bool(value)


def ordinal_of(d: date, *, from_end: bool = False) -> int:
    """Which occurrence of its weekday ``d`` is within its month.

    Counts 1..5 from the start, or -1..-5 from the end with ``from_end=True``, so that
    ``nth_weekday(d.year, d.month, d.weekday(), ordinal_of(d)) == d``.

    >>> from datetime import date
    >>> ordinal_of(date(2026, 11, 26))
    4
    >>> ordinal_of(date(2026, 11, 26), from_end=True)
    -1
    """
    d, from_end = check_date(d), _flag("from_end", from_end)
    if from_end:
        return -((calendar.monthrange(d.year, d.month)[1] - d.day) // 7 + 1)
    return (d.day - 1) // 7 + 1


def week_of_month(d: date, first_weekday: SupportsIndex = Weekday.MONDAY) -> int:
    """Which week of its month ``d`` falls in, counting from 1.

    Week 1 runs from the first of the month to the day before the first
    ``first_weekday`` after it, matching the rows of ``calendar.Calendar(first_weekday)``.
    Weeks start on Monday unless told otherwise.

    >>> from datetime import date
    >>> from nthweekday import SUNDAY
    >>> week_of_month(date(2026, 11, 2))
    2
    >>> week_of_month(date(2026, 11, 2), SUNDAY)
    1
    """
    d, start = check_date(d), check_weekday(first_weekday)
    lead = (date(d.year, d.month, 1).weekday() - start) % 7
    return (lead + d.day - 1) // 7 + 1


def _step(d: date, weekday: SupportsIndex, strict: bool, sign: int) -> date:
    d, day, strict = check_date(d), check_weekday(weekday), _flag("strict", strict)
    gap = sign * (day - d.weekday()) % 7
    if strict and gap == 0:
        gap = 7
    base = date(d.year, d.month, d.day)
    try:
        return base + timedelta(days=sign * gap)
    except OverflowError:
        side = "after" if sign > 0 else "before"
        name = day.name.title()
        raise NoSuchDayError(f"no {name} {side} {base} within years 1..9999") from None


def next_weekday(d: date, weekday: SupportsIndex, *, strict: bool = False) -> date:
    """The first ``weekday`` on or after ``d``, or strictly after it with ``strict=True``.

    Always returns a ``date``, also for a ``datetime``. Raises ``NoSuchDayError`` when
    the answer would fall after the year 9999.

    >>> from datetime import date
    >>> from nthweekday import MONDAY
    >>> next_weekday(date(2026, 10, 12), MONDAY)
    datetime.date(2026, 10, 12)
    >>> next_weekday(date(2026, 10, 12), MONDAY, strict=True)
    datetime.date(2026, 10, 19)
    """
    return _step(d, weekday, strict, 1)


def previous_weekday(d: date, weekday: SupportsIndex, *, strict: bool = False) -> date:
    """The last ``weekday`` on or before ``d``, or strictly before it with ``strict=True``.

    Always returns a ``date``, also for a ``datetime``. Raises ``NoSuchDayError`` when
    the answer would fall before the year 1.

    >>> from datetime import date
    >>> from nthweekday import FRIDAY
    >>> previous_weekday(date(2026, 10, 12), FRIDAY)
    datetime.date(2026, 10, 9)
    """
    return _step(d, weekday, strict, -1)
