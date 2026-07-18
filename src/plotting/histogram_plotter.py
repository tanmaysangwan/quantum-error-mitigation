from pathlib import Path

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

_COLOURS = {
    "ideal":     "#2196F3",
    "noisy":     "#F44336",
    "mitigated": "#4CAF50",
}
_LABELS = {
    "ideal":     "Ideal (no noise)",
    "noisy":     "Noisy",
    "mitigated": "Mitigated",
}
_FOOTERS = {
    "ideal":     "Noiseless simulation — what the quantum computer should produce",
    "noisy":     "With quantum noise applied — realistic near-term device behaviour",
    "mitigated": "After error mitigation — corrected result closer to ideal",
}


def save_histogram(
    counts: dict,
    filename: str,
    category: str = "ideal",
    title: str | None = None,
) -> None:
    """
    Save a labelled measurement histogram as a PNG.

    Bars show probability of each bitstring outcome.
    Blue = ideal, Red = noisy, Green = mitigated.

    Args:
        counts:   {bitstring: count} measurement results.
        filename: Base filename (no extension).
        category: 'ideal', 'noisy', or 'mitigated'.
        title:    Optional custom title.
    """
    output_dir = Path("results/figures") / category
    output_dir.mkdir(parents=True, exist_ok=True)

    colour = _COLOURS.get(category, "#9E9E9E")
    label  = _LABELS.get(category, category.capitalize())
    footer = _FOOTERS.get(category, "")

    total  = sum(counts.values())
    states = sorted(counts.keys())
    probs  = [counts[s] / total for s in states]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(states, probs, color=colour, edgecolor="white", linewidth=0.8, zorder=3)

    for bar, prob in zip(bars, probs):
        if prob > 0.01:
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.01,
                f"{prob:.3f}",
                ha="center", va="bottom",
                fontsize=10, fontweight="bold",
            )

    ax.set_title(title or f"Bell State Measurement Results — {label}",
                 fontsize=14, fontweight="bold", pad=14)
    ax.set_xlabel("Measured Bitstring  (qubit 1, qubit 0)", fontsize=12)
    ax.set_ylabel("Probability", fontsize=12)
    ax.set_ylim(0, 1.1)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0%}"))
    ax.grid(axis="y", linestyle="--", alpha=0.5, zorder=0)
    ax.set_axisbelow(True)
    ax.legend(handles=[mpatches.Patch(color=colour, label=label)], fontsize=10)

    fig.text(0.5, 0.01, footer, ha="center", fontsize=9, color="#555555", style="italic")
    fig.tight_layout(rect=[0, 0.04, 1, 1])
    fig.savefig(output_dir / f"{filename}_histogram.png", dpi=150)
