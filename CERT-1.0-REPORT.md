# nthweekday 1.0.0 certification report

The 1.0.0 certification bar (19 items) applied to nthweekday. PyPI has no release of
the name (`https://pypi.org/pypi/nthweekday/json` answered 404 on 2026-10-24), so 1.0.0
is the first upload and there is no upgrade path to check; every change is listed
against 0.2.0 on `main` (5adde42).

Progress:
- [x] Branch `release/1.0.0` created from `main` (5adde42)
- [x] Baseline gates on 0.2.0
- [x] API review and 1.0.0 changes (item 1)
- [x] Errors, typing, docstrings and doctests (items 2 to 5)
- [x] Ground truth re-fetched, grammar and oracles (item 7)
- [x] Contract, fuzz and author mutation round (items 6, 9, 18)
- [x] Docs: README, GUIDE, CHANGELOG (items 11, 12)
- [x] Packaging, e2e, every Python (items 8, 10, 13, 14)
- [x] Gates (item 15)
- [x] PR and trace guard
- [ ] Five QA lenses report PASS (item 19)
- [ ] Independent reviewer reports PASS (item 16)

## Scorecard

| # | Item | Result |
| --- | --- | --- |
| 1 | Public API reviewed for stability | PASS: 20 names kept from 0.2.0; signatures, defaults and return types pinned by `tests/test_contract_api.py`; changes in CHANGELOG |
| 2 | `__all__` exact, no private imports in docs | PASS: `tests/test_contract.py`, `tests/test_docs_examples.py` |
| 3 | Docstrings with runnable examples, doctests | PASS: 43 doctests found from the package top, every public name covered; README (21) and GUIDE (34) results run as tests |
| 4 | Typed end to end | PASS: `mypy --strict src tests`, `py.typed` shipped, a consumer script type-checks against the installed wheel |
| 5 | Typed, documented, bounded errors | PASS: `NoSuchDayError` (a `ValueError`), `ValueError`, `TypeError`; messages quote at most 40 characters and never print a huge integer |
| 6 | Contract tests of every public name | PASS |
| 7 | Real ground truth | PASS: 5 sources re-fetched 2026-10-24 (hashes unchanged), grammar read from the RFC text, `python-dateutil` and `calendar` oracles |
| 8 | Real e2e from the wheel | PASS: built wheel in a fresh venv, CLI by subprocess, consumer typing; no PyPI release to upgrade from |
| 9 | Seeded fuzz, no crash, hang or blowup | PASS: `tests/test_fuzz.py` |
| 10 | Supported Pythons | PASS: CPython 3.10.19, 3.11.5, 3.12.12, 3.13.2, 3.14.2, 3.14.2t (389 passed each); 3.8 and 3.9 below `requires-python` (pip refuses the wheel on 3.9.25) |
| 11 | README and `twine check` | PASS: `twine check --strict` on wheel and sdist, absolute links, badge |
| 12 | Dated CHANGELOG section | PASS: 1.0.0, 2026-10-24 |
| 13 | pyproject 1.0.0, Production/Stable | PASS |
| 14 | sdist and wheel contents | PASS |
| 15 | Gates each exit 0 | PASS: see Gates |
| 16 | Independent reviewer | pending (orchestrator) |
| 17 | PR and trace guard | PR from `release/1.0.0`, trace guard CLEAN; merge and publish left to the maintainer |
| 18 | Contracts bite (mutations) | PASS: author round 30 of 30 killed |
| 19 | Five independent QA lenses | pending (orchestrator) |

## Baseline on 0.2.0 (before any change)

On `release/1.0.0` at 5adde42: `ruff format --check .`, `ruff check .` and
`mypy --strict src tests` exit 0. Defects found in 0.2.0 by reading and then reproducing:

