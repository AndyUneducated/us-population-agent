#!/usr/bin/env python3
"""Probe Snowflake Cortex AI availability for the current account."""

from __future__ import annotations

import os
import sys

try:
    import snowflake.connector
except ImportError:
    print("Install: pip install snowflake-connector-python python-dotenv")
    sys.exit(1)

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


def main() -> int:
    if load_dotenv:
        load_dotenv()

    conn = snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        role=os.environ.get("SNOWFLAKE_ROLE", "ACCOUNTADMIN"),
        warehouse=os.environ.get("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH"),
    )
    cur = conn.cursor()

    models = [
        "claude-haiku-4-5",
        "snowflake-llama-3.3-70b",
        "mistral-7b",
    ]
    any_ok = False
    for model in models:
        try:
            cur.execute(
                f"SELECT AI_COMPLETE('{model}', 'Say hello in one word') AS response"
            )
            print(f"OK  AI_COMPLETE({model}):", str(cur.fetchone()[0])[:100])
            any_ok = True
        except Exception as e:
            print(f"FAIL AI_COMPLETE({model}):", e)

    try:
        cur.execute(
            "SELECT AI_EMBED('snowflake-arctic-embed-m', 'total population') AS emb"
        )
        emb = cur.fetchone()[0]
        print(f"OK  AI_EMBED: dim={len(emb) if emb else 0}")
        any_ok = True
    except Exception as e:
        print(f"FAIL AI_EMBED:", e)

    conn.close()

    if any_ok:
        print("\n=> Cortex is AVAILABLE. Set LLM_PROVIDER=cortex")
        return 0
    print("\n=> Cortex NOT available (likely trial account). Use LLM_PROVIDER=openai fallback.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
