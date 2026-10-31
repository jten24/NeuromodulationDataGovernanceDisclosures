"""
Table 1: system characteristics from the characteristics workbook, grouped by neuromodulation type.
"""

from pathlib import Path
from great_tables import GT, loc, style
import config as cfg
from tables.style import apply_paper_style, save_table

# Columns shown, in order.
COLUMNS = [
    "Device", "Manufacturer", "PMA #", "Product Code", "Indication", "Implant Location", "Neuromodulation Type",
    "Sensing Capability (Y/N)", "Remote Monitoring Capability (Y/N)", "Remote Monitoring or Programming (Y/N)",
    "Patient App (Y/N)", "App on Patient's Own Phone (Y/N)", "App on Company-Provided Device (Y/N)",
    "Clinician Portal (Y/N)", "Cloud Upload (Y/N)", "Data Export Features (Y/N)",
    "Patient App Name", "Clinician Portal Name", "Programmer Type (Dedicated vs Tablet)",
]
YES_NO_COLUMNS = [c for c in COLUMNS if c.endswith("(Y/N)")]

# Column widths in pixels. The first column is shown as "System" (renamed after the data are assembled).
WIDTHS = {
    "System": 210, "Manufacturer": 135, "PMA #": 85, "Product Code": 80, "Indication": 150,
    "Implant Location": 120, "Neuromodulation Type": 128, "Patient App Name": 150,
    "Clinician Portal Name": 150, "Programmer Type (Dedicated vs Tablet)": 115,
    **{c: 88 for c in YES_NO_COLUMNS},
    "Remote Monitoring or Programming (Y/N)": 118,
}
GROUP_COLUMN = "__group"

FOOTNOTE = (
    "*ND (not disclosed) indicates that the feature was not explicitly described in the publicly accessible documentation "
    "reviewed and should not be interpreted as evidence that the feature is absent. N/A indicates not applicable because the "
    "system has no corresponding app or portal. No indicates that the system does not have the feature (for example, no app or "
    "internet connection). Systems are grouped by neuromodulation type; systems with two types (SCS, Peripheral) are listed under "
    "their first type and are counted in both types in Tables 2 and 3. "
    "Abbreviations: DBS, deep brain stimulation; HDE, humanitarian device exemption; PMA, premarket approval; PNS, peripheral nerve stimulation; "
    "RNS, responsive neurostimulation; SCS, spinal cord stimulation; SNM, sacral neuromodulation; VNS, vagus nerve stimulation."
)

def build_table(ds):
    """DataFrame in display order (grouped by type), with the display name in column 'System' and a '__group' key."""
    table = ds.characteristics.copy()
    table["Device"] = ds.systems["display_name"].values          # company + product instead of the workbook's name
    table = table[COLUMNS].copy()
    table[GROUP_COLUMN] = ds.systems["primary_type"].values
    table = table.fillna("")

    type_rank = {t: i for i, t in enumerate(cfg.TYPE_ORDER)}
    table["__rank"] = table[GROUP_COLUMN].map(type_rank)
    table["__source_order"] = range(len(table))
    table = table.sort_values(["__rank", "__source_order"]).drop(columns=["__rank", "__source_order"]).reset_index(drop=True)
    return table.rename(columns={"Device": "System"})

def build(ds, out_dir):
    """Write table1_device_characteristics.png/.pdf and source_data/table1_data.csv."""
    out_dir = Path(out_dir)
    (out_dir / "source_data").mkdir(parents=True, exist_ok=True)
    table = build_table(ds)
    table.drop(columns=[GROUP_COLUMN]).to_csv(out_dir / "source_data" / "table1_data.csv", index=False)

    # Group headings read e.g. 'Deep brain stimulation (DBS) - 3 systems'.
    counts = table[GROUP_COLUMN].value_counts()

    def heading(t):
        """Group heading text for neuromodulation type `t`."""
        return f"{cfg.TYPE_LONG[t]} - {counts[t]} system{'s' if counts[t] != 1 else ''}"

    table["__label"] = table[GROUP_COLUMN].map(heading)
    table = table.drop(columns=[GROUP_COLUMN]).rename(columns={"__label": GROUP_COLUMN})
    group_order = [heading(t) for t in cfg.TYPE_ORDER if t in counts]

    gt = (
        GT(table, groupname_col=GROUP_COLUMN)
        .tab_header(title="Table 1. Characteristics of Included Implantable Neuromodulation Systems and "
                          "Publicly Disclosed Digital Ecosystem Features.")
        .tab_source_note(source_note=FOOTNOTE)
        .cols_align(align="left")
        .cols_width({c: f"{WIDTHS[c]}px" for c in table.columns if c != GROUP_COLUMN})
        .row_group_order(groups=group_order)
    )
    gt = apply_paper_style(gt, body_size="11pt", label_size="11pt", padding="5px", source_size="10pt")
    gt = gt.tab_style(
        style=[style.text(weight="bold", color="#222222", size="11pt"), style.fill(color="#ececec")],
        locations=loc.row_groups(),
    )
    save_table(gt, out_dir, "table1_device_characteristics", window_size=(2500, 1200))