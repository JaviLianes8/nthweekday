"""Nth weekday of a month or a year, and the reverse question for a date."""

from __future__ import annotations

import calendar
from datetime import date, timedelta

from ._weekday import (
    Weekday,
    _int_in,
    check_date,
    check_month,
    check_weekday,
    check_year,
)

_ORDINALS = ("first", "second", "third", "fourth", "fifth")


class NoSuchDayError(ValueError):
    """The requested occurrence does not exist, such as a fifth Monday in a 4-Monday month."""


def _ordinal_words(n: int) -> str:
    if n > 0:
        if n <= len(_ORDINALS):
            return _ORDINALS[n - 1]
        suffix = "th" if n % 100 in (11, 12, 13) else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
        return f"{n}{suffix}"
    # Only -5 can be absent in a month and only -53 in a year, so -1 needs no "last".
    return f"{_ordinal_words(-n)}-to-last"


def _pick(days: range, n: int, where: str, day: Weekday) -> int:
    try:
        return days[n - 1 if n > 0 else n]
    except IndexError:
        name = day.name.title()
        raise NoSuchDayError(f"{where} has no {_ordinal_words(n)} {name}") from None


def _month_days(year: int, month: int, weekday: Weekday) -> range:
    first = date(year, month, 1).weekday()
    length = calendar.monthrange(year, month)[1]
    return range(1 + (weekday - first) % 7, length + 1, 7)


def weekdays_in_month(year: int, month: int, weekday: int) -> list[date]:
    """Every date in the month that falls on ``weekday`` (Monday=0), in order."""
    year, month, day = check_year(year), check_month(month), check_weekday(weekday)
    return [date(year, month, d) for d in _month_days(year, month, day)]


def nth_weekday(year: int, month: int, weekday: int, n: int) -> date:
    """The ``n``-th ``weekday`` of the month (Monday=0).

    ``n`` is 1..5 counting from the start or -1..-5 counting from the end (-1 is the
    last). Raises ``NoSuchDayError`` when the month has no such occurrence, such as a
    fifth Monday in a month with four.
    """
    year, month, day = check_year(year), check_month(month), check_weekday(weekday)
    if _int_in("n", n, -5, 5) == 0:
        raise ValueError("n must be in 1..5 or -5..-1, got 0")
    where = f"{year:04d}-{month:02d}"
    return date(year, month, _pick(_month_days(year, month, day), n, where, day))


def last_weekday(year: int, month: int, weekday: int) -> date:
    """The last ``weekday`` of the month (Monday=0)."""
    return nth_weekday(year, month, weekday, -1)


def nth_weekday_in_year(year: int, weekday: int, n: int) -> date:
    """The ``n``-th ``weekday`` of the year, as RFC 5545 counts BYDAY in a YEARLY rule.

    ``n`` is 1..53 or -53..-1. Raises ``NoSuchDayError`` for a 53rd occurrence in a
    year that has only 52.
    """
    year, day = check_year(year), check_weekday(weekday)
    if _int_in("n", n, -53, 53) == 0:
        raise ValueError("n must be in 1..53 or -53..-1, got 0")
    start = date(year, 1, 1)
    length = 366 if calendar.isleap(year) else 365
    offsets = range((day - start.weekday()) % 7, length, 7)
    return start + timedelta(days=_pick(offsets, n, f"{year:04d}", day))


def ordinal_of(d: date, *, from_end: bool = False) -> int:
    """Which occurrence of its weekday ``d`` is within its month.

    Counts 1..5 from the start, or -1..-5 from the end with ``from_end=True``, so that
    ``nth_weekday(d.year, d.month, d.weekday(), ordinal_of(d)) == d``.
    """
    d = check_date(d)
    if from_end:
        return -((calendar.monthrange(d.year, d.month)[1] - d.day) // 7 + 1)
    return (d.day - 1) // 7 + 1


def week_of_month(d: date, first_weekday: int = Weekday.MONDAY) -> int:
    """Which week of its month ``d`` falls in, counting from 1.

    Week 1 runs from the first of the month to the day before the first
    ``first_weekday`` after it, matching the rows of ``calendar.Calendar(first_weekday)``.
    Weeks start on Monday unless told otherwise.
    """
    d, start = check_date(d), check_weekday(first_weekday)
    lead = (date(d.year, d.month, 1).weekday() - start) % 7
    return (lead + d.day - 1) // 7 + 1


def _step(d: date, weekday: int, strict: bool, sign: int) -> date:
    d, day = check_date(d), check_weekday(weekday)
    gap = sign * (day - d.weekday()) % 7
    if strict and gap == 0:
        gap = 7
    base = date(d.year, d.month, d.day)
    try:
        return base + timedelta(days=sign * gap)
    except OverflowError:
        side = "after" if sign > 0 else "before"
        raise ValueError(f"no {day.name.title()} {side} {base} within years 1..9999") from None


def next_weekday(d: date, weekday: int, *, strict: bool = False) -> date:
    """The first ``weekday`` on or after ``d``, or strictly after it with ``strict=True``."""
    return _step(d, weekday, strict, 1)


def previous_weekday(d: date, weekday: int, *, strict: bool = False) -> date:
    """The last ``weekday`` on or before ``d``, or strictly before it with ``strict=True``."""
    return _step(d, weekday, strict, -1)
