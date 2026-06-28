#!/usr/bin/env python3
"""Phase 3 smoke test: imports and agent via same path as Streamlit app."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from census_agent.agent.orchestrator import CensusAgent
from census_agent.agent.rewriter import Message


def main() -> int:
    # Import streamlit app module
    import importlib.util

    spec = importlib.util.spec_from_file_location("app", ROOT / "app.py")
    assert spec and spec.loader
    importlib.util.module_from_spec(spec)

    with CensusAgent() as agent:
        history = [
            Message(role="user", content="What is the population of California?"),
            Message(role="assistant", content="California has 39M people."),
        ]
        r1 = agent.ask("What is the population of California?")
        r2 = agent.ask("What about Texas?", history=history)

    errors = []
    if r1.refused or r1.error or not r1.rows:
        errors.append(f"single turn failed: {r1.error}")
    if r2.refused or r2.error or not r2.rows:
        errors.append(f"multi-turn failed: {r2.error}")

    if errors:
        print("Phase 3 FAILED:")
        for e in errors:
            print(" -", e)
        return 1

    print(f"OK single: CA pop = {r1.rows[0].get('value')}")
    print(f"OK follow-up: TX pop = {r2.rows[0].get('value')}")
    print("OK app.py imports streamlit")
    print("\nPhase 3 acceptance: PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
