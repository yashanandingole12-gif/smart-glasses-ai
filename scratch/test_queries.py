import httpx
import time
import json

queries = [
    "How do I tie a shoelace?",
    "How do I cook a biryani?",
    "Which car is best?",
    "What is 25 * 4?",
    "Good morning"
]

print("=== STARTING SMART GLASSES AI QUERY TEST ===")
for q in queries:
    t0 = time.time()
    try:
        resp = httpx.post(
            "http://127.0.0.1:8001/api/v1/agent/message",
            json={"message": q, "session_id": "test-session-live"},
            timeout=20.0
        )
        dt = (time.time() - t0) * 1000.0
        data = resp.json()
        print("--------------------------------------------------")
        print(f"QUERY: {q}")
        print(f"STATUS: {resp.status_code} ({dt:.1f}ms)")
        meta = data.get("metadata", {})
        print(f"PROVIDER: {meta.get('llm_provider')}, MODEL: {meta.get('llm_model')}")
        print(f"SOURCES: {data.get('sources')}")
        print(f"RESPONSE:\n{data.get('response')}\n")
    except Exception as e:
        print(f"ERROR on '{q}':", e)

print("=== QUERY TEST COMPLETE ===")
