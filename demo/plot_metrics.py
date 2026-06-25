"""Plot metrics from a Poisson load test JSONL results file.

Generates multiple charts to visualize platform performance:
  1. Latency over time (scatter, colored by capability)
  2. Latency distribution (histogram, per capability)
  3. Per-model request count (bar chart)
  4. CDF of latency (overall and per capability)
  5. Arrival vs completion timeline

Usage:
    python demo/plot_metrics.py demo/results_20260625_120000.jsonl
    python demo/plot_metrics.py demo/results_20260625_120000.jsonl --output demo/charts/
"""

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib
import numpy as np

matplotlib.rcParams.update({
    "figure.facecolor": "#0d1117",
    "axes.facecolor": "#161b22",
    "axes.edgecolor": "#30363d",
    "axes.labelcolor": "#c9d1d9",
    "text.color": "#c9d1d9",
    "xtick.color": "#8b949e",
    "ytick.color": "#8b949e",
    "grid.color": "#21262d",
    "legend.facecolor": "#161b22",
    "legend.edgecolor": "#30363d",
    "font.size": 11,
})

CAPABILITY_COLORS = {
    "chat": "#58a6ff",
    "summarization": "#3fb950",
    "reasoning": "#d2a8ff",
}


def load_results(path: str) -> list[dict]:
    records = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def plot_latency_over_time(results: list[dict], out_dir: Path):
    """Scatter plot: request arrival time vs latency, colored by capability."""
    fig, ax = plt.subplots(figsize=(14, 6))
    
    for cap, color in CAPABILITY_COLORS.items():
        subset = [r for r in results if r["capability"] == cap and r["status_code"] == 200]
        if not subset:
            continue
        x = [r["arrival_time_s"] for r in subset]
        y = [r["latency_ms"] / 1000 for r in subset]
        ax.scatter(x, y, c=color, label=cap, alpha=0.7, s=30, edgecolors="none")

    ax.set_xlabel("Arrival Time (seconds)")
    ax.set_ylabel("Latency (seconds)")
    ax.set_title("Request Latency Over Time", fontsize=14, fontweight="bold")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_dir / "latency_over_time.png", dpi=150)
    plt.close(fig)
    print(f"  Saved: latency_over_time.png")


def plot_latency_histogram(results: list[dict], out_dir: Path):
    """Histogram of latency per capability."""
    fig, ax = plt.subplots(figsize=(12, 6))

    for cap, color in CAPABILITY_COLORS.items():
        lats = [r["latency_ms"] / 1000 for r in results if r["capability"] == cap and r["status_code"] == 200]
        if not lats:
            continue
        ax.hist(lats, bins=40, alpha=0.6, color=color, label=f"{cap} (n={len(lats)})", edgecolor="none")

    ax.set_xlabel("Latency (seconds)")
    ax.set_ylabel("Count")
    ax.set_title("Latency Distribution by Capability", fontsize=14, fontweight="bold")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_dir / "latency_histogram.png", dpi=150)
    plt.close(fig)
    print(f"  Saved: latency_histogram.png")


def plot_model_distribution(results: list[dict], out_dir: Path):
    """Bar chart showing how many requests each model served."""
    ok = [r for r in results if r["status_code"] == 200]
    model_counts: dict[str, int] = {}
    for r in ok:
        name = r.get("model_name") or "unknown"
        # Shorten name for display
        short = name.split("/")[-1] if "/" in name else name
        model_counts[short] = model_counts.get(short, 0) + 1

    if not model_counts:
        return

    fig, ax = plt.subplots(figsize=(12, 5))
    models = list(model_counts.keys())
    counts = list(model_counts.values())
    colors = ["#58a6ff", "#3fb950", "#d2a8ff", "#f0883e", "#f778ba"]
    bar_colors = [colors[i % len(colors)] for i in range(len(models))]

    bars = ax.barh(models, counts, color=bar_colors, edgecolor="none", height=0.6)
    for bar, count in zip(bars, counts):
        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height() / 2,
                str(count), va="center", ha="left", color="#c9d1d9", fontsize=10)

    ax.set_xlabel("Number of Requests Served")
    ax.set_title("Request Distribution Across Models", fontsize=14, fontweight="bold")
    ax.grid(True, alpha=0.3, axis="x")
    fig.tight_layout()
    fig.savefig(out_dir / "model_distribution.png", dpi=150)
    plt.close(fig)
    print(f"  Saved: model_distribution.png")


