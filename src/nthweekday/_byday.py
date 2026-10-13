"""RFC 5545 BYDAY values: ``MO``, ``1MO``, ``-1FR``, and comma lists of them."""

from __future__ import annotations

import re
from calendar import monthrange
from dataclasses import dataclass
from datetime import date, timedelta

from ._month import NoSuchDayError, nth_weekday_in_year
from ._weekday import Weekday, _int_in, check_month, check_weekday, check_year

# weekdaynum = [[plus / minus] ordwk] weekday, ordwk = 1*2DIGIT (1 to 53), RFC 5545 3.3.10.
# Enumerated values are case-insensitive (RFC 5545 section 2), so the code is matched as such.
_WEEKDAYNUM = re.compile(r"(?:([+-]?)([0-9]{1,2}))?(SU|MO|TU|WE|TH|FR|SA)", re.IGNORECASE)


@dataclass(frozen=True)
class ByDay:
    """One BYDAY entry: a weekday, optionally with an ordinal (``-1FR`` is the last Friday).

    ``ordinal`` is ``None`` for every such weekday in the period, or 1..53 / -53..-1.
    ``str()`` gives the canonical RFC 5545 form.
    """

    weekday: Weekday
    ordinal: int | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "weekday", check_weekday(self.weekday))
        if self.ordinal is not None and _int_in("ordinal", self.ordinal, -53, 53) == 0:
            raise ValueError("ordinal must be in 1..53 or -53..-1, got 0")

    def __repr__(self) -> str:
        tail = "" if self.ordinal is None else f", {self.ordinal}"
        return f"ByDay({self.weekday!r}{tail})"

    def __str__(self) -> str:
        return f"{'' if self.ordinal is None else self.ordinal}{self.weekday.code}"


def parse_byday(value: str) -> tuple[ByDay, ...]:
    """Parse a BYDAY value such as ``"1SU,-1SU"`` into ``ByDay`` entries, in order.

    Accepts exactly the RFC 5545 grammar: an optional sign and one or two digits for 1..53,
    then a two-letter code. Raises ``ValueError`` on anything else, including spaces.
    """
    if not isinstance(value, str):
        raise TypeError(f"BYDAY value must be a str, got {type(value).__name__}")
    entries = []
    for item in value.split(","):
        # A non-ASCII letter that case-folds into a code still fails in Weekday.parse.
        match = _WEEKDAYNUM.fullmatch(item)
        if match is None:
            raise ValueError(f"invalid BYDAY entry {item!r} in {value!r}")
        sign, digits, code = match.groups()
        ordinal = None if digits is None else int(sign + digits)
        if ordinal is not None and not 1 <= abs(ordinal) <= 53:
            raise ValueError(f"BYDAY ordinal must be 1..53, got {item!r}")
        entries.append(ByDay(Weekday.parse(code), ordinal))
    return tuple(entries)


def byday_dates(year: int, month: int | None, value: str | ByDay) -> list[date]:
    """The dates a BYDAY value selects in one month, or in a whole year with ``month=None``.

    With a month this is the MONTHLY meaning: ``2MO`` is the second Monday of that month
    and an ordinal past the last occurrence selects nothing. With ``month=None`` it is the
    YEARLY meaning without BYMONTH: ``20MO`` is the twentieth Monday of the year. The
    result is sorted and has no duplicates.
    """
    year = check_year(year)
    if month is not None:
        month = check_month(month)
    entries = (value,) if isinstance(value, ByDay) else parse_byday(value)
    if month is None:
        start, end = date(year, 1, 1), date(year, 12, 31)
    else:
        start, end = date(year, month, 1), date(year, month, monthrange(year, month)[1])
    found: set[date] = set()
    for entry in entries:
        found.update(_select(entry, year, month, start, end))
    return sorted(found)


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
