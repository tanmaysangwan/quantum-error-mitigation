"""
Benchmark visualisation.

Reads results/data/benchmark_results.csv and generates:
  1. Heatmap — error reduction % per technique × noise level (one per circuit)
  2. Fidelity vs noise level line plot (one per circuit)
  3. Sampling overhead bar chart (technique comparison)
  4. Summary comparison table printed to terminal
"""

import csv
from pathlib import Path
from collections import defaultdict

import matplotlib.pyplot as plt
import numpy as np


RESULTS_CSV  = Path("results/data/benchmark_results.csv")
OUTPUT_DIR   = Path("results/figures/comparison")

TECHNIQUE_COLORS = {
    "MEM": "#2196F3",
    "ZNE": "#FF9800",
    "PEC": "#9C27B0",
    "CDR": "#F44336",
    "VD":  "#4CAF50",
    "DD":  "#607D8B",
}


def load_results() -> list[dict]:
    """Load benchmark CSV into a list of dicts with numeric types."""
    rows = []
    with open(RESULTS_CSV, newline="") as f:
        for row in csv.DictReader(f):
            row["noise_level"]       = float(row["noise_level"])
            row["fidelity"]          = float(row["fidelity"])
            row["error_reduction_%"] = float(row["error_reduction_%"])
            row["sampling_overhead"] = float(row["sampling_overhead"])
            row["error_before"]      = float(row["error_before"])
            row["error_after"]       = float(row["error_after"])
            rows.append(row)
    return rows


def _group(rows: list[dict]) -> dict:
    """Group rows by circuit → technique → noise_level."""
    grouped = defaultdict(lambda: defaultdict(dict))
    for r in rows:
        grouped[r["circuit"]][r["technique"]][r["noise_level"]] = r
    return grouped


def plot_heatmaps(grouped: dict) -> None:
    """One heatmap per circuit: techniques × noise levels, colour = error reduction %."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for circuit_name, techniques in grouped.items():
        technique_names = sorted(techniques.keys())
        noise_levels    = sorted({nl for t in techniques.values() for nl in t.keys()})

        data = np.full((len(technique_names), len(noise_levels)), np.nan)
        for i, tech in enumerate(technique_names):
            for j, nl in enumerate(noise_levels):
                if nl in techniques[tech]:
                    data[i, j] = techniques[tech][nl]["error_reduction_%"]

        fig, ax = plt.subplots(figsize=(10, 4))
        cmap = plt.cm.RdYlGn  # red=bad, green=good
        im   = ax.imshow(data, cmap=cmap, vmin=0, vmax=100, aspect="auto")

        ax.set_xticks(range(len(noise_levels)))
        ax.set_xticklabels([f"{nl:.0%}" for nl in noise_levels], fontsize=11)
        ax.set_yticks(range(len(technique_names)))
        ax.set_yticklabels(technique_names, fontsize=11)
        ax.set_xlabel("Noise Level (depolarizing error rate)", fontsize=11)
        ax.set_title(f"Error Reduction % — {circuit_name} Circuit",
                     fontsize=13, fontweight="bold", pad=12)

        # Annotate each cell.
        for i in range(len(technique_names)):
            for j in range(len(noise_levels)):
                val = data[i, j]
                if not np.isnan(val):
                    text_color = "white" if val < 20 or val > 80 else "black"
                    ax.text(j, i, f"{val:.0f}%", ha="center", va="center",
                            fontsize=10, fontweight="bold", color=text_color)
                else:
                    ax.text(j, i, "N/A", ha="center", va="center",
                            fontsize=9, color="#888888")

        plt.colorbar(im, ax=ax, label="Error Reduction %")
        fig.tight_layout()
        fig.savefig(OUTPUT_DIR / f"{circuit_name.lower().replace('-','_')}_heatmap.png", dpi=150)
        print(f"  Saved: {circuit_name} heatmap")


def plot_fidelity_lines(grouped: dict) -> None:
    """One line plot per circuit: fidelity vs noise level, one line per technique."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for circuit_name, techniques in grouped.items():
        fig, ax = plt.subplots(figsize=(9, 5))

        noise_levels = sorted({nl for t in techniques.values() for nl in t.keys()})
        noise_pct    = [f"{nl:.0%}" for nl in noise_levels]

        for tech, noise_data in sorted(techniques.items()):
            fidelities = [noise_data[nl]["fidelity"] if nl in noise_data else None
                          for nl in noise_levels]
            valid_x = [noise_pct[i] for i, v in enumerate(fidelities) if v is not None]
            valid_y = [v for v in fidelities if v is not None]
            if valid_y:
                ax.plot(valid_x, valid_y, marker="o", linewidth=2, markersize=7,
                        color=TECHNIQUE_COLORS.get(tech, "#333333"), label=tech)

        ax.set_title(f"Fidelity vs Noise Level — {circuit_name}", fontsize=13,
                     fontweight="bold", pad=12)
        ax.set_xlabel("Noise Level", fontsize=11)
        ax.set_ylabel("Fidelity (1 = perfect recovery)", fontsize=11)
        ax.set_ylim(0.6, 1.05)
        ax.axhline(y=1.0, color="#AAAAAA", linestyle="--", linewidth=1)
        ax.grid(linestyle="--", alpha=0.4)
        ax.legend(fontsize=10)
        fig.tight_layout()
        fig.savefig(OUTPUT_DIR / f"{circuit_name.lower().replace('-','_')}_fidelity.png", dpi=150)
        print(f"  Saved: {circuit_name} fidelity line plot")


