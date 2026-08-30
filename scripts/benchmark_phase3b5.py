import asyncio
import time
import statistics
from httpx import AsyncClient, ASGITransport
from backend.app.main import app

async def run_benchmark():
    print("=" * 60)
    print("PHASE 3B.5 BASELINE & OPTIMIZATION LATENCY BENCHMARK")
    print("Running 20 iterations per query type...")
    print("=" * 60)

    transport = ASGITransport(app=app)
    queries = [
        ("What time is it? (Simple Fast-Path)", "What time is it?"),
        ("Hello (General Conversational)", "Hello"),
        ("Check my email (Gmail Tool)", "Check my email.")
    ]

    results = {}

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Warmup
        await client.get("/api/v1/health")

        for label, query in queries:
            latencies = []
            context_times = []
            backend_times = []

            for i in range(20):
                t0 = time.time()
                resp = await client.post("/api/v1/agent/message", json={
                    "session_id": f"bench_{label[:5]}_{i}",
                    "message": query,
                    "request_id": f"req_bench_{i}"
                })
                total_dur = (time.time() - t0) * 1000.0
                latencies.append(total_dur)

                data = resp.json()
                timings = data.get("metadata", {}).get("timings", {})
                if "context_ms" in timings and timings["context_ms"] is not None:
                    context_times.append(timings["context_ms"])
                if "total_ms" in timings and timings["total_ms"] is not None:
                    backend_times.append(timings["total_ms"])

            latencies.sort()
            n = len(latencies)
            p95_idx = int(n * 0.95)

            results[label] = {
                "min": min(latencies),
                "median": statistics.median(latencies),
                "p95": latencies[min(p95_idx, n - 1)],
                "max": max(latencies),
                "avg": statistics.mean(latencies),
                "context_avg": statistics.mean(context_times) if context_times else 0.0,
                "backend_avg": statistics.mean(backend_times) if backend_times else 0.0
            }

    print("\n" + "=" * 70)
    print(f"{'QUERY TYPE':<35} | {'MEDIAN':<9} | {'P95':<9} | {'MIN':<7} | {'AVG':<7}")
    print("-" * 70)
    for label, r in results.items():
        print(f"{label:<35} | {r['median']:>6.1f}ms | {r['p95']:>6.1f}ms | {r['min']:>4.1f}ms | {r['avg']:>4.1f}ms")
    print("=" * 70 + "\n")

    return results

if __name__ == "__main__":
    asyncio.run(run_benchmark())
