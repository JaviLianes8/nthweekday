# nthweekday 1.0.0 certification report

The 1.0.0 certification bar (19 items) applied to nthweekday. PyPI has no release of
the name (`https://pypi.org/pypi/nthweekday/json` answered 404 on 2026-10-24 and again
on 2026-10-25), so 1.0.0 is the first upload and there is no upgrade path to check;
every change is listed against 0.2.0 on `main` (5adde42).

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
- [x] QA lenses round 1: every finding fixed (fcbfc64 and the report commit)
- [x] Author follow-up: three more surviving mutants closed, one defect fixed (d89a99f)
- [x] Resumed 2026-10-25: PyPI re-checked (404), CHANGELOG dated 2026-10-25, gates re-run
- [x] QA lenses round 2 (a, c, e on 5c2d0db): every finding fixed (86ef53e and the report commit)
- [x] QA lenses round 3 (a, c, e on 057be74): every finding fixed (9a5b316, 886daf0, 7921b71 and the report commit)
- [x] QA lenses round 4 (a, e on ad36216): every finding fixed (f470e34 and the report commit)
- [x] QA lenses round 5 (a, e on 558ce09): every finding fixed (47e6b79 and the report commit)
- [x] QA lenses round 6 (a on ea1f46c): every finding fixed (6f41373 and the report commit)
- [ ] Five QA lenses report PASS (item 19)
- [ ] Independent reviewer reports PASS (item 16)

## Scorecard

| # | Item | Result |
| --- | --- | --- |
| 1 | Public API reviewed for stability | PASS: 20 names kept from 0.2.0; signatures, defaults and return types pinned by `tests/test_contract_api.py`; changes in CHANGELOG |
| 2 | `__all__` exact, no private imports in docs | PASS: `tests/test_contract.py`, `tests/test_docs_examples.py` |
| 3 | Docstrings with runnable examples, doctests | PASS: 44 examples in 17 docstrings, pinned exactly, every public name covered; README (21) and GUIDE (37) results run as tests, counts pinned |
| 4 | Typed end to end | PASS: `mypy --strict src tests`, `py.typed` shipped, a consumer script type-checks against the installed wheel; integer parameters typed `SupportsIndex` for mypy and pyright (`Weekday(value)` included), checked by `tests/test_typing.py` on every interpreter (mypy, and pyright when installed) and `tests/test_weekday_call.py`; an unpacked call such as `Weekday(*[3])` type-checks under both; the calls both checkers must refuse (`Weekday(None)`, `Weekday("MO")`, `Weekday(4.0)`, extra arguments) pinned by `tests/test_typing.py` |
| 5 | Typed, documented, bounded errors | PASS: `NoSuchDayError` (a `ValueError`), `ValueError`, `TypeError`; messages quote at most 40 characters and never print a huge integer |
| 6 | Contract tests of every public name | PASS |
| 7 | Real ground truth | PASS: 5 sources re-fetched 2026-10-24 (hashes unchanged), grammar read from the RFC text, `python-dateutil` and `calendar` oracles |
| 8 | Real e2e from the wheel | PASS: built wheel in a fresh venv, CLI by subprocess, consumer typing; no PyPI release to upgrade from |
| 9 | Seeded fuzz, no crash, hang or blowup | PASS: `tests/test_fuzz.py`; QA round 3 replay of lens (c)'s 60,000-argv corpus on 3.10 to 3.14: no problem, no difference between versions |
| 10 | Supported Pythons | PASS: CPython 3.10.19, 3.11.5, 3.12.12, 3.13.2, 3.14.2, 3.14.2t (486 passed, numpy test skipped, each; QA round 3); 3.8 and 3.9 below `requires-python` (pip refuses the wheel on 3.9.25) |
| 11 | README and `twine check` | PASS: `twine check --strict` on wheel and sdist, absolute links, badge |
| 12 | Dated CHANGELOG section | PASS: 1.0.0, 2026-10-25 |
| 13 | pyproject 1.0.0, Production/Stable | PASS |
| 14 | sdist and wheel contents | PASS |
| 15 | Gates each exit 0 | PASS: see Gates |
| 16 | Independent reviewer | pending (orchestrator) |
| 17 | PR and trace guard | PR from `release/1.0.0`, trace guard CLEAN; merge and publish left to the maintainer |
| 18 | Contracts bite (mutations) | PASS: author round 30 of 30 killed; round 1 follow-ups 14 of 14; author follow-up 4 of 4; QA round 2 fixes 10 of 10; QA round 3 fixes 19 of 19; QA round 4 fixes 7 of 7; QA round 5 fixes 6 of 6 |
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
and `pytest` (487 passed after QA round 3, the two opt-in e2e tests deselected)
exit 0; `pytest -m e2e` 2 passed.

## QA lenses (item 19) and independent review (item 16)

### Round 1

Five fresh reviewers, one per lens, on `release/1.0.0` at 6b2fd91. Lens (b) reported no
finding. Every other finding was fixed in fcbfc64, with the direct `quote()` check and
the exact README and GUIDE counts added in the commit that records this round; each
behaviour fix has a contract test
that failed on 6b2fd91 (the `format()` test fails there on Python 3.10 only, where the
behaviour differed) and passes now.

