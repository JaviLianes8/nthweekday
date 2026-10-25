"""The 1.0.0 promise: signatures, return types, error types and module names stay put."""

from __future__ import annotations

import inspect
import pickle
from collections.abc import Callable
from datetime import date

import pytest

import nthweekday
from nthweekday import (
    FRIDAY,
    MONDAY,
    SATURDAY,
    SUNDAY,
    ByDay,
    NoSuchDayError,
    Weekday,
    byday_dates,
    last_weekday,
    next_weekday,
    nth_weekday,
    nth_weekday_in_year,
    ordinal_of,
    parse_byday,
    previous_weekday,
    week_of_month,
    weekdays_in_month,
)

IDX = "SupportsIndex"
SIGNATURES = {
    "byday_dates": f"(year: '{IDX}', month: '{IDX} | None', "
    "value: 'str | ByDay | Iterable[ByDay]') -> 'list[date]'",
    "last_weekday": f"(year: '{IDX}', month: '{IDX}', weekday: '{IDX}') -> 'date'",
    "next_weekday": f"(d: 'date', weekday: '{IDX}', *, strict: 'bool' = False) -> 'date'",
    "nth_weekday": f"(year: '{IDX}', month: '{IDX}', weekday: '{IDX}', n: '{IDX}') -> 'date'",
    "nth_weekday_in_year": f"(year: '{IDX}', weekday: '{IDX}', n: '{IDX}') -> 'date'",
    "ordinal_of": "(d: 'date', *, from_end: 'bool' = False) -> 'int'",
    "parse_byday": "(value: 'str') -> 'tuple[ByDay, ...]'",
    "previous_weekday": f"(d: 'date', weekday: '{IDX}', *, strict: 'bool' = False) -> 'date'",
    "week_of_month": f"(d: 'date', first_weekday: '{IDX}' = Weekday.MONDAY) -> 'int'",
    "weekdays_in_month": f"(year: '{IDX}', month: '{IDX}', weekday: '{IDX}') -> 'list[date]'",
}


@pytest.mark.parametrize("name", sorted(SIGNATURES))
def test_function_signatures_are_pinned(name: str) -> None:
    assert str(inspect.signature(getattr(nthweekday, name))) == SIGNATURES[name]


def test_class_signatures_are_pinned() -> None:
    assert str(inspect.signature(ByDay)) == (
        f"(weekday: '{IDX}', ordinal: '{IDX} | None' = None) -> 'None'"
    )
    assert [(m.name, m.value) for m in Weekday] == [
        ("MONDAY", 0),
        ("TUESDAY", 1),
        ("WEDNESDAY", 2),
        ("THURSDAY", 3),
        ("FRIDAY", 4),
        ("SATURDAY", 5),
        ("SUNDAY", 6),
    ]
    assert str(inspect.signature(Weekday.parse)) == "(text: 'str') -> 'Weekday'"
    assert str(inspect.signature(Weekday.from_iso)) == f"(number: '{IDX}') -> 'Weekday'"


def test_functions_report_the_package_and_classes_their_defining_module() -> None:
    classes = {"ByDay": "_byday", "NoSuchDayError": "_month", "Weekday": "_weekday"}
    for name in nthweekday.__all__:
        if not name.isupper():
            module = f"nthweekday.{classes[name]}" if name in classes else "nthweekday"
            assert getattr(nthweekday, name).__module__ == module, name
    for function in (nth_weekday, parse_byday):
        assert pickle.loads(pickle.dumps(function)) is function
        assert b"nthweekday._" not in pickle.dumps(function)


def test_the_package_keeps_no_helper_names_from_its_setup() -> None:
    assert not {"_obj", "_member", "_func"} & set(vars(nthweekday))


def test_return_types_are_plain() -> None:
    assert type(nth_weekday(2026, 1, MONDAY, 1)) is date
    assert type(last_weekday(2026, 1, MONDAY)) is date
    assert type(nth_weekday_in_year(2026, MONDAY, 1)) is date
    assert type(weekdays_in_month(2026, 1, MONDAY)) is list
    assert type(byday_dates(2026, 1, "MO")) is list
    assert type(parse_byday("MO")) is tuple
    assert type(ordinal_of(date(2026, 1, 5))) is int
    assert type(week_of_month(date(2026, 1, 5))) is int
    assert type(ByDay(1, 2).ordinal) is int and type(ByDay(1).weekday) is Weekday


