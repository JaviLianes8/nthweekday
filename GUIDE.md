# nthweekday guide

The behaviour of every public name in detail. Each Python block below runs as a test:
every `expression  # -> value` line must hold.

## Weekdays

Weekdays are numbered like `date.weekday()`: Monday is 0 and Sunday is 6. `Weekday` is an
`IntEnum` and `MONDAY` to `SUNDAY` are its members, so a plain int works anywhere a
weekday is asked for, and the members work anywhere an int does.

```python
from datetime import date

from nthweekday import FRIDAY, MONDAY, SUNDAY, THURSDAY, Weekday

FRIDAY == 4  # -> True
date(2026, 10, 23).weekday() == FRIDAY  # -> True
Weekday(6)  # -> Weekday.SUNDAY
str(Weekday.MONDAY)  # -> 'MONDAY'
f"{FRIDAY} is day {FRIDAY:02d}"  # -> 'FRIDAY is day 04'
f"{MONDAY!s:>8}"  # -> '  MONDAY'
Weekday.SUNDAY.iso  # -> 7
Weekday.from_iso(1)  # -> Weekday.MONDAY
Weekday.THURSDAY.code  # -> 'TH'
Weekday.parse("thu")  # -> Weekday.THURSDAY
Weekday.parse("Thursday")  # -> Weekday.THURSDAY
```

`Weekday.parse` reads the two-letter RFC 5545 code, the three-letter English abbreviation
or the full English name, in any letter case, and raises `ValueError` for anything else
(`TypeError` for a non-string). `Weekday(n)` checks `n` as the table below says, so
`Weekday(True)` and `Weekday(4.0)` raise `TypeError` and `Weekday(7)` raises `ValueError`.
It takes exactly one argument: anything more (the enum functional API, or a keyword such
as `module=`) raises `TypeError`.

`str()`, and `format()` without a spec, give the name; `format()` with a spec formats the
number, so `f"{day:02d}"` gives `04`. Both hold on every supported Python version. To pad
the name, convert it first: `f"{day!s:>8}"`.

## Argument checks

Every function checks its arguments before it computes anything:

| Argument | Accepted | Otherwise |
| --- | --- | --- |
| `year` | 1 to 9999, the range of `datetime` | `ValueError` |
| `month` | 1 to 12 | `ValueError` |
| `weekday`, `first_weekday`, `Weekday(n)` | 0 to 6, or a `Weekday` | `ValueError` |
| `n` in a month | 1 to 5 or -5 to -1 | `ValueError` |
| `n` in a year, `ByDay.ordinal` | 1 to 53 or -53 to -1 | `ValueError` |
| a date | `datetime.date` or `datetime.datetime` | `TypeError` |
| `strict`, `from_end` | `True` or `False` | `TypeError` |

