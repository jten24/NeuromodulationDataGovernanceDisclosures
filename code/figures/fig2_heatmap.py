"""
Figure 2: heatmap of scores (systems x criteria, grouped by company and dimension) with a total-score column.
"""

from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import BoundaryNorm, ListedColormap
import config as cfg
from data_io import short_label

def _plot_frame(ds, scores):
    """Rows and labels in display order: returns (system ids, row labels, scores as systems x criteria)."""
    order = ds.company_grouped_order()
    labels = [short_label(ds.systems.at[i, "display_name"]) for i in order]
    return order, labels, scores[order].to_numpy().T

def _write_source_csv(ds, order, labels, data, out_dir, suffix):
    """Exactly what is drawn, one row per system, for reference and checking."""
    table = pd.DataFrame(data, columns=[f"{c}. {n}" for c, n in zip(range(1, data.shape[1] + 1), ds.criteria_short)])
    table.insert(0, "device_id", order)
    table.insert(1, "device", labels)
    table["total_score"] = data.sum(axis=1)
    table.to_csv(Path(out_dir) / "source_data" / f"figure2_data{suffix}.csv", index=False)

def build(ds, matrix_key, out_dir):
    """Draw Figure 2 for one scoring matrix and write PNG + PDF (+ the plotted data as CSV)."""
    out_dir = Path(out_dir)
    (out_dir / "source_data").mkdir(parents=True, exist_ok=True)
    meta = cfg.MATRICES[matrix_key]

    order, labels, data = _plot_frame(ds, ds.scores(matrix_key))
    totals = data.sum(axis=1)
    n_systems, n_criteria = data.shape
    _write_source_csv(ds, order, labels, data, out_dir, meta["suffix"])

    cmap = ListedColormap([cfg.SCORE_COLORS[1], cfg.SCORE_COLORS[2], cfg.SCORE_COLORS[3]])
    norm = BoundaryNorm([0.5, 1.5, 2.5, 3.5], cmap.N)   # bins centered on the integer scores 1, 2, 3

    plt.rcParams["font.family"] = "serif"
    plt.rcParams["font.serif"] = ["Times New Roman", "Times", "DejaVu Serif"]
    plt.rcParams["font.size"] = 12
    plt.rcParams["axes.titlesize"] = 12
    plt.rcParams["axes.labelsize"] = 12

    # Three side-by-side axes: heatmap | total-score column | color bar.
    fig = plt.figure(figsize=(19, 12.5), dpi=600)
    grid = fig.add_gridspec(1, 3, width_ratios=[24, 1.9, 0.55], wspace=0.035)
    ax = fig.add_subplot(grid[0, 0])
    ax_total = fig.add_subplot(grid[0, 1], sharey=ax)
    ax_bar = fig.add_subplot(grid[0, 2])

    image = ax.imshow(data, cmap=cmap, norm=norm, aspect="auto", interpolation="none")
    ax.set_xticks(np.arange(n_criteria))
    ax.set_xticklabels(ds.criteria_short, rotation=45, ha="right", fontsize=12)
    ax.set_yticks(np.arange(n_systems))
    ax.set_yticklabels(labels, fontsize=12)
    ax.set_xlabel("Disclosure Criteria (grouped by governance dimension)", fontsize=12)
    ax.set_ylabel("Neuromodulation Systems", fontsize=12)
    title = "Figure 2. Public-Facing Disclosure Concern Heatmap by Governance Dimension."
    if matrix_key != "company_policy":
        title = title[:-1] + f" ({meta['label']} scoring matrix)."
    fig.suptitle(title, fontsize=12, y=0.985)

    # White hairlines between cells (minor gridlines sit on the cell edges).
    ax.set_xticks(np.arange(-0.5, n_criteria, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, n_systems, 1), minor=True)
    ax.grid(which="minor", color="white", linestyle="-", linewidth=0.5)
    ax.tick_params(which="minor", bottom=False, left=False)

    # Thick vertical lines: a line before the first criterion of every dimension except the first.
    for _, criteria in cfg.DIMENSIONS[1:]:
        ax.axvline(criteria[0] - 1 - 0.5, color="black", linewidth=2)

    # Thick horizontal lines: after each same-company block (the first 4 rows, then the next 4).
    _, block_sizes = ds.company_group_sizes()
    boundaries = np.cumsum(block_sizes).tolist()
    for b in boundaries:
        ax.axhline(b - 0.5, color="black", linewidth=2)

    # Right-hand column with each system's total score.
    ax_total.set_xlim(0, 1)
    ax_total.set_ylim(n_systems - 0.5, -0.5)
    ax_total.set_facecolor("#f4f4f4")
    for y, total in enumerate(totals):
        ax_total.text(0.5, y, f"{int(total)}", ha="center", va="center", fontsize=12, fontweight="bold", color="#222222")
    ax_total.set_xticks([])
    ax_total.tick_params(axis="y", left=False, labelleft=False)
    ax_total.set_yticks(np.arange(-0.5, n_systems, 1), minor=True)
    ax_total.grid(which="minor", axis="y", color="white", linestyle="-", linewidth=0.5)
    ax_total.tick_params(which="minor", left=False)
    for b in boundaries:
        ax_total.axhline(b - 0.5, color="black", linewidth=2)
    for spine in ("top", "right", "bottom", "left"):
        ax_total.spines[spine].set_visible(False)
    ax_total.set_title("Total\nScore", fontsize=12, fontweight="bold", pad=6)

    colorbar = fig.colorbar(image, cax=ax_bar, ticks=[1, 2, 3])
    colorbar.set_label("Disclosure Concern Score")

    fig.subplots_adjust(left=0.275, right=0.955, top=0.955, bottom=0.255)
    stem = f"figure2_disclosure_concern_heatmap_by_manufacturer{meta['suffix']}"
    fig.savefig(out_dir / f"{stem}.png", dpi=600)
    fig.savefig(out_dir / f"{stem}.pdf")
    plt.close(fig)
    print(f"Wrote {out_dir / (stem + '.png')}")