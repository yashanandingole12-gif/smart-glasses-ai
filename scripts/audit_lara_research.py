import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lara_research import LaraResearch

def audit_research_apis():
    print("=====================================================")
    print("   LARA RESEARCH ENGINE -- LIVE API AUDIT & STATUS   ")
    print("=====================================================")

    lara = LaraResearch()
    query = "quantum computing"

    for name, connector in lara.connectors.items():
        t0 = time.time()
        try:
            res = connector.search(query, limit=3)
            lat_ms = (time.time() - t0) * 1000
            status = "ACTIVE [PASS]" if res else "ACTIVE (0 results)"
            print(f"- {name.upper():<18}: {status:<15} ({len(res)} papers in {lat_ms:.1f}ms)")
            if res:
                print(f"  Top result: '{res[0].title[:65]}...'")
        except Exception as e:
            print(f"- {name.upper():<18}: ERROR ({e})")

    # Unified search with deduplication
    t0 = time.time()
    unified = lara.search(query, limit=3)
    t_total = (time.time() - t0) * 1000
    print("-----------------------------------------------------")
    print(f"Unified Parallel Search: {len(unified)} unique papers returned in {t_total:.1f}ms")
    print("=====================================================")

if __name__ == "__main__":
    audit_research_apis()