| Lens | Id | Finding | Fix | Contract |
| --- | --- | --- | --- | --- |
| a, d | a-F1, d-F2 | `format()` of a `Weekday` differed between 3.10 and 3.11+; `f"{FRIDAY:d}"` failed on 3.10 | `Weekday.__format__`: the name without a spec, `int` formatting with one; GUIDE and docstring | `test_contract_edges.py::test_format_gives_the_name_without_a_spec_and_formats_the_number_with_one` |
| a, c | a-F2, c-F2 | `Weekday(x)` skipped the argument checks (`Weekday(True)`, `Weekday(4.0)`, `Weekday("4")`, `Weekday(10**5000)`) | a metaclass `__call__` runs the shared check before the lookup | `test_contract_edges.py::test_the_constructor_checks_its_argument_like_every_function` |
| a | a-F3 | `ByDay` was typed `weekday: Weekday`, so `ByDay(date.weekday(), -1)` failed `mypy --strict` | explicit `__init__(weekday: int, ordinal: int \| None = None)`; the field stays a `Weekday`; pinned signature updated | `test_contract_api.py::test_class_signatures_are_pinned`, `test_contract_edges.py::test_byday_takes_an_int_weekday_and_stores_a_weekday`, e2e consumer under `mypy --strict` |
| a | a-F4 | CHANGELOG: undated 0.2.0 and 0.1.0, no link definitions | dates from git (2026-10-13, 2026-10-12) and link definitions for every version | docs |
| c | c-F1 | argparse errors repeated unknown options and extra arguments in full | an option-like argument over 40 characters is refused with `quote()`; extra arguments are reported through `quote()` | `test_contract_edges.py::test_command_line_errors_quote_at_most_40_characters` (9 vectors) |
| c | c-F3 | numpy 1.x `bool_` passed as 0/1 | `_as_int` refuses numpy's bool scalar by type | `test_contract_edges.py::test_numpy_bool_scalars_are_refused_like_bool`, `test_real_numpy_bools_are_refused` |
| c | c-F4 | `quote()` and the parsers called a `str` subclass's own `__repr__`, `upper`, `split` | the text is read through `str.__str__` first | `test_contract_edges.py::test_str_subclasses_are_read_as_plain_strings` |
| d | d-F1 | `inspect.getsource` failed for `ByDay`, `Weekday`, `NoSuchDayError` (wrong source on 3.13+) because their `__module__` was rewritten | the classes keep their defining module; only the functions are rewritten; GUIDE Stability says which module pickles of the classes name and that it stays importable in 1.x | `test_contract_edges.py::test_public_classes_keep_their_source_and_functions_report_the_package`, `test_pickles_of_the_classes_load_from_their_defining_modules`, `test_contract_api.py::test_functions_report_the_package_and_classes_their_defining_module` |
| d | d-F3 | the sdist shipped CONTRIBUTING without `requirements-dev.txt` | added to the sdist include list | `test_e2e_wheel.py::test_sdist_ships_the_manifest_but_no_upstream_copies` |
| e | e-F1 (W25) | no test bounded `TypeError` messages | none needed | `test_contract_edges.py::test_type_errors_name_the_type_and_never_the_value` (10 entry points) |
| e | e-F2 (X01) | `python -m nthweekday` exit codes were not pinned | none needed | `test_cli.py::test_python_m_exits_with_the_code_of_main`, and the e2e test runs exit 1 and 2 through `python -m` |
| e | e-F3 (P05) | the method `__module__` rewrite was untested and the doctest test had a floor | the method rewrite is gone with d-F1 (methods keep their module, like their classes); the doctest test pins the exact 17 docstrings and 44 examples, collected from the package and from each class | `test_docs_examples.py::test_every_public_name_has_a_docstring_example_that_passes` |
| e | e-F4 (C14) | `-h` after a signed BYDAY was not pinned | none needed | `test_cli.py::test_options_may_come_after_a_signed_byday` |
| e | e-F5 (C15) | an explicit `--` was not pinned | none needed | `test_cli.py::test_an_explicit_double_dash_keeps_a_signed_byday` |
| e | e-F6 (M17, M20) | year padding below 1000 in messages was not pinned | none needed | `test_year.py::test_years_below_1000_are_padded_to_four_digits_in_messages` |

Lens (e)'s P05 asked for a test that methods report `nthweekday` as their module. That
promise conflicted with d-F1 (a class and its methods must name the file that defines
them for `inspect.getsource`), so the GUIDE no longer makes it; the risk P05 showed,
docstrings silently dropped, is closed by the exact doctest list.

Behaviour changes, all in the CHANGELOG 1.0.0 section: `Weekday(n)` checks `n`;
`format()` of a `Weekday` with a spec formats the number on 3.10 too; `ByDay` accepts
`weekday: int` in its signature; numpy 1.x bool scalars raise `TypeError`; `str`
subclasses are read as plain text; the command line bounds every error; the classes keep
their defining module.

Re-verified after the fixes, on this PC under a machine turn: the sdist built from the
tree and the wheel built from the sdist pass `twine check --strict`; the sdist now holds
`requirements-dev.txt`. The wheel installed in a fresh venv per interpreter and the
sdist's suite run with `src` removed and the fetched sources present: CPython 3.10.19,
3.11.5, 3.12.12, 3.13.2, 3.14.2 and 3.14.2 free-threaded, 418 passed and 1 skipped (the
real numpy test, numpy absent) on each. With numpy 1.26.4 on 3.11.5,
`nth_weekday(2026, np.bool_(True), ...)` raises `TypeError` and the edge contracts pass.
`pytest -m e2e`: 2 passed. Gates on the tree: `ruff format --check .`, `ruff check .`,
`mypy --strict src`, `mypy --strict src tests` and `pytest` (419 passed) exit 0.

Mutants for this round, each applied alone to a copy of the tree, full suite with `-x`:

