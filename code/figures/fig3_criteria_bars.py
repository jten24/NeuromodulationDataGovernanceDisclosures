"""
Figure 3: highest-concern criteria. Panel A: criterion total score. Panel B: number of systems scoring 3. Top ten, ties kept.
"""

from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import analysis
import config as cfg

TOP_N = 10
BAR_COLOR = "#4c72b0"

def build(ds, matrix_key, out_dir):
    """Draw Figure 3 for one scoring matrix and write PNG + PDF (+ the plotted data as CSV)."""
    out_dir = Path(out_dir)
    (out_dir / "source_data").mkdir(parents=True, exist_ok=True)
    meta = cfg.MATRICES[matrix_key]

    criteria = analysis.rank_criteria(analysis.criterion_table(ds.scores(matrix_key), ds.criteria_short))
    top = analysis.top_with_ties(criteria, TOP_N)
    top[["criterion_no", "criterion", "dimension", "total_score", "n_score_3"]].to_csv(
        out_dir / "source_data" / f"figure3_data{meta['suffix']}.csv", index=False)

    n_systems = cfg.N_SYSTEMS
    max_total = 3 * n_systems          # every system scoring 3 on the criterion
    plt.rcParams["font.family"] = "serif"
    plt.rcParams["font.serif"] = ["Times New Roman", "Times", "DejaVu Serif"]
    plt.rcParams["font.size"] = 12

    # Figure height grows with the number of bars; the two panels share the criterion labels on the y-axis.
    fig, (ax_a, ax_b) = plt.subplots(1, 2, figsize=(17, 0.46 * len(top) + 2.8), sharey=True, dpi=600)
    y = np.arange(len(top))[::-1]      # rank 1 at the top

    ax_a.barh(y, top["total_score"], color=BAR_COLOR, height=0.68)
    ax_a.set_xlim(0, max_total)
    ax_a.set_xticks(np.arange(0, max_total + 1, 15))
    ax_a.set_xlabel(f"Total concern score: sum of scores across all {n_systems} systems (maximum {max_total})", fontsize=12)
    ax_a.set_title("A. Highest-Concern Disclosure Criteria (Total Score)", fontsize=14, pad=10)
    for yy, value in zip(y, top["total_score"]):
        ax_a.text(value + 0.8, yy, f"{int(value)}", va="center", ha="left", fontsize=12)

    ax_b.barh(y, top["n_score_3"], color=BAR_COLOR, height=0.68)
    ax_b.set_xlim(0, n_systems)
    ax_b.set_xticks(np.arange(0, n_systems + 1, 5))
    ax_b.set_xlabel(f"Number of systems scoring 3 (high concern), out of {n_systems}", fontsize=12)
    ax_b.set_title("B. Systems Scoring 3 for the Same Criteria", fontsize=14, pad=10)
    for yy, value in zip(y, top["n_score_3"]):
        ax_b.text(value + 0.25, yy, f"{int(value)}", va="center", ha="left", fontsize=12)

    ax_a.set_yticks(y)
    ax_a.set_yticklabels([f"{n}. {label}" for n, label in zip(top["criterion_no"], top["criterion"])], fontsize=12)
    for ax in (ax_a, ax_b):
        ax.grid(axis="x", linestyle=":", linewidth=0.6, color="#bbbbbb")
        ax.set_axisbelow(True)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)

    title = "Figure 3. Highest-Concern Disclosure Criteria Across Implantable Neuromodulation Systems."
    if meta["tag"] != "CP":
        title = title[:-1] + f" ({meta['label']} scoring matrix)."
    fig.suptitle(title, fontsize=14, y=0.985)

    tie_note = analysis.tie_sentence(criteria, TOP_N)
    footnote = (f"Criteria shown are the {TOP_N} with the highest total scores across all {n_systems} systems "
                "(ties ordered by number of systems scoring 3, then criterion number); criteria are listed in the same order in both panels.")
    if tie_note:
        footnote += "\n" + tie_note
    fig.text(0.5, 0.012, footnote, ha="center", va="bottom", fontsize=10)
    fig.subplots_adjust(left=0.27, right=0.975, top=0.88, bottom=0.155 if tie_note else 0.13, wspace=0.08)

    stem = f"figure3_highest_concern_criteria{meta['suffix']}"
    fig.savefig(out_dir / f"{stem}.png", dpi=600)
    fig.savefig(out_dir / f"{stem}.pdf")
    plt.close(fig)
    print(f"Wrote {out_dir / (stem + '.png')}")