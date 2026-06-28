"""Graceful degradation messages and detectors."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum


class DegradationKind(str, Enum):
    OFF_TOPIC = "off_topic"
    UNSAFE = "unsafe"
    NOT_IN_DATASET = "not_in_dataset"
    AMBIGUOUS_GEO = "ambiguous_geo"
    ZIP_GRANULARITY = "zip_granularity"
    RETRIEVAL_MISS = "retrieval_miss"
    SQL_INVALID = "sql_invalid"
    SQL_GENERATION_FAILED = "sql_generation_failed"
    EXECUTION_FAILED = "execution_failed"
    EMPTY_RESULT = "empty_result"
    PROMPT_INJECTION = "prompt_injection"
    NO_PATH = "no_path"


@dataclass(frozen=True)
class Degradation:
    kind: DegradationKind
    user_message: str
    error_code: str


PROMPT_INJECTION_PATTERNS = [
    r"ignore (all )?(previous|above) instructions",
    r"disregard (your|the) (rules|instructions)",
    r"you are now",
]

AMBIGUOUS_GEO_PATTERNS = [
    r"\bthe south(ern)?\b",
    r"\bthe midwest\b",
    r"\bnortheast\b",
]

ZIP_PATTERN = re.compile(r"\b\d{5}(?:-\d{4})?\b")


def detect_prompt_injection(text: str) -> bool:
    lower = text.lower()
    return any(re.search(p, lower) for p in PROMPT_INJECTION_PATTERNS)


def detect_zip_question(text: str) -> bool:
    return bool(ZIP_PATTERN.search(text))


def detect_ambiguous_geo(text: str) -> bool:
    lower = text.lower()
    return any(re.search(p, lower) for p in AMBIGUOUS_GEO_PATTERNS)


def degradation_for(kind: DegradationKind, **ctx: str) -> Degradation:
    year = ctx.get("year", "2020")
    if kind == DegradationKind.PROMPT_INJECTION:
        return Degradation(
            kind=kind,
            error_code="prompt_injection",
            user_message=(
                "I can only answer good-faith questions about US Census demographics. "
                "Please ask a direct question about population, income, housing, or employment."
            ),
        )
    if kind == DegradationKind.ZIP_GRANULARITY:
        return Degradation(
            kind=kind,
            error_code="zip_granularity",
            user_message=(
                "This dataset is at **census block group** granularity, not ZIP code. "
                "I can answer at state or county level, or describe the nearest available geography."
            ),
        )
    if kind == DegradationKind.AMBIGUOUS_GEO:
        region = ctx.get("region", "the requested region")
        return Degradation(
            kind=kind,
            error_code="ambiguous_geo",
            user_message=(
                f"'{region}' is ambiguous. I'm using the best matching geography I can infer. "
                f"For clarity, specify a state or county (e.g., 'Texas' or 'Cook County, IL'). "
                f"Results use {year} ACS 5-year estimates."
            ),
        )
    if kind == DegradationKind.EMPTY_RESULT:
        return Degradation(
            kind=kind,
            error_code="empty_result",
            user_message=(
                "I ran a census query but found no matching records for that filter. "
                "Try broadening the geography or choosing a metric available in ACS block-group data."
            ),
        )
    if kind == DegradationKind.EXECUTION_FAILED:
        return Degradation(
            kind=kind,
            error_code="execution_failed",
            user_message=(
                "I'm having trouble running the census query right now. "
                "Please try again in a moment or narrow your question to a state or county."
            ),
        )
    raise ValueError(f"Unhandled degradation kind: {kind}")