| # | Mutation | Verdict | First test that failed |
| --- | --- | --- | --- |
| W25 | `TypeError` message shows `repr(value)` | killed | `test_contract_edges.py::test_numpy_bool_scalars_are_refused_like_bool` |
| X01 | `__main__` drops `sys.exit` | killed | `test_cli.py::test_python_m_exits_with_the_code_of_main` |
| P05 | functions keep their private module | killed | `test_contract_api.py::test_functions_report_the_package_and_classes_their_defining_module` |
| C14 | only `--` flags moved before a signed BYDAY | killed | `test_cli.py::test_options_may_come_after_a_signed_byday` |
| C15 | user `--` guard removed | killed | `test_cli.py::test_an_explicit_double_dash_keeps_a_signed_byday` |
| M17 | year message unpadded in `nth_weekday_in_year` | killed | `test_year.py::test_years_below_1000_are_padded_to_four_digits_in_messages` |
| M20 | year message unpadded in `nth_weekday` | killed | `test_year.py::test_years_below_1000_are_padded_to_four_digits_in_messages` |
| N1 | `Weekday(x)` check removed | killed | `test_contract_edges.py::test_the_constructor_checks_its_argument_like_every_function` |
| N2 | numpy bool check removed | killed | `test_contract_edges.py::test_numpy_bool_scalars_are_refused_like_bool` |
| N3 | `parse_byday` uses the subclass's methods | killed | `test_contract_edges.py::test_str_subclasses_are_read_as_plain_strings` |
| N4 | `quote()` uses the subclass's `__repr__` | killed (after adding a direct `quote()` check; it survived the first run) | `test_contract_edges.py::test_str_subclasses_are_read_as_plain_strings` |
| N5 | long option check removed | killed | `test_contract_edges.py::test_command_line_errors_quote_at_most_40_characters[args4]` |
| N6 | extra arguments not quoted | killed | `test_contract_edges.py::test_command_line_errors_quote_at_most_40_characters[args0]` |
| N7 | `ByDay` stores the int unconverted | killed | `test_byday.py::test_byday_validates_its_fields` |

### Author follow-up after round 1

Three further mutants on the round 1 fixes survived a run of the suite at 9b5bfb3; each
pointed at a missing contract, and one at a real defect.

- `Weekday(x, *args, **kwargs)` passed any extra argument to the enum machinery. A
  keyword alone made it an unchecked lookup again (`Weekday(True, module=None)` gave
  `Weekday.TUESDAY`), and `Weekday("x" * 10**6, "y")` raised a `ValueError` of
  1,000,032 characters. Fixed: `Weekday()` takes exactly one argument and raises a fixed
  `TypeError` for anything more (the functional API cannot extend an enum with members, so
  no working call is lost). CHANGELOG and GUIDE updated.
- The numpy bool check names `bool_` (numpy 1.x) and `bool` (numpy 2.x); only the first
  name was tested. Checked on this PC: numpy 1.26.4 on 3.11.5 has `numpy.bool_` with
  `__index__`, numpy 2.3.4 on 3.13.2 has `numpy.bool` without it; both raise `TypeError`
  and the edge contracts pass with each installed.
- The long-option guard was only tested far past the limit; an option of 41 to 80
  characters was not pinned, and argparse repeats an explicit argument in full.

| # | Mutation | Verdict | First test that failed |
| --- | --- | --- | --- |
| S06 | extra keywords passed through to the lookup | killed | `test_contract_edges.py::test_the_constructor_checks_its_argument_like_every_function` |
| S06b | extra arguments passed through to the enum machinery | killed | `test_contract_edges.py::test_the_constructor_checks_its_argument_like_every_function` |
| S15 | numpy 2.x `bool` name dropped | killed | `test_contract_edges.py::test_numpy_bool_scalars_are_refused_like_bool[bool]` |
| S28 | long-option guard at 80 characters instead of 40 | killed | `test_contract_edges.py::test_an_option_past_the_quote_limit_is_cut[41]` |

Re-verified under a machine turn on this PC: `pytest` 425 passed, `pytest -m e2e` 2
passed; the sdist and the wheel built from it pass `twine check --strict`, with the same
contents as before; the wheel in a fresh venv and the sdist's suite with `src` removed and
the fetched sources present on CPython 3.10.19, 3.11.5, 3.12.12, 3.13.2, 3.14.2 and 3.14.2
free-threaded: 424 passed and 1 skipped (the real numpy test, numpy absent) on each.

Disputed findings: none.

### Round 2

Lenses (a), (c) and (e) reviewed `release/1.0.0` at 5c2d0db and reported the findings
below. Every one is fixed in 86ef53e. Each behaviour fix has a contract test that failed
on 5c2d0db (run with the new tests on Python 3.10.19 and 3.13.2: 12 failed on 3.10, 6 on
3.13, where argparse already handles a second `--` and is not quadratic) and passes now.
e-F1 was a missing contract, not a defect: its test passes on 5c2d0db and kills the
mutant.