Any integer type is accepted through `__index__` (numpy integers included), and the
integer parameters are typed `typing.SupportsIndex`, so such a value type-checks too.
`bool`, `float` and `str` are refused with `TypeError`, since `True` as a month or `2.0`
as an ordinal is a bug rather than intent; numpy's bool scalar counts as a `bool`. The
flags `strict` and `from_end` are not read by truth value: anything but a `bool` (or
numpy's bool scalar), such as `from_end="no"` or `strict=None`, raises `TypeError`. A `str`
subclass is read as its plain text, without calling its own methods. Error messages
quote at most 40 characters of a text argument, never print a huge integer in full, and
never repeat the value of an argument of the wrong type.

## Errors

- `NoSuchDayError` (a `ValueError` subclass): the arguments are valid but the day does
  not exist, such as a fifth Monday in a month with four, a 53rd Friday in a year with
  52, or a next Saturday after 9999-12-31.
- `ValueError`: an argument out of range, or text that is not a valid BYDAY value or
  weekday name.
- `TypeError`: an argument of the wrong type.

```python
from nthweekday import NoSuchDayError, nth_weekday

try:
    nth_weekday(2026, 9, MONDAY, 5)
except NoSuchDayError as error:
    message = str(error)
message  # -> '2026-09 has no fifth Monday'
isinstance(NoSuchDayError("x"), ValueError)  # -> True
```

## The nth weekday of a month

```python
from nthweekday import last_weekday, weekdays_in_month

nth_weekday(2026, 11, THURSDAY, 4)  # -> date(2026, 11, 26)
nth_weekday(2026, 10, FRIDAY, -2)  # -> date(2026, 10, 23)
last_weekday(2026, 5, MONDAY)  # -> date(2026, 5, 25)
[d.day for d in weekdays_in_month(2026, 10, MONDAY)]  # -> [5, 12, 19, 26]
```

`nth_weekday(year, month, weekday, n)` counts from the start for `n` from 1 to 5 and from
the end for `n` from -1 (the last) to -5. Every month has at least four of each weekday,
so only `5` and `-5` can raise `NoSuchDayError`. `last_weekday` is `nth_weekday` with
`n=-1` and never raises it. `weekdays_in_month` returns the four or five dates in order.

## The nth weekday of a year

```python
from nthweekday import nth_weekday_in_year

nth_weekday_in_year(1998, MONDAY, 20)  # -> date(1998, 5, 18)
nth_weekday_in_year(2026, MONDAY, -1)  # -> date(2026, 12, 28)
nth_weekday_in_year(2026, THURSDAY, 53)  # -> date(2026, 12, 31)
```

This is how RFC 5545 counts a numbered BYDAY in a YEARLY rule without BYMONTH. A year has
52 or 53 of each weekday, so only `53` and `-53` can raise `NoSuchDayError`.

## Questions about a date

```python
from nthweekday import next_weekday, ordinal_of, previous_weekday, week_of_month

ordinal_of(date(2026, 11, 26))  # -> 4
ordinal_of(date(2026, 11, 26), from_end=True)  # -> -1
week_of_month(date(2026, 11, 2))  # -> 2
week_of_month(date(2026, 11, 2), SUNDAY)  # -> 1
next_weekday(date(2026, 10, 12), MONDAY)  # -> date(2026, 10, 12)
next_weekday(date(2026, 10, 12), MONDAY, strict=True)  # -> date(2026, 10, 19)
previous_weekday(date(2026, 10, 12), FRIDAY)  # -> date(2026, 10, 9)
```

- `ordinal_of(d)` is the inverse of `nth_weekday`: for every date,
  `nth_weekday(d.year, d.month, d.weekday(), ordinal_of(d)) == d`, and the same holds
  with `from_end=True`.
- `week_of_month(d, first_weekday=MONDAY)` numbers the rows of
  `calendar.Calendar(first_weekday)` from 1: week 1 runs from the first of the month to
  the day before the first `first_weekday` after it.
- `next_weekday` and `previous_weekday` include `d` itself unless `strict=True`. They
  return a `date` for a `datetime` too, and raise `NoSuchDayError` when the answer would
  fall outside the years 1 to 9999.

## RFC 5545 BYDAY

```python
from nthweekday import ByDay, byday_dates, parse_byday

parse_byday("1SU,-1SU")  # -> (ByDay(Weekday.SUNDAY, 1), ByDay(Weekday.SUNDAY, -1))
parse_byday("+02mo")  # -> (ByDay(Weekday.MONDAY, 2),)
str(ByDay(FRIDAY, -1))  # -> '-1FR'
str(ByDay(FRIDAY))  # -> 'FR'
ByDay(date(2026, 10, 23).weekday(), -1)  # -> ByDay(Weekday.FRIDAY, -1)
[d.day for d in byday_dates(2026, 3, "1SU,-1SU")]  # -> [1, 29]
[d.day for d in byday_dates(2026, 10, "FR,1FR")]  # -> [2, 9, 16, 23, 30]
byday_dates(2026, 9, "5MO")  # -> []
byday_dates(2026, 11, ByDay(THURSDAY, 4))  # -> [date(2026, 11, 26)]
byday_dates(1998, None, "20MO")  # -> [date(1998, 5, 18)]
```

`parse_byday(value)` accepts exactly a comma-separated list of RFC 5545 `weekdaynum`
entries (section 3.3.10): an optional `+` or `-` and one or two digits for an ordinal
from 1 to 53, then one of `SU`, `MO`, `TU`, `WE`, `TH`, `FR`, `SA` in any letter case.
Spaces, empty entries, `0`, three digits and non-ASCII look-alike characters raise
`ValueError`. It returns the entries in order, as a tuple of `ByDay`.

`ByDay(weekday, ordinal=None)` is a frozen, hashable dataclass. `weekday` is typed
`SupportsIndex`, so a `date.weekday()` value, a `Weekday` or a numpy integer type-checks;
it checks both fields as in the table above and stores a `Weekday` and an `int`. `str()`
writes the canonical form (no `+`, no leading zero, upper case), which `parse_byday` reads
back to an equal value.

`byday_dates(year, month, value)` takes a BYDAY string, one `ByDay` or an iterable of
them, and returns the dates selected, sorted and without duplicates:

- With a month, ordinals count within the month (the MONTHLY meaning); an ordinal past
  the last occurrence, including any above 5, selects nothing.
- With `month=None`, ordinals count within the whole year (the YEARLY meaning without
  BYMONTH).
- A plain weekday selects every such day of the period. The entries form one list, so
  `FR,1FR` selects every Friday.

## Command line

The `nthweekday` script (and `python -m nthweekday`) prints the dates a BYDAY value
selects, one ISO date per line:

```
nthweekday 2026-11 4TH            # one month
nthweekday 2026 -1FR              # each month of 2026
nthweekday --yearly 1998 20MO     # ordinals counted within the year
```

A signed value such as `-1FR` is never taken for an option, and every argument after
the first `--` is read as a value. The options are `-h`, and `--help`, `--version` and
`--yearly` or any prefix of them such as `--y`; none takes a value. Anything else that
starts with `-`, such as `-help`, `-hx`, `--yearly=1` or `--=x`, is an unknown option,
the same on every Python version. When `-h` or `--version` is given, the first of the two
wins over unknown options and missing values. The tool exits 0 when it printed dates, 1
when the value selects nothing in that period, and 2 on bad input, with the reason on
standard error. That reason quotes at most 40 characters of any argument, escaped as a
Python string literal, so it never writes a control character to the terminal.

## Stability

From 1.0.0 on, the names in `nthweekday.__all__`, their parameter names, defaults,
return types and error types follow Semantic Versioning. The functions report
`nthweekday` as their module. `Weekday`, `ByDay` and `NoSuchDayError` report the module
that defines them, so that `inspect.getsource` and debuggers find their code; pickles of
them name that module, and it stays importable under that name in every 1.x release.
Messages of errors are for people and may be reworded in a minor release; their types
will not change.
