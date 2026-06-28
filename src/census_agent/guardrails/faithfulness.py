"""Check that numeric claims in answers are grounded in query results."""

from __future__ import annotations

import re
from typing import Any


def _normalize_num(n: str) -> str:
    key = n.replace(",", "")
    if "." in key:
        try:
            f = float(key)
            if f == int(f):
                return str(int(f))
        except ValueError:
            pass
    return key


def _extract_numbers(text: str) -> set[str]:
    """Normalize numbers for comparison (strip commas, keep digits and decimal)."""
    found = re.findall(r"\d[\d,]*\.?\d*", text)
    normalized = set()
    for n in found:
        key = _normalize_num(n)
        if key:
            normalized.add(key)
    return normalized


def _significant_answer_numbers(text: str) -> set[str]:
    """Numbers that should be grounded in query results (ignore years and small prose digits)."""
    years = {str(y) for y in range(2010, 2031)}
    significant: set[str] = set()
    for n in _extract_numbers(text):
        digits = n.replace(".", "")
        if n in years:
            continue
        if len(digits) < 4:
            continue
        significant.add(n)
    return significant


def _number_in_rows(n: str, row_nums: set[str]) -> bool:
    if n in row_nums:
        return True
    try:
        target = float(n)
    except ValueError:
        return False
    for r in row_nums:
        try:
            rv = float(r)
        except ValueError:
            continue
        if abs(rv - target) < max(0.01, abs(target) * 0.001):
            return True
        if round(rv, 2) == round(target, 2):
            return True
    return False


def check_faithfulness(answer: str, rows: list[dict[str, Any]]) -> tuple[bool, str]:
    """
    Return (ok, reason). Answer numbers should appear in serialized row values.
    Allows ACS year mentions and small integers from prose.
    """
    if not rows:
        return True, "no_rows"

    answer_nums = _significant_answer_numbers(answer)
    if not answer_nums:
        return True, "no_significant_numbers_in_answer"

    row_text = " ".join(str(v) for row in rows for v in row.values())
    row_nums = _extract_numbers(row_text)

    missing = [n for n in answer_nums if not _number_in_rows(n, row_nums)]
    if missing:
        return False, f"ungrounded_numbers:{','.join(missing[:5])}"
    return True, "grounded"
