"""
Reads and validates the input workbooks into a Dataset (score matrices, system characteristics, system table).
"""

import re
import openpyxl
import pandas as pd
import config as cfg

# --------------------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------------------
def normalize_name(text):
    """Lower-case and strip everything except letters and digits ('Axonics Sacral' -> 'axonicssacral')."""
    return re.sub(r"[^a-z0-9]", "", str(text).lower())

def parent_company(manufacturer):
    """Parent company used to group systems in Figure 2 and Table S2.
    'Boston Scientific (Axonics)'      -> 'Boston Scientific'
    'SPR Therapeutics (now Medtronic)' -> 'Medtronic'
    """
    m = re.match(r"^(.*?)\s*\((.*)\)\s*$", str(manufacturer).strip())
    if not m:
        return str(manufacturer).strip()
    head, inner = m.group(1).strip(), m.group(2).strip()
    if inner.lower().startswith("now "):
        return inner[4:].strip()
    return head

def split_types(type_string):
    """'SCS, Peripheral' -> ['SCS', 'Peripheral']."""
    return [t.strip() for t in str(type_string).split(",") if t.strip()]

def sheet_rows(path, sheet):
    """All rows of one worksheet as lists of cell values (formulas replaced by their cached values)."""
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    try:
        return [list(r) for r in wb[sheet].iter_rows(values_only=True)]
    finally:
        wb.close()

# --------------------------------------------------------------------------------------
# Scores
# --------------------------------------------------------------------------------------
def read_scoring_sheet(path, sheet, n_systems=cfg.N_SYSTEMS):
    """Read one scoring matrix.

    Layout: row 1 = header with system numbers 1..n; rows 2-25 = criteria 1-24 with the
    criterion text in column A and a 1/2/3 score per system; row 26 = scorer notes; further down a 'Key' block
    listing system name, number and privacy-policy URL.

    Returns a dict with
      criteria : the 24 full criterion labels ('1. User Notification ...: Whether users ...')
      scores   : DataFrame, index = criterion number 1..24, columns = system id 1..n
      notes    : {system id: scorer note}
      key      : DataFrame(id, name_in_scoring_file, privacy_url)
    """
    rows = sheet_rows(path, sheet)
    header_ids = [rows[0][c] for c in range(1, n_systems + 1)]
    if header_ids != list(range(1, n_systems + 1)):
        raise ValueError(f"{sheet}: unexpected system header {header_ids}")

    criteria, data = [], []
    for r in range(1, cfg.N_CRITERIA + 1):
        label = rows[r][0]
        if not str(label).startswith(f"{r}."):
            raise ValueError(f"{sheet}: row {r + 1} label {label!r} is not criterion {r}")
        values = rows[r][1: n_systems + 1]
        if any(v not in (1, 2, 3) for v in values):
            raise ValueError(f"{sheet}: criterion {r} has values outside 1/2/3: {values}")
        criteria.append(str(label).strip())
        data.append([int(v) for v in values])
    scores = pd.DataFrame(data, index=range(1, cfg.N_CRITERIA + 1), columns=range(1, n_systems + 1))

    notes_row = rows[cfg.N_CRITERIA + 1]
    if not str(notes_row[0]).lower().startswith("notes"):
        raise ValueError(f"{sheet}: expected a notes row after criterion 24, got {notes_row[0]!r}")
    notes = {i: notes_row[i] for i in range(1, n_systems + 1) if notes_row[i] is not None}

    key_rows, in_key_block = [], False
    for row in rows:
        if row[0] == "Key":
            in_key_block = True
            continue
        if in_key_block and isinstance(row[1], int):
            key_rows.append((row[1], str(row[0]).strip(), row[2]))
    key = pd.DataFrame(key_rows, columns=["id", "name_in_scoring_file", "privacy_url"]).sort_values("id")
    return dict(criteria=criteria, scores=scores, notes=notes, key=key.reset_index(drop=True))

def read_characteristics(path=cfg.CHARACTERISTICS_WORKBOOK):
    """Read the system-characteristics table (Table 1 content), one row per system."""
    df = pd.read_excel(path, sheet_name="Table1", keep_default_na=False, na_values=[""])
    if len(df) != cfg.N_SYSTEMS:
        raise ValueError(f"Table1 has {len(df)} rows, expected {cfg.N_SYSTEMS}")
    if not (df["Neuromodulation Mode"].astype(str) == df["Neuromodulation Type"].astype(str)).all():
        raise ValueError("Table1: 'Neuromodulation Mode' and 'Neuromodulation Type' differ")
    return df

