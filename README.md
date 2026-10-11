# nthweekday

Find the nth weekday of a month (third Thursday, last Friday) and related calendar queries, zero dependencies.

## Install

```
pip install nthweekday
```

## Usage

```python
from datetime import date
from nthweekday import (
    nth_weekday,
    last_weekday,
    week_of_month,
    weekdays_in_month,
    THURSDAY,
    FRIDAY,
    MONDAY,
)

# Third Thursday of October 2026
nth_weekday(2026, 10, THURSDAY, 3)      # date(2026, 10, 15)

# Last Friday of the month (also nth_weekday(..., -1))
last_weekday(2026, 10, FRIDAY)          # date(2026, 10, 30)
nth_weekday(2026, 10, FRIDAY, -1)       # date(2026, 10, 30)

# Which week of the month a date falls in (weeks start on Monday)
week_of_month(date(2026, 10, 15))       # 3

# Every Monday in the month
weekdays_in_month(2026, 10, MONDAY)     # [5, 12, 19, 26] as date objects

# A fifth occurrence that does not exist raises a clear error
nth_weekday(2026, 9, MONDAY, 5)         # ValueError: 2026-09 has no fifth Monday
```

Weekdays follow the `datetime` convention: Monday is 0 and Sunday is 6. The
constants `MONDAY` through `SUNDAY` are exported for readability. `n` runs from 1
to 5, or -1 for the last occurrence.

## Why

The standard `calendar` module exposes `monthcalendar` and `monthrange`, but no
direct "nth weekday" helper, so the third-Thursday and last-Friday logic that
recurring-event scheduling needs gets rewritten by hand every time. The existing
options fall short: `nthBday` pulls in pandas, `calendarutil` and `monthinfo`
only cover the first and last weekday, and `dateutil.rrule` is a heavy dependency
for a single lookup. This is a small, typed, dependency-free library that answers
exactly those calendar questions.

## License

MIT. See [LICENSE](LICENSE).

## Links

- Website: https://lianes8studio.com
- GitHub: https://github.com/JaviLianes8
- LinkedIn: https://www.linkedin.com/in/jlianes/
