from datetime import date

import pytest

from nthweekday import (
    FRIDAY,
    MONDAY,
    THURSDAY,
    last_weekday,
    nth_weekday,
    week_of_month,
    weekdays_in_month,
)


def test_third_thursday() -> None:
    assert nth_weekday(2026, 10, THURSDAY, 3) == date(2026, 10, 15)


def test_first_monday() -> None:
    assert nth_weekday(2026, 10, MONDAY, 1) == date(2026, 10, 5)


def test_last_friday() -> None:
    assert last_weekday(2026, 10, FRIDAY) == date(2026, 10, 30)


def test_negative_one_means_last() -> None:
    assert nth_weekday(2026, 10, FRIDAY, -1) == last_weekday(2026, 10, FRIDAY)


def test_fifth_occurrence_present() -> None:
    assert nth_weekday(2026, 10, THURSDAY, 5) == date(2026, 10, 29)


def test_fifth_occurrence_absent_raises() -> None:
    with pytest.raises(ValueError, match="no fifth"):
        nth_weekday(2026, 9, MONDAY, 5)


def test_week_of_month() -> None:
    assert week_of_month(date(2026, 10, 1)) == 1
    assert week_of_month(date(2026, 10, 15)) == 3
    assert week_of_month(date(2026, 10, 31)) == 5


def test_weekdays_in_month_count_five() -> None:
    assert len(weekdays_in_month(2026, 10, THURSDAY)) == 5


def test_weekdays_in_month_count_four() -> None:
    assert len(weekdays_in_month(2026, 9, MONDAY)) == 4


def test_leap_february_has_five_thursdays() -> None:
    assert weekdays_in_month(2024, 2, THURSDAY) == [
        date(2024, 2, 1),
        date(2024, 2, 8),
        date(2024, 2, 15),
        date(2024, 2, 22),
        date(2024, 2, 29),
    ]
    assert last_weekday(2024, 2, THURSDAY) == date(2024, 2, 29)


def test_short_february_has_four_thursdays() -> None:
    assert len(weekdays_in_month(2023, 2, THURSDAY)) == 4
    with pytest.raises(ValueError):
        nth_weekday(2023, 2, THURSDAY, 5)


def test_rejects_bad_weekday() -> None:
    with pytest.raises(ValueError, match="weekday"):
        weekdays_in_month(2026, 10, 7)


def test_rejects_bad_month() -> None:
    with pytest.raises(ValueError, match="month"):
        weekdays_in_month(2026, 13, MONDAY)


def test_rejects_bad_n() -> None:
    with pytest.raises(ValueError, match="n must be"):
        nth_weekday(2026, 10, MONDAY, 6)
