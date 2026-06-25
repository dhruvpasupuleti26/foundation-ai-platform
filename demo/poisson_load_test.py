"""Poisson-arrival multi-capability load test for Foundation AI Platform.

Simulates realistic traffic by sending requests according to a Poisson
process (exponentially distributed inter-arrival times). Each request
randomly targets one of multiple capabilities. All per-request metrics
are logged to a JSONL file for later analysis and plotting.

Usage:
    python demo/poisson_load_test.py --requests 100 --rate 0.5 --capability chat
    python demo/poisson_load_test.py --requests 200 --rate 1.0 --multi-capability
"""

import asyncio
import argparse
import json
import random
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx

# ── Configuration ────────────────────────────────────────────────────
BASE_URL = "http://localhost:8000"

CAPABILITY_WEIGHTS = {
    "chat": 0.60,
    "summarization": 0.20,
    "reasoning": 0.20,
}

PROMPTS = {
    "chat": [
        "Tell me a fun fact about black holes.",
        "What is the capital of Mongolia?",
        "Explain quantum entanglement in one sentence.",
        "Write a haiku about rain.",
        "What makes a good leader?",
        "Suggest a creative name for a pet goldfish.",
        "What is the speed of light in km/s?",
        "Tell me a short joke.",
        "Who invented the telephone?",
        "What are the primary colors?",
    ],
    "summarization": [
        "Summarize the concept of machine learning in two sentences.",
        "Give a one-paragraph summary of the French Revolution.",
        "Summarize how photosynthesis works.",
        "Briefly explain the theory of relativity.",
        "Summarize what an API is for a non-technical person.",
    ],
    "reasoning": [
        "If all roses are flowers and some flowers fade quickly, can we conclude some roses fade quickly? Explain.",
        "A bat and ball cost $1.10. The bat costs $1 more than the ball. How much does the ball cost? Think step by step.",
        "There are 3 boxes. One has apples, one has oranges, one has both. All labels are wrong. You pick one fruit from one box. How do you label all boxes?",
        "Is it possible for a month to have 5 Mondays, 5 Tuesdays, and 5 Wednesdays? Explain.",
        "If you overtake the person in 2nd place in a race, what place are you in now?",
    ],
}