| Lens | Id | Finding | Fix | Contract |
| --- | --- | --- | --- | --- |
| a | a-F1 | `Weekday(n)` was typed `Any` for pyright (metaclass `__call__` returned `Any`) | `__call__(cls: type[_E], value: object, ...) -> _E`; pyright 1.1.405 strict on the lens's probe now reveals `Weekday` and reports the attribute and assignment errors (0 errors and `Any` on 5c2d0db) | `test_weekday_call.py::test_the_call_is_typed_to_return_the_class_it_is_called_on` |
| a | a-F2 | `inspect.signature(Weekday)` and `help(Weekday)` showed `(value: Any, *args, **kwargs)` before 3.12 and `(*values)` after | the metaclass gives `__signature__` as `(value)` | `test_weekday_call.py::test_the_signature_is_one_value_on_every_version` |
| a, c | a-F3, c-C1 | a signed BYDAY followed by `--` was read as an option (exit 2 on 3.10 to 3.13); a second `--` crashed on 3.10 and 3.11 (traceback, exit 1) | the command line splits its arguments itself in one pass: after the first `--` everything is a value, before it a signed BYDAY is a value; argparse only sees the options and stand-ins for the values, so its version-dependent `--` handling no longer matters; GUIDE and CHANGELOG | `test_cli_arguments.py::test_a_signed_byday_before_a_double_dash_is_still_a_value`, `test_a_second_double_dash_is_a_value` (4 argvs), `test_values_are_read_in_order_and_the_rest_is_refused` |
| c | c-C2 | sorting out the arguments was quadratic (`a not in flags` on a list) | the one-pass split; argparse itself is quadratic in the number of options before 3.12, so each distinct option is read on its own and an unknown option given several times is reported once (CHANGELOG) | `test_cli_arguments.py::test_splitting_the_arguments_takes_linear_time` (3 shapes, 2,000 against 16,000 arguments) |
| a, c | a-F4, c-C3 | `byday_dates` replaced an error of the caller's iterable with its own message and read a wrong-typed iterable to the end (`itertools.count()` never returned) | only `iter(value)` is guarded; entries are checked one at a time while read, so the first wrong entry stops the read; CHANGELOG | `test_byday.py::test_byday_dates_lets_errors_of_the_callers_iterable_through`, `test_byday_dates_stops_at_the_first_entry_of_the_wrong_type` |
| e | e-F1 (B16) | no contract for a falsy month that is not `None` (`False`, `0`) | none needed | `test_byday.py::test_byday_dates_checks_a_falsy_month` (string, `ByDay` and list values) |

Replayed on the fixed tree, on CPython 3.10.19, 3.11.5, 3.12.12, 3.13.2 and 3.14.2:
`nthweekday 2026-11 -1FR --` prints 2026-11-27 and exits 0, `nthweekday 2026 -1FR
--yearly --` prints 2026-12-25, `nthweekday 2026 -- --` and `nthweekday -- 2026 --`
exit 2 with `invalid BYDAY entry '--'`, and `inspect.signature(Weekday)` is `(value)`.
The lens's generator raising `TypeError` comes through with its own message and
`__suppress_context__` false; an iterator of 10**7 ints is read once before the
`TypeError`. A differential run of 29 argvs through `main` on 3.10 and 3.13 (help,
version, abbreviations, unknown and long options, `--` placements, `-`, `+1FR`) gives
the same exit code and output as 5c2d0db except the documented single report of a
repeated unknown option.

Mutants on these fixes, each applied alone to a copy of the tree, the new and the CLI
test files run with `-x` on 3.10.19 and 3.13.2:

| # | Mutation | Verdict | First test that failed |
| --- | --- | --- | --- |
| R01 | values after the first `--` dropped instead of read | killed | `test_cli_arguments.py::test_a_second_double_dash_is_a_value[args0]` |
| R02 | a signed BYDAY taken for an option | killed | `test_cli_arguments.py::test_a_signed_byday_before_a_double_dash_is_still_a_value` |
| R03 | repeated options not collapsed | killed (survived on 3.13 until the single-report vector was added) | `test_cli_arguments.py::test_values_are_read_in_order_and_the_rest_is_refused[args5]`; on 3.10 also the linear-time test |
| R04 | values past the second ignored | killed | `test_cli_arguments.py::test_values_are_read_in_order_and_the_rest_is_refused[args3]` |
| R05 | iterable read whole before the type check | killed | `test_byday.py::test_byday_dates_stops_at_the_first_entry_of_the_wrong_type` |
| R06 | `tuple(value)` back inside the guard | killed | `test_byday.py::test_byday_dates_lets_errors_of_the_callers_iterable_through` |
| R07 | `__signature__` removed | killed | `test_weekday_call.py::test_the_signature_is_one_value_on_every_version` |
| R08 | `__call__` annotated `-> Any` again | killed | `test_weekday_call.py::test_the_call_is_typed_to_return_the_class_it_is_called_on` |
| R09 | `--` honoured only in first position | killed | `test_cli_arguments.py::test_a_second_double_dash_is_a_value[args0]` |
| B16 | `if month:` for `if month is not None:` (lens e) | killed | `test_byday.py::test_byday_dates_checks_a_falsy_month[MO]` |

Re-verified under a machine turn on this PC: `pytest` 446 passed, `pytest -m e2e` 2
passed; the sdist and the wheel built from it pass `twine check --strict`, the wheel holds
the package, `py.typed`, the entry point and LICENSE only; the wheel in a fresh venv and
the sdist's suite with `src` removed and the fetched sources present on CPython 3.10.19,
3.11.5, 3.12.12, 3.13.2, 3.14.2 and 3.14.2 free-threaded: 445 passed and 1 skipped (the
real numpy test, numpy absent) on each (the first 3.11.5 run printed no summary line; it
was run again on its own and passed). Gates on the tree: `ruff format --check .`,
`ruff check .`, `mypy --strict src`, `mypy --strict src tests` and `pytest` exit 0.

Disputed findings (round 2): none.

### Round 3

Lenses (a), (c) and (e) reviewed `release/1.0.0` at 057be74 and reported the findings
below. Every one is fixed in 9a5b316, 886daf0 and 7921b71. The behaviour contracts were
added first and run on 057be74 with Python 3.13.2: the flag tests (9), the BYDAY message
tests (5, the updated surrogate count included), the typing test (20 mypy errors) and the
option tests (14) failed there and pass now. e-F2 to e-F5 were missing contracts, not
defects: their tests pass on 057be74 and kill the lens's mutants (table below).