- `nth_weekday(10**5000, 1, 0, 1)` failed while building its own message ("Exceeds the
  limit (4300 digits) for integer string conversion") instead of naming the argument.
- `parse_byday("x" * 1000)` gave a 2,028 character message; `Weekday.parse` and the
  command line quoted their whole input too.
- `byday_dates(2026, 1, 5)` let `'int' object is not iterable` through.
- `next_weekday(date(9999, 12, 31), SATURDAY)` raised a plain `ValueError`, while every
  other absent day raises `NoSuchDayError`.
- No public docstring had a runnable example; there was no GUIDE; the README linked
  LICENSE relatively; the public classes pickled through their private modules;
  `release.ps1` refused any upload once the name existed on PyPI.

## API review (item 1)

Kept: the twenty public names of 0.2.0 with their parameter names, defaults and return
types. Changed, all in the CHANGELOG: `NoSuchDayError` for steps past the calendar
limits, `TypeError` with its own message from `byday_dates`, bounded messages, the
module of every public name is `nthweekday`. Internal: `_month.py` split in two
(`_relative.py` holds the questions about a date) to keep files under 200 lines with
the new examples.

## Ground truth (item 7)

Fetched on 2026-10-24 by `scripts/fetch_upstream.py` into the ignored `data/upstream`
folder; `data/upstream/MANIFEST.json` records URL, revision, size, sha256 and licence,
and all five downloads matched the hashes pinned on 2026-10-13. Nothing fetched is
committed or shipped.

- RFC 5545 (https://www.rfc-editor.org/rfc/rfc5545.txt): `tests/test_rfc5545_grammar.py`
  reads the `bywdaylist`, `weekdaynum`, `plus`, `minus`, `ordwk` and `weekday` ABNF
  rules, the "1 to 53" comment and the code-to-day comment out of the text, turns them
  into a regular expression with an ABNF reader written in the test, and compares it
  with `parse_byday` on all 271,453 strings of up to five characters over a
  12-character alphabet and on 20,000 seeded random lists. The BYDAY examples of
  section 3.8.5.3 and 3.6.5 are vectors located in the fetched text.
- 5 U.S.C. 6103 and the OPM federal holiday pages for 2011 to 2030; the Banking and
  Financial Dealings Act 1971 schedule 1 and the GOV.UK bank holidays dataset.
- `python-dateutil` 2.9.0.post0 `rrule`, run in the suite: every (year, month, weekday,
  n) from 1990 to 2040, year ordinals 1 to 53 at the calendar limits, random lists.
- The standard `calendar` module: every month of the 400-year Gregorian cycle
  2000 to 2399 and of the years 1 to 100 and 9900 to 9999, every weekday and ordinal.
- Verified facts for the README comparison, run on 2026-10-24 with dateutil
  2.9.0.post0: `relativedelta(day=1, weekday=MO(5))` from 2026-09-01 gives 2026-10-05;
  `rrule(MONTHLY, byweekday=[FR, FR(1)])` gives only 2026-10-02 in October 2026;
  `byweekday=[MO(20)]` raises `IndexError`; `calendar` on 3.14.2 has no nth weekday
  function.

## Fuzz and hostile input (item 9)

`tests/test_fuzz.py`: 60,000 seeded hostile strings (lone surrogates, NUL, look-alike
letters, long runs) through `parse_byday`: only `ValueError`, messages under 300
characters, every accepted value round trips through `str`; 900 random BYDAY lists and
1,800 nth queries against a day-by-day walk of the calendar; 800 random command lines
exit 0, 1 or 2 with short messages; five input shapes timed at 20,000 and 160,000
units (linear); 1 MB strings, integers past 5,000 digits and 150,000-entry lists.

## Author mutation round (item 18)

30 mutants over every module, each applied alone to a fresh copy of the tree (fetched
sources present), the full suite run with `-x` and a 300 s per-test limit. All 30
killed; the column shows the first failing test.

| # | File | Mutation | Verdict | First test that failed |
| --- | --- | --- | --- | --- |
| M1 | `_month.py` | month range drops the last day | killed | `test_fuzz.py::test_nth_queries_match_a_day_by_day_walk[0]` |
| M2 | `_month.py` | positive ordinal off by one | killed | `test_byday.py::test_byday_dates_yearly_absent_53rd_selects_nothing` |
| M3 | `_month.py` | -5 refused in a month | killed | `test_contract_api.py::test_absent_days_raise_no_such_day_error_and_nothing_else` |
| M4 | `_month.py` | leap years lose 31 December | killed | `test_fuzz.py::test_byday_dates_match_a_day_by_day_walk[0]` |
| M5 | `_month.py` | ordinal word "13rd" | killed | `test_year.py::test_ordinal_words_use_the_right_suffix` |
| M6 | `_month.py` | absent day raises plain `ValueError` | killed | `test_byday.py::test_byday_dates_yearly_absent_53rd_selects_nothing` |
| M7 | `_relative.py` | ordinal from the end off by one | killed | `test_docs_examples.py::test_documented_results_are_true[README.md-20]` |
| M8 | `_relative.py` | `week_of_month` operands swapped | killed | `test_docs_examples.py::test_documented_results_are_true[README.md-20]` |
| M9 | `_relative.py` | strict step skips the wrong day | killed | `test_contract_api.py::test_absent_days_raise_no_such_day_error_and_nothing_else` |
| M10 | `_relative.py` | step past 9999 raises plain `ValueError` | killed | `test_contract_api.py::test_absent_days_raise_no_such_day_error_and_nothing_else` |
| M11 | `_relative.py` | `datetime` in gives `datetime` out | killed | `test_relative.py::test_next_weekday_returns_a_date_for_a_datetime` |
| M12 | `_byday.py` | three-digit ordinals accepted | killed | `test_byday.py::test_parse_rejects_anything_outside_the_grammar[001MO]` |
| M13 | `_byday.py` | ordinal 54 accepted by the parser | killed | `test_cli.py::test_bad_input_exits_2[args5]` |
| M14 | `_byday.py` | non-ASCII look-alikes accepted | killed | `test_byday.py::test_non_ascii_letters_are_reported_as_invalid_entries` |
| M15 | `_byday.py` | monthly negative ordinal off by one | killed | `test_byday.py::test_byday_dates_accepts_what_parse_byday_returns` |
| M16 | `_byday.py` | `byday_dates` result unsorted | killed | `test_byday.py::test_byday_dates_monthly_plain_weekday_is_every_one` |
| M17 | `_byday.py` | `str(ByDay)` writes the code first | killed | `test_byday.py::test_str_gives_back_the_canonical_form[1MO]` |
| M18 | `_byday.py` | `ByDay` refuses 53 | killed | `test_byday.py::test_parse_follows_the_weekdaynum_grammar[53MO-53]` |
| M19 | `_weekday.py` | ISO number off by one | killed | `test_docs_examples.py::test_documented_results_are_true[README.md-20]` |
| M20 | `_weekday.py` | SA and SU codes swapped | killed | `test_byday.py::test_parse_single_and_list_entries` |
| M21 | `_weekday.py` | `bool` accepted as an integer | killed | `test_byday.py::test_byday_validates_its_fields` |
| M22 | `_weekday.py` | escaped quotes no longer bounded | killed | `test_contract_api.py::test_messages_quote_at_most_40_characters_and_no_huge_number` |
| M23 | `_weekday.py` | huge integers printed in messages | killed | `test_contract_api.py::test_messages_quote_at_most_40_characters_and_no_huge_number` |
| M24 | `_weekday.py` | weekday names case-sensitive | killed | `test_byday.py::test_parse_is_case_insensitive` |
| M25 | `_cli.py` | no match exits 0 | killed | `test_cli.py::test_nothing_matched_exits_1` |
| M26 | `_cli.py` | the yearly listing skips December | killed | `test_cli.py::test_signed_byday_is_not_taken_for_an_option` |
| M27 | `_cli.py` | `--yearly` check inverted | killed | `test_cli.py::test_options_may_come_after_a_signed_byday` |
| M28 | `__init__.py` | public names keep private modules | killed | `test_contract_api.py::test_public_names_report_the_package_as_their_module` |
| M29 | `_month.py` | `last_weekday` gives the second to last | killed | `test_docs_examples.py::test_documented_results_are_true[README.md-20]` |
| M30 | `_byday.py` | a single `ByDay` selects nothing | killed | `test_byday.py::test_byday_dates_accepts_a_byday_value` |

## Packaging, e2e and Pythons (items 8, 10, 13, 14)

- `python -m build` and `twine check --strict` pass for `nthweekday-1.0.0.tar.gz` and
  `nthweekday-1.0.0-py3-none-any.whl`. The wheel holds the seven modules, `py.typed`,
  `entry_points.txt` and `licenses/LICENSE`; its metadata has no runtime requirement.
  The sdist holds the sources, tests, scripts, README, GUIDE, CHANGELOG, CONTRIBUTING,
  LICENSE and the upstream manifest, and no fetched copy, report or cache.
- `pytest -m e2e`: the wheel installed in a fresh venv, the `nthweekday` script and
  `python -m nthweekday` driven by subprocess (exit 0, 1, 2, `--version`), a consumer
  script type-checked with `mypy --strict` against the installed package and run with
  `-I` from an empty folder.
- Every interpreter on this PC from `requires-python` up, the wheel installed in a
  fresh venv and the sdist's own suite run with `src` removed and the fetched sources
  present: CPython 3.10.19, 3.11.5, 3.12.12, 3.13.2, 3.14.2 and 3.14.2 free-threaded
  (GIL disabled), 389 passed, 0 skipped each.

## Gates (item 15)

On this PC with the fetched sources present, each command on its own:
`ruff format --check .`, `ruff check .`, `mypy --strict src`, `mypy --strict src tests`
and `pytest` (389 passed, the two opt-in e2e tests deselected) exit 0;
`pytest -m e2e` 2 passed.

## QA lenses (item 19) and independent review (item 16)

Pending; run by the maintainer on fresh reviewers after this preparation stage.
