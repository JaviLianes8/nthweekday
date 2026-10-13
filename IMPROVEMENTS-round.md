# nthweekday improvement round

Progress:
- [x] Brainstorm ranked improvements (this file)
- [x] Pin the ground truth: upstream copies in a local folder with a tracked manifest
- [x] Typed weekdays: `Weekday` enum, ISO numbering, name parsing
- [x] Full ordinal range: `n` in 1..5 and -5..-1, a dedicated error for absent days
- [x] Ordinal of a date, next and previous weekday, Sunday-start weeks
- [x] RFC 5545 BYDAY: parse, format, monthly and yearly expansion
- [x] Command line tool
- [x] Contracts: dateutil oracle, RFC vectors, US federal and UK bank holidays, README examples
- [x] Docs and packaging: README, CHANGELOG, metadata, installed-wheel e2e test
- [x] Gates: ruff format, ruff check, mypy --strict, pytest
- [x] Mutation run: removing guarded logic makes the suite fail
- [ ] Independent review findings fixed with regression tests
- [ ] Pull request opened, guard clean

## Starting point

`0.1.0` gives `nth_weekday`, `last_weekday`, `weekdays_in_month`, `week_of_month` and the
`MONDAY` to `SUNDAY` integer constants. Compared with the sources below:

- `n` accepts 1..5 and -1 only. RFC 5545 lets a monthly BYDAY count from the end too
  (`-2MO` is the second-to-last Monday), so -2..-5 are rejected for no reason.
- A missing fifth occurrence raises a plain `ValueError`, the same type as a bad month,
  so a caller cannot tell "this month has no fifth Monday" from "you passed garbage".
- Booleans and floats slip through: `nth_weekday(2026, True, 0, 1)` answers for January.
- There is no way to go from a date back to its ordinal ("is this the last Friday?"),
  no "next Tuesday after" helper (US Election Day, the Scottish St Andrew's Day
  substitute), no ISO 1..7 numbering and no Sunday-start weeks for `week_of_month`.
- Nothing reads or writes RFC 5545 BYDAY values, which is where most recurring-event
  data comes from.
- The tests are hand-picked dates. Nothing compares against an independent
  implementation, a standard, or real holiday calendars; the README examples are not
  executed; there is no installed-wheel test and `check.ps1` lints `src tests` only.

## Sources (fetched 2026-10-13)

- RFC 5545 section 3.3.10, https://www.rfc-editor.org/rfc/rfc5545.txt: the `weekdaynum`
  grammar (`[[plus / minus] ordwk] weekday`, `ordwk` 1 to 53, two-letter day codes), the
  BYDAY meaning inside MONTHLY and YEARLY rules, case-insensitive enumerated values
  (section 2), and the worked examples in section 3.8.5.3 used as test vectors.
- 5 U.S.C. 6103(a), https://www.govinfo.gov/content/pkg/USCODE-2023-title5/html/USCODE-2023-title5-partIII-subpartE-chap61-subchapI-sec6103.htm:
  the six federal holidays defined by an nth weekday.
- OPM federal holiday schedules 2011 to 2030,
  https://www.opm.gov/policy-data-oversight/pay-leave/federal-holidays/: the published
  dates those rules must reproduce.
- Banking and Financial Dealings Act 1971, schedule 1 (as amended),
  https://www.legislation.gov.uk/ukpga/1971/80/schedule/1: last Monday in May and in
  August (England and Wales, Northern Ireland), first Monday in May and in August
  (Scotland), and the St Andrew's Day rule (30 November, or the first Monday after it
  when that is a weekend).
- GOV.UK bank holidays, https://www.gov.uk/bank-holidays.json: published dates for
  2019 to 2028 in the three divisions.
- Python `datetime` docs, https://docs.python.org/3/library/datetime.html: `weekday()`
  is Monday 0 to Sunday 6 and `isoweekday()` is Monday 1 to Sunday 7 (ISO 8601).
- python-dateutil 2.9.0 `rrule`, used only as a test oracle, never at run time.

The OPM page, the GOV.UK JSON, the statute pages and the RFC text are not committed:
`data/upstream/MANIFEST.json` pins URL, size, sha256 and licence,
`scripts/fetch_upstream.py` fetches them into the ignored folder, and the tests that read
them skip while they are absent. Short vectors cited from the RFC live in the tests with
the URL next to them; the holiday rules are written in our own words.

## Ranked brainstorm

1. Full monthly ordinal range: `n` in 1..5 and -5..-1, strict integer checks (no bool,
   no float), year limited to 1..9999 with a clear message, and `NoSuchDayError`, a
   `ValueError` subclass raised only when the occurrence is absent. Contract: every
   (year, month, weekday, n) over 1990..2040 matches dateutil `rrule`, plus the
   proleptic Gregorian edges (year 1 and year 9999).
2. `Weekday` as an `IntEnum` (the constants stay plain-int compatible) with `iso`,
   `from_iso()`, `code` (`MO`) and `parse()` for codes, short and full English names.
3. `ordinal_of(d)` and `ordinal_of(d, from_end=True)`: which occurrence a date is.
   Contract: round-trips with `nth_weekday` for every day of several years.
4. `next_weekday(d, weekday, strict=False)` and `previous_weekday`: "the Tuesday after
   the first Monday", St Andrew's Day substitutes. Range errors become `ValueError`.
5. `week_of_month(d, first_weekday=...)` for Sunday-start calendars, checked against
   `calendar.Calendar(firstweekday).monthdayscalendar` rows.
6. RFC 5545 BYDAY: `ByDay` value type, `parse_byday("1SU,-1SU")`, `str()` back to the
   canonical form, and `byday_dates(year, month, value)` with MONTHLY semantics, or
   `month=None` for YEARLY semantics (ordinals up to 53 count within the year).
   `nth_weekday_in_year` backs the yearly case. Contract: RFC vectors, dateutil oracle
   for random lists, grammar edge cases (`+1MO`, `01MO`, `0MO`, `54MO`, `+MO`).
7. Holiday contracts: the six 5 U.S.C. 6103 rules reproduce every OPM date 2011..2030;
   the 1971 Act rules reproduce every GOV.UK date 2019..2028 except the two dates moved
   by proclamation (VE day 2020, Platinum Jubilee 2022), which are listed by hand.
8. Command line tool `nthweekday` (and `python -m nthweekday`): `nthweekday 2026-11 4TH`
   prints ISO dates; a bare year expands each month; `--yearly` uses year ordinals.
9. Runnable docs: every `# ->` line in the README is executed by a test.
10. Packaging: console script, keywords, classifiers, installed-wheel e2e test, sdist
    without upstream data, `check.ps1` over the whole tree.

Considered and left out:

- A holiday calendar: holidays here are test cases, not a feature. Fixed-date holidays
  and their observed-day shifts belong to a holiday library.
- Full RRULE expansion (BYSETPOS, INTERVAL, COUNT): that is a recurrence engine; this
  library covers the BYDAY piece that recurrence engines share.
- Non-Gregorian calendars and years outside 1..9999: `datetime` does not represent them.
