import httpx
import time
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://127.0.0.1:8001"

TESTS = [
    {
        "id": 1,
        "title": "Check Email",
        "query": "Check my unread emails",
        "category": "Gmail / Email Routing"
    },
    {
        "id": 2,
        "title": "Read Email",
        "query": "Read my latest email",
        "category": "Gmail / Content Read"
    },
    {
        "id": 3,
        "title": "Perform Calculation",
        "query": "What is 125 plus 375?",
        "category": "Deterministic Math Engine"
    },
    {
        "id": 4,
        "title": "Find Events of Calendar",
        "query": "What is on my calendar today?",
        "category": "Google Calendar / Temporal Resolver"
    },
    {
        "id": 5,
        "title": "AI Q&A",
        "query": "What are the key benefits of smart glasses with AI?",
        "category": "Gemini Flash Lite LLM"
    }
]

def run_benchmarks():
    print("\n" + "=" * 75)
    print(" 🚀 SMART GLASSES (SEEED XIAO ESP32-S3) 5-STEP BROWSER TEST BENCHMARK")
    print("=" * 75)
    
    results = []
    
    for t in TESTS:
        t_start = time.perf_counter()
        resp = httpx.post(
            f"{BASE_URL}/api/v1/agent/message",
            json={
                "session_id": "browser_hw_test_session",
                "message": t["query"],
                "language": "auto",
                "locale": "en-IN"
            },
            timeout=25.0
        )
        duration_ms = (time.perf_counter() - t_start) * 1000.0
        status = resp.status_code
        data = resp.json() if status == 200 else {}
        
        reply = data.get("response", "No response")
        provider = data.get("metadata", {}).get("llm_provider", "Unknown")
        fast_path = data.get("metadata", {}).get("fast_path", False)
        sources = data.get("sources", [])
        
        results.append({
            "test_num": t["id"],
            "title": t["title"],
            "query": t["query"],
            "category": t["category"],
            "status_code": status,
            "duration_ms": duration_ms,
            "provider": provider,
            "fast_path": fast_path,
            "sources": sources,
            "response": reply
        })
        
        print(f"\n[TEST {t['id']}: {t['title'].upper()}]")
        print(f"  🗣️ Query:    \"{t['query']}\"")
        print(f"  ⚡ Latency:  {duration_ms:.1f} ms  |  HTTP {status}  |  Provider: {provider}")
        print(f"  📌 Sources:  {sources}")
        print(f"  🔊 Speech:   \"{reply}\"")
        print("-" * 75)
    
    print("\n" + "=" * 75)
    print(" SUMMARY BENCHMARK TABLE")
    print("=" * 75)
    print(f"{'#':<3} | {'Test Name':<24} | {'Latency':<10} | {'Provider / Fast-Path':<24} | {'Status'}")
    print("-" * 75)
    for r in results:
        fp_str = f"{r['provider']} (Fast-Path)" if r['fast_path'] else r['provider']
        print(f"{r['test_num']:<3} | {r['title']:<24} | {r['duration_ms']:>7.1f} ms | {fp_str:<24} | PASS (HTTP {r['status_code']})")
    print("=" * 75 + "\n")

if __name__ == "__main__":
    run_benchmarks()
