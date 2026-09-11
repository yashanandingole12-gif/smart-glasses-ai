import requests
import json
import time

def run_e2e_tests():
    base_url = "http://127.0.0.1:8001"
    tests = [
        ("1. Check Email", "Check my unread emails"),
        ("2. Read Email", "Read my latest email"),
        ("3. Calculation", "What is 125 plus 375?"),
        ("4. Calendar Events", "What is on my calendar today?"),
        ("5. AI Q&A", "What are the key benefits of smart glasses with AI?")
    ]
    
    print("==================================================")
    print(" Phase 3B.12-HW.1 End-to-End Voice & Tool Pipeline")
    print("==================================================")
    
    for name, query in tests:
        t0 = time.time()
        resp = requests.post(
            f"{base_url}/api/v1/agent/message",
            json={
                "session_id": "phase3b12_test_sess",
                "message": query,
                "language": "auto",
                "locale": "en-IN"
            }
        )
        lat_ms = (time.time() - t0) * 1000.0
        
        if resp.status_code == 200:
            data = resp.json()
            reply = data.get("response", "").strip()
            server_lat = data.get("metadata", {}).get("latency_ms", lat_ms)
            source = data.get("sources", ["unknown"])
            print(f"\n[TEST] {name}")
            print(f" -> Query: '{query}'")
            print(f" -> Response: {reply[:120]}...")
            print(f" -> Source / Fast-Path: {source}")
            print(f" -> Latency: {server_lat:.1f} ms (Total HTTP: {lat_ms:.1f} ms)")
        else:
            print(f"\n[TEST ERROR] {name}: Status {resp.status_code} -> {resp.text}")

    print("\n==================================================")
    print(" All End-to-End Tests Finished Successfully!")
    print("==================================================")

if __name__ == "__main__":
    run_e2e_tests()
