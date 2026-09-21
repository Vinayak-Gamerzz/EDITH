"""Tests for indexed multi-account email configuration."""
import pytest

from zenith.core.config import settings
from zenith.core import tools as tool_registry
from zenith.core.prompts import build_system_prompt
from zenith.tools import mail


def test_multi_email_accounts_select_by_name_without_password_leak(monkeypatch):
    monkeypatch.setattr(settings, "email_accounts", [
        {"name": "personal", "email": "personal@example.com", "password": "secret-1", "host": "imap.gmail.com"},
        {"name": "work", "email": "work@example.com", "password": "secret-2", "host": "imap.example.com"},
    ])

    assert mail._select_account("work")["email"] == "work@example.com"
    assert mail._select_account("personal@example.com")["name"] == "personal"
    assert "secret" not in str(mail.account_list())


@pytest.mark.anyio
async def test_email_accounts_tool_is_registered_and_safe(monkeypatch):
    monkeypatch.setattr(settings, "email_accounts", [
        {"name": "work", "email": "work@example.com", "password": "secret", "host": "imap.gmail.com"},
    ])
    result = await tool_registry.call_tool("email_accounts", {})
    assert result["ok"] is True
    assert "work@example.com" in result["result"]
    assert "secret" not in result["result"]


def test_assistant_identity_is_edith(monkeypatch):
    monkeypatch.setattr(settings, "assistant_name", "Edith")
    prompt = build_system_prompt()
    assert "You are Edith" in prompt