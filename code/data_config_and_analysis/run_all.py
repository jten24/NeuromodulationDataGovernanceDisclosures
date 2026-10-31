"""Runs every step (figures, tables, summary) and writes to outputs/.

    python run_all.py                       all steps, Company Policy matrix
    python run_all.py --with-ifu            also the IFU-matrix versions, in <out>/IFU/
    python run_all.py --only fig2,table2    selected steps
    python run_all.py --out some/folder     output folder

Steps: fig1 fig2 fig3 table1 table2 table3 table4 table5 tableS1 tableS2 summary
"""

import argparse
import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # folder holding figures/ and tables/
import config as cfg
import results_summary
from data_io import Dataset
from figures import fig1_prisma, fig2_heatmap, fig3_criteria_bars
from tables import (table1_characteristics, table2_domain_scores, table3_top_criteria, table4_themes, table5_consent_checklist, tableS1_rubric, tableS2_scores)

# (step name, module, depends on the scoring matrix?)
STEPS = [
    ("fig1", fig1_prisma, False),
    ("fig2", fig2_heatmap, True),
    ("fig3", fig3_criteria_bars, True),
    ("table1", table1_characteristics, False),
    ("table2", table2_domain_scores, True),
    ("table3", table3_top_criteria, True),
    ("table4", table4_themes, False),
    ("table5", table5_consent_checklist, False),
    ("tableS1", tableS1_rubric, False),
    ("tableS2", tableS2_scores, True),
    ("summary", results_summary, True),
]

def run_steps(ds, out_dir, matrix_key, selected, only_matrix_dependent=False):
    """Run the selected steps for one scoring matrix and write into `out_dir`."""
    for name, module, depends_on_matrix in STEPS:
        if name not in selected:
            continue
        if only_matrix_dependent and not depends_on_matrix:
            continue                                   # e.g. Table 1 is identical for every matrix; build it once
        started = time.time()
        if depends_on_matrix:
            module.build(ds, matrix_key, out_dir)
        else:
            module.build(ds, out_dir)
        print(f"  [{name}] done in {time.time() - started:.0f}s")

def main(argv=None):
    """Parse arguments, load and validate the data once, then run the selected steps."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", default=str(cfg.DEFAULT_OUT_DIR), help="output folder (default: outputs/)")
    parser.add_argument("--with-ifu", action="store_true", help="also build the matrix-dependent outputs for the IFU matrix")
    parser.add_argument("--only", default="", help="comma-separated step names to run (default: all)")
    args = parser.parse_args(argv)

    all_steps = [name for name, _, _ in STEPS]
    selected = [s.strip() for s in args.only.split(",") if s.strip()] or all_steps
    unknown = [s for s in selected if s not in all_steps]
    if unknown:
        parser.error(f"unknown step(s) {unknown}; choose from {all_steps}")

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    ds = Dataset()

    print(f"Company Policy matrix -> {out_dir}")
    run_steps(ds, out_dir, "company_policy", selected)
    if args.with_ifu:
        ifu_dir = out_dir / "IFU"
        ifu_dir.mkdir(parents=True, exist_ok=True)
        print(f"IFU matrix -> {ifu_dir}")
        run_steps(ds, ifu_dir, "ifu", selected, only_matrix_dependent=True)
    return 0

if __name__ == "__main__":
    sys.exit(main())