| Lens | Id | Finding | Fix | Contract |
| --- | --- | --- | --- | --- |
| a | a-F1 | `strict` and `from_end` were read by truth value (`from_end="no"` gave -3, `strict=None` passed) | checked with the other arguments: a `bool` or numpy's bool scalar, `TypeError` otherwise; GUIDE table row and paragraph, README, CHANGELOG | `test_relative.py::test_the_keyword_flags_take_a_bool_and_nothing_else` (8 values, 3 calls), `test_the_keyword_flags_are_checked_before_anything_is_computed`, `test_the_keyword_flags_take_numpy_bool_scalars_as_bools` |
| a | a-F2 | `invalid BYDAY entry X in Y` quoted two 40-character pieces, up to 80 characters of input | the bad entry is quoted once, followed by its place in a list, `(entry 21 of 21)`; CHANGELOG | `test_contract_api.py::test_a_bad_byday_entry_is_quoted_once_with_its_position` (4 vectors); the surrogate count in `test_messages_quote_at_most_40_characters_and_no_huge_number` is now one piece |
| a | a-F3 | the CHANGELOG said 0.2.0 crashed on `nthweekday 2026 -- --` | reworded: 0.2.0 (5adde425) on 3.10.19 and 3.11.5 prints `[] selects no date in 2026` and exits 1, replayed here; the traceback belonged to 5c2d0db (`str.__str__` on a list), replayed too | docs |
| a | a-F4 | the integer parameters were annotated `int`, so a numpy integer failed mypy and pyright although it ran | every integer parameter is typed `typing.SupportsIndex`, and `Weekday` declares a `__new__(value: SupportsIndex)` for type checkers only (mypy reads an enum call through `__new__`); pinned signatures updated; GUIDE, README, CHANGELOG | `test_typing.py::test_any_integer_type_type_checks_where_an_integer_is_asked_for` (mypy `--strict` on a caller of the 11 integer entry points with an `__index__` class, against the source tree and against the installed wheel), the e2e consumer, the pinned signatures in `test_contract_api.py`. pyright 1.1.414 strict on the lens's probe: 0 errors, `Weekday(np.int64(4))` is `Weekday`; mypy with numpy 2.3.5 accepts numpy integers in `Weekday`, `ByDay` and `nth_weekday` |
| c | c-C1 | `--=...` (and `-=...` on 3.12+) reached stderr unescaped through argparse's "ambiguous option" error | options are read by hand with one rule: `-h`, or a prefix of exactly one of `--help`, `--version`, `--yearly`; anything else that starts with `-` is unknown and reported through `quote()`; argparse only sees the canonical names, each once, and stand-ins for the values | `test_cli_options.py::test_errors_never_write_an_unprintable_character` (6 options, before and after the values) |
| c | c-C2 | `-help`, `-hx` and `-= 2026 MO --version` gave different exit codes on 3.10/3.11 and 3.12+ | the same rule: unknown on every version, and the first of `-h` and `--version` wins over unknown options; GUIDE, CHANGELOG | `test_malformed_options_are_unrecognized_on_every_version` (9 options), `test_the_first_of_help_and_version_wins_over_anything_else` (7 argvs) |
| e | e-F1 (N37) | the linear-time test let a quadratic de-duplication pass at times | argparse is called once whatever the number of arguments; the old timing test is replaced by a call count and a wider timing ratio | `test_cli_options.py::test_argparse_reads_at_most_the_three_options_and_two_values` (one call with 3 arguments for 20,000 options), `test_reading_the_arguments_takes_linear_time` (1,000 against 64,000 arguments, at most 256 times as long, 3 shapes) |
| e | e-F2 (N46) | `-h` next to an unknown option was not pinned | none needed | `test_the_first_of_help_and_version_wins_over_anything_else` (`-q -h`, `-q --version`, `-= 2026 MO --version`) |
| e | e-F3 (N50) | which of `-h` and `--version` wins was not pinned | none needed | the same test (`-h --version`, `--version -h`, `--vers --he`) |
| e | e-F4 (N14) | `from None` for a non-iterable value was not pinned | none needed | `test_byday.py::test_byday_dates_hides_the_internal_error_of_a_value_that_is_not_iterable` |
| e | e-F5 (N42) | the 40-character boundary of the long-option guard was not pinned | none needed | `test_cli_options.py::test_the_long_option_guard_starts_past_40_characters` (40 and 41 characters, exact messages) |

Behaviour changes, all in the CHANGELOG 1.0.0 section: the flags raise `TypeError` for
anything but a `bool`; a bad BYDAY entry is quoted once with its place; the integer
parameters are typed `SupportsIndex` (the types only widen); `-help`, `-hx`, `--yearly=1`,
`--=x` and `-=x` are unknown options on every version.

Mutants on these fixes, each applied alone to a copy of the tree with the fetched sources,
the whole suite run with `-x` and a 300 s per-test limit on 3.13.2. T08, T11, T13, T14 and
T16 are lens (e)'s N14, N50, N37, N42 and N46 on the new code.

