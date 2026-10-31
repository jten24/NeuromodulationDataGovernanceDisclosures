"""
Supplementary Table S2: full score matrix (criteria x systems, same system order as Figure 2) with a total-score row.
"""

from pathlib import Path
import pandas as pd
from great_tables import GT, loc, style
import analysis
import config as cfg
from data_io import short_label
from tables.style import save_table

COLUMN_WIDTHS_PX = {"score": 99, "dimension": 90, "criterion": 215}
FONT = "Times New Roman"

# --------------------------------------------------------------------------------------
# Text wrapping
# --------------------------------------------------------------------------------------
def wrap_words(text, max_len=22):
    """Greedy word wrap into lines of at most `max_len` characters, joined with newlines."""
    words = str(text).split()
    if not words:
        return str(text)
    lines, current = [], []
    for word in words:
        if len(" ".join(current + [word])) <= max_len:
            current.append(word)
        else:
            if current:
                lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))
    return "\n".join(lines)

def wrap_criterion(text, body_max_len=28):
    """'3. Threat Notification: Breach reporting ...' -> title on its own line, definition wrapped below it."""
    text = str(text).strip()
    if ":" not in text:
        return wrap_words(text, body_max_len)
    title, body = text.split(":", 1)
    return f"{title.strip()}:\n{wrap_words(body.strip(), body_max_len)}"

def dimension_label(dim):
    """'Data Security' -> 'Data Security (18-23)'."""
    criteria = dict(cfg.DIMENSIONS)[dim]
    span = f"{criteria[0]}" if len(criteria) == 1 else f"{criteria[0]}-{criteria[-1]}"
    return f"{dim} ({span})"

# --------------------------------------------------------------------------------------
# Table content
# --------------------------------------------------------------------------------------
def build_frame(ds, scores, order, names):
    """Rows: 24 criteria then 'Total'. Returns (display frame with wrapped text, plain frame for CSV)."""
    totals = analysis.system_totals(scores)
    rows = []
    for c in scores.index:
        row = {"Dimension": wrap_words(dimension_label(cfg.CRITERION_TO_DIM[c]), 16),
               "Criterion": wrap_criterion(ds.criteria[c - 1], 36)}
        row.update({name: int(scores.at[c, i]) for i, name in zip(order, names)})
        rows.append(row)
    total_row = {"Dimension": "Total", "Criterion": wrap_words("Total score (sum of 24 criteria; range 24-72)", 36)}
    total_row.update({name: int(totals[i]) for i, name in zip(order, names)})
    rows.append(total_row)
    display = pd.DataFrame(rows)

    plain = display.copy()
    plain["Dimension"] = ["" if k == len(plain) - 1 else cfg.CRITERION_TO_DIM[k + 1] for k in range(len(plain))]
    plain["Criterion"] = [ds.criteria[k] if k < cfg.N_CRITERIA else "Total score" for k in range(len(plain))]
    return display, plain

def company_column_boundaries(ds, order, names):
    """Names of the first system of each new company block (and of the first single-company system)."""
    boundaries, prev_parent, prev_multi = [], None, None
    for position, i in enumerate(order):
        parent = ds.systems.at[i, "parent"]
        multi = ds.systems.at[i, "parent_group_size"] > 1
        if position > 0 and ((multi and parent != prev_parent) or (multi != prev_multi)):
            boundaries.append(names[position])
        prev_parent, prev_multi = parent, multi
    return boundaries

