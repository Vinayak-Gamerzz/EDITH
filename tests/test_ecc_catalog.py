"""Tests for the vendored ECC agent, skill, and command catalog."""
from zenith.integrations.ecc_catalog import get_asset, search, summary
from zenith.core import tools as tool_registry
from unittest.mock import patch


def test_ecc_catalog_imported_counts_and_representative_assets():
    counts = summary()
    assert counts["agents"] >= 60
    assert counts["skills"] >= 400
    assert counts["commands"] >= 80
    assert get_asset("code-reviewer", "agents") is not None
    assert get_asset("accessibility", "skills") is not None
    assert get_asset("code-review", "commands") is not None


def test_ecc_search_is_scoped_and_returns_metadata():
    results = search("review", kind="commands", limit=5)
    assert results
    assert all(item["kind"] == "commands" for item in results)
    assert all(item["path"].endswith(".md") for item in results)


def test_ecc_tools_are_registered():
    assert {"ecc_catalog", "ecc_search", "ecc_get"}.issubset(tool_registry.TOOLS)


def test_ecc_agent_can_be_resolved_as_a_zenith_specialist():
    from zenith.agents.agent_service import AgentService

    with patch("zenith.agents.agent_service.store.get_custom_agent", return_value=None):
        profile = AgentService().get_agent_profile("code-reviewer")
    assert profile["type"] == "ecc"
    assert "code review" in profile["system"].lower()
    assert "share_finding" in profile["tools"]