| # | Mutation | Verdict | First test that failed |
| --- | --- | --- | --- |
| T01 | flag check removed | killed | `test_relative.py::test_the_keyword_flags_take_a_bool_and_nothing_else[no]` |
| T02 | `strict` unchecked | killed | `test_relative.py::test_the_keyword_flags_take_a_bool_and_nothing_else[no]` |
| T03 | `strict` checked only when the day itself matches | killed | `test_relative.py::test_the_keyword_flags_are_checked_before_anything_is_computed` |
| T04 | numpy's bool scalar refused as a flag | killed | `test_relative.py::test_the_keyword_flags_take_numpy_bool_scalars_as_bools[bool_]` |
| T05 | the whole value quoted again | killed | `test_contract_api.py::test_messages_quote_at_most_40_characters_and_no_huge_number` |
| T06 | entry place counted from 0 | killed | `test_contract_api.py::test_a_bad_byday_entry_is_quoted_once_with_its_position[list]` |
| T07 | place shown for a single entry | killed | `test_contract_api.py::test_a_bad_byday_entry_is_quoted_once_with_its_position[one]` |
| T08 | `from None` dropped | killed | `test_byday.py::test_byday_dates_hides_the_internal_error_of_a_value_that_is_not_iterable` |
| T09 | `-h<more>` read as `-h` | killed | `test_cli_options.py::test_malformed_options_are_unrecognized_on_every_version[-help]` |
| T10 | `--option=value` read as the option | killed | `test_cli_options.py::test_malformed_options_are_unrecognized_on_every_version[--yearly=1]` |
| T11 | options sorted | killed | `test_cli_options.py::test_the_first_of_help_and_version_wins_over_anything_else[args4-version]` |
| T12 | options not de-duplicated | killed | `test_cli_options.py::test_argparse_reads_at_most_the_three_options_and_two_values` |
| T13 | quadratic de-duplication of unknown options | killed | `test_cli_options.py::test_reading_the_arguments_takes_linear_time[repeated]` |
| T14 | long-option guard at 40 instead of past 40 | killed | `test_cli_options.py::test_the_long_option_guard_starts_past_40_characters` |
| T15 | unknown options passed to argparse | killed | `test_cli_options.py::test_errors_never_write_an_unprintable_character[--=\x1b[2J]` |
| T16 | options read only up to the first unknown one | killed | `test_cli_options.py::test_the_first_of_help_and_version_wins_over_anything_else[args0-version]` |
| T17 | type-checking `Weekday.__new__` typed `int` | killed | `test_typing.py::test_any_integer_type_type_checks_where_an_integer_is_asked_for` |
| T18 | `nth_weekday` `n` typed `int` | killed | `test_contract_api.py::test_function_signatures_are_pinned[nth_weekday]` |
| T19 | `ByDay` `ordinal` typed `int` | killed | `test_contract_api.py::test_class_signatures_are_pinned` |

The linear-time test was run three times each on 3.10.19 and 3.13.2: the tree passed all
six runs (0.4 to 0.6 s for the three shapes), and the T13 mutant failed all three shapes
in all six runs (55 to 78 s).

Re-verified under machine turns on this PC: `python -m build` gives the sdist and the
wheel built from it, both pass `twine check --strict`; the wheel holds the seven modules,
`py.typed`, the entry point and LICENSE only. The wheel in a fresh venv (with mypy, so the
typing contract runs against the installed package) and the sdist's suite with `src`
removed and the fetched sources present on CPython 3.10.19, 3.11.5, 3.12.12, 3.13.2,
3.14.2 and 3.14.2 free-threaded: 486 passed and 1 skipped (the real numpy test, numpy
absent) on each. `pytest -m e2e`: 2 passed. Lens (a)'s and lens (c)'s repros through
`python -m nthweekday` on 3.10.19 and 3.13.2: every stderr printable, the same exit code
and output on both. Lens (c)'s `cli_fuzz.py` (seed 11, 60,000 argv) on 3.10.19, 3.11.5,
3.12.12, 3.13.2 and 3.14.2: no problem on any, and `cli_compare.py` finds no exit code or
stdout difference between them (4,079 on 057be74). Gates on the tree: `ruff format
--check .`, `ruff check .`, `mypy --strict src`, `mypy --strict src tests` and `pytest`
(487 passed) exit 0.

Disputed findings (round 3): none.

### Round 4

Lenses (a) and (e) reviewed `release/1.0.0` at ad36216. Lens (a) found every round 3
finding fixed and reported one gap; lens (e) found its five earlier findings killed and
reported five surviving mutants out of 38 probes on the changed code (2 more proven
equivalent). All six are fixed in f470e34. a-N1 was a defect: its contract
(`test_the_call_types_its_value_as_supports_index`) was run on ad36216 with Python 3.13.2
and failed there (`object` is not `SupportsIndex`); it passes now. e-N1 to e-N5 were
missing contracts, not defects: their new cases pass on ad36216 and kill the lens's
mutants (table below).

| Lens | Id | Finding | Fix | Contract |
| --- | --- | --- | --- | --- |
| a | a-N1 | pyright reads `Weekday(value)` through the metaclass `__call__`, whose `value` was typed `object`, so `Weekday("MO")`, `Weekday(4.0)` and `Weekday(None)` passed pyright strict while the CHANGELOG and GUIDE said the parameter is `SupportsIndex` | the metaclass `__call__` types `value` as `SupportsIndex` (with an override ignore, as `EnumMeta.__call__` takes any value); the CHANGELOG entry says pyright now flags those calls. pyright 1.1.414 strict: the three calls give 3 errors (0 before), `Weekday(Index())`, `Weekday(3)`, `Weekday(Weekday.MONDAY)` and `Weekday(value=2)` give 0; pyright strict on `_weekday.py` reports no new error (one fewer: its old override error is gone) | `test_weekday_call.py::test_the_call_types_its_value_as_supports_index`; `test_typing.py` (mypy `--strict` over the source tree) also fails if the annotation goes back to `object`, as the ignore becomes unused |
| e | e-N1 (C20) | that `-h` or `--version` still wins after `--yearly` was not pinned | none needed | `test_cli_options.py::test_the_first_of_help_and_version_wins_over_anything_else` (`--yearly --version`, `--yearly -h`, `--ye --vers`) |
| e | e-N2 (C06, C08) | case-sensitive option matching was not pinned | none needed | `test_malformed_options_are_unrecognized_on_every_version` (`--YEARLY`, `--Help`, `-H`) |
| e | e-N3 (C07) | refusal of an option with surrounding whitespace was not pinned | none needed | the same test (`--yearly `, `--h\t`, `-h `) |
| e | e-N4 (C14) | the order of several unknown options in the message was not pinned | none needed | `test_cli_options.py::test_unknown_options_are_listed_in_the_order_given` (`-b -a 2026 MO -c` reports `'-b -a -c'`) |
| e | e-N5 (C19) | the long-option guard was tested on the first option only | none needed | `test_cli_options.py::test_the_long_option_guard_reads_every_option` (`-q` then a 41-character option: `unrecognized option ... (41 characters)`) |

