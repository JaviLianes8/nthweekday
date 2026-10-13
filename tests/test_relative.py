import calendar
from datetime import date, datetime, timedelta

import pytest

from nthweekday import (
    MONDAY,
    SATURDAY,
    SUNDAY,
    TUESDAY,
    Weekday,
    next_weekday,
    nth_weekday,
    ordinal_of,
    previous_weekday,
    week_of_month,
)


def _days(year: int) -> list[date]:
    start = date(year, 1, 1)
    return [start + timedelta(days=k) for k in range((date(year + 1, 1, 1) - start).days)]


@pytest.mark.parametrize("year", [1, 1900, 2000, 2024, 2026, 9998])
def test_ordinal_of_round_trips_with_nth_weekday(year: int) -> None:
    for d in _days(year):
        for from_end in (False, True):
            n = ordinal_of(d, from_end=from_end)
            assert 1 <= abs(n) <= 5 and (n < 0) is from_end
            assert nth_weekday(d.year, d.month, d.weekday(), n) == d


def test_ordinal_of_known_dates() -> None:
    assert ordinal_of(date(2026, 11, 26)) == 4  # Thanksgiving 2026
    assert ordinal_of(date(2026, 11, 26), from_end=True) == -1
    assert ordinal_of(datetime(2026, 10, 1, 23, 59)) == 1


def test_ordinal_of_rejects_non_dates() -> None:
    with pytest.raises(TypeError, match=r"datetime\.date"):
        ordinal_of("2026-10-01")  # type: ignore[arg-type]


@pytest.mark.parametrize("first", list(Weekday))
@pytest.mark.parametrize("year", [2024, 2026])
def test_week_of_month_matches_calendar_rows(first: Weekday, year: int) -> None:
    cal = calendar.Calendar(first)
    for month in range(1, 13):
        for row, week in enumerate(cal.monthdayscalendar(year, month), start=1):
            for day in filter(None, week):
                assert week_of_month(date(year, month, day), first) == row


def test_week_of_month_defaults_to_monday_weeks() -> None:
    assert week_of_month(date(2026, 10, 1)) == 1
    assert week_of_month(date(2026, 10, 15)) == 3
    assert week_of_month(date(2026, 10, 31)) == 5
    # Sunday 2026-11-01 is alone in week 1 with Monday weeks, but opens week 1 with Sunday weeks.
    assert week_of_month(date(2026, 11, 2)) == 2
    assert week_of_month(date(2026, 11, 2), SUNDAY) == 1


def test_week_of_month_rejects_bad_first_weekday() -> None:
    with pytest.raises(ValueError, match="weekday"):
        week_of_month(date(2026, 10, 1), 7)


def test_next_and_previous_weekday_include_the_day_itself_by_default() -> None:
    monday = date(2026, 10, 12)
    assert next_weekday(monday, MONDAY) == monday
    assert previous_weekday(monday, MONDAY) == monday
    assert next_weekday(monday, MONDAY, strict=True) == date(2026, 10, 19)
    assert previous_weekday(monday, MONDAY, strict=True) == date(2026, 10, 5)


def test_next_and_previous_weekday_every_pair() -> None:
    start = date(2026, 10, 12)
    for offset in range(7):
        d = start + timedelta(days=offset)
        for day in Weekday:
            after = next_weekday(d, day)
            before = previous_weekday(d, day)
            assert after.weekday() == day and 0 <= (after - d).days <= 6
            assert before.weekday() == day and 0 <= (d - before).days <= 6
            assert 1 <= (next_weekday(d, day, strict=True) - d).days <= 7
            assert 1 <= (d - previous_weekday(d, day, strict=True)).days <= 7


def test_us_election_day_is_the_tuesday_after_the_first_monday_of_november() -> None:
    # Hand-written rule and dates, not taken from a fetched source.
    for year, expected in [(2026, 3), (2020, 3), (2022, 8), (2016, 8)]:
        got = next_weekday(nth_weekday(year, 11, MONDAY, 1), TUESDAY, strict=True)
        assert got == date(year, 11, expected)


def test_next_weekday_returns_a_date_for_a_datetime() -> None:
    got = next_weekday(datetime(2026, 10, 12, 18, 30), SATURDAY)
    assert type(got) is date and got == date(2026, 10, 17)


def test_relative_steps_past_the_calendar_limits_raise_value_error() -> None:
    with pytest.raises(ValueError, match="no Saturday after 9999-12-31"):
        next_weekday(date(9999, 12, 31), SATURDAY)
    with pytest.raises(ValueError, match="no Sunday before 0001-01-01"):
        previous_weekday(date(1, 1, 1), SUNDAY)
    assert next_weekday(date(9999, 12, 31), 4) == date(9999, 12, 31)
