"""
Table 2: mean and median domain scores overall and mean by neuromodulation type.
"""

from pathlib import Path
import pandas as pd
from great_tables import GT, loc, style
import analysis
import config as cfg
from tables.style import apply_paper_style, save_table

def build_frame(scores, membership):
    """One row per dimension plus the overall row; columns Mean, Median and one mean per type."""
    domain_table = analysis.domain_means(scores)
    stats = analysis.cohort_domain_stats(domain_table)
    by_type = analysis.type_domain_means(domain_table, membership)
    per_criterion_overall = analysis.system_totals(scores) / cfg.N_CRITERIA      # total score / 24

    rows = []
    for dim, criteria in cfg.DIMENSIONS:
        span = f"{criteria[0]}" if len(criteria) == 1 else f"{criteria[0]}-{criteria[-1]}"
        row = {"Governance dimension": f"{dim} (criteri{'on' if len(criteria) == 1 else 'a'} {span})",
               "Mean": stats.at[dim, "mean"], "Median": stats.at[dim, "median"]}
        for t in cfg.TYPE_ORDER:
            row[f"{t} (n = {len(membership[t])})"] = float(by_type.at[t, dim])
        rows.append(row)

    overall = {"Governance dimension": "All 24 criteria (overall)",
               "Mean": float(per_criterion_overall.mean()), "Median": float(per_criterion_overall.median())}
    for t in cfg.TYPE_ORDER:
        overall[f"{t} (n = {len(membership[t])})"] = float(per_criterion_overall[membership[t]].mean())
    rows.append(overall)
    return pd.DataFrame(rows)

def build(ds, matrix_key, out_dir):
    """Write table2_domain_concern_scores(.png/.pdf) and source_data/table2_data.csv for one scoring matrix."""
    out_dir = Path(out_dir)
    (out_dir / "source_data").mkdir(parents=True, exist_ok=True)
    meta = cfg.MATRICES[matrix_key]

    frame = build_frame(ds.scores(matrix_key), ds.type_membership())
    frame.to_csv(out_dir / "source_data" / f"table2_data{meta['suffix']}.csv", index=False)

    type_columns = [c for c in frame.columns if "(n = " in c]
    value_columns = ["Mean", "Median"] + type_columns
    title = "Table 2. Disclosure Concern Scores by Governance Dimension, Overall and by Neuromodulation Type."
    if meta["tag"] != "CP":
        title = title[:-1] + f" ({meta['label']} scoring matrix)."
    note = (
        "Scores range from 1 (low concern) to 3 (high concern). A system's dimension score is the mean of its criterion scores "
        f"within the dimension; Mean and Median are taken across all {cfg.N_SYSTEMS} systems, and type columns show the mean across "
        "systems of that type. Systems labeled SCS, Peripheral are counted in both the SCS and Peripheral groups. "
        "The final row uses all 24 criteria (system total score divided by 24). "
        "DBS, deep brain stimulation; SCS, spinal cord stimulation; VNS, vagus nerve stimulation; RNS, responsive neurostimulation."
    )
    gt = (
        GT(frame)
        .tab_header(title=title)
        .tab_spanner(label=f"All systems (n = {cfg.N_SYSTEMS})", columns=["Mean", "Median"])
        .tab_spanner(label="Mean score by neuromodulation type", columns=type_columns)
        .fmt_number(columns=value_columns, decimals=2)
        .cols_width({"Governance dimension": "330px", "Mean": "90px", "Median": "90px", **{c: "140px" for c in type_columns}})
        .tab_source_note(source_note=note)
    )
    gt = apply_paper_style(gt)
    gt = gt.cols_align(align="center", columns=value_columns).cols_align(align="left", columns=["Governance dimension"])
    gt = gt.tab_style(style=style.text(weight="bold"), locations=loc.body(rows=[len(frame) - 1]))   # bold 'overall' row
    save_table(gt, out_dir, f"table2_domain_concern_scores{meta['suffix']}", window_size=(2200, 1000))