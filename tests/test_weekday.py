from datetime import date, timedelta

import pytest

from nthweekday import MONDAY, SUNDAY, Weekday


def test_numbering_matches_date_weekday_and_isoweekday() -> None:
    # 2026-10-12 is a Monday; walk a whole week.
    for offset in range(7):
        d = date(2026, 10, 12) + timedelta(days=offset)
        day = Weekday(d.weekday())
        assert day.iso == d.isoweekday()
        assert Weekday.from_iso(d.isoweekday()) is day


def test_iso_numbers_at_both_ends() -> None:
    assert (MONDAY.iso, SUNDAY.iso) == (1, 7)


@pytest.mark.parametrize("bad", [0, 8, -1])
def test_from_iso_rejects_out_of_range(bad: int) -> None:
    with pytest.raises(ValueError, match=r"ISO weekday must be in 1\.\.7"):
        Weekday.from_iso(bad)


@pytest.mark.parametrize("bad", [True, 1.0, "1", None])
def test_from_iso_rejects_non_int_with_type_error(bad: object) -> None:
    with pytest.raises(TypeError, match="ISO weekday must be an int"):
        Weekday.from_iso(bad)  # type: ignore[arg-type]


def test_str_is_the_name_on_every_python() -> None:
    assert str(Weekday.MONDAY) == "MONDAY"
    assert f"{Weekday.SUNDAY}" == "SUNDAY"


def test_codes_follow_rfc5545() -> None:
    assert [d.code for d in Weekday] == ["MO", "TU", "WE", "TH", "FR", "SA", "SU"]


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("MO", Weekday.MONDAY),
        ("mo", Weekday.MONDAY),
        ("Tue", Weekday.TUESDAY),
        ("wednesday", Weekday.WEDNESDAY),
        ("THURSDAY", Weekday.THURSDAY),
        ("Fr", Weekday.FRIDAY),
        ("sat", Weekday.SATURDAY),
        ("Sunday", Weekday.SUNDAY),
    ],
)
def test_parse_accepts_codes_short_and_full_names(text: str, expected: Weekday) -> None:
    assert Weekday.parse(text) is expected


@pytest.mark.parametrize(
    "bad", ["", "M", "Mond", " MO", "MO ", "Tues", "lunes", "\u039cO", "\u017fu", "\u017fun"]
)
def test_parse_rejects_anything_else(bad: str) -> None:
    with pytest.raises(ValueError, match="unknown weekday"):
        Weekday.parse(bad)


def test_parse_rejects_non_strings() -> None:
    with pytest.raises(TypeError):
        Weekday.parse(0)  # type: ignore[arg-type]
