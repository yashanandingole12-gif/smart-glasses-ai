import os
import sys
import json
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

os.environ["USE_MOCK_EMAIL"] = "1"
os.environ["USE_MOCK_CALENDAR"] = "1"

QUERIES = [
    # 1. Email Search with Topic Filter
    ("Email (Topic Filter)", "check my mail related to internship", lambda r: "internship" in r.lower() or "internshala" in r.lower()),
    
    # 2. Email Reading (Entity Sender)
    ("Email (Entity Read)", "read the email from LinkedIn", lambda r: "linkedin" in r.lower()),
    
    # 3. Calendar Relative Day
    ("Calendar (Tomorrow)", "what is on my calendar tomorrow?", lambda r: "tomorrow" in r.lower() or "event" in r.lower()),
    
    # 4. Native Device Call Action
    ("Call Control (Answer)", "answer the call", lambda r: "answering" in r.lower()),
    
    # 5. Native Device Call Outgoing
    ("Call Control (Make)", "call Rahul Sharma", lambda r: "calling rahul" in r.lower() or "rahul" in r.lower()),
    
    # 6. Call Control (Hangup)", "hang up", lambda r: "call ended" in r.lower()),
    ("Call Control (Hangup)", "hang up", lambda r: "call ended" in r.lower()),
    
    # 7. Deterministic Math (<50ms)
    ("Deterministic Math", "what is 125 + 375?", lambda r: "500" in r),
    
    # 8. General Knowledge QA (Shoelace)
    ("General QA (Shoelace)", "How do I tie a shoelace?", lambda r: len(r.strip()) > 10 and not any(kw in r.lower() for kw in ["calendar", "email", "sms"])),
    
    # 9. General Knowledge QA (Biryani)
    ("General QA (Biryani)", "How do I cook a biryani?", lambda r: len(r.strip()) > 10 and not any(kw in r.lower() for kw in ["calendar", "email", "sms"])),
    
    # 10. General Knowledge QA (Car)
    ("General QA (Car)", "Which car is best?", lambda r: len(r.strip()) > 10 and not any(kw in r.lower() for kw in ["calendar", "email", "sms"])),
    
    # 11. Academic arXiv Search
    ("Academic Research", "search arxiv for multimodal ai", lambda r: "paper" in r.lower() or "multimodal" in r.lower())
]

def run_matrix():
    print("=" * 70)
    print(" PHASE 3B.11 CAPABILITY & QUERY UNDERSTANDING VERIFICATION MATRIX")
    print("=" * 70)
    
    all_passed = True
    session_id = f"matrix_test_{int(time.time())}"
    
    for category, query, validator in QUERIES:
        t0 = time.time()
        resp = client.post("/api/v1/agent/message", json={
            "session_id": session_id,
            "message": query
        })
        lat_ms = (time.time() - t0) * 1000.0
        
        if resp.status_code != 200:
            print(f"[FAIL] [{category}] HTTP {resp.status_code} ({lat_ms:.1f}ms): {resp.text}")
            all_passed = False
            continue
            
        data = resp.json()
        reply = data.get("response", "")
        passed = validator(reply)
        
        status_icon = "[PASS]" if passed else "[FAIL]"
        if not passed:
            all_passed = False
            
        print(f"{status_icon} [{category}] Query: \"{query}\" ({lat_ms:.1f}ms)")
        print(f"   Response: \"{reply[:120]}{'...' if len(reply) > 120 else ''}\"")
        if data.get("actions"):
            print(f"   Actions: {data['actions']}")
        print()
        
    print("=" * 70)
    if all_passed:
        print("[SUCCESS] ALL 11 CAPABILITY & INTENT VERIFICATION TESTS PASSED!")
    else:
        print("[WARN] SOME MATRIX TESTS FAILED.")
    print("=" * 70)
    return all_passed

if __name__ == "__main__":
    success = run_matrix()
    sys.exit(0 if success else 1)
