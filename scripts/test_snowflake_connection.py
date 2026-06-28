#!/usr/bin/env python3
"""Quick Snowflake connectivity check. Requires snowflake-connector-python."""

from __future__ import annotations

import os
import sys

try:
    import snowflake.connector
except ImportError:
    print("Install first: pip install snowflake-connector-python python-dotenv")
    sys.exit(1)

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


def main() -> int:
    if load_dotenv:
        load_dotenv()

    account = os.environ.get("SNOWFLAKE_ACCOUNT")
    user = os.environ.get("SNOWFLAKE_USER")
    role = os.environ.get("SNOWFLAKE_ROLE", "ACCOUNTADMIN")
    warehouse = os.environ.get("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH")
    password = os.environ.get("SNOWFLAKE_PASSWORD")
    authenticator = os.environ.get("SNOWFLAKE_AUTHENTICATOR")

    missing = [k for k, v in {
        "SNOWFLAKE_ACCOUNT": account,
        "SNOWFLAKE_USER": user,
    }.items() if not v]
    if missing:
        print(f"Missing env vars: {', '.join(missing)}")
        return 1

    connect_kwargs: dict = {
        "account": account,
        "user": user,
        "role": role,
        "warehouse": warehouse,
    }

    if authenticator:
        connect_kwargs["authenticator"] = authenticator
    elif password:
        connect_kwargs["password"] = password
    else:
        print(
            "Set SNOWFLAKE_PASSWORD (PAT) or SNOWFLAKE_AUTHENTICATOR=externalbrowser"
        )
        return 1

    print(f"Connecting to account={account} user={user} warehouse={warehouse} ...")
    try:
        conn = snowflake.connector.connect(**connect_kwargs)
        cur = conn.cursor()
        cur.execute(
            "SELECT CURRENT_USER(), CURRENT_ROLE(), CURRENT_WAREHOUSE(), CURRENT_VERSION()"
        )
        row = cur.fetchone()
        print("OK:", row)
        database = os.environ.get("SNOWFLAKE_DATABASE")
        schema = os.environ.get("SNOWFLAKE_SCHEMA", "PUBLIC")
        if database:
            cur.execute(f"SHOW TABLES IN {database}.{schema}")
            tables = [r[1] for r in cur.fetchmany(30)]
            print(f"Tables in {database}.{schema} (first 30): {tables}")
        else:
            cur.execute("SHOW DATABASES")
            dbs = [r[1] for r in cur.fetchmany(20)]
            print(f"Databases (first 20): {dbs}")
        conn.close()
        return 0
    except Exception as e:
        print("FAILED:", e)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