# --------------------------------------------------------------------------------------
# Dataset
# --------------------------------------------------------------------------------------
class Dataset:
    """Validated, aligned inputs for every figure and table."""

    def __init__(self):
        self.characteristics = read_characteristics()
        self.matrices = {key: read_scoring_sheet(cfg.SCORING_WORKBOOK, meta["sheet"]) for key, meta in cfg.MATRICES.items()}

        # Both scoring sheets must describe the same instrument.
        self.criteria = self.matrices["company_policy"]["criteria"]
        if self.matrices["ifu"]["criteria"] != self.criteria:
            raise ValueError("Company Policy and IFU sheets use different criterion labels")
        # 'Transparency Reporting: Availability of ...' -> 'Transparency Reporting'
        self.criteria_short = [re.sub(r"^\d+\.\s*", "", c.split(":", 1)[0]).strip() for c in self.criteria]
        self.systems = self._build_systems()

    def scores(self, matrix_key):
        """24 x 25 score DataFrame for 'company_policy' or 'ifu'."""
        return self.matrices[matrix_key]["scores"]

    def _build_systems(self):
        """One row per system: display name, source names, manufacturer, parent company, types."""
        key_cp, key_ifu = self.matrices["company_policy"]["key"], self.matrices["ifu"]["key"]
        if not key_cp.equals(key_ifu):
            raise ValueError("System key differs between Company Policy and IFU sheets")

        records = []
        for spec in cfg.SYSTEMS:
            i = spec["id"]
            name_in_scoring = key_cp.loc[key_cp["id"] == i, "name_in_scoring_file"].iloc[0]
            row = self.characteristics.iloc[i - 1]
            # Name prefixes in all three inputs must match config.SYSTEMS.
            if not normalize_name(name_in_scoring).startswith(spec["scoring_key"]):
                raise ValueError(f"System {i}: scoring-file name {name_in_scoring!r} != expected {spec['scoring_key']!r}")
            if not normalize_name(row["Device"]).startswith(spec["table1_key"]):
                raise ValueError(f"System {i}: Table 1 name {row['Device']!r} != expected {spec['table1_key']!r}")
            types = split_types(row["Neuromodulation Type"])
            records.append(dict(
                id=i,
                display_name=spec["name"],
                name_in_scoring_file=name_in_scoring,
                name_in_table1_file=row["Device"],
                manufacturer=row["Manufacturer"],
                parent=parent_company(row["Manufacturer"]),
                types=types,
                primary_type=types[0],          # first-listed type; used to place the system in Table 1
                type_string=row["Neuromodulation Type"],
                privacy_url=key_cp.loc[key_cp["id"] == i, "privacy_url"].iloc[0],
            ))
        systems = pd.DataFrame(records).set_index("id", drop=False)
        systems["parent_group_size"] = systems["parent"].map(systems["parent"].value_counts())
        return systems

    # ---- display order for Figure 2 and Table S2 ---------------------------------------
    def company_grouped_order(self):
        """System ids with same-company systems adjacent."""
        s = self.systems
        group_parents = []
        for i in s.index:
            if s.at[i, "parent_group_size"] > 1 and s.at[i, "parent"] not in group_parents:
                group_parents.append(s.at[i, "parent"])
        grouped = [i for p in group_parents for i in s.index if s.at[i, "parent"] == p]
        singles = [i for i in s.index if s.at[i, "parent_group_size"] == 1]
        return grouped + singles

    def company_group_sizes(self):
        """Sizes of the consecutive multi-system company blocks in company_grouped_order()."""
        sizes, parents = [], []
        for i in self.company_grouped_order():
            if self.systems.at[i, "parent_group_size"] > 1:
                parent = self.systems.at[i, "parent"]
                if parents and parents[-1] == parent:
                    sizes[-1] += 1
                else:
                    parents.append(parent)
                    sizes.append(1)
        return parents, sizes

    def type_membership(self):
        """{type: [system ids]}. A system typed 'SCS, Peripheral' is a member of BOTH groups."""
        members = {t: [] for t in cfg.TYPE_ORDER}
        for i in self.systems.index:
            for t in self.systems.at[i, "types"]:
                if t not in members:
                    raise ValueError(f"Unknown neuromodulation type {t!r}")
                members[t].append(i)
        return members

def short_label(display_name):
    """Display name without the trailing ' System' (used where space is tight: Figure 2, Table S2)."""
    return display_name[:-7] if display_name.endswith(" System") else display_name