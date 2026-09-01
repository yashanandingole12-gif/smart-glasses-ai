import asyncio
import time
import statistics
from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.app.services.llm_router import llm_router, RoutingTier

async def run_benchmark():
    print("=" * 80)
    print("PHASE 3B.6 CRITICAL LATENCY & MULTI-TIER ROUTING BENCHMARK")
    print("Running empirical measurements across all categories...")
    print("=" * 80)

    transport = ASGITransport(app=app)
    results = {}

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Warmup
        await client.get("/api/v1/health")
        await client.post("/api/v1/agent/message", json={"session_id": "warm", "message": "time"})

        # Category 1: Deterministic Fast-Path
        cat1 = "1. Deterministic Fast-Path ('What time is it?')"
        cat1_times = []
        for i in range(10):
            t0 = time.time()
            resp = await client.post("/api/v1/agent/message", json={
                "session_id": f"bench_det_{i}",
                "message": "What time is it?",
                "request_id": f"req_det_{i}"
            })
            cat1_times.append((time.time() - t0) * 1000.0)

        # Category 2: Fast Conversational LLM Router
        cat2 = "2. Fast Conversational Router ('Hello')"
        cat2_times = []
        for i in range(5):
            t0 = time.time()
            resp = await client.post("/api/v1/agent/message", json={
                "session_id": f"bench_fast_{i}",
                "message": "Hello there",
                "request_id": f"req_fast_{i}"
            })
            cat2_times.append((time.time() - t0) * 1000.0)

        # Category 3: Gmail Intent
        cat3 = "3. Gmail Intent ('Check my email.')"
        cat3_times = []
        for i in range(5):
            t0 = time.time()
            resp = await client.post("/api/v1/agent/message", json={
                "session_id": f"bench_mail_{i}",
                "message": "Check my email.",
                "request_id": f"req_mail_{i}"
            })
            cat3_times.append((time.time() - t0) * 1000.0)

        # Category 4: Hard Timeout & Fallback Cascade
        cat4 = "4. Hard Timeout & Fallback (Simulated 0.1s Timeout)"
        cat4_times = []
        for i in range(10):
            t0 = time.time()
            messages = [{"role": "user", "content": "Explain quantum mechanics."}]
            resp_router = await llm_router.generate_with_budget(
                messages=messages,
                per_attempt_timeout=0.1,
                global_deadline_seconds=0.3
            )
            cat4_times.append((time.time() - t0) * 1000.0)

        categories = [
            (cat1, cat1_times),
            (cat2, cat2_times),
            (cat3, cat3_times),
            (cat4, cat4_times)
        ]

        print("\n" + "=" * 80)
        print(f"{'CATEGORY':<45} | {'P50':<8} | {'P95':<8} | {'P99':<8} | {'MAX':<8}")
        print("-" * 80)

        for label, times in categories:
            times.sort()
            n = len(times)
            p50 = statistics.median(times)
            p95 = times[min(int(n * 0.95), n - 1)]
            p99 = times[min(int(n * 0.99), n - 1)]
            max_t = max(times)
            min_t = min(times)

            results[label] = {
                "p50": p50,
                "p95": p95,
                "p99": p99,
                "max": max_t,
                "min": min_t
            }

            print(f"{label:<45} | {p50:>5.1f}ms | {p95:>5.1f}ms | {p99:>5.1f}ms | {max_t:>5.1f}ms")

        print("=" * 80 + "\n")

    return results

if __name__ == "__main__":
    asyncio.run(run_benchmark())
