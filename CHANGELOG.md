# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2026-10-24

The public API is now stable: the twenty names in `nthweekday.__all__`, their parameter
names, defaults, return types and error types follow Semantic Versioning from this
release on. 0.2.0 was never published to PyPI, so 1.0.0 is the first release there.

### Stable

- Month queries: `nth_weekday`, `last_weekday` and `weekdays_in_month`.
- Year queries: `nth_weekday_in_year`, counted as RFC 5545 counts BYDAY in a YEARLY rule.
- Date queries: `ordinal_of`, `week_of_month`, `next_weekday` and `previous_weekday`.
- RFC 5545 BYDAY: `parse_byday`, `ByDay` and `byday_dates`.
- Weekdays: `Weekday` and the `MONDAY` to `SUNDAY` constants.
- Errors: `NoSuchDayError` (a `ValueError`) when the day does not exist, `ValueError`
  for an argument out of range or invalid text, `TypeError` for the wrong type.
- The `nthweekday` command line tool and `python -m nthweekday`, with exit codes 0, 1
  and 2.

### Changed

- `next_weekday` and `previous_weekday` raise `NoSuchDayError` instead of a plain
  `ValueError` when the answer would fall outside the years 1 to 9999. Code that catches
  `ValueError` is unaffected.
- `byday_dates` raises `TypeError` with its own message for a value that is neither a
  string, a `ByDay` nor an iterable (it let the error of `tuple()` through).
- Error messages quote at most 40 characters of a text argument and describe a huge
  integer by its size instead of printing it; before, a long BYDAY value or weekday name
  was repeated in full, and an integer past 4300 digits failed while building the message.
- The command line quotes the BYDAY value when it selects no date, and every error it
  reports, including those about unknown options and extra arguments, quotes at most 40
  characters of an argument.
- `Weekday(n)` checks `n` as the functions do: `bool`, `float` and `str` raise
  `TypeError` (`Weekday(True)` gave `Weekday.TUESDAY` and `Weekday(4.0)` gave
  `Weekday.FRIDAY`), and an integer out of range raises `ValueError` naming 0..6.
  It takes exactly one argument: extra positional or keyword arguments raise
  `TypeError`, so no form of the call skips the check or repeats a long text.
- `format()` of a `Weekday` follows one rule on every Python version: the name without a
  spec, the number with one (`f"{FRIDAY:02d}"` is `04`). On Python 3.10 a spec used to
  format the name, and `d` raised `ValueError`.
- `ByDay` takes `weekday: int` in its signature, so a `date.weekday()` value type-checks;
  it accepted one at run time already and still stores a `Weekday`.
- numpy's bool scalar is refused like `bool` with numpy 1.x too (it has `__index__`
  there).
- A `str` subclass passed to `parse_byday` or `Weekday.parse` is read as its plain text;
  its own methods (`__repr__`, `upper`, `split`) are no longer called.
- The functions report `nthweekday` as their module, so pickles of them refer to
  `nthweekday.<name>`. The classes keep the module that defines them, as in 0.2.0.

### Added

- Every public name has a docstring with an example that runs as a test.
- A GUIDE describing every public name, the argument checks and the errors.

## [0.2.0] - 2026-10-13

### Added

- `Weekday`, an `IntEnum` with `iso`, `from_iso()`, `code` and `parse()`; the `MONDAY` to
  `SUNDAY` constants are now its members and still compare equal to plain ints.
- Negative ordinals down to -5 in `nth_weekday` (`-2` is the second-to-last).
- `NoSuchDayError`, a `ValueError` subclass raised only when the occurrence is absent.
- `ordinal_of`, `next_weekday`, `previous_weekday` and `nth_weekday_in_year`.
- `week_of_month(d, first_weekday)` for weeks that start on another day.
- RFC 5545 BYDAY support: `ByDay`, `parse_byday` and `byday_dates` with the MONTHLY and
  YEARLY meanings.
- The `nthweekday` command line tool and `python -m nthweekday`.

### Changed

- Arguments are checked strictly: years 1 to 9999, and `bool`, `float` or `str` values
  raise `TypeError` instead of being accepted or failing later. Integer types other
  than `int` (such as numpy integers) are still accepted through `__index__`.

## [0.1.0] - 2026-10-12

- First release: `nth_weekday`, `last_weekday`, `week_of_month`,
  `weekdays_in_month`, and the `MONDAY` through `SUNDAY` constants.

[Unreleased]: https://github.com/JaviLianes8/nthweekday/commits/main
[1.0.0]: https://pypi.org/project/nthweekday/1.0.0/
[0.2.0]: https://github.com/JaviLianes8/nthweekday/tree/5adde425cbd21cd33da7db1c011e4a6c6a067c8a
[0.1.0]: https://github.com/JaviLianes8/nthweekday/tree/d26b8d67c848c2c96a8583996f286be4099951f8
