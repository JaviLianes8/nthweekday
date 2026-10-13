# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0]

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

## [0.1.0]

- First release: `nth_weekday`, `last_weekday`, `week_of_month`,
  `weekdays_in_month`, and the `MONDAY` through `SUNDAY` constants.
