from datetime import date, datetime

import pytest

from nthweekday import (
    FRIDAY,
    MONDAY,
    SUNDAY,
    THURSDAY,
    TUESDAY,
    NoSuchDayError,
    last_weekday,
    nth_weekday,
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


def test_negative_ordinals_count_from_the_end() -> None:
    # October 2026 Thursdays: 1, 8, 15, 22, 29.
    got = [nth_weekday(2026, 10, THURSDAY, -k).day for k in range(1, 6)]
    assert got == [29, 22, 15, 8, 1]


def test_fifth_occurrence_present() -> None:
    assert nth_weekday(2026, 10, THURSDAY, 5) == date(2026, 10, 29)


def test_fifth_occurrence_absent_raises_no_such_day() -> None:
    with pytest.raises(NoSuchDayError, match="2026-09 has no fifth Monday"):
        nth_weekday(2026, 9, MONDAY, 5)


def test_fifth_from_last_absent_raises_no_such_day() -> None:
    with pytest.raises(NoSuchDayError, match="has no fifth-to-last Monday"):
        nth_weekday(2026, 9, MONDAY, -5)


def test_weekdays_in_month_count_five_and_four() -> None:
    assert len(weekdays_in_month(2026, 10, THURSDAY)) == 5
    assert len(weekdays_in_month(2026, 9, MONDAY)) == 4


def test_leap_february_has_five_thursdays() -> None:
    assert [d.day for d in weekdays_in_month(2024, 2, THURSDAY)] == [1, 8, 15, 22, 29]
    assert last_weekday(2024, 2, THURSDAY) == date(2024, 2, 29)


def test_short_february_has_four_thursdays() -> None:
    assert len(weekdays_in_month(2023, 2, THURSDAY)) == 4
    with pytest.raises(NoSuchDayError):
        nth_weekday(2023, 2, THURSDAY, 5)


def test_february_of_a_common_year_can_have_exactly_four_of_each() -> None:
    # 2026-02-01 is a Sunday and the month has 28 days.
    assert all(len(weekdays_in_month(2026, 2, day)) == 4 for day in range(7))


def test_proleptic_gregorian_limits() -> None:
    assert nth_weekday(1, 1, MONDAY, 1) == date(1, 1, 1)
    assert last_weekday(9999, 12, FRIDAY) == date(9999, 12, 31)
    assert nth_weekday(9999, 12, SUNDAY, -1) == date(9999, 12, 26)


def test_century_rule_1900_is_not_leap_but_2000_is() -> None:
    assert weekdays_in_month(1900, 2, THURSDAY)[-1] == date(1900, 2, 22)
    assert weekdays_in_month(2000, 2, TUESDAY)[-1] == date(2000, 2, 29)


@pytest.mark.parametrize(
    ("args", "message"),
    [
        ((0, 1, MONDAY, 1), "year must be in 1..9999"),
        ((10000, 1, MONDAY, 1), "year must be in 1..9999"),
        ((2026, 0, MONDAY, 1), "month must be in 1..12"),
        ((2026, 13, MONDAY, 1), "month must be in 1..12"),
        ((2026, 10, -1, 1), "weekday must be in 0..6"),
        ((2026, 10, 7, 1), "weekday must be in 0..6"),
        ((2026, 10, MONDAY, 0), "n must be in 1..5 or -5..-1"),
        ((2026, 10, MONDAY, 6), "n must be in 1..5 or -5..-1, got 6"),
        ((2026, 10, MONDAY, -6), "n must be in 1..5 or -5..-1, got -6"),
    ],
)
def test_rejects_out_of_range_arguments(args: tuple[int, int, int, int], message: str) -> None:
    with pytest.raises(ValueError, match=message) as caught:
        nth_weekday(*args)
    assert not isinstance(caught.value, NoSuchDayError)


@pytest.mark.parametrize(
    "args",
    [
        (2026, True, MONDAY, 1),
        (2026, 10, True, 1),
        (2026, 10, MONDAY, True),
        (2026.0, 10, MONDAY, 1),
        ("2026", 10, MONDAY, 1),
        (2026, 10, MONDAY, 1.0),
    ],
)
def test_rejects_bool_float_and_str_arguments(args: tuple[object, ...]) -> None:
    with pytest.raises(TypeError, match="must be an int"):
        nth_weekday(*args)  # type: ignore[arg-type]


def test_weekdays_in_month_validates_like_nth_weekday() -> None:
    with pytest.raises(ValueError, match="weekday"):
        weekdays_in_month(2026, 10, 7)
    with pytest.raises(ValueError, match="month"):
        weekdays_in_month(2026, 13, MONDAY)
    with pytest.raises(TypeError):
        weekdays_in_month(2026, 10, None)  # type: ignore[arg-type]


def test_results_are_plain_dates() -> None:
    got = nth_weekday(2026, 10, MONDAY, 1)
    assert type(got) is date and not isinstance(got, datetime)


class _Index:
    """An integer type that is not int, like numpy.int64: it only offers __index__."""

    def __init__(self, value: int) -> None:
        self.value = value

    def __index__(self) -> int:
        return self.value


def test_accepts_integer_types_through_index() -> None:
    got = nth_weekday(_Index(2026), _Index(11), _Index(3), _Index(4))
    assert got == date(2026, 11, 26)
