"""Shared pytest fixtures."""

from __future__ import annotations

import os

import pytest


def gemini_api_available() -> bool:
    return bool(os.environ.get("GEMINI_API_KEY", "").strip())


@pytest.fixture(scope="session")
def gemini_available() -> bool:
    return gemini_api_available()


@pytest.fixture
def require_gemini(gemini_available: bool) -> None:
    if not gemini_available:
        pytest.skip("GEMINI_API_KEY not set")