def plot_latency_cdf(results: list[dict], out_dir: Path):
    """CDF of latency, overall and per capability."""
    fig, ax = plt.subplots(figsize=(12, 6))

    # Overall
    all_lats = sorted([r["latency_ms"] / 1000 for r in results if r["status_code"] == 200])
    if all_lats:
        y = np.linspace(0, 1, len(all_lats))
        ax.plot(all_lats, y, color="#f0883e", linewidth=2, label="Overall")

    # Per capability
    for cap, color in CAPABILITY_COLORS.items():
        lats = sorted([r["latency_ms"] / 1000 for r in results if r["capability"] == cap and r["status_code"] == 200])
        if not lats:
            continue
        y = np.linspace(0, 1, len(lats))
        ax.plot(lats, y, color=color, linewidth=1.5, linestyle="--", label=cap)

    ax.set_xlabel("Latency (seconds)")
    ax.set_ylabel("Cumulative Probability")
    ax.set_title("Latency CDF", fontsize=14, fontweight="bold")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_dir / "latency_cdf.png", dpi=150)
    plt.close(fig)
    print(f"  Saved: latency_cdf.png")


def plot_timeline(results: list[dict], out_dir: Path):
    """Gantt-style timeline: each request is a horizontal bar from arrival to completion."""
    ok = [r for r in results if r["status_code"] == 200]
    ok.sort(key=lambda r: r["arrival_time_s"])

    if not ok:
        return

    fig, ax = plt.subplots(figsize=(14, max(6, len(ok) * 0.08)))

    for i, r in enumerate(ok):
        start = r["arrival_time_s"]
        dur = r["latency_ms"] / 1000
        color = CAPABILITY_COLORS.get(r["capability"], "#8b949e")
        ax.barh(i, dur, left=start, height=0.8, color=color, alpha=0.7, edgecolor="none")

    ax.set_xlabel("Time (seconds)")
    ax.set_ylabel("Request #")
    ax.set_title("Request Timeline (Arrival → Completion)", fontsize=14, fontweight="bold")

    # Legend
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor=c, label=cap) for cap, c in CAPABILITY_COLORS.items()]
    ax.legend(handles=legend_elements, loc="upper right")
    ax.grid(True, alpha=0.3, axis="x")
    fig.tight_layout()
    fig.savefig(out_dir / "request_timeline.png", dpi=150)
    plt.close(fig)
    print(f"  Saved: request_timeline.png")


def main():
    parser = argparse.ArgumentParser(description="Plot Poisson load test metrics")
    parser.add_argument("results_file", help="Path to the JSONL results file")
    parser.add_argument(
        "--output", type=str, default=None,
        help="Output directory for charts (default: same dir as results file)",
    )
    args = parser.parse_args()

    results_path = Path(args.results_file)
    if not results_path.exists():
        print(f"Error: {results_path} not found")
        return

    out_dir = Path(args.output) if args.output else results_path.parent / "charts"
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n  Loading results from: {results_path}")
    results = load_results(str(results_path))
    print(f"  Loaded {len(results)} records\n")

    print("  Generating charts...")
    plot_latency_over_time(results, out_dir)
    plot_latency_histogram(results, out_dir)
    plot_model_distribution(results, out_dir)
    plot_latency_cdf(results, out_dir)
    plot_timeline(results, out_dir)

    print(f"\n  All charts saved to: {out_dir}/")


if __name__ == "__main__":
    main()
