"""The ``Weekday`` enum and the argument checks every query shares."""

from __future__ import annotations

import inspect
import operator
from datetime import MAXYEAR, MINYEAR, date
from enum import EnumMeta, IntEnum
from typing import TypeVar

_CODES = ("MO", "TU", "WE", "TH", "FR", "SA", "SU")
# Error messages quote at most this many characters of what the caller passed.
_QUOTE_LIMIT = 40
_E = TypeVar("_E")
_ONE_VALUE = inspect.Signature(
    [inspect.Parameter("value", inspect.Parameter.POSITIONAL_OR_KEYWORD)]
)


class _CheckedEnumType(EnumMeta):
    # Typed through the class it is called on, so a checker that reads this signature
    # (pyright does, mypy has its own enum rule) sees Weekday(n) return a Weekday.
    def __call__(cls: type[_E], value: object, *args: object, **kwargs: object) -> _E:
        # A lookup by value matches True and 4.0 too, as they equal 1 and 4; check it first
        # so that Weekday(x) refuses what every function refuses. Extra arguments belong to
        # the functional API, which cannot extend an enum with members; a keyword alone
        # (module=, qualname=) would turn the call back into an unchecked lookup.
        if args or kwargs:
            raise TypeError("Weekday() takes one argument, the weekday number")
        day: _E = super().__call__(_int_in("weekday", value, 0, 6))  # type: ignore[misc]
        return day

    @property
    def __signature__(cls) -> inspect.Signature:
        # help() and inspect.signature() showed this metaclass before 3.12 and the enum
        # functional API after; both hide the one-argument call.
        return _ONE_VALUE


class Weekday(IntEnum, metaclass=_CheckedEnumType):
    """A day of the week numbered like ``date.weekday()``: Monday is 0, Sunday is 6.

    Members are plain ints, so they work anywhere a ``date.weekday()`` value does.
    ``Weekday(n)`` checks ``n`` as every function does. ``str()`` and ``format()``
    without a spec give the name; ``format()`` with a spec formats the number.

    >>> Weekday.FRIDAY == 4
    True
    >>> Weekday(6)
    Weekday.SUNDAY
    >>> str(Weekday.MONDAY)
    'MONDAY'
    >>> f"{Weekday.FRIDAY} is day {Weekday.FRIDAY:02d}"
    'FRIDAY is day 04'
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

    def __str__(self) -> str:
        # IntEnum changed str() to the number in 3.11; pin one answer on every version.
        return self.name

    def __format__(self, spec: str) -> str:
        # Before 3.11 a spec formatted the name, or failed for "d"; pin one rule everywhere.
        return self.name if not spec else int.__format__(self.value, spec)

    @property
    def iso(self) -> int:
        """ISO 8601 number, as ``date.isoweekday()``: Monday is 1, Sunday is 7.

        >>> Weekday.SUNDAY.iso
        7
        """
        return self.value + 1

    @property
    def code(self) -> str:
        """The two-letter RFC 5545 code.

        >>> Weekday.THURSDAY.code
        'TH'
        """
        return _CODES[self.value]

    @classmethod
    def from_iso(cls, number: int) -> Weekday:
        """The weekday with ISO number ``number`` (1 is Monday, 7 is Sunday).

        >>> Weekday.from_iso(1)
        Weekday.MONDAY
        """
        return cls(_int_in("ISO weekday", number, 1, 7) - 1)

    @classmethod
    def parse(cls, text: str) -> Weekday:
        """Read a weekday from ``MO``, ``Mon`` or ``Monday``, in any letter case.

        Raises ``ValueError`` for any other text and ``TypeError`` for a non-string.

        >>> Weekday.parse("fri")
        Weekday.FRIDAY
        >>> Weekday.parse("SU")
        Weekday.SUNDAY
        """
        if not isinstance(text, str):
            raise TypeError(f"weekday name must be a str, got {type(text).__name__}")
        text = str.__str__(text)  # a str subclass is read as its plain text
        found = _NAMES.get(text.upper()) if text.isascii() else None
        if found is None:
            raise ValueError(f"unknown weekday name {quote(text)}")
        return found


_NAMES: dict[str, Weekday] = {}
for _day in Weekday:
    _NAMES[_day.code] = _day
    _NAMES[_day.name[:3]] = _day
    _NAMES[_day.name] = _day


def quote(text: str) -> str:
    """``repr(text)``, cut to a bounded length so a huge argument never floods a message."""
    text = str.__str__(text)  # never a subclass's own __repr__ or __len__
    shown = len(text)
    # Escaped characters make a repr up to ten times longer than the text it shows.
    while shown > _QUOTE_LIMIT or len(repr(text[:shown])) > 2 * _QUOTE_LIMIT + 2:
        shown = min(shown, _QUOTE_LIMIT + 1) - 1
    if shown == len(text):
        return repr(text)
    return f"{text[:shown]!r}... ({len(text)} characters)"


def _shown(number: int) -> str:
    # str() of a huge int is slow and, since 3.11, refused past 4300 digits.
    if abs(number) < 10**18:
        return str(number)
    return f"an integer of {number.bit_length()} bits"


def _is_bool(value: object) -> bool:
    # numpy's bool scalar (bool_ before 2.0, bool after) is not a bool subclass, and before
    # numpy 2.0 it has __index__, so it is known by its type.
    kind = type(value)
    return isinstance(value, bool) or (
        kind.__module__ == "numpy" and kind.__name__ in ("bool_", "bool")
    )


def _as_int(name: str, value: object) -> int:
    # bool is an int subclass; True as a month or weekday is a bug, never intent. Other
    # integer types (numpy and the like) are welcome through __index__; floats are not.
    if not _is_bool(value):
        try:
            return operator.index(value)  # type: ignore[arg-type]
        except TypeError:
            pass
    raise TypeError(f"{name} must be an int, got {type(value).__name__}")


def _int_in(name: str, value: object, low: int, high: int, *, nonzero: bool = False) -> int:
    number = _as_int(name, value)
    if not low <= number <= high or (nonzero and number == 0):
        span = f"1..{high} or -{high}..-1" if nonzero else f"{low}..{high}"
        raise ValueError(f"{name} must be in {span}, got {_shown(number)}")
    return number


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
