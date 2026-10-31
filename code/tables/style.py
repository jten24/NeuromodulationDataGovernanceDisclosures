"""
Shared great_tables style (Times New Roman, journal rules) and save_table, which renders PNG and PDF via headless Chrome.
"""

from pathlib import Path
from great_tables import loc, style

FONT_NAMES = ["Times New Roman", "Times", "DejaVu Serif"]

def apply_paper_style(table, body_size="12pt", label_size="12pt", padding="6px", source_size="10pt"):
    """Apply the standard journal-table options and text styles to a GT object."""
    return (
        table.tab_options(
            table_width="100%",
            table_layout="fixed",
            table_font_names=FONT_NAMES,
            table_font_size=body_size,
            table_font_color="#555555",
            heading_align="center",
            heading_title_font_size="12pt",
            source_notes_font_size=source_size,
            source_notes_multiline=True,
            column_labels_font_size=label_size,
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
            data_row_padding=padding,
        )
        .tab_style(
            style=style.text(color="#222222", weight="bold", size=label_size, align="left"),
            locations=loc.column_labels(),
        )
        .tab_style(
            style=style.text(font="Times New Roman", size=body_size, align="left", whitespace="pre-wrap"),
            locations=loc.body(),
        )
    )

def save_table(gt, out_dir, stem, window_size=None):
    """Save a GT table as <stem>.png and <stem>.pdf at 3x scale.

    `window_size` is the headless-browser window used for layout. It is set explicitly for most tables because the
    default (6000 x 6000) can make Chrome tile a short table several times in the screenshot.
    """
    out_dir = Path(out_dir)
    options = {"scale": 3.0}
    if window_size is not None:
        options["window_size"] = window_size
    gt.save(str(out_dir / f"{stem}.png"), **options)
    gt.save(str(out_dir / f"{stem}.pdf"), **options)
    print(f"Wrote {out_dir / (stem + '.png')}")