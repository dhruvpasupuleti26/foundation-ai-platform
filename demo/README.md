# Foundation AI Platform — Demo

This folder contains scripts to benchmark and visualize the platform's
multi-model, multi-capability serving performance.

## Scripts

### `poisson_load_test.py`
Sends requests following a **Poisson arrival process** (realistic traffic
simulation). Supports single-capability and multi-capability modes.

```bash
# Single capability (chat), 100 requests, ~1 every 2 seconds
python demo/poisson_load_test.py --requests 100 --rate 0.5

# Multi-capability (60% chat, 20% summarization, 20% reasoning)
python demo/poisson_load_test.py --requests 200 --rate 1.0 --multi-capability
```

Outputs:
- `demo/results_<timestamp>.jsonl` — per-request metrics (JSONL)
- `demo/results_<timestamp>.server_metrics.json` — server-side telemetry snapshot

### `plot_metrics.py`
Reads a JSONL results file and generates publication-quality charts.

```bash
python demo/plot_metrics.py demo/results_20260625_120000.jsonl
```

Generates in `demo/charts/`:
| Chart | Description |
|-------|-------------|
| `latency_over_time.png` | Scatter plot of latency vs arrival time |
| `latency_histogram.png` | Latency distribution per capability |
| `model_distribution.png` | Bar chart of requests per model |
| `latency_cdf.png` | Cumulative distribution function |
| `request_timeline.png` | Gantt-style arrival→completion view |

## Model ↔ Capability Mapping

| Model | Capability |
|-------|-----------|
| `TinyLlama/TinyLlama-1.1B-Chat-v1.0` | chat |
| `Qwen/Qwen2.5-0.5B-Instruct` | chat |
| `Qwen/Qwen2.5-7B-Instruct` | chat |
| `Qwen/Qwen2.5-1.5B-Instruct` | summarization |
| `deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B` | reasoning |

## Prerequisites

```bash
pip install matplotlib numpy httpx
```
