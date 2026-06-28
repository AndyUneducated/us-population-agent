#!/usr/bin/env python3
"""Quick Ollama connectivity check."""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


def main() -> int:
    if load_dotenv:
        load_dotenv()

    base = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434/v1").rstrip("/")
    host = base.replace("/v1", "")
    fast = os.environ.get("OLLAMA_MODEL_FAST", "qwen3.5:9b")
    main_model = os.environ.get("OLLAMA_MODEL_MAIN", "qwen3.6:27b")
    embed = os.environ.get("OLLAMA_EMBED_MODEL", "qwen3-embedding:8b")

    # List models
    try:
        with urllib.request.urlopen(f"{host}/api/tags", timeout=5) as resp:
            tags = json.loads(resp.read())
        installed = {m["name"] for m in tags.get("models", [])}
        print("Installed models:", sorted(installed))
    except Exception as e:
        print(f"FAIL: Ollama not reachable at {host}: {e}")
        print("Start with: ollama serve")
        return 1

    for name, label in [(fast, "fast"), (main_model, "main")]:
        if name not in installed:
            print(f"WARN: {label} model '{name}' not installed. Run: ollama pull {name}")
            continue
        body = json.dumps({
            "model": name,
            "messages": [{"role": "user", "content": "Say hello in one word."}],
            "stream": False,
        }).encode()
        req = urllib.request.Request(
            f"{host}/api/chat",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read())
            content = data.get("message", {}).get("content", "")
            print(f"OK  chat({name}): {content[:80]}")
        except Exception as e:
            print(f"FAIL chat({name}): {e}")

    if embed in installed:
        body = json.dumps({"model": embed, "prompt": "total population"}).encode()
        req = urllib.request.Request(
            f"{host}/api/embeddings",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read())
            emb = data.get("embedding", [])
            print(f"OK  embed({embed}): dim={len(emb)}")
        except Exception as e:
            print(f"FAIL embed({embed}): {e}")
    else:
        print(f"WARN: embed model '{embed}' not installed. Run: ollama pull {embed}")

    print("\n=> Ollama ready. Set LLM_PROVIDER=ollama in .env")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
