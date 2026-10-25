from __future__ import annotations

import itertools
from collections.abc import Iterator
from datetime import date

import pytest

from nthweekday import FRIDAY, MONDAY, SUNDAY, ByDay, Weekday, byday_dates, parse_byday


def test_parse_single_and_list_entries() -> None:
    assert parse_byday("-1FR") == (ByDay(FRIDAY, -1),)
    assert parse_byday("1SU,-1SU") == (ByDay(SUNDAY, 1), ByDay(SUNDAY, -1))
    assert parse_byday("MO") == (ByDay(MONDAY),)


@pytest.mark.parametrize(
    ("text", "ordinal"),
    [("+1MO", 1), ("01MO", 1), ("+01MO", 1), ("53MO", 53), ("-53MO", -53), ("20MO", 20)],
)
def test_parse_follows_the_weekdaynum_grammar(text: str, ordinal: int) -> None:
    assert parse_byday(text) == (ByDay(MONDAY, ordinal),)


def test_parse_is_case_insensitive() -> None:
    assert parse_byday("-1fr,mo") == (ByDay(FRIDAY, -1), ByDay(MONDAY))


@pytest.mark.parametrize(
    "bad",
    [
        "",
        "0MO",
        "-0MO",
        "54MO",
        "-54MO",
        "123MO",
        "+MO",
        "-MO",
        "1",
        "MON",
        "1 MO",
        " MO",
        "MO,",
        ",MO",
        "MO,,TU",
        "1MO;2TU",
        "\uff11MO",
        "1M\u039f",
        "1\u017fU",
        "001MO",
        "+001MO",
    ],
)
def test_parse_rejects_anything_outside_the_grammar(bad: str) -> None:
    with pytest.raises(ValueError):
        parse_byday(bad)


def test_parse_rejects_non_strings() -> None:
    with pytest.raises(TypeError):
        parse_byday(None)  # type: ignore[arg-type]


@pytest.mark.parametrize("text", ["MO", "1MO", "-1FR", "20MO", "-53SU", "5TH"])
def test_str_gives_back_the_canonical_form(text: str) -> None:
    (entry,) = parse_byday(text)
    assert str(entry) == text


def test_str_normalises_sign_and_padding_and_case() -> None:
    assert [str(e) for e in parse_byday("+01mo,-02We")] == ["1MO", "-2WE"]


def test_byday_validates_its_fields() -> None:
    assert ByDay(4, -1).weekday is Weekday.FRIDAY
    for weekday, ordinal in [(7, None), (-1, None), (0, 0), (0, 54), (0, -54)]:
        with pytest.raises(ValueError):
            ByDay(weekday, ordinal)
    bad_types: list[tuple[object, object]] = [(True, None), (0, True), (0.0, None), (0, 1.0)]
    for weekday_value, ordinal_value in bad_types:
        with pytest.raises(TypeError):
            ByDay(weekday_value, ordinal_value)  # type: ignore[arg-type]
    with pytest.raises(AttributeError):
        ByDay(Weekday.MONDAY).ordinal = 1  # type: ignore[misc]


def test_byday_normalises_index_integers_to_int() -> None:
    class Index:
        def __index__(self) -> int:
            return 2

    entry = ByDay(Index(), Index())  # type: ignore[arg-type]
    assert entry == ByDay(Weekday.WEDNESDAY, 2) and str(entry) == "2WE"
    assert type(entry.ordinal) is int and entry.weekday is Weekday.WEDNESDAY


def test_byday_dates_monthly_plain_weekday_is_every_one() -> None:
    assert [d.day for d in byday_dates(2026, 10, "TH")] == [1, 8, 15, 22, 29]


def test_byday_dates_merges_sorts_and_deduplicates() -> None:
    got = byday_dates(2026, 10, "-1TH,TH,5TH,1MO")
    assert [d.day for d in got] == [1, 5, 8, 15, 22, 29]


def test_byday_dates_accepts_a_byday_value() -> None:
    assert byday_dates(2026, 11, ByDay(Weekday.THURSDAY, 4)) == [date(2026, 11, 26)]


def test_byday_dates_accepts_what_parse_byday_returns() -> None:
    parsed = parse_byday("1SU,-1SU")
    assert byday_dates(2026, 3, parsed) == byday_dates(2026, 3, "1SU,-1SU")
    assert byday_dates(2026, 3, iter(parsed)) == [date(2026, 3, 1), date(2026, 3, 29)]


def test_byday_dates_rejects_other_entries() -> None:
    with pytest.raises(TypeError, match="ByDay entries"):
        byday_dates(2026, 3, ["1SU"])  # type: ignore[list-item]


def test_non_ascii_letters_are_reported_as_invalid_entries() -> None:
    for bad in ("\u017fu", "1\u017fU", "-1\u212aR"):
        with pytest.raises(ValueError, match="invalid BYDAY entry"):
            parse_byday(bad)


def test_byday_dates_absent_occurrence_selects_nothing() -> None:
    assert byday_dates(2026, 9, "5MO") == []


def test_byday_dates_yearly_plain_weekday_covers_the_year() -> None:
    assert len(byday_dates(2026, None, "TH")) == 53  # 2026 starts on a Thursday
    assert len(byday_dates(2026, None, "FR")) == 52


def test_byday_dates_yearly_absent_53rd_selects_nothing() -> None:
    # 2026 starts and ends on a Thursday, so it has 53 Thursdays and 52 Fridays.
    assert byday_dates(2026, None, "53TH") == [date(2026, 12, 31)]
    assert byday_dates(2026, None, "53FR,-53FR") == []


def test_byday_dates_at_the_calendar_limits() -> None:
    assert byday_dates(9999, 12, "-1FR") == [date(9999, 12, 31)]
    assert byday_dates(9999, None, "-1FR") == [date(9999, 12, 31)]
    assert byday_dates(1, 1, "1MO") == [date(1, 1, 1)]


def test_byday_dates_rejects_bad_period() -> None:
    with pytest.raises(ValueError, match="month"):
        byday_dates(2026, 13, "MO")
    with pytest.raises(ValueError, match="year"):
        byday_dates(0, None, "MO")
    with pytest.raises(TypeError):
        byday_dates(2026, True, "MO")


def test_byday_dates_lets_errors_of_the_callers_iterable_through() -> None:
    def entries() -> Iterator[ByDay]:
        yield ByDay(FRIDAY, 1)
        raise TypeError("bug in the caller")

    with pytest.raises(TypeError, match="bug in the caller") as caught:
        byday_dates(2026, 10, entries())
    assert not caught.value.__suppress_context__


def test_byday_dates_stops_at_the_first_entry_of_the_wrong_type() -> None:
    with pytest.raises(TypeError, match="ByDay entries"):
        byday_dates(2026, 1, itertools.count())  # type: ignore[arg-type]
    pulled = iter([ByDay(MONDAY), "MO", ByDay(SUNDAY)])
    with pytest.raises(TypeError, match="ByDay entries"):
        byday_dates(2026, 1, pulled)  # type: ignore[arg-type]
    assert next(pulled) == ByDay(SUNDAY)


@pytest.mark.parametrize("value", ["MO", ByDay(MONDAY), [ByDay(MONDAY)]])
def test_byday_dates_checks_a_falsy_month(value: str | ByDay | list[ByDay]) -> None:
    with pytest.raises(TypeError, match="month must be an int, got bool"):
        byday_dates(2026, False, value)
    with pytest.raises(ValueError, match=r"month must be in 1\.\.12, got 0$"):
        byday_dates(2026, 0, value)
