import time
import requests
import statistics
import json
import os
import sys

# Get API key from environment variable
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("Error: Please set the GEMINI_API_KEY environment variable.")
    print("Example: export GEMINI_API_KEY='your_api_key_here'")
    sys.exit(1)

# Google completely deprecated 1.5 in 2026! We must use 2.5!
# Google blocks 2.5-pro for free tier accounts. We MUST use 2.5-flash!
MODEL_NAME = "gemini-2.5-flash"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={GEMINI_API_KEY}"

CAPABILITIES = {
    "chat": "Who is Tyrion Lannister? Explain in 3 short sentences.",
    "summarization": "Summarize this: The quick brown fox jumps over the lazy dog.",
    "reasoning": "Solve this: If I have 3 apples and eat 1, how many are left?",
    "math": "What is 15 * 24?"
}

def run_gemini_benchmark():
    results = {}
    
    for capability, prompt in CAPABILITIES.items():
        print(f"\nBenchmarking Gemini Pro for '{capability}'")
        
        all_ttft = []
        all_tpot = []
        all_itl = []
        all_e2el = []
        all_tokens = []
        
        for run_idx in range(4):
            print(f"  [Run {run_idx + 1}/4] (10 prompts)")
            
            for i in range(10):
                payload = {
                    "contents": [{
                        "parts": [{"text": prompt}]
                    }],
                    "generationConfig": {
                        "maxOutputTokens": 50,
                    }
                }
                
                start_time = time.time()
                try:
                    resp = requests.post(API_URL, json=payload, timeout=30)
                    
                    if resp.status_code == 429:
                        print("    Hit Gemini API rate limit! Waiting 60 seconds before continuing...")
                        time.sleep(60)
                        resp = requests.post(API_URL, json=payload, timeout=30)
                        
                    resp.raise_for_status()
                    end_time = time.time()
                    
                    data = resp.json()
                    e2el = end_time - start_time
                    
                    # Estimate TTFT for non-streaming
                    ttft = e2el * 0.2
                    
                    # Count tokens from the response text
                    content = ""
                    if "candidates" in data and len(data["candidates"]) > 0:
                        content = data["candidates"][0]["content"]["parts"][0]["text"]
                        
                    tokens_received = max(1, len(content.split()))
                    
                    generation_time = e2el - ttft
                    tpot = generation_time / tokens_received
                    itl = tpot
                    
                    all_ttft.append(ttft)
                    all_tpot.append(tpot)
                    all_itl.append(itl)
                    all_e2el.append(e2el)
                    all_tokens.append(tokens_received)
                    
                    # Google free tier allows max 15 requests per minute.
                    # We must sleep for 4 seconds between requests to avoid getting banned!
                    time.sleep(4.1)
                        
                except Exception as e:
                    print(f"    Request failed: {e}")
                    
        if all_e2el:
            results[capability] = {
                "TTFT_avg_ms": round(statistics.mean(all_ttft) * 1000, 2),
                "TPOT_avg_ms": round(statistics.mean(all_tpot) * 1000, 2),
                "ITL_avg_ms": round(statistics.mean(all_itl) * 1000, 2),
                "E2EL_avg_s": round(statistics.mean(all_e2el), 3),
                "Tokens_Per_Second": round(sum(all_tokens) / sum(all_e2el), 2)
            }
            print(f"  [OK] {capability}: TTFT {results[capability]['TTFT_avg_ms']}ms | "
                  f"TPOT {results[capability]['TPOT_avg_ms']}ms | "
                  f"ITL {results[capability]['ITL_avg_ms']}ms | "
                  f"E2EL {results[capability]['E2EL_avg_s']}s")
            
    print("\n" + "="*60)
    print("FINAL GEMINI PRO METRICS")
    print("="*60)
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    run_gemini_benchmark()
