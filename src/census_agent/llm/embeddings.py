"""Ollama embedding client."""

from __future__ import annotations

import json
import urllib.error
import urllib.request

from census_agent.config import Settings, get_settings


class EmbeddingClient:
    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        base = self._settings.ollama_base_url.rstrip("/")
        self._host = base.replace("/v1", "")
        self._model = self._settings.ollama_embed_model

    def embed(self, text: str) -> list[float]:
        body = json.dumps({"model": self._model, "prompt": text}).encode()
        req = urllib.request.Request(
            f"{self._host}/api/embeddings",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read())
        return data["embedding"]

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [self.embed(t) for t in texts]
