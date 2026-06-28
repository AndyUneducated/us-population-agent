#!/usr/bin/env python3
"""Quick Google Gemini API connectivity check."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from census_agent.config import get_settings
from census_agent.llm.chat import ChatClient


def main() -> int:
    settings = get_settings()
    if not settings.gemini_api_key:
        print("FAIL: GEMINI_API_KEY not set in .env")
        return 1

    client = ChatClient(settings)
    reply = client.complete(
        system="Reply with exactly: ok",
        user="ping",
        temperature=0,
    )
    if "ok" not in reply.lower():
        print(f"WARN: unexpected reply: {reply!r}")

    print(f"OK: Gemini model {settings.gemini_model} is reachable")
    print(f"Reply: {reply[:120]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
