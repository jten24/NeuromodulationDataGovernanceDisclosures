"""
Figure 1: PRISMA flow diagram. Counts are recorded in config.PRISMA_COUNTS.
"""

from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import config as cfg

HEADER_COLOR = "#F4B183"   # orange title band
SIDE_COLOR = "#5B9BD5"     # blue phase labels (Identification / Screening / Included)
EDGE_COLOR = "#1a1a1a"

def check_counts(c=cfg.PRISMA_COUNTS):
    """Assert that the recorded PRISMA counts add up and match the number of scored systems."""
    assert c["records_screened"] - c["excluded_total"] == c["systems_assessed"]
    assert (c["excluded_duplicate"] + c["excluded_pma_unverified"] + c["excluded_incorrect_device"]
            + c["excluded_incorrect_pma"]) == c["excluded_total"]
    assert c["systems_assessed"] - c["excluded_before_scoring"] == c["original_pull_systems"]
    assert c["original_pull_systems"] + c["added_by_reference_matching"] == cfg.N_SYSTEMS
    assert c["original_pull_systems"] == cfg.N_ORIGINAL_SYSTEMS

def _box(ax, x, y, w, h, text, fc="white", fontsize=8.5, weight="normal", color="#1a1a1a", rotation=0):
    """A rectangle with centered text, in axes coordinates (x, y = lower-left corner)."""
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="square,pad=0", facecolor=fc, edgecolor=EDGE_COLOR,
                                linewidth=1.1, transform=ax.transAxes, clip_on=False))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fontsize, fontweight=weight,
            color=color, linespacing=1.35, rotation=rotation, transform=ax.transAxes)

def _arrow(ax, x1, y1, x2, y2):
    """A filled-head arrow from (x1, y1) to (x2, y2), in axes coordinates."""
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=12, linewidth=1.1,
                                 color=EDGE_COLOR, transform=ax.transAxes, clip_on=False))
def _draw_identification(ax, c):
    _box(ax, 0.015, 0.755, 0.055, 0.125, "Identification", fc=SIDE_COLOR, fontsize=8, weight="bold", color="white", rotation=90)
    _box(ax, 0.10, 0.755, 0.40, 0.125,
         f"FDA Product Codes Identified\n(n = {c['product_codes']})\n\nOriginal database pull:\nOctober 17, 2025", fontsize=9)
    _box(ax, 0.62, 0.755, 0.35, 0.125,
         "Records Removed Before Screening\nDuplicate records removed (n = 0)\n"
         "Records marked as ineligible by\nautomation tools (n = 0)\nRecords removed for other reasons (n = 0)",
         fontsize=8)
    _arrow(ax, 0.50, 0.817, 0.62, 0.817)
    _arrow(ax, 0.30, 0.755, 0.30, 0.725)

def _draw_screening(ax, c):
    _box(ax, 0.015, 0.455, 0.055, 0.255, "Screening", fc=SIDE_COLOR, fontsize=8, weight="bold", color="white", rotation=90)
    _box(ax, 0.10, 0.585, 0.40, 0.125,
         f"Candidate FDA-Linked Device\nRecords Screened\n(n = {c['records_screened']})", fontsize=9)
    _box(ax, 0.62, 0.572, 0.35, 0.150,
         f"Records Excluded (n = {c['excluded_total']})\nDuplicate records (n = {c['excluded_duplicate']})\n"
         f"PMA could not be verified (n = {c['excluded_pma_unverified']})\n"
         f"Incorrect device (n = {c['excluded_incorrect_device']})\nIncorrect PMA (n = {c['excluded_incorrect_pma']})",
         fontsize=8)
    _arrow(ax, 0.50, 0.647, 0.62, 0.647)
    _arrow(ax, 0.30, 0.585, 0.30, 0.555)
    _box(ax, 0.10, 0.430, 0.40, 0.125,
         f"Candidate Systems Assessed\nfor Public-Facing Documentation\n(n = {c['systems_assessed']})", fontsize=9)
    _box(ax, 0.62, 0.445, 0.35, 0.095,
         f"Systems Excluded Before Scoring\n(n = {c['excluded_before_scoring']})\nLeads and ancillary components\n"
         f"(n = {c['excluded_before_scoring']})", fontsize=8)
    _arrow(ax, 0.50, 0.492, 0.62, 0.492)
    _arrow(ax, 0.30, 0.430, 0.30, 0.400)

def _draw_included(ax, c):
    """Original pull -> four systems added by reference matching -> final cohort."""
    _box(ax, 0.015, 0.055, 0.055, 0.330, "Included", fc=SIDE_COLOR, fontsize=8, weight="bold", color="white", rotation=90)
    _box(ax, 0.16, 0.300, 0.46, 0.085,
         f"Systems from the original\nOctober 17, 2025 database pull\n(n = {c['original_pull_systems']})", fontsize=9)
    _arrow(ax, 0.39, 0.300, 0.39, 0.270)
    _box(ax, 0.16, 0.155, 0.46, 0.115,
         f"Systems added by reference matching (n = {c['added_by_reference_matching']})\n"
         "SetPoint, Curonix Freedom,\nBiotronik Prospera, and SPRINT\n"
         "No second database search", fontsize=9)
    _arrow(ax, 0.39, 0.155, 0.39, 0.125)
    _box(ax, 0.16, 0.040, 0.46, 0.085,
         f"Systems Included in Final\nPolicy Audit\n(n = {cfg.N_SYSTEMS})", fontsize=10, weight="bold")

def build(ds, out_dir):
    """Draw Figure 1 and write figure1_PRISMA.png / .pdf."""
    check_counts()
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    c = cfg.PRISMA_COUNTS

    plt.rcParams["font.family"] = "serif"
    plt.rcParams["font.serif"] = ["Times New Roman", "Times", "DejaVu Serif"]

    fig, ax = plt.subplots(figsize=(11.2, 13.4), dpi=200)
    ax.set_axis_off()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    fig.text(0.06, 0.975, "Figure 1. Identification of Implantable Neuromodulation Systems Included in the Policy Audit.",
             ha="left", va="top", fontsize=11, fontweight="bold")
    fig.text(0.06, 0.952, "PRISMA 2020 flow diagram for new systematic reviews which included searches of databases and registers only",
             ha="left", va="top", fontsize=8, style="italic", color="#333333")
    _box(ax, 0.14, 0.905, 0.78, 0.032, "Identification of Implantable Neuromodulation Systems for Policy Audit",
         fc=HEADER_COLOR, fontsize=9, weight="bold")

    _draw_identification(ax, c)
    _draw_screening(ax, c)
    _draw_included(ax, c)

    fig.subplots_adjust(left=0.02, right=0.98, top=0.93, bottom=0.02)
    stem = out_dir / "figure1_PRISMA"
    fig.savefig(stem.with_suffix(".png"), dpi=300)
    fig.savefig(stem.with_suffix(".pdf"))
    plt.close(fig)
    print(f"Wrote {stem.with_suffix('.png')}")