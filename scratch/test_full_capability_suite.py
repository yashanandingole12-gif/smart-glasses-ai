import httpx
import time
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://127.0.0.1:8001"

def print_separator(title):
    print("\n" + "=" * 65)
    print(f" {title}")
    print("=" * 65)

def send_message(query: str, session_id: str = "test_cap_session", confirmed_action: bool = None, confirmed_action_id: str = None):
    t0 = time.time()
    payload = {
        "session_id": session_id,
        "message": query,
        "client_timestamp": time.time()
    }
    if confirmed_action is not None:
        payload["confirmed_action"] = confirmed_action
    if confirmed_action_id is not None:
        payload["confirmed_action_id"] = confirmed_action_id

    resp = httpx.post(f"{BASE_URL}/api/v1/agent/message", json=payload, timeout=25.0)
    dur_ms = (time.time() - t0) * 1000.0
    data = resp.json()
    return resp.status_code, dur_ms, data

def run_suite():
    print_separator("TEST 1: EMAIL CAPABILITIES (READ, SEARCH, SEND)")
    
    # 1.1 Read unread emails
    code, dur, data = send_message("Check my unread emails")
    print(f"\n[1.1 Query: 'Check my unread emails']")
    print(f"Status: {code} ({dur:.1f}ms) | Source: {data.get('sources')}")
    print(f"Response: {data.get('response')}")

    # 1.2 Search specific email
    code, dur, data = send_message("Check my college emails")
    print(f"\n[1.2 Query: 'Check my college emails']")
    print(f"Status: {code} ({dur:.1f}ms) | Source: {data.get('sources')}")
    print(f"Response: {data.get('response')}")

    # 1.3 Read email content
    code, dur, data = send_message("Read my latest email")
    print(f"\n[1.3 Query: 'Read my latest email']")
    print(f"Status: {code} ({dur:.1f}ms) | Source: {data.get('sources')}")
    print(f"Response: {data.get('response')}")

    # 1.4 Compose & Send Email (2-step confirmation)
    code, dur, data = send_message("Send an email to professor@college.edu saying I will attend the seminar tomorrow")
    print(f"\n[1.4 Query: 'Send email to professor...']")
    print(f"Status: {code} ({dur:.1f}ms) | Requires Confirmation: {data.get('requires_confirmation')}")
    print(f"Confirmation Prompt: {data.get('confirmation_prompt')}")
    print(f"Actions: {data.get('actions')}")
    print(f"Response: {data.get('response')}")

    action_id = data.get("confirmation_action_id")
    if not action_id and data.get("actions"):
        action_id = data["actions"][0].get("action_id")

    if action_id:
        # Confirm sending
        code2, dur2, data2 = send_message(
            query="Yes, send it",
            confirmed_action=True,
            confirmed_action_id=action_id
        )
        print(f"\n[1.5 Confirmation: 'Yes, send it' (Action ID: {action_id[:8]}...)]")
        print(f"Status: {code2} ({dur2:.1f}ms) | Response: {data2.get('response')}")

    print_separator("TEST 2: CALENDAR CAPABILITIES (READ, FIND FREE TIME, PLAN EVENT)")

    # 2.1 Today's events
    code, dur, data = send_message("What is on my calendar today?")
    print(f"\n[2.1 Query: 'What is on my calendar today?']")
    print(f"Status: {code} ({dur:.1f}ms) | Source: {data.get('sources')}")
    print(f"Response: {data.get('response')}")

    # 2.2 Tomorrow's events
    code, dur, data = send_message("What do I have tomorrow?")
    print(f"\n[2.2 Query: 'What do I have tomorrow?']")
    print(f"Status: {code} ({dur:.1f}ms) | Source: {data.get('sources')}")
    print(f"Response: {data.get('response')}")

    # 2.3 Next event
    code, dur, data = send_message("What is my next event?")
    print(f"\n[2.3 Query: 'What is my next event?']")
    print(f"Status: {code} ({dur:.1f}ms) | Source: {data.get('sources')}")
    print(f"Response: {data.get('response')}")

    # 2.4 Plan / Schedule new event
    code, dur, data = send_message("Schedule a project review meeting tomorrow at 4 PM")
    print(f"\n[2.4 Query: 'Schedule a project review meeting tomorrow at 4 PM']")
    print(f"Status: {code} ({dur:.1f}ms) | Requires Confirmation: {data.get('requires_confirmation')}")
    print(f"Response: {data.get('response')}")

    cal_action_id = data.get("confirmation_action_id")
    if not cal_action_id and data.get("actions"):
        cal_action_id = data["actions"][0].get("action_id")

    if cal_action_id:
        code2, dur2, data2 = send_message(
            query="Yes, schedule the event",
            confirmed_action=True,
            confirmed_action_id=cal_action_id
        )
        print(f"\n[2.5 Confirmation: 'Yes, schedule the event' (Action ID: {cal_action_id[:8]}...)]")
        print(f"Status: {code2} ({dur2:.1f}ms) | Response: {data2.get('response')}")

    print_separator("TEST 3: GENERAL KNOWLEDGE & CONVERSATIONAL QA")

    qa_queries = [
        "How do I cook a biryani?",
        "How do I tie a shoelace?",
        "Which car is best for city commuting?",
        "What is 45 * 12?"
    ]

    for q in qa_queries:
        code, dur, data = send_message(q)
        print(f"\n[Query: '{q}']")
        print(f"Status: {code} ({dur:.1f}ms) | Provider: {data.get('metadata', {}).get('llm_provider')} ({data.get('metadata', {}).get('llm_model')})")
        print(f"Response: {data.get('response')[:200]}...")

    print_separator("TEST SUITE COMPLETED SUCCESSFULLY")

if __name__ == "__main__":
    run_suite()