# ── Per-request worker ───────────────────────────────────────────────
async def send_request(
    client: httpx.AsyncClient,
    index: int,
    capability: str,
    results: list,
    start_time: float,
):
    """Fire a single request and record the metrics."""
    prompt = random.choice(PROMPTS.get(capability, PROMPTS["chat"]))
    payload = {
        "capability": capability,
        "messages": [{"role": "user", "content": prompt}],
    }

    arrival_time = time.perf_counter() - start_time
    t0 = time.perf_counter()
    status_code = 0
    model_name = ""
    error = ""

    try:
        response = await client.post(
            f"{BASE_URL}/v1/chat/completions",
            json=payload,
            timeout=None,
        )
        status_code = response.status_code
        if response.status_code == 200:
            body = response.json()
            model_name = body.get("model", "")
        else:
            error = response.text[:200]
    except Exception as e:
        error = str(e)[:200]

    latency_s = time.perf_counter() - t0
    latency_ms = latency_s * 1000

    record = {
        "request_index": index,
        "capability": capability,
        "model_name": model_name,
        "status_code": status_code,
        "latency_ms": round(latency_ms, 2),
        "arrival_time_s": round(arrival_time, 3),
        "completion_time_s": round(arrival_time + latency_s, 3),
        "error": error,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    results.append(record)

    tag = "OK" if status_code == 200 else "FAIL"
    print(
        f"  [{tag}] Req {index:04d} | {capability:15s} | "
        f"{latency_ms:10.0f}ms | {model_name}"
    )


# ── Main driver ──────────────────────────────────────────────────────
async def main():
    parser = argparse.ArgumentParser(
        description="Poisson-arrival multi-capability load test"
    )
    parser.add_argument(
        "--requests", type=int, default=100,
        help="Total number of requests to send (default: 100)",
    )
    parser.add_argument(
        "--rate", type=float, default=0.5,
        help="Mean arrival rate λ (requests/sec). Default 0.5 = 1 req every 2s",
    )
    parser.add_argument(
        "--capability", type=str, default=None,
        help="Force all requests to a single capability (e.g. chat)",
    )
    parser.add_argument(
        "--multi-capability", action="store_true", default=False,
        help="Enable multi-capability mode (60%% chat, 20%% summarization, 20%% reasoning)",
    )
    parser.add_argument(
        "--output", type=str, default=None,
        help="Output JSONL log file path (default: demo/results_<timestamp>.jsonl)",
    )
    args = parser.parse_args()

    # Determine output path
    demo_dir = Path(__file__).parent
    if args.output:
        out_path = Path(args.output)
    else:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = demo_dir / f"results_{ts}.jsonl"

    # Build capability list
    if args.capability:
        capabilities_pool = [args.capability]
        weights = [1.0]
    elif args.multi_capability:
        capabilities_pool = list(CAPABILITY_WEIGHTS.keys())
        weights = list(CAPABILITY_WEIGHTS.values())
    else:
        capabilities_pool = ["chat"]
        weights = [1.0]

    print("=" * 70)
    print("  Foundation AI Platform — Poisson Load Test")
    print("=" * 70)
    print(f"  Requests     : {args.requests}")
    print(f"  Arrival rate : λ = {args.rate} req/s (avg gap = {1/args.rate:.1f}s)")
    print(f"  Capabilities : {capabilities_pool}")
    print(f"  Output log   : {out_path}")
    print("=" * 70)
    print()

    results: list[dict] = []
    tasks: list[asyncio.Task] = []
    wall_start = time.perf_counter()

    async with httpx.AsyncClient() as client:
        for i in range(args.requests):
            # Poisson inter-arrival: exponentially distributed gap
            if i > 0:
                gap = random.expovariate(args.rate)
                await asyncio.sleep(gap)

            capability = random.choices(capabilities_pool, weights=weights, k=1)[0]
            task = asyncio.create_task(
                send_request(client, i, capability, results, wall_start)
            )
            tasks.append(task)

        # Wait for all in-flight requests to finish
        print("\n  Waiting for all in-flight requests to complete...\n")
        await asyncio.gather(*tasks)

    wall_time = time.perf_counter() - wall_start

    # ── Write JSONL log ──────────────────────────────────────────────
    results.sort(key=lambda r: r["request_index"])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")

    # ── Print summary ────────────────────────────────────────────────
    ok_results = [r for r in results if r["status_code"] == 200]
    fail_results = [r for r in results if r["status_code"] != 200]

    print("=" * 70)
    print("  RESULTS SUMMARY")
    print("=" * 70)
    print(f"  Total requests   : {len(results)}")
    print(f"  Successful       : {len(ok_results)}")
    print(f"  Failed           : {len(fail_results)}")
    print(f"  Wall-clock time  : {wall_time:.1f}s")
    print()

    if ok_results:
        latencies = [r["latency_ms"] for r in ok_results]
        latencies.sort()
        avg = sum(latencies) / len(latencies)
        p50 = latencies[len(latencies) // 2]
        p95 = latencies[int(len(latencies) * 0.95)]
        p99 = latencies[int(len(latencies) * 0.99)]

        print(f"  Overall Latency:")
        print(f"    Average : {avg:,.0f} ms")
        print(f"    P50     : {p50:,.0f} ms")
        print(f"    P95     : {p95:,.0f} ms")
        print(f"    P99     : {p99:,.0f} ms")
        print()

        # Per-capability breakdown
        cap_groups: dict[str, list[float]] = {}
        for r in ok_results:
            cap_groups.setdefault(r["capability"], []).append(r["latency_ms"])

        print("  Per-Capability Breakdown:")
        print(f"  {'Capability':20s} {'Count':>6s} {'Avg (ms)':>10s} {'P50 (ms)':>10s} {'P95 (ms)':>10s}")
        print("  " + "-" * 60)
        for cap, lats in sorted(cap_groups.items()):
            lats.sort()
            c_avg = sum(lats) / len(lats)
            c_p50 = lats[len(lats) // 2]
            c_p95 = lats[int(len(lats) * 0.95)]
            print(f"  {cap:20s} {len(lats):6d} {c_avg:10,.0f} {c_p50:10,.0f} {c_p95:10,.0f}")
        print()

        # Per-model breakdown
        model_groups: dict[str, list[float]] = {}
        for r in ok_results:
            model_groups.setdefault(r["model_name"] or "unknown", []).append(r["latency_ms"])

        print("  Per-Model Breakdown:")
        print(f"  {'Model':45s} {'Count':>6s} {'Avg (ms)':>10s}")
        print("  " + "-" * 65)
        for model, lats in sorted(model_groups.items()):
            m_avg = sum(lats) / len(lats)
            print(f"  {model:45s} {len(lats):6d} {m_avg:10,.0f}")
        print()

    print(f"  Detailed log written to: {out_path}")
    print("=" * 70)

    # ── Fetch server-side metrics ────────────────────────────────────
    print("\n  Fetching server-side inference metrics...\n")
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(
                f"{BASE_URL}/v1/inference/metrics?limit={args.requests}",
                timeout=10.0,
            )
            if resp.status_code == 200:
                server_metrics = resp.json()
                server_path = out_path.with_suffix(".server_metrics.json")
                with open(server_path, "w") as f:
                    json.dump(server_metrics, f, indent=2)
                print(f"  Server metrics saved to: {server_path}")

                summary = server_metrics.get("summary", {})
                print(f"  Server-side summary:")
                print(f"    Total requests              : {summary.get('total_requests', 'N/A')}")
                print(f"    Avg E2E latency (ms)        : {summary.get('average_e2e_latency_ms', 'N/A')}")
                print(f"    Avg TTFT (ms)               : {summary.get('average_ttft_ms', 'N/A')}")
                print(f"    Avg TPOT (ms)               : {summary.get('average_tpot_ms', 'N/A')}")
                print(f"    Speculative decoding reqs   : {summary.get('requests_with_speculative_decoding', 'N/A')}")
            else:
                print(f"  Failed to fetch server metrics: {resp.status_code}")
        except Exception as e:
            print(f"  Could not fetch server metrics: {e}")


if __name__ == "__main__":
    asyncio.run(main())
