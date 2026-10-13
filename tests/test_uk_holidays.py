"""UK bank holidays defined by an nth weekday, checked against the GOV.UK dataset.

Rules: Banking and Financial Dealings Act 1971, schedule 1 as amended,
https://www.legislation.gov.uk/ukpga/1971/80/schedule/1 (last Monday in May and in August
for England and Wales and for Northern Ireland; first Monday in May and in August and the
St Andrew's Day rule for Scotland). The early May holiday in England, Wales and Northern
Ireland and the late May holiday in Scotland are set each year by proclamation as the first
and the last Monday in May. Dates: https://www.gov.uk/bank-holidays.json. Both fetched
2026-10-13; the rule table is our own restatement.
"""

from __future__ import annotations

import json
from datetime import date

import pytest
from conftest import UPSTREAM, needs, upstream_text

from nthweekday import MONDAY, next_weekday, nth_weekday

EW_NI = {"Spring bank holiday": (5, -1), "Summer bank holiday": (8, -1)}
SCOTLAND = {"Spring bank holiday": (5, -1), "Summer bank holiday": (8, 1)}
EARLY_MAY = {"Early May bank holiday": (5, 1)}
RULES = {"england-and-wales": EW_NI, "northern-ireland": EW_NI, "scotland": SCOTLAND}
# Dates moved by proclamation, listed by hand: VE day 2020, the Platinum Jubilee 2022.
MOVED = {("Early May bank holiday (VE day)", date(2020, 5, 8)): date(2020, 5, 4)}
MOVED_SPRING = {date(2022, 6, 2): date(2022, 5, 30)}


def _st_andrews(year: int) -> date:
    # 30 November, or the first Monday after it when it falls on a weekend.
    day = date(year, 11, 30)
    return next_weekday(day, MONDAY) if day.weekday() >= 5 else day


@pytest.mark.parametrize(
    ("year", "expected"), [(2025, date(2025, 12, 1)), (2026, date(2026, 11, 30))]
)
def test_st_andrews_day_substitute(year: int, expected: date) -> None:
    # Hand-checked against the GOV.UK Scotland list: 2025-12-01 and 2026-11-30.
    assert _st_andrews(year) == expected


@needs("uk-bfda-1971-schedule-1.html")
def test_rule_wording_appears_in_the_act() -> None:
    text = upstream_text("uk-bfda-1971-schedule-1.html")
    for wording in (
        "The last Monday in May.",
        "The last Monday in August.",
        "The first Monday in May.",
        "The first Monday in August.",
    ):
        assert wording in text, wording


@needs("uk-bank-holidays.json")
def test_every_gov_uk_date_matches_the_rules() -> None:
    data = json.loads((UPSTREAM / "uk-bank-holidays.json").read_text(encoding="utf-8"))
    checked = 0
    for division, rules in RULES.items():
        for event in data[division]["events"]:
            title, day = event["title"].replace("\u2019", "'"), date.fromisoformat(event["date"])
            if title == "St Andrew's Day":
                assert _st_andrews(day.year) == day
            elif (title, day) in MOVED:
                # The rule still names the day the proclamation moved the holiday away from.
                assert nth_weekday(day.year, 5, MONDAY, 1) == MOVED[(title, day)]
            elif title in rules or title in EARLY_MAY:
                month, n = {**rules, **EARLY_MAY}[title]
                expected = MOVED_SPRING.get(day, day)
                assert nth_weekday(day.year, month, MONDAY, n) == expected, (division, title)
            else:
                continue
            checked += 1
    years = {date.fromisoformat(e["date"]).year for e in data["scotland"]["events"]}
    # Three rule-based holidays per division per year, plus St Andrew's Day in Scotland.
    assert checked == 3 * 3 * len(years) + len(years)
