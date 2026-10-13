from datetime import date

import pytest

from nthweekday import FRIDAY, MONDAY, THURSDAY, NoSuchDayError, nth_weekday_in_year


def test_first_and_last_of_the_year() -> None:
    assert nth_weekday_in_year(2026, THURSDAY, 1) == date(2026, 1, 1)
    assert nth_weekday_in_year(2026, THURSDAY, 53) == date(2026, 12, 31)
    assert nth_weekday_in_year(2026, MONDAY, -1) == date(2026, 12, 28)
    assert nth_weekday_in_year(2026, THURSDAY, -53) == date(2026, 1, 1)


@pytest.mark.parametrize(
    ("n", "message"),
    [(53, "2026 has no 53rd Friday"), (-53, "2026 has no 53rd-to-last Friday")],
)
def test_absent_53rd_raises_no_such_day(n: int, message: str) -> None:
    with pytest.raises(NoSuchDayError, match=message):
        nth_weekday_in_year(2026, FRIDAY, n)


@pytest.mark.parametrize("n", [0, 54, -54])
def test_rejects_out_of_range_n(n: int) -> None:
    with pytest.raises(ValueError, match=f"n must be in 1..53 or -53..-1, got {n}") as caught:
        nth_weekday_in_year(2026, MONDAY, n)
    assert not isinstance(caught.value, NoSuchDayError)


@pytest.mark.parametrize("args", [(2026, MONDAY, True), (2026, True, 1), (True, MONDAY, 1)])
def test_rejects_bools(args: tuple[object, ...]) -> None:
    with pytest.raises(TypeError, match="must be an int"):
        nth_weekday_in_year(*args)  # type: ignore[arg-type]


def test_ordinal_words_use_the_right_suffix() -> None:
    from nthweekday._month import _ordinal_words

    words = {n: _ordinal_words(n) for n in (1, 5, 6, 11, 12, 13, 21, 22, 23, 31, 52, 53)}
    assert words == {
        1: "first",
        5: "fifth",
        6: "6th",
        11: "11th",
        12: "12th",
        13: "13th",
        21: "21st",
        22: "22nd",
        23: "23rd",
        31: "31st",
        52: "52nd",
        53: "53rd",
    }
    assert _ordinal_words(-2) == "second-to-last"
