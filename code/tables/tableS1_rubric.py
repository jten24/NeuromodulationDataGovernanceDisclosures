"""
Supplementary Table S1: scoring rubric, formatted from inputs/rubric_text.xlsx.
"""

from html import escape
from pathlib import Path
import pandas as pd
from great_tables import GT, loc, style
import config as cfg
from tables.style import apply_paper_style, save_table

TITLE = "Table S1. Security Scoring Rubric and Criterion Definitions"
SCALE_NOTE = ("Scale: 1 = Low Risk; 2 = Some Concerns; 3 = High Risk. Each numbered criterion represents a specific "
              "privacy practice assessed across manufacturers.")
SOURCE_COLUMNS = ["Criterion", "Dimension", "Definition", "Indicators", "High Risk", "Low Risk", "Some Concerns"]
RISK_COLUMN = "Risk Level Scoring Insight"
COLUMN_WIDTHS = {"Criterion": "12%", "Dimension": "9.5%", "Definition": "25%", "Indicators": "22.5%", RISK_COLUMN: "31%"}
WINDOW_SIZE = (4636, 4023)

def risk_html(row):
    """'High Risk: ...<br>Low Risk: ...<br>Some Concerns: ...' with the three labels in bold."""
    return "<br>".join(f"<b>{label}:</b> {escape(str(row[label]))}" for label in ("High Risk", "Low Risk", "Some Concerns"))

def build_frame():
    """Read the rubric text and return the display frame (one row per criterion)."""
    rubric = pd.read_excel(cfg.RUBRIC_TEXT_XLSX, sheet_name=0)
    if list(rubric.columns) != SOURCE_COLUMNS:
        raise ValueError(f"Unexpected rubric columns: {list(rubric.columns)}")
    if len(rubric) != cfg.N_CRITERIA:
        raise ValueError(f"Expected {cfg.N_CRITERIA} criteria, found {len(rubric)}")
    frame = rubric[["Criterion", "Dimension", "Definition", "Indicators"]].copy()
    frame[RISK_COLUMN] = [risk_html(row) for _, row in rubric.iterrows()]
    return frame

def build(ds, out_dir):
    """Write tableS1_rubric.png/.pdf."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    frame = build_frame()

    gt = (
        GT(frame)
        .tab_header(title=TITLE, subtitle=SCALE_NOTE)
        .cols_align(align="left")
        .cols_width(COLUMN_WIDTHS)
        .fmt(lambda value: value, columns=RISK_COLUMN)       # the risk column holds HTML (bold labels)
    )
    gt = apply_paper_style(gt, body_size="8pt", label_size="8pt", padding="5px", source_size="8pt")
    gt = gt.tab_options(heading_subtitle_font_size="7pt")
    save_table(gt, out_dir, "tableS1_rubric", window_size=WINDOW_SIZE)