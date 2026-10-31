"""
Functions for analysis statistics: system totals, domain means and medians, type-level means, criterion totals and rankings.
"""

import numpy as np
import pandas as pd
import config as cfg

# --------------------------------------------------------------------------------------
# Per-system statistics
# --------------------------------------------------------------------------------------
def system_totals(scores):
    """Sum of the 24 criterion scores for each system (Series indexed by system id)."""
    return scores.sum(axis=0)

def domain_means(scores):
    """Mean score of each system within each governance dimension (DataFrame: systems x 7 domains)."""
    out = pd.DataFrame(index=scores.columns, columns=cfg.DIM_NAMES, dtype=float)
    for dim, criteria in cfg.DIMENSIONS:
        out[dim] = scores.loc[criteria].mean(axis=0)
    return out

def total_score_summary(totals):
    """Mean, median, quartiles (linear interpolation) and range of the system total scores."""
    q1, q3 = np.percentile(totals, [25, 75])
    return dict(n=len(totals), mean=float(totals.mean()), median=float(totals.median()),
                q1=float(q1), q3=float(q3), min=int(totals.min()), max=int(totals.max()))

# --------------------------------------------------------------------------------------
# Cohort-level and type-level domain statistics
# --------------------------------------------------------------------------------------
def cohort_domain_stats(domain_mean_table):
    """Mean and median across systems of the per-system domain means ('All systems' columns of Table 2)."""
    return pd.DataFrame({"mean": domain_mean_table.mean(axis=0), "median": domain_mean_table.median(axis=0)})

def type_domain_means(domain_mean_table, membership):
    """Mean across the member systems of the per-system domain means, for each neuromodulation type."""
    return pd.DataFrame({t: domain_mean_table.loc[ids].mean(axis=0) for t, ids in membership.items() if ids}).T

# --------------------------------------------------------------------------------------
# Criterion-level statistics
# --------------------------------------------------------------------------------------
def criterion_table(scores, criteria_short):
    """One row per criterion: total score over all systems (max 75), mean, and counts of 1s, 2s and 3s."""
    table = pd.DataFrame({
        "criterion_no": scores.index,
        "criterion": criteria_short,
        "dimension": [cfg.CRITERION_TO_DIM[c] for c in scores.index],
        "total_score": scores.sum(axis=1).values,
        "mean_score": scores.mean(axis=1).values,
        "n_score_3": (scores == 3).sum(axis=1).values,
        "n_score_2": (scores == 2).sum(axis=1).values,
        "n_score_1": (scores == 1).sum(axis=1).values,
    })
    table.index = table["criterion_no"].values
    return table

def rank_criteria(criteria):
    """Order criteria by total score (high to low); ties by number of 3s, then by criterion number."""
    return criteria.sort_values(["total_score", "n_score_3", "criterion_no"], ascending=[False, False, True])

def top_with_ties(criteria, n):
    """The top-n criteria; every criterion tied with the nth is kept too, so no tie is broken arbitrarily."""
    ranked = rank_criteria(criteria)
    cutoff = ranked["total_score"].iloc[n - 1]
    return ranked[ranked["total_score"] >= cutoff]

def tie_sentence(criteria, n):
    """Plain-language note naming the extra criteria kept because of a tie ('' when there is no tie)."""
    ranked = rank_criteria(criteria)
    shown = top_with_ties(criteria, n)
    if len(shown) == n:
        return ""
    cutoff = int(ranked["total_score"].iloc[n - 1])
    n_tied = int((ranked["total_score"] == cutoff).sum())
    extra = shown.iloc[n:]
    names = ", ".join(f"{int(r.criterion_no)}. {r.criterion}" for r in extra.itertuples())
    return (f"Because {n_tied} criteria share the {n}th-ranked total score ({cutoff}), {len(shown)} criteria are shown; "
            f"the additional criteria (ranked after the {n}th by number of systems scoring 3) are: {names}.")

def criteria_by_type(scores, membership, criterion_numbers):
    """For each neuromodulation type and criterion: number of member systems, mean score, number/share scoring 3."""
    rows = []
    for t, ids in membership.items():
        if not ids:
            continue
        for c in criterion_numbers:
            values = scores.loc[c, ids]
            rows.append(dict(type=t, criterion_no=c, n_devices=len(ids), mean_score=float(values.mean()),
                             n_score_3=int((values == 3).sum()), share_score_3=float((values == 3).mean())))
    return pd.DataFrame(rows)