Behaviour change, in the CHANGELOG 1.0.0 section: pyright now flags a value that is not
an integer passed to `Weekday(value)`, as mypy already did. Nothing changes at run time.

Mutants on these fixes, each applied alone to a copy of the tree with the fetched sources,
the whole suite run with `-x` and a 300 s per-test limit on 3.13.2. U02 to U07 are lens
(e)'s C20, C06, C08, C07, C14 and C19.

| # | Mutation | Verdict | First test that failed |
| --- | --- | --- | --- |
| U01 | `Weekday` call value typed `object` again | killed | `test_typing.py::test_any_integer_type_type_checks_where_an_integer_is_asked_for` (and `test_weekday_call.py::test_the_call_types_its_value_as_supports_index`) |
| U02 | only the first known option passed to argparse | killed | `test_cli_options.py::test_the_first_of_help_and_version_wins_over_anything_else[args7-version]` |
| U03 | long option folded to lower case | killed | `test_cli_options.py::test_malformed_options_are_unrecognized_on_every_version[--YEARLY]` |
| U04 | `-h` folded to lower case | killed | `test_cli_options.py::test_malformed_options_are_unrecognized_on_every_version[-H]` |
| U05 | option stripped of whitespace | killed | `test_cli_options.py::test_malformed_options_are_unrecognized_on_every_version[--yearly ]` |
| U06 | unknown options sorted | killed | `test_cli_options.py::test_unknown_options_are_listed_in_the_order_given` |
| U07 | long-option guard on the first option only | killed | `test_cli_options.py::test_the_long_option_guard_reads_every_option` |

Gates on the tree, under a machine turn on this PC with CPython 3.13.2: `ruff format
--check .`, `ruff check .`, `mypy --strict src`, `mypy --strict src tests` and `pytest`
(499 passed) exit 0; `pytest -m e2e`: 2 passed.

Disputed findings (round 4): none.

### Round 5

Lenses (a) and (e) reviewed `release/1.0.0` at 558ce09. Lens (a) found a-N1 fixed and
reported two findings (N2, N3); lens (e) found its five earlier findings killed and
reported one surviving mutant (W21) out of 21 probes. All three are fixed in 47e6b79.
N3 was a defect for pyright users: its contract
(`test_the_call_types_extra_arguments_as_never_given`) was run on 558ce09 with Python
3.13.2 and failed there (`object` is not `NoReturn`); it passes now. W21 was a missing
contract: the new negative typing test passes on 558ce09 and fails on the lens's mutant.
N2 was a docs overclaim, fixed in the CHANGELOG.

| Lens | Id | Finding | Fix | Contract |
| --- | --- | --- | --- | --- |
| a | N2 | the CHANGELOG said both checkers flag `None` passed to any integer parameter, but `byday_dates`' `month` and `ByDay`'s `ordinal` take `None` by design | the sentence now says `str` or `float` anywhere, and `None` anywhere but those two | `tests/test_typing.py` type-checks `byday_dates(2026, None, "MO")` and `ByDay(1, None)` as accepted |
| a | N3 | the metaclass `__call__` typed extra arguments `object`, so pyright accepted `Weekday(3, 4)` and `Weekday(3, module="x")`, which always raise `TypeError` and which mypy rejects | `*args: NoReturn, **kwargs: NoReturn`. pyright 1.1.414 strict on lens (a)'s probes: `arity.py` 4 errors (2 before: `Weekday(3, 4)` and `Weekday(3, module="x")` now flagged), `valid.py` 0, `invalid.py` 7, `n1_repro.py` 3, `every_param.py` 16 (unchanged); `_weekday.py` keeps its one pre-existing error; `mypy --strict src tests` clean for `--python-version` 3.10 to 3.14 | `tests/test_weekday_call.py::test_the_call_types_extra_arguments_as_never_given` |
| e | N6-W21 | no contract pinned that mypy refuses `Weekday(None)`: the only negative line was typed `object` | none needed | `tests/test_typing.py::test_a_weekday_call_without_one_integer_fails_type_checking` runs mypy `--strict` on `Weekday(None)`, `Weekday("MO")`, `Weekday(4.0)` (each `[arg-type]`), `Weekday(3, 4)` and `Weekday(3, module="x")` (each `[call-arg]`) and requires exactly those errors on those lines |

Behaviour change, in the CHANGELOG 1.0.0 section: pyright now flags extra arguments to
`Weekday(value)`, as mypy already did. Nothing changes at run time.

Mutants on these fixes, each applied alone to a copy of the tree with the fetched sources,
the whole suite run with `-x` and a 300 s per-test limit on 3.13.2. V03 is lens (e)'s W21.

| # | Mutation | Verdict | First test that failed |
| --- | --- | --- | --- |
| V01 | `Weekday` call extra positional arguments typed `object` | killed | `test_weekday_call.py::test_the_call_types_extra_arguments_as_never_given` |
| V02 | `Weekday` call extra keyword arguments typed `object` | killed | `test_weekday_call.py::test_the_call_types_extra_arguments_as_never_given` |
| V03 | `__new__` stub value typed `SupportsIndex \| None` | killed | `test_typing.py::test_a_weekday_call_without_one_integer_fails_type_checking` |
| V04 | `__new__` stub value typed `object` | killed | `test_typing.py::test_a_weekday_call_without_one_integer_fails_type_checking` |
| V05 | `__new__` stub takes `*args: object` | killed | `test_typing.py::test_a_weekday_call_without_one_integer_fails_type_checking` |
| V06 | `__new__` stub takes `**kwargs: object` | killed | `test_typing.py::test_a_weekday_call_without_one_integer_fails_type_checking` |

