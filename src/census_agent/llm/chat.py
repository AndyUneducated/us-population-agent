"""Google Gemini chat completion client (REST API)."""

from __future__ import annotations

import json
import ssl
import time
import urllib.error
import urllib.request

import certifi

from census_agent.config import Settings, get_settings


class ChatClient:
    def __init__(self, settings: Settings | None = None, model: str | None = None) -> None:
        self._settings = settings or get_settings()
        self._api_key = self._settings.gemini_api_key
        self._model = model or self._settings.gemini_model
        self._base = self._settings.gemini_base_url.rstrip("/")

    def complete(self, system: str, user: str, temperature: float = 0.1) -> str:
        if not self._api_key:
            raise RuntimeError("GEMINI_API_KEY is not set")

        url = f"{self._base}/models/{self._model}:generateContent"
        payload = {
            "systemInstruction": {"parts": [{"text": system}]},
            "contents": [{"role": "user", "parts": [{"text": user}]}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": 800,
            },
        }
        body = json.dumps(payload).encode()
        ssl_ctx = ssl.create_default_context(cafile=certifi.where())
        last_error: Exception | None = None

        for attempt in range(3):
            req = urllib.request.Request(
                url,
                data=body,
                headers={
                    "Content-Type": "application/json",
                    "X-goog-api-key": self._api_key,
                },
                method="POST",
            )
            try:
                with urllib.request.urlopen(req, timeout=120, context=ssl_ctx) as resp:
                    data = json.loads(resp.read())
                break
            except urllib.error.HTTPError as e:
                err_body = e.read().decode(errors="replace")
                last_error = RuntimeError(f"Gemini API HTTP {e.code}: {err_body}")
                if e.code in {429, 503} and attempt < 2:
                    time.sleep(2 ** attempt)
                    continue
                raise last_error from e
        else:
            if last_error:
                raise last_error
            raise RuntimeError("Gemini request failed")

        candidates = data.get("candidates") or []
        if not candidates:
            err = data.get("error") or data.get("promptFeedback") or data
            raise RuntimeError(f"Gemini returned no candidates: {err}")

        parts = candidates[0].get("content", {}).get("parts") or []
        text = "".join(p.get("text", "") for p in parts if isinstance(p.get("text"), str))
        return text.strip()