def test_absent_days_raise_no_such_day_error_and_nothing_else() -> None:
    absent: list[Callable[[], object]] = [
        lambda: nth_weekday(2026, 9, MONDAY, 5),
        lambda: nth_weekday(2026, 9, MONDAY, -5),
        lambda: nth_weekday_in_year(2026, FRIDAY, 53),
        lambda: nth_weekday_in_year(2026, FRIDAY, -53),
        lambda: next_weekday(date(9999, 12, 31), SATURDAY),
        lambda: next_weekday(date(9999, 12, 31), FRIDAY, strict=True),
        lambda: previous_weekday(date(1, 1, 1), SUNDAY),
        lambda: previous_weekday(date(1, 1, 1), MONDAY, strict=True),
    ]
    for call in absent:
        with pytest.raises(NoSuchDayError):
            call()


def test_bad_arguments_raise_plain_value_error_not_no_such_day() -> None:
    bad: list[Callable[[], object]] = [
        lambda: nth_weekday(2026, 9, MONDAY, 6),
        lambda: nth_weekday(2026, 9, MONDAY, 0),
        lambda: nth_weekday(2026, 13, MONDAY, 1),
        lambda: nth_weekday(10000, 1, MONDAY, 1),
        lambda: nth_weekday(2026, 1, 7, 1),
        lambda: nth_weekday_in_year(2026, FRIDAY, 54),
        lambda: parse_byday("6XX"),
        lambda: Weekday.parse("Mondays"),
        lambda: Weekday.from_iso(0),
    ]
    for call in bad:
        with pytest.raises(ValueError) as caught:
            call()
        assert type(caught.value) is ValueError


@pytest.mark.parametrize(
    "call",
    [
        lambda: nth_weekday(2026.0, 1, 0, 1),  # type: ignore[arg-type]
        lambda: nth_weekday(2026, True, 0, 1),
        lambda: nth_weekday(2026, 1, "MO", 1),  # type: ignore[arg-type]
        lambda: last_weekday(2026, 1, None),  # type: ignore[arg-type]
        lambda: weekdays_in_month("2026", 1, 0),  # type: ignore[arg-type]
        lambda: nth_weekday_in_year(2026, 0, 1.0),  # type: ignore[arg-type]
        lambda: ordinal_of("2026-01-01"),  # type: ignore[arg-type]
        lambda: week_of_month(date(2026, 1, 1), 0.0),  # type: ignore[arg-type]
        lambda: next_weekday(20260101, 0),  # type: ignore[arg-type]
        lambda: previous_weekday(date(2026, 1, 1), False),
        lambda: parse_byday(b"MO"),  # type: ignore[arg-type]
        lambda: byday_dates(2026, 1, 5),  # type: ignore[arg-type]
        lambda: byday_dates(2026, 1, [ByDay(MONDAY), "MO"]),  # type: ignore[list-item]
        lambda: Weekday.parse(0),  # type: ignore[arg-type]
        lambda: Weekday.from_iso("1"),  # type: ignore[arg-type]
    ],
)
def test_wrong_types_raise_type_error(call: object) -> None:
    with pytest.raises(TypeError):
        call()  # type: ignore[operator]


def test_messages_quote_at_most_40_characters_and_no_huge_number() -> None:
    with pytest.raises(ValueError) as caught:
        Weekday.parse("x" * 41)
    assert str(caught.value) == "unknown weekday name '" + "x" * 40 + "'... (41 characters)"
    with pytest.raises(ValueError) as caught:
        Weekday.parse("x" * 40)
    assert str(caught.value) == "unknown weekday name '" + "x" * 40 + "'"
    with pytest.raises(ValueError) as caught:
        parse_byday(chr(0xD800) * 30)
    assert str(caught.value).count(r"\ud800") == 13
    with pytest.raises(ValueError) as caught:
        nth_weekday(2026, 1, MONDAY, 10**18 - 1)
    assert str(caught.value).endswith(f"got {10**18 - 1}")
    with pytest.raises(ValueError) as caught:
        nth_weekday(2026, 1, MONDAY, -(10**18))
    assert str(caught.value) == "n must be in 1..5 or -5..-1, got an integer of 60 bits"


@pytest.mark.parametrize(
    ("value", "message"),
    [
        ("XX", "invalid BYDAY entry 'XX'"),
        ("MO,XX,FR", "invalid BYDAY entry 'XX' (entry 2 of 3)"),
        (
            "MO," * 20 + "Z" * 52,
            "invalid BYDAY entry '" + "Z" * 40 + "'... (52 characters) (entry 21 of 21)",
        ),
        ("x" * 1000, "invalid BYDAY entry '" + "x" * 40 + "'... (1000 characters)"),
    ],
    ids=["one", "list", "long-entry", "long-value"],
)
def test_a_bad_byday_entry_is_quoted_once_with_its_position(value: str, message: str) -> None:
    # One quoted piece of at most 40 characters; the whole value is not quoted beside it.
    with pytest.raises(ValueError) as caught:
        parse_byday(value)
    assert str(caught.value) == message