Gates on the tree, under a machine turn on this PC with CPython 3.13.2: `ruff format
--check .`, `ruff check .`, `mypy --strict src`, `mypy --strict src tests` and `pytest`
(501 passed) exit 0; `pytest -m e2e`: 2 passed.

Disputed findings (round 5): none.

### Round 6

Lens (a) reviewed `release/1.0.0` at ea1f46c. It found N1, N2 and N3 fixed and reported
one new finding (N4), fixed in 6f41373. N4 was a defect for pyright users: typing the metaclass
`__call__`'s extra arguments `NoReturn` (47e6b79) made pyright refuse unpacked calls that
run, which it accepted at 558ce09 and in 0.2.0. Its contracts were run on ea1f46c with
the 3.13.2 venv that has pyright 1.1.414 and failed there:
`test_pyright_accepts_what_runs` (4 `reportArgumentType` errors, one per unpacked call),
`test_pyright_refuses_a_weekday_call_without_one_integer` (the extra arguments were
refused as `reportArgumentType`, not as a call with too many arguments) and
`test_type_checkers_see_a_call_of_one_value_and_nothing_else` (no checker-only
signature). All three pass now.

| Lens | Id | Finding | Fix | Contract |
| --- | --- | --- | --- | --- |
| a | N4 | the metaclass `__call__` typed its extras `*args: NoReturn, **kwargs: NoReturn`, so pyright strict and basic refused `Weekday(*[3])`, `Weekday(**{"value": 3})`, `Weekday(*vals)` and `Weekday(**kw)` (4 errors), which run and which mypy accepts; the CHANGELOG did not say so | under `if TYPE_CHECKING:` the metaclass declares `__call__(cls: type[_E], value: SupportsIndex) -> _E` with no extras; the run-time method, its annotations and its checks are unchanged in the `else:` branch. pyright 1.1.414 strict on lens (a)'s probes: the 4 unpacked calls 0 errors, `sweep_bad.py` 8 (every bad call, now as `reportCallIssue`), `arity.py` 4, `every_param.py` 16, `invalid.py` 7, `n1_repro.py` 3, `valid.py` 0, `sweep_ok.py` 0; mypy 2.4.0 `--strict` gives the same counts as before (sweep_bad 9 on 8 lines, the rest equal); `_weekday.py` keeps its one pre-existing pyright error; `inspect.signature(Weekday)` is still `(value)` and `Weekday(3, 4)` still raises `TypeError`. `_weekday.py` is 200 lines. The CHANGELOG says checkers see the call taking one value and nothing else, and both accept an unpacked call that runs | `tests/test_typing.py::test_pyright_accepts_what_runs` (pyright strict on the mypy caller, which now has the 4 unpacked calls) and `::test_pyright_refuses_a_weekday_call_without_one_integer` (each refused line, with pyright's rule), both skipped when pyright is not installed; `tests/test_weekday_call.py::test_type_checkers_see_a_call_of_one_value_and_nothing_else` reads the checker-only signature from the source and runs everywhere; the mypy caller in `test_typing.py` also holds the 4 unpacked calls |

Behaviour change, in the CHANGELOG 1.0.0 section: none against 0.2.0 at run time;
pyright accepts unpacked calls again, as it did in 0.2.0, while still refusing extra
arguments.

Mutants on this fix, each applied alone to a copy of the tree with the fetched sources,
the whole suite run with `-x` and a 300 s per-test limit in the 3.13.2 venv with pyright.
X01 to X06 were also run against `tests/test_weekday_call.py` alone with the gate's
3.13.2 (no pyright): each killed by
`test_type_checkers_see_a_call_of_one_value_and_nothing_else`.

| # | Mutation | Verdict | First test that failed |
| --- | --- | --- | --- |
| X01 | checker-only call takes `*args: NoReturn, **kwargs: NoReturn` (ea1f46c) | killed | `test_typing.py::test_pyright_accepts_what_runs` |
| X02 | checker-only call takes `*args: object` | killed | `test_typing.py::test_pyright_refuses_a_weekday_call_without_one_integer` |
| X03 | checker-only call takes `**kwargs: object` | killed | `test_typing.py::test_pyright_refuses_a_weekday_call_without_one_integer` |
| X04 | checker-only call value typed `object` | killed | `test_typing.py::test_pyright_refuses_a_weekday_call_without_one_integer` |
| X05 | checker-only call value typed `SupportsIndex \| None` | killed | `test_typing.py::test_pyright_refuses_a_weekday_call_without_one_integer` |
| X06 | checker-only call returns `int` | killed | `test_typing.py::test_pyright_accepts_what_runs` |
| X07 | run-time call lets a keyword alone through | killed | `test_contract_edges.py::test_the_constructor_checks_its_argument_like_every_function` |

Gates on the tree, under a machine turn on this PC with CPython 3.13.2: `ruff format
--check .`, `ruff check .`, `mypy --strict src`, `mypy --strict src tests` and `pytest`
(502 passed, the 2 pyright tests skipped) exit 0; `pytest -m e2e`: 2 passed. The suite in
the 3.13.2 venv with pyright 1.1.414: 504 passed. `test_typing.py`, `test_weekday_call.py`,
`test_docs_examples.py`, `test_contract_api.py` and `test_contract.py` on 3.10.19 and
3.14.2: 53 passed and 2 skipped (pyright not installed there) on each.

Disputed findings (round 6): none.
