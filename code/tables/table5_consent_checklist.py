"""
Table 5: consent checklist, formatted from inputs/checklist_text.xlsx, in versions with and without the 'Changes over time' row.
"""

from pathlib import Path
import pandas as pd
from great_tables import GT
import config as cfg
from tables.style import apply_paper_style, save_table

ELEMENT, QUESTION = "Minimum disclosure element", "Patient-facing question"

# The proposed extra checklist row.
NEW_ROW = {
    "Domain": "Changes over time",
    ELEMENT: ("Notify patients of new or expanded data uses or sharing (for example, new recipients, purposes, or features) "
              "that occur after initial consent, and state whether patients can accept or decline them"),
    QUESTION: "“Will I be told if how my data is used or shared changes?”",
    "Responsible party": "Manufacturer",
}
INSERT_AFTER_DOMAIN = "Third-party sharing"
TITLE = "Table 5. Minimum Disclosure and Consent Checklist for Connected Implantable Neuromodulation Systems."
COLUMN_WIDTHS = {"Domain": "15%", ELEMENT: "35%", QUESTION: "30%", "Responsible party": "20%"}

def _render(table, stem, out_dir):
    gt = GT(table).tab_header(title=TITLE).cols_align(align="left").cols_width(COLUMN_WIDTHS)
    gt = apply_paper_style(gt).tab_options(table_width="1500px")
    save_table(gt, out_dir, stem, window_size=(1700, 1000))

def build(ds, out_dir):
    """Write both versions of Table 5 (.png/.pdf) and their source data (.xlsx)."""
    out_dir = Path(out_dir)
    (out_dir / "source_data").mkdir(parents=True, exist_ok=True)

    source = pd.read_excel(cfg.CHECKLIST_TEXT_XLSX, sheet_name=0)
    if list(source.columns) != list(NEW_ROW):
        raise ValueError(f"Unexpected checklist columns: {list(source.columns)}")
    without_new = source

    position = without_new.index[without_new["Domain"] == INSERT_AFTER_DOMAIN]
    if len(position) != 1:
        raise ValueError(f"Could not find unique row {INSERT_AFTER_DOMAIN!r} in the checklist source")
    cut = int(position[0]) + 1
    with_new = pd.concat([without_new.iloc[:cut], pd.DataFrame([NEW_ROW]), without_new.iloc[cut:]], ignore_index=True)

    without_new.to_excel(out_dir / "source_data" / "Table3_Data_without_new_question.xlsx", index=False)
    with_new.to_excel(out_dir / "source_data" / "Table3_Data_with_new_question.xlsx", index=False)
    _render(without_new, "table5_consent_checklist_without_new_question", out_dir)
    _render(with_new, "table5_consent_checklist_with_new_question", out_dir)