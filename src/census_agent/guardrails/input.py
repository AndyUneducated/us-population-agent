"""Input guardrails: fast rule-based classification."""

from __future__ import annotations

import re
from enum import Enum


class IntentClass(str, Enum):
    IN_SCOPE = "in_scope"
    OUT_OF_SCOPE = "out_of_scope"
    UNSAFE = "unsafe"


OFF_TOPIC_PATTERNS = [
    r"\bweather\b",
    r"\bwrite (a )?poem\b",
    r"\brecipe\b",
    r"\bstock price\b",
    r"\bignore (all )?(previous|above) instructions\b",
    r"\bjailbreak\b",
]

UNSAFE_PATTERNS = [
    r"\bhow to (make|build) (a )?bomb\b",
    r"\bhack\b",
]

CENSUS_SIGNALS = [
    r"\bpopulation\b",
    r"\bincome\b",
    r"\bcensus\b",
    r"\bcounty\b",
    r"\bstate\b",
    r"\bhousehold\b",
    r"\bunemployment\b",
    r"\bhousing\b",
    r"\bhomeownership\b",
    r"\bowner occupied\b",
    r"\bage\b",
    r"\bmedian age\b",
    r"\b人口\b",
    r"\breligion\b",
    r"\breligious\b",
]


def classify_input(text: str) -> IntentClass:
    lower = text.lower()
    for pat in UNSAFE_PATTERNS:
        if re.search(pat, lower):
            return IntentClass.UNSAFE
    for pat in OFF_TOPIC_PATTERNS:
        if re.search(pat, lower):
            return IntentClass.OUT_OF_SCOPE
    for pat in CENSUS_SIGNALS:
        if re.search(pat, lower, re.IGNORECASE):
            return IntentClass.IN_SCOPE
    # Short follow-ups like "what about Texas?" inherit context in rewriter
    if re.search(r"\b(what about|how about|and)\b", lower):
        return IntentClass.IN_SCOPE
    return IntentClass.OUT_OF_SCOPE


def refusal_message(intent: IntentClass) -> str:
    if intent == IntentClass.UNSAFE:
        return "I can't help with that request. I answer questions about US Census population and demographics."
    return (
        "I'm a US Census data assistant. I can answer questions about population, income, "
        "housing, employment, and related demographics by state or county. "
        "Please ask a census-related question."
    )
