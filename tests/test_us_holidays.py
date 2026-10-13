"""US federal holidays defined by an nth weekday, checked against OPM's published dates.

Rules: 5 U.S.C. 6103(a), https://www.govinfo.gov/content/pkg/USCODE-2023-title5/html/USCODE-2023-title5-partIII-subpartE-chap61-subchapI-sec6103.htm
Dates: OPM schedules, https://www.opm.gov/policy-data-oversight/pay-leave/federal-holidays/
Both fetched 2026-10-13. The rule table below is our own restatement of the statute.
"""

from __future__ import annotations

import re
from datetime import date, datetime

import pytest
from conftest import needs, upstream_text

from nthweekday import MONDAY, THURSDAY, nth_weekday

# OPM name -> (month, weekday, n, the statute's wording of the rule)
RULES = {
    "Birthday of Martin Luther King, Jr.": (1, MONDAY, 3, "the third Monday in January"),
    "Washington's Birthday": (2, MONDAY, 3, "the third Monday in February"),
    "Memorial Day": (5, MONDAY, -1, "the last Monday in May"),
    "Labor Day": (9, MONDAY, 1, "the first Monday in September"),
    "Columbus Day": (10, MONDAY, 2, "the second Monday in October"),
    "Thanksgiving Day": (11, THURSDAY, 4, "the fourth Thursday in November"),
}
# A few OPM dates kept inline so the rules are exercised without the fetched page.
CITED = [
    ("Thanksgiving Day", date(2026, 11, 26)),
    ("Memorial Day", date(2027, 5, 31)),
    ("Labor Day", date(2026, 9, 7)),
    ("Birthday of Martin Luther King, Jr.", date(2030, 1, 21)),
    ("Columbus Day", date(2011, 10, 10)),
    ("Washington's Birthday", date(2028, 2, 21)),
]
_ROW = re.compile(
    r"(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday), "
    r"([A-Z][a-z]+) (\d{1,2})(?:, (\d{4}))? \**\s*(" + "|".join(map(re.escape, RULES)) + ")"
)


def _rule(name: str, year: int) -> date:
    month, weekday, n, _ = RULES[name]
    return nth_weekday(year, month, weekday, n)


@pytest.mark.parametrize(("name", "expected"), CITED)
def test_cited_opm_dates(name: str, expected: date) -> None:
    assert _rule(name, expected.year) == expected


@needs("usc-5-6103.htm")
def test_rule_table_matches_the_statute() -> None:
    text = upstream_text("usc-5-6103.htm")
    for name, (_, _, _, wording) in RULES.items():
        assert f"{name}, {wording}." in text, name


@needs("opm-federal-holidays.html")
def test_every_opm_schedule_matches_the_rules() -> None:
    text = upstream_text("opm-federal-holidays.html")
    sections = re.split(r"(\d{4}) Holiday Schedule", text)[1:]
    checked: dict[int, set[str]] = {}
    for year_text, body in zip(sections[::2], sections[1::2], strict=True):
        year = int(year_text)
        for weekday, month_name, day, row_year, name in _ROW.findall(body):
            shown = datetime.strptime(f"{month_name} {day} {row_year or year}", "%B %d %Y")
            assert shown.strftime("%A") == weekday, (year, name)
            assert _rule(name, year) == shown.date(), (year, name)
            checked.setdefault(year, set()).add(name)
    assert set(checked) >= set(range(2011, 2031))
    assert all(names == set(RULES) for names in checked.values()), checked
