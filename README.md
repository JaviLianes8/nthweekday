# nthweekday

Find the nth weekday of a month (third Thursday, last Friday), read RFC 5545 BYDAY values
such as `-1FR` or `1SU,-1SU`, and answer the related calendar questions. Typed, zero
dependencies.

## Install

```
pip install nthweekday
```

## Usage

```python
from datetime import date

from nthweekday import (
    FRIDAY,
    MONDAY,
    SUNDAY,
    THURSDAY,
    TUESDAY,
    NoSuchDayError,
    Weekday,
    last_weekday,
    next_weekday,
    nth_weekday,
    ordinal_of,
    week_of_month,
    weekdays_in_month,
)

nth_weekday(2026, 11, THURSDAY, 4)  # -> date(2026, 11, 26)
last_weekday(2026, 5, MONDAY)  # -> date(2026, 5, 25)
nth_weekday(2026, 10, FRIDAY, -2)  # -> date(2026, 10, 23)
[d.day for d in weekdays_in_month(2026, 10, MONDAY)]  # -> [5, 12, 19, 26]
```

`n` runs from 1 to 5, or from -1 (the last) to -5 (the fifth from the end). A month with
only four of that weekday raises `NoSuchDayError`, a `ValueError` subclass, so it can be
told apart from a bad argument:

```python
try:
    nth_weekday(2026, 9, MONDAY, 5)
except NoSuchDayError as exc:
    message = str(exc)
message  # -> '2026-09 has no fifth Monday'
```

Going the other way, and stepping to a weekday:

```python
ordinal_of(date(2026, 11, 26))  # -> 4
ordinal_of(date(2026, 11, 26), from_end=True)  # -> -1
week_of_month(date(2026, 11, 2))  # -> 2
week_of_month(date(2026, 11, 2), SUNDAY)  # -> 1

# US Election Day: the Tuesday after the first Monday in November.
next_weekday(nth_weekday(2026, 11, MONDAY, 1), TUESDAY, strict=True)  # -> date(2026, 11, 3)
```

Weekdays follow `date.weekday()`: Monday is 0 and Sunday is 6. `Weekday` is an `IntEnum`,
so `MONDAY` to `SUNDAY` are plain ints too, and it converts to and from the other common
spellings:

```python
Weekday.parse("Fri")  # -> Weekday.FRIDAY
Weekday.from_iso(7)  # -> Weekday.SUNDAY
Weekday.MONDAY.iso  # -> 1
Weekday.THURSDAY.code  # -> 'TH'
```

Every argument is checked: years 1 to 9999 (the range `datetime` supports), months 1 to
12, weekdays 0 to 6, and `bool` or `float` values are refused with `TypeError`.

## RFC 5545 BYDAY

```python
from nthweekday import ByDay, byday_dates, nth_weekday_in_year, parse_byday

parse_byday("1SU,-1SU")  # -> (ByDay(Weekday.SUNDAY, 1), ByDay(Weekday.SUNDAY, -1))
str(ByDay(FRIDAY, -1))  # -> '-1FR'
[d.day for d in byday_dates(2026, 3, "1SU,-1SU")]  # -> [1, 29]
byday_dates(2026, 9, "5MO")  # -> []
byday_dates(1998, None, "20MO")  # -> [date(1998, 5, 18)]
nth_weekday_in_year(2026, MONDAY, -1)  # -> date(2026, 12, 28)
```

`parse_byday` accepts exactly the `weekdaynum` grammar of RFC 5545 section 3.3.10 (an
optional sign and an ordinal from 1 to 53 before a two-letter code, any letter case) and
`str()` gives back the canonical form. `byday_dates(year, month, value)` uses the MONTHLY
meaning: ordinals count within the month and an occurrence past the last one selects
nothing. With `month=None` it uses the YEARLY meaning without BYMONTH, where ordinals
count within the year. The result is sorted and has no duplicates; a plain weekday and a
numbered one in the same list are combined, as the RFC defines BYDAY as one list.

## Command line

```
$ nthweekday 2026-11 4TH
2026-11-26
$ nthweekday 2026 -1FR        # every month of 2026
2026-01-30
...
2026-12-25
$ nthweekday --yearly 1998 20MO
1998-05-18
```

It prints one ISO date per line and exits 0, exits 1 when nothing matched, and 2 on bad
input. `python -m nthweekday` works the same.

## How it is tested

- Every (year, month, weekday, n) from 1990 to 2040, the year ordinals 1 to 53 at the
  calendar limits, and random BYDAY lists are compared with `python-dateutil`'s `rrule`,
  used only in the tests.
- The worked examples of RFC 5545 are test vectors.
- The six US federal holidays defined by a weekday rule in 5 U.S.C. 6103 reproduce every
  date OPM published for 2011 to 2030, and the UK bank holiday rules of the Banking and
  Financial Dealings Act 1971 reproduce the GOV.UK dates, apart from the two days moved
  by proclamation.
- The upstream pages are not part of the repository: `python scripts/fetch_upstream.py`
  fetches them into `data/upstream/`, checked against the pinned manifest, and the tests
  that need them skip until then.
- Every `# ->` line in this README is executed by the test suite.

## Why

The standard `calendar` module exposes `monthcalendar` and `monthrange`, but no direct
"nth weekday" helper, so the third-Thursday and last-Friday logic that recurring events
need gets rewritten by hand every time. `dateutil.rrule` covers it as part of a full
recurrence engine; this library is the small, typed, dependency-free piece for when the
question is just which day it is.

## License

MIT. See [LICENSE](LICENSE).

## Links

- Website: https://lianes8studio.com
- GitHub: https://github.com/JaviLianes8
- LinkedIn: https://www.linkedin.com/in/jlianes/
