"""
Writes results_summary.txt: the quoted total-score, domain and top-criteria sentences with their supporting tables.
"""

from pathlib import Path
import analysis
import config as cfg

def total_score_sentence(ds, totals):
    """Range/mean/median/IQR of the system total scores, and which systems are lowest and highest."""
    summary = analysis.total_score_summary(totals)
    lowest = totals.sort_values().head(5)
    highest = totals.sort_values(ascending=False).head(3)
    name = lambda i: ds.systems.at[i, "display_name"]
    return (
        f"Total scores across the {cfg.N_SYSTEMS} systems ranged from {summary['min']} to {summary['max']} "
        f"(mean {summary['mean']:.1f}, median {summary['median']:g}, interquartile range {summary['q1']:g}-{summary['q3']:g}). "
        "The lowest totals were observed for " + "; ".join(f"{name(i)} ({v})" for i, v in lowest.items())
        + ", and the highest for " + "; ".join(f"{name(i)} ({v})" for i, v in highest.items()) + "."
    )

def domain_sentence(stats):
    """Two lowest-concern and three highest-concern domains, with mean and median of each."""
    ordered = stats["mean"].sort_values()
    low = list(ordered.index[:2])
    high = list(ordered.index[-3:][::-1])
    fmt = lambda d: f"{d.lower()} (mean {stats.at[d, 'mean']:.2f}, median {stats.at[d, 'median']:.2f})"
    return (f"{low[0][0].upper() + fmt(low[0])[1:]} and {fmt(low[1])} showed the lowest disclosure concern, whereas "
            f"{fmt(high[0])}, {fmt(high[1])} and {fmt(high[2])} showed the highest.")

def criterion_sentence(criteria):
    """The four criteria with the highest total score, each with its number of 3s and its total."""
    top = analysis.rank_criteria(criteria).head(4)
    parts = [f"{r.criterion} (scored 3 in {int(r.n_score_3)} of {cfg.N_SYSTEMS} systems; total {int(r.total_score)} of {3 * cfg.N_SYSTEMS})"
             for r in top.itertuples()]
    return "The most common high-concern items were " + "; ".join(parts) + "."

def build(ds, matrix_key, out_dir):
    """Write results_summary.txt for one scoring matrix; returns the three sentences."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    scores = ds.scores(matrix_key)
    totals = analysis.system_totals(scores)
    stats = analysis.cohort_domain_stats(analysis.domain_means(scores))
    criteria = analysis.criterion_table(scores, ds.criteria_short)
    membership = ds.type_membership()

    sentences = {"totals": total_score_sentence(ds, totals), "domains": domain_sentence(stats),
                 "criteria": criterion_sentence(criteria)}

    lines = [f"RESULTS SUMMARY - {cfg.MATRICES[matrix_key]['label']} scoring matrix", "=" * 100, "",
             "Total scores", sentences["totals"], "",
             "Domain means and medians", sentences["domains"], "",
             "Highest-concern criteria", sentences["criteria"], "",
             "Domain statistics (mean / median across systems of each system's domain mean)"]
    lines += [f"  {dim:<26} mean {stats.at[dim, 'mean']:.2f}   median {stats.at[dim, 'median']:.2f}" for dim in cfg.DIM_NAMES]
    lines += ["", "Criteria ranked by total score (maximum 75), with number of systems scoring 3"]
    for row in analysis.rank_criteria(criteria).itertuples():
        lines.append(f"  {int(row.criterion_no):>2}. {row.criterion:<48} total {int(row.total_score):>2}   3s: {int(row.n_score_3):>2}")
    lines += ["", "Systems by neuromodulation type (systems typed 'SCS, Peripheral' count in both)"]
    lines += [f"  {t}: n = {len(membership[t])}" for t in cfg.TYPE_ORDER]

    (out_dir / "results_summary.txt").write_text("\n".join(lines) + "\n", encoding="utf8")
    print(f"Wrote {out_dir / 'results_summary.txt'}")
    return sentences