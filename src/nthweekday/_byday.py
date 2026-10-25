"""RFC 5545 BYDAY values: ``MO``, ``1MO``, ``-1FR``, and comma lists of them."""

from __future__ import annotations

import re
from calendar import monthrange
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from datetime import date, timedelta

from ._month import NoSuchDayError, nth_weekday_in_year
from ._weekday import Weekday, _int_in, check_month, check_weekday, check_year, quote

_VALUE_TYPES = "value must be a BYDAY string, a ByDay or ByDay entries"
# weekdaynum = [[plus / minus] ordwk] weekday, ordwk = 1*2DIGIT (1 to 53), RFC 5545 3.3.10.
# Enumerated values are case-insensitive (RFC 5545 section 2), so the code is matched as such.
_WEEKDAYNUM = re.compile(r"(?:([+-]?)([0-9]{1,2}))?(SU|MO|TU|WE|TH|FR|SA)", re.IGNORECASE)


@dataclass(frozen=True, init=False)
class ByDay:
    """One BYDAY entry: a weekday, optionally with an ordinal (``-1FR`` is the last Friday).

    ``weekday`` is 0..6 or a ``Weekday`` and is stored as a ``Weekday``. ``ordinal`` is
    ``None`` for every such weekday in the period, or 1..53 / -53..-1.
    ``str()`` gives the canonical RFC 5545 form. Frozen and hashable.

    >>> from nthweekday import FRIDAY
    >>> ByDay(FRIDAY, -1)
    ByDay(Weekday.FRIDAY, -1)
    >>> str(ByDay(FRIDAY, -1))
    '-1FR'
    >>> str(ByDay(FRIDAY))
    'FR'
    """

    weekday: Weekday
    ordinal: int | None = None

    def __init__(self, weekday: int, ordinal: int | None = None) -> None:
        # Written out so that an int weekday type-checks while the field stays a Weekday.
        object.__setattr__(self, "weekday", check_weekday(weekday))
        if ordinal is not None:
            ordinal = _int_in("ordinal", ordinal, -53, 53, nonzero=True)
        object.__setattr__(self, "ordinal", ordinal)

    def __repr__(self) -> str:
        tail = "" if self.ordinal is None else f", {self.ordinal}"
        return f"ByDay({self.weekday!r}{tail})"

    def __str__(self) -> str:
        return f"{'' if self.ordinal is None else self.ordinal}{self.weekday.code}"


def parse_byday(value: str) -> tuple[ByDay, ...]:
    """Parse a BYDAY value such as ``"1SU,-1SU"`` into ``ByDay`` entries, in order.

    Accepts exactly the RFC 5545 grammar: an optional sign and one or two digits for 1..53,
    then a two-letter code, in any letter case. Raises ``ValueError`` on anything else,
    including spaces and an empty value, and ``TypeError`` for a non-string.

    >>> parse_byday("1SU,-1SU")
    (ByDay(Weekday.SUNDAY, 1), ByDay(Weekday.SUNDAY, -1))
    >>> parse_byday("+02mo")
    (ByDay(Weekday.MONDAY, 2),)
    """
    if not isinstance(value, str):
        raise TypeError(f"BYDAY value must be a str, got {type(value).__name__}")
    value = str.__str__(value)  # a str subclass is read as its plain text
    entries = []
    for item in value.split(","):
        # IGNORECASE folds some non-ASCII letters into codes (long s matches S).
        match = _WEEKDAYNUM.fullmatch(item) if item.isascii() else None
        if match is None:
            raise ValueError(f"invalid BYDAY entry {quote(item)} in {quote(value)}")
        sign, digits, code = match.groups()
        ordinal = None if digits is None else int(sign + digits)
        if ordinal is not None and not 1 <= abs(ordinal) <= 53:
            raise ValueError(f"BYDAY ordinal must be 1..53, got {quote(item)}")
        entries.append(ByDay(Weekday.parse(code), ordinal))
    return tuple(entries)


def byday_dates(year: int, month: int | None, value: str | ByDay | Iterable[ByDay]) -> list[date]:
    """The dates a BYDAY value selects in one month, or in a whole year with ``month=None``.

    With a month this is the MONTHLY meaning: ``2MO`` is the second Monday of that month
    and an ordinal past the last occurrence selects nothing. With ``month=None`` it is the
    YEARLY meaning without BYMONTH: ``20MO`` is the twentieth Monday of the year.
    ``value`` is a BYDAY string, one ``ByDay`` or several (what ``parse_byday`` returns).
    The result is sorted and has no duplicates. Raises ``ValueError`` for a bad year,
    month or BYDAY string and ``TypeError`` for arguments of the wrong type.

    >>> [d.day for d in byday_dates(2026, 3, "1SU,-1SU")]
    [1, 29]
    >>> byday_dates(2026, 9, "5MO")
    []
    >>> byday_dates(1998, None, "20MO")
    [datetime.date(1998, 5, 18)]
    """
    year = check_year(year)
    if month is not None:
        month = check_month(month)
    if isinstance(value, str):
        entries = parse_byday(value)
    elif isinstance(value, ByDay):
        entries = (value,)
    else:
        try:
            items = iter(value)
        except TypeError:
            raise TypeError(_VALUE_TYPES) from None
        # Read outside the try, so an error of the caller's own iterable comes through
        # unchanged, and checked one by one, so a wrong entry stops the read at once.
        entries = tuple(_checked(items))
    if month is None:
        start, end = date(year, 1, 1), date(year, 12, 31)
    else:
        start, end = date(year, month, 1), date(year, month, monthrange(year, month)[1])
    found: set[date] = set()
    for entry in entries:
        found.update(_select(entry, year, month, start, end))
    return sorted(found)


def _checked(items: Iterator[object]) -> Iterator[ByDay]:
    for entry in items:
        if not isinstance(entry, ByDay):
            raise TypeError(_VALUE_TYPES)
        yield entry


def _select(entry: ByDay, year: int, month: int | None, start: date, end: date) -> list[date]:
    day, n = entry.weekday, entry.ordinal
    first = start + timedelta(days=(day - start.weekday()) % 7)
    every = [first + timedelta(weeks=k) for k in range((end - first).days // 7 + 1)]
    if n is None:
        return every
    if month is None:
        try:
            return [nth_weekday_in_year(year, day, n)]
        except NoSuchDayError:
            return []
    picked = n - 1 if n > 0 else n
    return [every[picked]] if -len(every) <= picked < len(every) else []
