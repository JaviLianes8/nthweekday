"""Independent oracles: python-dateutil's rrule (a test-only dependency) and the rows of the
standard calendar module."""

from __future__ import annotations

import calendar
import random
from datetime import date, datetime

import pytest

from nthweekday import (
    NoSuchDayError,
    byday_dates,
    nth_weekday,
    nth_weekday_in_year,
    weekdays_in_month,
)

rrule_module = pytest.importorskip("dateutil.rrule")
MONTHLY, YEARLY = rrule_module.MONTHLY, rrule_module.YEARLY
DAYS = (
    rrule_module.MO,
    rrule_module.TU,
    rrule_module.WE,
    rrule_module.TH,
    rrule_module.FR,
    rrule_module.SA,
    rrule_module.SU,
)


CODES = ("MO", "TU", "WE", "TH", "FR", "SA", "SU")


def _month_end(year: int, month: int) -> datetime:
    return datetime(year, month, calendar.monthrange(year, month)[1])


def _oracle(freq: int, year: int, month: int | None, days: list[object]) -> list[date]:
    start = datetime(year, month or 1, 1)
    end = datetime(year, 12, 31) if month is None else _month_end(year, month)
    rule = rrule_module.rrule(freq, byweekday=days, dtstart=start, until=end)
    return [d.date() for d in rule]


@pytest.mark.parametrize("year", range(1990, 2041))
def test_monthly_ordinals_match_rrule(year: int) -> None:
    for month in range(1, 13):
        for day, oracle_day in enumerate(DAYS):
            assert weekdays_in_month(year, month, day) == _oracle(
                MONTHLY, year, month, [oracle_day]
            )
            for n in (1, 2, 3, 4, 5, -1, -2, -3, -4, -5):
                expected = _oracle(MONTHLY, year, month, [oracle_day(n)])
                try:
                    got = [nth_weekday(year, month, day, n)]
                except NoSuchDayError:
                    got = []
                assert got == expected, (year, month, day, n)


@pytest.mark.parametrize("year", [1, 2, 1600, 1900, 2000, 2024, 2026, 2100, 9998, 9999])
def test_yearly_ordinals_match_rrule(year: int) -> None:
    for day, oracle_day in enumerate(DAYS):
        for n in (*range(1, 54), *range(-53, 0)):
            expected = _oracle(YEARLY, year, None, [oracle_day(n)])
            try:
                got = [nth_weekday_in_year(year, day, n)]
            except NoSuchDayError:
                got = []
            assert got == expected, (year, day, n)


@pytest.mark.parametrize("seed", range(60))
def test_random_byday_lists_match_the_union_of_rrule_entries(seed: int) -> None:
    # dateutil intersects plain and numbered weekdays given together ("FR,1FR" yields only
    # the first Friday) while RFC 5545 BYDAY is one list, so each entry is asked alone and
    # the answers are merged. dateutil raises IndexError for some monthly ordinals above 5
    # (20MO), so those are covered by test_monthly_ordinals_past_five_select_nothing.
    rng = random.Random(seed)
    year = rng.choice([1, 1700, 1999, 2024, 2026, 9999])
    month = rng.choice([None, *range(1, 13)])
    limit = 53 if month is None else 5
    freq = YEARLY if month is None else MONTHLY
    entries, expected = [], set()
    for _ in range(rng.randint(1, 4)):
        day = rng.randrange(7)
        n = rng.choice([None, rng.randint(1, limit), -rng.randint(1, limit)])
        prefix = "" if n is None else f"{n:+d}" if rng.random() < 0.3 else str(n)
        entries.append(prefix + CODES[day])
        expected.update(_oracle(freq, year, month, [DAYS[day] if n is None else DAYS[day](n)]))
    value = ",".join(entries)
    assert byday_dates(year, month, value) == sorted(expected), value


def test_monthly_ordinals_past_five_select_nothing() -> None:
    # Hand-written: a month holds at most five of any weekday, so 6..53 never match.
    for n in (6, 7, 30, 53):
        assert byday_dates(2026, 10, f"{n}TH") == []
        assert byday_dates(2026, 10, f"-{n}TH") == []


# The Gregorian calendar repeats every 400 years, so one whole cycle covers every month
# layout; the first and last centuries add the limits of datetime.
CYCLE_YEARS = [*range(2000, 2400), *range(1, 101), *range(9900, 10000)]


@pytest.mark.parametrize("chunk", range(0, len(CYCLE_YEARS), 50))
def test_every_month_layout_matches_the_calendar_module(chunk: int) -> None:
    cal = calendar.Calendar()
    for year in CYCLE_YEARS[chunk : chunk + 50]:
        for month in range(1, 13):
            rows = [(d, wd) for d, wd in cal.itermonthdays2(year, month) if d]
            for day in range(7):
                expected = [date(year, month, d) for d, wd in rows if wd == day]
                assert weekdays_in_month(year, month, day) == expected
                for n in (1, 2, 3, 4, 5, -1, -2, -3, -4, -5):
                    index = n - 1 if n > 0 else len(expected) + n
                    try:
                        got = [nth_weekday(year, month, day, n)]
                    except NoSuchDayError:
                        got = []
                    assert got == ([expected[index]] if 0 <= index < len(expected) else [])
