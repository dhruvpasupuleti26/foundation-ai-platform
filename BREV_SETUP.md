# Brev Setup & Testing Guide

Commands to update your existing Brev machine to the latest code and validate the SSD Auto-Sync, Capability-Based Routing, and Load Balancing features.

---

## 1. Update the Repo on Brev

Run these on your **Brev SSH terminal**:

```bash
# Navigate to the repo (already cloned on your machine)
cd foundation-ai-platform

# Pull the latest changes
git pull origin main

# Re-install in case dependencies changed
pip install -e ".[dev]"
```

> **Important — DB Reset for Auto-Sync:** We want to test the platform's ability to automatically detect your downloaded models from the SSD and sync them without creating duplicates. 
> Delete the old database before starting:
> ```bash
> rm -f data/platform.db
> ```

---

## 2. Start the Platform Server

```bash
# From inside foundation-ai-platform/
uvicorn llm_platform.gateway.app:create_default_app \
    --factory \
    --host 0.0.0.0 \
    --port 8000 \
    --reload

# You should see:
# [Bootstrap] Initialized with N models in registry.
# [SSD Sync] Found un-registered model on SSD: Qwen/Qwen2.5-0.5B-Instruct. Auto-registering...
# [Lifecycle Worker] Starting lifecycle management background worker.
# INFO:     Uvicorn running on http://0.0.0.0:8000
```

Keep this terminal open. Open a **second terminal** for all the test commands below.

---

## 3. Verify SSD Auto-Sync

The `bootstrap.py` script automatically scans `data/model-cache/` and registers any models it finds with the default `["chat"]` capability. Verify there are no duplicates:

```bash
# List capabilities → model mapping
curl -s http://localhost:8000/v1/models/capabilities | python3 -m json.tool
```

You should see all your SSD models (like `Qwen2.5-1.5B`, `Qwen2.5-0.5B`, `DeepSeek-R1`, `TinyLlama`) neatly listed exactly once under the `"chat"` capability!

---

## 4. Spin Up Multiple Models for Load Balancing

Right now, all models have the `chat` capability, but none are loaded into the GPU. To test load balancing across multiple active models, we need to spin up two of them.

**Terminal 1 (Spin up Model A):**
Send a generic chat request. The router will pick the first available model (e.g., DeepSeek or Qwen 1.5B) and cold start it.
```bash
curl -s -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "capability": "chat",
    "messages": [{"role": "user", "content": "What is 2+2?"}]
  }' | python3 -m json.tool
```
*(Wait 1-2 minutes for this to finish booting from SSD to GPU).*

**Terminal 2 (Spin up Model B):**
To force a second, distinct model to spin up alongside the first one, explicitly request it by name.
```bash
curl -s -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "capability": "chat",
    "model": "Qwen/Qwen2.5-0.5B-Instruct",
    "messages": [{"role": "user", "content": "What is 3+3?"}]
  }' | python3 -m json.tool
```

Check the GPU status to confirm BOTH containers are now running and taking up memory!
```bash
curl -s http://localhost:8000/v1/gpu/status | python3 -m json.tool
```

---

## 5. Test Capability Load Balancing

Now that both Model A and Model B are `READY` and `HOT` for the `"chat"` capability, the router will automatically load balance across them.

Send this generic request 4 or 5 times rapidly:
```bash
curl -s -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "capability": "chat",
    "messages": [{"role": "user", "content": "Tell me a joke!"}]
  }' | python3 -m json.tool
```

**Verify the Load Balancing:**
Check the metrics snapshot. Look at the `recent_requests` array and observe how the `model_name` randomly bounces between the two models you spun up!
```bash
curl -s "http://localhost:8000/v1/inference/metrics?limit=10" | python3 -m json.tool
```

---

## 6. Test Eviction (GPU Full Scenario)

Fill up the GPU VRAM so the router is forced to forcefully evict one of your running models to make room for a new one.

```bash
# Register an existing SSD model with a fake, inflated memory requirement so the GPU Tracker thinks the GPU is full.
curl -s -X POST http://localhost:8000/v1/models/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    "version": "1.0",
    "family": "llama",
    "engine": "vllm",
    "capabilities": ["embedding"],
    "memory_requirement_gb": 22,
    "ownership": "test",
    "metadata": {}
  }' | python3 -m json.tool

# Trigger an embedding request to spin up the container and allocate the 22GB
curl -s -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"capability": "embedding", "model": "TinyLlama/TinyLlama-1.1B-Chat-v1.0", "messages": [{"role": "user", "content": "Hi!"}]}' \
  | python3 -m json.tool

# GPU status should now reflect 22GB allocated, leaving only ~2GB available.
curl -s http://localhost:8000/v1/gpu/status | python3 -m json.tool

# Wait 15 seconds for the lifecycle state of the 22GB model to transition from HOT to WARM
sleep 15

# Now try to route a chat request (requires 4GB). Since 4GB > 2GB free, the router must evict the 22GB model!
curl -s -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"capability": "chat", "messages": [{"role": "user", "content": "Hi!"}]}' \
  | python3 -m json.tool
```

---

## Troubleshooting

**vLLM container fails to start:**
```bash
# Check Docker logs for the container
docker logs vllm-qwen-qwen2-5-1-5b-instruct --tail 50

# Check if port is already in use
ss -tlnp | grep 800
```

**GPU tracker not reflecting reality:**
```bash
# Check actual GPU usage
nvidia-smi
# Compare with platform's bookkeeping
curl -s http://localhost:8000/v1/gpu/status
```
