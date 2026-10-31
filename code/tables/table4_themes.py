"""
Table 4: qualitative themes, formatted from inputs/themes_text.xlsx.
"""

from pathlib import Path
import pandas as pd
from great_tables import GT
import config as cfg
from tables.style import apply_paper_style, save_table

TITLE = "Table 4. Recurring Qualitative Themes in Public-Facing Data Governance Disclosures."
COLUMN_WIDTHS = {
    "Theme": "15%",
    "Common disclosure pattern": "30%",
    "Limitation": "25%",
    "Relevance to neuromodulation consent": "30%",
}

def build(ds, out_dir):
    """Write table4_disclosure_themes.png/.pdf."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    themes = pd.read_excel(cfg.THEMES_TEXT_XLSX, sheet_name=0)
    if list(themes.columns) != list(COLUMN_WIDTHS):
        raise ValueError(f"Unexpected themes columns: {list(themes.columns)}")

    gt = GT(themes).tab_header(title=TITLE).cols_align(align="left").cols_width(COLUMN_WIDTHS)
    gt = apply_paper_style(gt)
    save_table(gt, out_dir, "table4_disclosure_themes")