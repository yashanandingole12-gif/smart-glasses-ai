import pytest
from backend.app.services.providers.email_provider import LaptopEmailProvider, resolve_email_search_query
from backend.app.tools.gmail_tools import gmail_search, gmail_read, gmail_send_message, gmail_reply_message
from backend.app.services.tool_registry import registry

def test_resolve_email_search_query_entity_mapping():
    # LinkedIn
    q_linkedin = resolve_email_search_query("read my LinkedIn email")
    assert "linkedin" in q_linkedin.lower()
    assert "from:" in q_linkedin

    # GitHub
    q_github = resolve_email_search_query("did GitHub send me any mail?")
    assert "github" in q_github.lower()

    # Empty / Unread
    assert resolve_email_search_query("") == "is:unread"
    assert resolve_email_search_query("check my email") == "is:unread"

def test_laptop_email_provider_search_and_read():
    provider = LaptopEmailProvider()

    # Search all
    overview = provider.search()
    assert overview["count"] >= 3
    assert overview["unread_count"] >= 1

    # Search LinkedIn
    linkedin_res = provider.search("linkedin")
    assert linkedin_res["count"] == 1
    assert "linkedin" in linkedin_res["messages"][0]["sender"].lower()

    # Search Rahul
    rahul_res = provider.search("rahul")
    assert rahul_res["count"] == 1
    assert "rahul" in rahul_res["messages"][0]["sender"].lower()

    # Read Stage 2 by ID
    read_res = provider.read(message_id="msg_001")
    assert read_res["status"] == "found"
    assert "Machine Learning" in read_res["email"]["body"]

def test_laptop_email_send_and_reply():
    provider = LaptopEmailProvider()

    # Send
    send_res = provider.send_message("test@example.com", "Project Update", "All tests are passing.")
    assert send_res["status"] == "sent"
    assert send_res["recipient"] == "test@example.com"

    # Reply
    reply_res = provider.reply_message("msg_002", "Got it, see you at 3 PM.")
    assert reply_res["status"] == "sent"
    assert "Re:" in reply_res["subject"]

def test_tool_registry_gmail_tools_registered():
    search_tool = registry.get_tool("gmail_search")
    assert search_tool is not None
    assert search_tool.requires_confirmation is False

    send_tool = registry.get_tool("gmail_send_message")
    assert send_tool is not None
    assert send_tool.requires_confirmation is True

    reply_tool = registry.get_tool("gmail_reply_message")
    assert reply_tool is not None
    assert reply_tool.requires_confirmation is True
