"""
Table 3: the six highest-concern criteria (chosen from the full cohort, ties kept) with totals and counts of 3s overall and by type.
"""

from pathlib import Path
import pandas as pd
from great_tables import GT
import analysis
import config as cfg
from tables.style import apply_paper_style, save_table

TOP_N = 6

def build_frames(ds, matrix_key):
    """Return (display frame, flat frame for CSV, tie note, membership)."""
    scores = ds.scores(matrix_key)
    criteria = analysis.rank_criteria(analysis.criterion_table(scores, ds.criteria_short))
    top = analysis.top_with_ties(criteria, TOP_N)
    numbers = top["criterion_no"].tolist()
    membership = ds.type_membership()
    by_type = analysis.criteria_by_type(scores, membership, numbers)

    display_rows, flat_rows = [], []
    for c in numbers:
        crit = criteria.loc[c]
        display = {"Criterion": f"{c}. {crit['criterion']}", "total": int(crit["total_score"]),
                   "n3": f"{int(crit['n_score_3'])}/{cfg.N_SYSTEMS}"}
        flat = {"criterion_no": c, "criterion": crit["criterion"], "total_score_all_devices": int(crit["total_score"]),
                "n_score_3_all_devices": int(crit["n_score_3"]), "n_devices": cfg.N_SYSTEMS}
        for t in cfg.TYPE_ORDER:
            cell = by_type[(by_type["type"] == t) & (by_type["criterion_no"] == c)].iloc[0]
            display[f"{t}__mean"] = float(cell["mean_score"])
            display[f"{t}__n3"] = f"{int(cell['n_score_3'])}/{int(cell['n_devices'])}"
            flat[f"{t}_mean_score"] = float(cell["mean_score"])
            flat[f"{t}_n_score_3"] = int(cell["n_score_3"])
            flat[f"{t}_n_devices"] = int(cell["n_devices"])
        display_rows.append(display)
        flat_rows.append(flat)
    return pd.DataFrame(display_rows), pd.DataFrame(flat_rows), analysis.tie_sentence(criteria, TOP_N), membership

def build(ds, matrix_key, out_dir):
    """Write table3_top_criteria_by_type(.png/.pdf) and source_data/table3_data.csv for one scoring matrix."""
    out_dir = Path(out_dir)
    (out_dir / "source_data").mkdir(parents=True, exist_ok=True)
    meta = cfg.MATRICES[matrix_key]

    frame, flat, tie_note, membership = build_frames(ds, matrix_key)
    flat.to_csv(out_dir / "source_data" / f"table3_data{meta['suffix']}.csv", index=False)

    title = f"Table 3. Highest-Concern Disclosure Criteria Overall and by Neuromodulation Type (Top {TOP_N} Criteria)."
    if meta["tag"] != "CP":
        title = title[:-1] + f" ({meta['label']} scoring matrix)."
    note = (
        f"The top {TOP_N} criteria are those with the highest total scores across all {cfg.N_SYSTEMS} systems (maximum total {3 * cfg.N_SYSTEMS}); "
        "they were identified from the full cohort and were not recomputed separately within each neuromodulation type. "
        "Mean = mean disclosure concern score per system (1 = low, 3 = high); Scored 3 = number of systems scoring 3 / number of systems of that type. "
        "Systems labeled SCS, Peripheral are counted in both the SCS and Peripheral groups. "
        "DBS, deep brain stimulation; SCS, spinal cord stimulation; VNS, vagus nerve stimulation; RNS, responsive neurostimulation."
        + (" " + tie_note if tie_note else "")
    )

    gt = GT(frame).tab_header(title=title)
    gt = gt.cols_label(**{"Criterion": "Criterion", "total": "Total score", "n3": "Systems scored 3"})
    gt = gt.tab_spanner(label=f"All systems (n = {cfg.N_SYSTEMS})", columns=["total", "n3"])
    widths = {"Criterion": "300px", "total": "100px", "n3": "150px"}
    for t in cfg.TYPE_ORDER:                      # one spanner per type, holding its 'Mean' and 'Scored 3' columns
        gt = gt.cols_label(**{f"{t}__mean": "Mean", f"{t}__n3": "Scored 3"})
        gt = gt.tab_spanner(label=f"{t} (n = {len(membership[t])})", columns=[f"{t}__mean", f"{t}__n3"])
        widths[f"{t}__mean"] = "70px"
        widths[f"{t}__n3"] = "85px"
    gt = gt.fmt_number(columns=[f"{t}__mean" for t in cfg.TYPE_ORDER], decimals=2)
    gt = gt.cols_width(widths).tab_source_note(source_note=note)
    gt = apply_paper_style(gt)
    gt = gt.cols_align(align="center", columns=[c for c in frame.columns if c != "Criterion"]).cols_align(align="left", columns=["Criterion"])
    save_table(gt, out_dir, f"table3_top_criteria_by_type{meta['suffix']}", window_size=(2200, 1000))