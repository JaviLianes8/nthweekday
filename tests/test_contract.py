import importlib.resources

import nthweekday

# The public API. Add every exported name here as the library grows; this list is the
# contract and the test below fails if the module and this list disagree.
PUBLIC_API: list[str] = [
    "FRIDAY",
    "MONDAY",
    "SATURDAY",
    "SUNDAY",
    "THURSDAY",
    "TUESDAY",
    "WEDNESDAY",
    "ByDay",
    "NoSuchDayError",
    "Weekday",
    "byday_dates",
    "last_weekday",
    "next_weekday",
    "nth_weekday",
    "nth_weekday_in_year",
    "ordinal_of",
    "parse_byday",
    "previous_weekday",
    "week_of_month",
    "weekdays_in_month",
]


def test_all_lists_exactly_the_public_api() -> None:
    assert sorted(nthweekday.__all__) == sorted(PUBLIC_API)


def test_every_exported_name_resolves() -> None:
    for name in nthweekday.__all__:
        assert hasattr(nthweekday, name)


def test_version_is_a_three_part_string() -> None:
    parts = nthweekday.__version__.split(".")
    assert len(parts) == 3
    assert all(part.isdigit() for part in parts)


def test_the_package_ships_type_information() -> None:
    assert importlib.resources.files("nthweekday").joinpath("py.typed").is_file()


def test_day_constants_are_the_enum_members_and_plain_ints() -> None:
    names = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]
    for number, name in enumerate(names):
        value = getattr(nthweekday, name)
        assert value is nthweekday.Weekday[name]
        assert value == number and isinstance(value, int)


def test_no_such_day_error_is_a_value_error() -> None:
    assert issubclass(nthweekday.NoSuchDayError, ValueError)
