"""Ollama chat completion client."""

from __future__ import annotations

import json
import urllib.request

from census_agent.config import Settings, get_settings


class ChatClient:
    def __init__(self, settings: Settings | None = None, model: str | None = None) -> None:
        self._settings = settings or get_settings()
        base = self._settings.ollama_base_url.rstrip("/")
        self._host = base.replace("/v1", "")
        self._model = model or self._settings.ollama_model_main

    def complete(self, system: str, user: str, temperature: float = 0.1) -> str:
        body = json.dumps(
            {
                "model": self._model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "stream": False,
                "options": {"temperature": temperature},
            }
        ).encode()
        req = urllib.request.Request(
            f"{self._host}/api/chat",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=180) as resp:
            data = json.loads(resp.read())
        return str(data.get("message", {}).get("content", "")).strip()
