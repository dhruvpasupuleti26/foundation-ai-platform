import time
import requests
import statistics
import json

API_URL = "http://127.0.0.1:8000/chat/completions"

CAPABILITIES = {
    "chat": "Who is Tyrion Lannister?",
    "summarization": "Summarize this: The quick brown fox jumps over the lazy dog.",
    "reasoning": "Solve this: If I have 3 apples and eat 1, how many are left?",
    "math": "What is 15 * 24?"
}

def run_benchmark():
    results = {}
    
    for capability, prompt in CAPABILITIES.items():
        print(f"\n🚀 Benchmarking capability: '{capability}'")
        latencies = []
        
        # We will run 4 inference metric records, each doing 10 requests
        for run_idx in range(4):
            print(f"  ▶ Run {run_idx + 1}/4 (10 prompts)")
            run_latencies = []
            
            for i in range(10):
                payload = {
                    "model": capability,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 15
                }
                
                start_time = time.time()
                try:
                    resp = requests.post(API_URL, json=payload, timeout=30)
                    resp.raise_for_status()
                    latency = time.time() - start_time
                    run_latencies.append(latency)
                except Exception as e:
                    print(f"    Request failed: {e}")
                    
            if run_latencies:
                avg_latency = statistics.mean(run_latencies)
                print(f"    Avg Latency: {avg_latency:.3f} seconds")
                latencies.extend(run_latencies)
                
        if latencies:
            overall_avg = statistics.mean(latencies)
            p90 = sorted(latencies)[int(len(latencies) * 0.9)]
            results[capability] = {
                "overall_avg": overall_avg,
                "p90": p90
            }
            print(f"  ✅ Capability '{capability}' Overall Avg: {overall_avg:.3f}s | P90: {p90:.3f}s")
            
    print("\n" + "="*40)
    print("🏆 FINAL METRICS")
    print("="*40)
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    run_benchmark()