def plot_overhead_bars(rows: list[dict]) -> None:
    """Bar chart of sampling overhead per technique (averaged across all experiments)."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    overhead_by_tech = defaultdict(list)
    for r in rows:
        overhead_by_tech[r["technique"]].append(r["sampling_overhead"])

    techniques = sorted(overhead_by_tech.keys())
    avg_overhead = [np.mean(overhead_by_tech[t]) for t in techniques]
    colors       = [TECHNIQUE_COLORS.get(t, "#333333") for t in techniques]

    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.bar(techniques, avg_overhead, color=colors, edgecolor="white", width=0.5)

    for bar, val in zip(bars, avg_overhead):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05,
                f"{val:.2f}×", ha="center", va="bottom", fontsize=10, fontweight="bold")

    ax.set_title("Sampling Overhead per Technique", fontsize=13, fontweight="bold", pad=12)
    ax.set_ylabel("Circuit Execution Multiplier", fontsize=11)
    ax.set_ylim(0, max(avg_overhead) * 1.2)
    ax.axhline(y=1.0, color="#AAAAAA", linestyle="--", linewidth=1, label="Baseline (no mitigation)")
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.legend(fontsize=10)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "sampling_overhead.png", dpi=150)
    print("  Saved: sampling overhead bar chart")


def plot_error_reduction_bars(grouped: dict) -> None:
    """Grouped bar chart: error reduction per technique at each noise level, one chart per circuit."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for circuit_name, techniques in grouped.items():
        noise_levels    = sorted({nl for t in techniques.values() for nl in t.keys()})
        technique_names = sorted(techniques.keys())
        x = np.arange(len(noise_levels))
        n = len(technique_names)
        width = 0.8 / n

        fig, ax = plt.subplots(figsize=(12, 5))

        for i, tech in enumerate(technique_names):
            values = [techniques[tech][nl]["error_reduction_%"]
                      if nl in techniques[tech] else 0.0
                      for nl in noise_levels]
            offset = (i - n / 2 + 0.5) * width
            bars   = ax.bar(x + offset, values, width, label=tech,
                            color=TECHNIQUE_COLORS.get(tech, "#333333"), edgecolor="white")

        ax.set_title(f"Error Reduction % by Technique — {circuit_name}",
                     fontsize=13, fontweight="bold", pad=12)
        ax.set_xlabel("Noise Level", fontsize=11)
        ax.set_ylabel("Error Reduction %", fontsize=11)
        ax.set_xticks(x)
        ax.set_xticklabels([f"{nl:.0%}" for nl in noise_levels])
        ax.axhline(y=0, color="black", linewidth=0.8)
        ax.grid(axis="y", linestyle="--", alpha=0.4)
        ax.legend(fontsize=9, ncol=3)
        fig.tight_layout()
        fig.savefig(OUTPUT_DIR / f"{circuit_name.lower().replace('-','_')}_error_reduction.png", dpi=150)
        print(f"  Saved: {circuit_name} error reduction bar chart")


def print_summary_table(grouped: dict) -> None:
    """Print a terminal summary table matching the problem statement's comparison table."""
    print("\n" + "=" * 80)
    print("PERFORMANCE COMPARISON — averaged across all noise levels")
    print("=" * 80)

    for circuit_name, techniques in grouped.items():
        print(f"\nCircuit: {circuit_name}")
        print(f"  {'Technique':<8} {'Avg Error Red%':>15} {'Avg Fidelity':>14} "
              f"{'Sampling OH':>13} {'Applicable':>12}")
        print("  " + "-" * 65)
        for tech in ["MEM", "ZNE", "PEC", "CDR", "VD", "DD"]:
            if tech in techniques:
                rows = list(techniques[tech].values())
                avg_er  = np.mean([r["error_reduction_%"] for r in rows])
                avg_fid = np.mean([r["fidelity"] for r in rows])
                avg_oh  = np.mean([r["sampling_overhead"] for r in rows])
                print(f"  {tech:<8} {avg_er:>14.1f}% {avg_fid:>14.4f} {avg_oh:>12.2f}×  {'Yes':>10}")
            else:
                print(f"  {tech:<8} {'—':>15} {'—':>14} {'—':>13}  {'N/A':>10}")


def main():
    if not RESULTS_CSV.exists():
        print(f"ERROR: {RESULTS_CSV} not found. Run 'python run.py benchmark' first.")
        return

    print("Loading benchmark results...")
    rows    = load_results()
    grouped = _group(rows)

    print("\nGenerating plots...")
    plot_heatmaps(grouped)
    plot_fidelity_lines(grouped)
    plot_overhead_bars(rows)
    plot_error_reduction_bars(grouped)
    print_summary_table(grouped)

    print(f"\nAll figures saved to {OUTPUT_DIR}/")
    plt.show()


if __name__ == "__main__":
    main()
