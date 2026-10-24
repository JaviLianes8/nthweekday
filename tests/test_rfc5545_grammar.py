"""parse_byday against the BYDAY grammar read out of the fetched RFC 5545 text.

Source: https://www.rfc-editor.org/rfc/rfc5545.txt (section 3.3.10, pinned in
data/upstream/MANIFEST.json). The ABNF rules are taken from the text and turned into a
regular expression here, so the reference never passes through the library's own
pattern. ABNF quoted strings are case-insensitive (RFC 5234 section 2.3), and section 3.1
of RFC 5545 says enumerated values are too.
"""

from __future__ import annotations

import itertools
import random
import re

import pytest
from conftest import needs, upstream_text

from nthweekday import ByDay, Weekday, parse_byday

RULES = ("bywdaylist", "weekdaynum", "plus", "minus", "ordwk", "weekday")
TOKEN = re.compile(r'\s*("[^"]*"|\d*\*\d*|\d+|[\[\]()/]|[A-Za-z][A-Za-z0-9-]*)')


def _rules(text: str) -> tuple[dict[str, str], str]:
    found = {}
    for name in RULES:
        match = re.search(rf"\b{name} += (.*?)(?= ;| [a-z]+ += |$)", text)
        assert match, name
        found[name] = match.group(1).strip()
    comment = re.search(r"ordwk += 1\*2DIGIT +;(\d+) to (\d+)", text)
    assert comment
    return found, f"{comment.group(1)}..{comment.group(2)}"


def _to_regex(definition: str, rules: dict[str, str]) -> str:
    tokens = TOKEN.findall(definition)
    assert "".join(tokens) == definition.replace(" ", ""), definition
    regex, used = _alternation(tokens, 0, rules)
    assert used == len(tokens), definition
    return regex


def _alternation(tokens: list[str], i: int, rules: dict[str, str]) -> tuple[str, int]:
    options = []
    while True:
        parts = []
        while i < len(tokens) and tokens[i] not in ("/", ")", "]"):
            part, i = _repetition(tokens, i, rules)
            parts.append(part)
        options.append("".join(parts))
        if i < len(tokens) and tokens[i] == "/":
            i += 1
            continue
        return "(?:" + "|".join(options) + ")", i


def _repetition(tokens: list[str], i: int, rules: dict[str, str]) -> tuple[str, int]:
    repeat = None
    if re.fullmatch(r"\d*\*\d*|\d+", tokens[i]):
        repeat, i = tokens[i], i + 1
    token = tokens[i]
    if token in ("(", "["):
        inner, i = _alternation(tokens, i + 1, rules)
        assert tokens[i] == {"(": ")", "[": "]"}[token]
        piece = inner + ("?" if token == "[" else "")
    elif token.startswith('"'):
        letters = (
            f"[{c.upper()}{c.lower()}]" if c.isalpha() else re.escape(c) for c in token[1:-1]
        )
        piece = "(?:" + "".join(letters) + ")"
    elif token == "DIGIT":
        piece = "[0-9]"
    else:
        piece = "(?:" + _to_regex(rules[token], rules) + ")"
    if repeat is not None:
        low, star, high = repeat.partition("*")
        piece += f"{{{low or 0},{high}}}" if star else f"{{{low}}}"
    return piece, i + 1


def _reference() -> tuple[re.Pattern[str], range, dict[str, Weekday]]:
    text = upstream_text("rfc5545.txt")
    rules, span = _rules(text)
    low, high = (int(x) for x in span.split(".."))
    codes = re.findall(r'"([A-Z]{2})"', rules["weekday"])
    names = re.search(r";Corresponding to (.*?) days of the week", text)
    assert names
    days = [w.strip(" ;") for w in re.split(r",| and ", names.group(1)) if w.strip(" ;")]
    mapping = {code: Weekday[name] for code, name in zip(codes, days, strict=True)}
    return re.compile(_to_regex(rules["bywdaylist"], rules)), range(low, high + 1), mapping


def _expected(value: str, ordwk: range, mapping: dict[str, Weekday]) -> tuple[ByDay, ...] | None:
    entries = []
    for item in value.split(","):
        code = item[-2:].upper()
        number = item[:-2]
        ordinal = int(number) if number.lstrip("+-") else None
        if ordinal is not None and abs(ordinal) not in ordwk:
            return None
        entries.append(ByDay(mapping[code], ordinal))
    return tuple(entries)


def _check(value: str, grammar: re.Pattern[str], ordwk: range, mapping: dict[str, Weekday]) -> None:
    expected = _expected(value, ordwk, mapping) if grammar.fullmatch(value) else None
    try:
        got: tuple[ByDay, ...] | None = parse_byday(value)
    except ValueError:
        got = None
    assert got == expected, value


@needs("rfc5545.txt")
def test_the_grammar_is_read_from_the_rfc() -> None:
    grammar, ordwk, mapping = _reference()
    assert ordwk == range(1, 54)
    assert mapping["SU"] is Weekday.SUNDAY and mapping["SA"] is Weekday.SATURDAY
    assert len(mapping) == 7
    assert grammar.fullmatch("1SU,-1SU") and not grammar.fullmatch("1SU,")


@needs("rfc5545.txt")
def test_every_short_string_agrees_with_the_grammar() -> None:
    grammar, ordwk, mapping = _reference()
    alphabet = "+-0159MoFR, "
    for length in range(6):
        for chars in itertools.product(alphabet, repeat=length):
            _check("".join(chars), grammar, ordwk, mapping)


@needs("rfc5545.txt")
@pytest.mark.parametrize("seed", range(4))
def test_random_lists_agree_with_the_grammar(seed: int) -> None:
    grammar, ordwk, mapping = _reference()
    rng = random.Random(seed)
    pieces = [
        "SU",
        "mo",
        "Tu",
        "WE",
        "th",
        "FR",
        "sa",
        "+",
        "-",
        "0",
        "1",
        "5",
        "3",
        "53",
        "54",
        "99",
        "007",
        ",",
        " ",
        "x",
        "S",
        chr(0x17F),
        chr(0x212A),
        ";",
        "\t",
    ]
    for _ in range(5000):
        _check(
            "".join(rng.choice(pieces) for _ in range(rng.randint(1, 12))), grammar, ordwk, mapping
        )
