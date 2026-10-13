"""The ``Weekday`` enum and the argument checks every query shares."""

from __future__ import annotations

from datetime import MAXYEAR, MINYEAR, date
from enum import IntEnum

_CODES = ("MO", "TU", "WE", "TH", "FR", "SA", "SU")


class Weekday(IntEnum):
    """A day of the week numbered like ``date.weekday()``: Monday is 0, Sunday is 6.

    Members are plain ints, so they work anywhere a ``date.weekday()`` value does.
    """

    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6

    def __repr__(self) -> str:
        return f"Weekday.{self.name}"

    @property
    def iso(self) -> int:
        """ISO 8601 number, as ``date.isoweekday()``: Monday is 1, Sunday is 7."""
        return self.value + 1

    @property
    def code(self) -> str:
        """The two-letter RFC 5545 code, such as ``MO``."""
        return _CODES[self.value]

    @classmethod
    def from_iso(cls, number: int) -> Weekday:
        """The weekday with ISO number ``number`` (1 is Monday, 7 is Sunday)."""
        if not _is_int(number) or not 1 <= number <= 7:
            raise ValueError(f"ISO weekday must be an int in 1..7, got {number!r}")
        return cls(number - 1)

    @classmethod
    def parse(cls, text: str) -> Weekday:
        """Read a weekday from ``MO``, ``Mon`` or ``Monday``, in any letter case."""
        if not isinstance(text, str):
            raise TypeError(f"weekday name must be a str, got {type(text).__name__}")
        found = _NAMES.get(text.upper()) if text.isascii() else None
        if found is None:
            raise ValueError(f"unknown weekday name {text!r}")
        return found


_NAMES: dict[str, Weekday] = {}
for _day in Weekday:
    _NAMES[_day.code] = _day
    _NAMES[_day.name[:3]] = _day
    _NAMES[_day.name] = _day


def _is_int(value: object) -> bool:
    # bool is an int subclass; True as a month or weekday is a bug, never intent.
    return isinstance(value, int) and not isinstance(value, bool)


def _int_in(name: str, value: object, low: int, high: int) -> int:
    if not _is_int(value):
        raise TypeError(f"{name} must be an int, got {type(value).__name__}")
    assert isinstance(value, int)
    if not low <= value <= high:
        raise ValueError(f"{name} must be in {low}..{high}, got {value}")
    return value


def check_year(year: object) -> int:
    return _int_in("year", year, MINYEAR, MAXYEAR)


def check_month(month: object) -> int:
    return _int_in("month", month, 1, 12)


def check_weekday(weekday: object) -> Weekday:
    return Weekday(_int_in("weekday", weekday, 0, 6))


def check_date(value: object) -> date:
    if not isinstance(value, date):
        raise TypeError(f"expected a datetime.date, got {type(value).__name__}")
    return value
