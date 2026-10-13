"""Worked examples from RFC 5545 section 3.8.5.3 and the VTIMEZONE examples in 3.6.5.

Source: https://www.rfc-editor.org/rfc/rfc5545.txt (fetched 2026-10-13). Each vector keeps
the RRULE line and the expected dates as the RFC prints them; when the RFC text has been
fetched, the test checks both still appear in it word for word.
"""

from __future__ import annotations

import re
from datetime import date

import pytest
from conftest import needs, upstream_text

from nthweekday import byday_dates

# (RRULE line, dates as printed, expected dates). Monthly rules are asked month by month.
MONTHLY = [
    (
        "RRULE:FREQ=MONTHLY;COUNT=10;BYDAY=1FR",
        "(1998 9:00 AM EST) January 2;February 6;March 6;April 3",
        "1FR",
        [date(1998, 1, 2), date(1998, 2, 6), date(1998, 3, 6), date(1998, 4, 3)],
    ),
    (
        "RRULE:FREQ=MONTHLY;INTERVAL=2;COUNT=10;BYDAY=1SU,-1SU",
        "(1998 9:00 AM EST) January 4,25;March 1,29",
        "1SU,-1SU",
        [date(1998, 1, 4), date(1998, 1, 25), date(1998, 3, 1), date(1998, 3, 29)],
    ),
    (
        "RRULE:FREQ=MONTHLY;COUNT=6;BYDAY=-2MO",
        "(1997 9:00 AM EST) November 17;December 22",
        "-2MO",
        [date(1997, 11, 17), date(1997, 12, 22)],
    ),
]
# The VTIMEZONE example: each DTSTART is the first instance of its yearly BYMONTH rule.
TIMEZONE = [
    ("DTSTART:20070311T020000 RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=2SU", "2SU", date(2007, 3, 11)),
    ("DTSTART:20071104T020000 RRULE:FREQ=YEARLY;BYMONTH=11;BYDAY=1SU", "1SU", date(2007, 11, 4)),
    ("DTSTART:19870405T020000 RRULE:FREQ=YEARLY;BYMONTH=4;BYDAY=1SU", "1SU", date(1987, 4, 5)),
    ("DTSTART:19671029T020000 RRULE:FREQ=YEARLY;BYMONTH=10;BYDAY=-1SU", "-1SU", date(1967, 10, 29)),
]
YEARLY = ("RRULE:FREQ=YEARLY;BYDAY=20MO", "(1998 9:00 AM EDT) May 18", "20MO", date(1998, 5, 18))


@pytest.mark.parametrize(("rule", "printed", "value", "expected"), MONTHLY)
def test_monthly_examples(rule: str, printed: str, value: str, expected: list[date]) -> None:
    months = sorted({(d.year, d.month) for d in expected})
    assert [d for y, m in months for d in byday_dates(y, m, value)] == expected


@pytest.mark.parametrize(("rule", "value", "expected"), TIMEZONE)
def test_timezone_examples(rule: str, value: str, expected: date) -> None:
    assert byday_dates(expected.year, expected.month, value) == [expected]


def test_yearly_twentieth_monday() -> None:
    _, _, value, expected = YEARLY
    assert byday_dates(1998, None, value) == [expected]
    assert byday_dates(1997, None, value) == [date(1997, 5, 19)]
    assert byday_dates(1999, None, value) == [date(1999, 5, 17)]


@needs("rfc5545.txt")
def test_vectors_appear_in_the_fetched_rfc() -> None:
    text = upstream_text("rfc5545.txt")
    quoted = [(rule, printed) for rule, printed, _, _ in MONTHLY]
    quoted.append((YEARLY[0], YEARLY[1]))
    for rule, _, _ in TIMEZONE:
        start, recur = rule.split(" ", 1)
        quoted.append((start, recur))
    for first, second in quoted:
        # The second part must follow the first closely: the dates belong to that rule
        # (or the RRULE to that DTSTART), not to another example elsewhere in the RFC.
        near = re.escape(first) + ".{0,400}?" + re.escape(second)
        assert re.search(near, text), (first, second)
