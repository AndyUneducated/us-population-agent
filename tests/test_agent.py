"""Agent pipeline tests (deterministic, no LLM)."""

from __future__ import annotations

from census_agent.agent.orchestrator import CensusAgent
from census_agent.agent.rewriter import Message
from census_agent.config import Settings
from census_agent.data.gateway import normalize_rows
from census_agent.guardrails.input import IntentClass, classify_input


def test_guardrail_off_topic() -> None:
    assert classify_input("What's the weather?") == IntentClass.OUT_OF_SCOPE


def test_agent_population_ca(agent_settings: Settings) -> None:
    with CensusAgent(settings=agent_settings) as agent:
        resp = agent.ask("What is the total population of California?")
    assert not resp.refused
    assert resp.rows
    assert float(resp.rows[0]["value"]) == 3000


def test_agent_refuses_poem(agent_settings: Settings) -> None:
    with CensusAgent(settings=agent_settings) as agent:
        resp = agent.ask("Write me a poem")
    assert resp.refused


def test_agent_followup_ca_then_tx(agent_settings: Settings) -> None:
    with CensusAgent(settings=agent_settings) as agent:
        first = agent.ask("What is the total population of California?")
        assert not first.refused
        assert first.rows
        assert first.rows[0]["region"] == "CA"

        history = [
            Message(role="user", content="What is the total population of California?"),
            Message(role="assistant", content=first.answer),
        ]
        second = agent.ask("What about Texas?", history=history)
        assert not second.refused
        assert second.error is None
        assert second.rows
        assert second.rows[0]["region"] == "TX"
        assert second.rows[0]["metric"] == "Total Population"
        assert "TX" in (second.sql or "")


def test_agent_followup_inherits_metric_from_assistant(agent_settings: Settings) -> None:
    assistant = (
        "Based on 2019 ACS 5-year estimates, **Total Population** for **CA** "
        "is approximately **3,000**."
    )
    with CensusAgent(settings=agent_settings) as agent:
        resp = agent.ask("What about Texas?", history=[Message(role="assistant", content=assistant)])
    assert not resp.refused
    assert resp.rows
    assert resp.rows[0]["region"] == "TX"


def test_normalize_rows_lowercases_snowflake_keys() -> None:
    rows = normalize_rows([{"REGION": "TX", "METRIC": "Total Population", "VALUE": 1.0}])
    assert rows[0]["region"] == "TX"
    assert rows[0]["value"] == 1.0