# --------------------------------------------------------------------------------------
# Build
# --------------------------------------------------------------------------------------
def build(ds, matrix_key, out_dir):
    """Write tableS2_heatmap_scores_criteria_rows_compact_horizontal(.png/.pdf) + source CSV for one matrix."""
    out_dir = Path(out_dir)
    (out_dir / "source_data").mkdir(parents=True, exist_ok=True)
    meta = cfg.MATRICES[matrix_key]
    scores = ds.scores(matrix_key)
    order = ds.company_grouped_order()
    names = [short_label(ds.systems.at[i, "display_name"]) for i in order]

    frame, plain = build_frame(ds, scores, order, names)
    plain.to_csv(out_dir / "source_data" / f"tableS2_data{meta['suffix']}.csv", index=False)

    # Horizontal rule above the first criterion of each new dimension and above the Total row.
    dims = [cfg.CRITERION_TO_DIM[c] for c in scores.index] + ["Total"]
    row_boundaries = [k for k in range(1, len(dims)) if dims[k] != dims[k - 1]]
    column_boundaries = company_column_boundaries(ds, order, names)

    label_columns = ["Dimension", "Criterion"]
    widths = {"Dimension": f"{COLUMN_WIDTHS_PX['dimension']}px", "Criterion": f"{COLUMN_WIDTHS_PX['criterion']}px",
              **{n: f"{COLUMN_WIDTHS_PX['score']}px" for n in names}}
    total_width = sum(int(v[:-2]) for v in widths.values())

    title = "Supplementary Table S2. System-Level Public Disclosure Concern Scores by Criterion"
    if meta["tag"] != "CP":
        title += f" ({meta['label']} scoring matrix)"
    note = (
        "Scale: 1 = Low Concern; 2 = Some Concern; 3 = High Concern. Total score = sum of the 24 criterion scores (range 24-72). "
        "Systems from the same parent company are adjacent and separated from other systems by vertical lines; "
        "horizontal lines separate governance dimensions. "
        "DBS, deep brain stimulation; PNS, peripheral nerve stimulation; RNS, responsive neurostimulation; SCS, spinal cord stimulation; VNS, vagus nerve stimulation."
    )

    gt = (
        GT(frame)
        .tab_header(title=title)
        .tab_source_note(source_note=note)
        .cols_label(**{n: wrap_words(n, 11) for n in names})
        .cols_align(align="center", columns=names)
        .cols_align(align="left", columns=label_columns)
        .cols_width(widths)
        .tab_options(
            table_width=f"{total_width}px",
            table_layout="fixed",
            container_height="auto",
            container_overflow_x="visible",
            container_overflow_y="visible",
            table_font_names=[FONT, "Times", "DejaVu Serif"],
            table_font_size="10pt",
            table_font_color="#555555",
            heading_align="center",
            heading_title_font_size="12pt",
            source_notes_font_size="10pt",
            source_notes_multiline=True,
            column_labels_font_size="8pt",
            column_labels_font_weight="bold",
            column_labels_border_top_style="solid",
            column_labels_border_top_width="2px",
            column_labels_border_top_color="#000000",
            column_labels_border_bottom_style="solid",
            column_labels_border_bottom_width="1px",
            column_labels_border_bottom_color="#000000",
            table_body_hlines_style="solid",
            table_body_hlines_width="1px",
            table_body_hlines_color="#000000",
            table_border_bottom_style="solid",
            table_border_bottom_width="2px",
            table_border_bottom_color="#000000",
            table_body_vlines_style="none",
            column_labels_vlines_style="none",
            table_border_left_style="none",
            table_border_right_style="none",
            row_striping_include_table_body=False,
            row_striping_include_stub=False,
            data_row_padding="22px",
        )
        .tab_style(style=style.text(color="#222222", weight="bold", size="8pt", align="center"), locations=loc.column_labels())
        .tab_style(style=style.text(font=FONT, size="9pt", align="left", whitespace="pre-wrap"), locations=loc.body(columns=label_columns))
        .tab_style(style=style.text(font=FONT, size="9pt", align="left", whitespace="pre-wrap"), locations=loc.column_labels(columns=label_columns))
        .tab_style(style=style.text(font=FONT, size="8pt", align="center", whitespace="pre-wrap"), locations=loc.column_labels(columns=names))
        .tab_style(style=style.text(font=FONT, size="10pt", align="center", weight="bold", color="#111111"), locations=loc.body(columns=names))
    )

    # Color every score cell (rows 0-23); the Total row (row 24) is left uncolored and bold.
    for r in range(cfg.N_CRITERIA):
        for name in names:
            gt = gt.tab_style(style=style.fill(color=cfg.SCORE_COLORS[int(frame.at[r, name])]), locations=loc.body(rows=r, columns=name))
    gt = gt.tab_style(style=style.text(weight="bold"), locations=loc.body(rows=[cfg.N_CRITERIA], columns=label_columns))
    for r in row_boundaries:
        gt = gt.tab_style(style=style.borders(sides="top", color="#000000", weight=3), locations=loc.body(rows=r))
    for name in column_boundaries:
        gt = gt.tab_style(style=style.borders(sides="left", color="#000000", weight=3), locations=loc.body(columns=name))
        gt = gt.tab_style(style=style.borders(sides="left", color="#000000", weight=3), locations=loc.column_labels(columns=name))

    save_table(gt, out_dir, f"tableS2_heatmap_scores_criteria_rows_compact_horizontal{meta['suffix']}", window_size=(3400, 3400))