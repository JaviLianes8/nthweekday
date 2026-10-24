"""Nth weekday of a month or a year."""

from __future__ import annotations

import calendar
from datetime import date, timedelta

from ._weekday import Weekday, _int_in, check_month, check_weekday, check_year

_ORDINALS = ("first", "second", "third", "fourth", "fifth")


class NoSuchDayError(ValueError):
    """The requested day does not exist, such as a fifth Monday in a month with four.

    A ``ValueError`` subclass, so code that catches ``ValueError`` keeps working, while
    ``except NoSuchDayError`` tells an absent day apart from a bad argument.

    >>> from nthweekday import MONDAY, nth_weekday
    >>> try:
    ...     nth_weekday(2026, 9, MONDAY, 5)
    ... except NoSuchDayError as error:
    ...     print(error)
    2026-09 has no fifth Monday
    """


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
    """Every date in the month that falls on ``weekday`` (Monday=0), in order.

    >>> from nthweekday import MONDAY
    >>> [d.day for d in weekdays_in_month(2026, 10, MONDAY)]
    [5, 12, 19, 26]
    """
    year, month, day = check_year(year), check_month(month), check_weekday(weekday)
    return [date(year, month, d) for d in _month_days(year, month, day)]


def nth_weekday(year: int, month: int, weekday: int, n: int) -> date:
    """The ``n``-th ``weekday`` of the month (Monday=0).

    ``n`` is 1..5 counting from the start or -1..-5 counting from the end (-1 is the
    last). Raises ``NoSuchDayError`` when the month has no such occurrence, such as a
    fifth Monday in a month with four, ``ValueError`` for an argument out of range and
    ``TypeError`` for one that is not an integer.

    >>> from nthweekday import FRIDAY, THURSDAY
    >>> nth_weekday(2026, 11, THURSDAY, 4)
    datetime.date(2026, 11, 26)
    >>> nth_weekday(2026, 10, FRIDAY, -2)
    datetime.date(2026, 10, 23)
    """
    year, month, day = check_year(year), check_month(month), check_weekday(weekday)
    n = _int_in("n", n, -5, 5, nonzero=True)
    where = f"{year:04d}-{month:02d}"
    return date(year, month, _pick(_month_days(year, month, day), n, where, day))


def last_weekday(year: int, month: int, weekday: int) -> date:
    """The last ``weekday`` of the month (Monday=0); every month has one.

    >>> from nthweekday import MONDAY
    >>> last_weekday(2026, 5, MONDAY)
    datetime.date(2026, 5, 25)
    """
    return nth_weekday(year, month, weekday, -1)


def nth_weekday_in_year(year: int, weekday: int, n: int) -> date:
    """The ``n``-th ``weekday`` of the year, as RFC 5545 counts BYDAY in a YEARLY rule.

    ``n`` is 1..53 or -53..-1. Raises ``NoSuchDayError`` for a 53rd occurrence in a
    year that has only 52.

    >>> from nthweekday import MONDAY
    >>> nth_weekday_in_year(1998, MONDAY, 20)
    datetime.date(1998, 5, 18)
    >>> nth_weekday_in_year(2026, MONDAY, -1)
    datetime.date(2026, 12, 28)
    """
    year, day = check_year(year), check_weekday(weekday)
    n = _int_in("n", n, -53, 53, nonzero=True)
    start = date(year, 1, 1)
    length = 366 if calendar.isleap(year) else 365
    offsets = range((day - start.weekday()) % 7, length, 7)
    return start + timedelta(days=_pick(offsets, n, f"{year:04d}", day))
