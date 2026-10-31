"""
Paths, instrument structure (criteria, dimensions), system list and display names, scoring matrices, colors, PRISMA counts.
"""

from pathlib import Path

# --------------------------------------------------------------------------------------
# 1. Paths
# --------------------------------------------------------------------------------------
PACKAGE_DIR = Path(__file__).resolve().parents[2]
INPUT_DIR = PACKAGE_DIR / "inputs"
DEFAULT_OUT_DIR = PACKAGE_DIR / "outputs"

# Scores: one sheet per scoring source (see MATRICES below), 25 systems x 24 criteria, values 1-3.
SCORING_WORKBOOK = INPUT_DIR / "scoring_workbook.xlsx"
# System characteristics (Table 1 content): manufacturer, regulatory identifiers, type, digital-ecosystem features, ...
CHARACTERISTICS_WORKBOOK = INPUT_DIR / "neuromodtable.xlsx"

# Text tables: themes (Table 4) and consent checklist (Table 5).
THEMES_TEXT_XLSX = INPUT_DIR / "themes_text.xlsx"
CHECKLIST_TEXT_XLSX = INPUT_DIR / "checklist_text.xlsx"
# Text of Table S1 (scoring rubric), one row per criterion.
RUBRIC_TEXT_XLSX = INPUT_DIR / "rubric_text.xlsx"

# --------------------------------------------------------------------------------------
# 2. Cohort size and scoring sources
# --------------------------------------------------------------------------------------
N_SYSTEMS = 25
N_ORIGINAL_SYSTEMS = 21   # systems from the original database pull (the other 4 were added manually)
N_CRITERIA = 24

# Scoring matrices: "company_policy" (manufacturer privacy policies) and "ifu" (instructions for use).
MATRICES = {
    "company_policy": {"sheet": "Scoring Matrix (Company Policy)", "label": "Company Policy", "suffix": "", "tag": "CP"},
    "ifu": {"sheet": "Scoring Matrix (IFU)", "label": "IFU", "suffix": "_IFU", "tag": "IFU"},
}

# --------------------------------------------------------------------------------------
# 3. Scoring instrument: criteria 1-24 grouped into seven governance dimensions
# --------------------------------------------------------------------------------------
DIMENSIONS = [
    ("Transparency", [1, 2, 3, 4]),
    ("Data Collection Purpose", [5, 6, 7, 8, 9]),
    ("Data Minimization", [10, 11, 12]),
    ("User Control and Rights", [13, 14, 15, 16]),
    ("Third-Party Data Sharing", [17]),
    ("Data Security", [18, 19, 20, 21, 22, 23]),
    ("Breach Notification", [24]),
]
DIM_NAMES = [name for name, _ in DIMENSIONS]
CRITERION_TO_DIM = {c: name for name, crits in DIMENSIONS for c in crits}

# Neuromodulation types in table order.
TYPE_ORDER = ["DBS", "SCS", "VNS", "RNS", "Peripheral"]
TYPE_LONG = {
    "DBS": "Deep brain stimulation (DBS)",
    "SCS": "Spinal cord stimulation (SCS)",
    "VNS": "Vagus nerve stimulation (VNS)",
    "RNS": "Responsive neurostimulation (RNS)",
    "Peripheral": "Peripheral stimulation",
}

# Disclosure-concern colors: 1 = low (green), 2 = some (amber), 3 = high (red). Used by Figure 2 and Table S2.
SCORE_COLORS = {1: "#1b9e77", 2: "#fdae61", 3: "#d7191c"}

# --------------------------------------------------------------------------------------
# 4. The 25 systems
# --------------------------------------------------------------------------------------
# The input files list the systems in the same order; the position `id` (1-25) is the join key.
# `scoring_key` and `table1_key` are lower-case name prefixes checked against the input rows at load time.
# `name` is the display name (company + product) used in figures and tables.
SYSTEMS = [
    dict(id=1, name="Boston Scientific (Axonics) Sacral Neuromodulation System", scoring_key="axonicssacral", table1_key="axonicssacral"),
    dict(id=2, name="Bioness (Bioventus) StimRouter Neuromodulation System", scoring_key="stimrouter", table1_key="stimrouter"),
    dict(id=3, name="Boston Scientific Vercise Deep Brain Stimulation System", scoring_key="vercise", table1_key="vercise"),
    dict(id=4, name="CVRx BAROSTIM NEO System", scoring_key="barostim", table1_key="barostim"),
    dict(id=5, name="LivaNova VNS Therapy for Epilepsy", scoring_key="vnstherapy", table1_key="vnstherapy"),
    dict(id=6, name="Inspire Medical Inspire V Upper Airway Stimulator", scoring_key="inspirev", table1_key="inspirev"),
    dict(id=7, name="Mainstay Medical ReActiv8 Neurostimulation System", scoring_key="reactiv8", table1_key="reactiv8"),
    dict(id=8, name="Enterra Medical Enterra Therapy", scoring_key="enterra", table1_key="enterra"),
    dict(id=9, name="Medtronic Intellis", scoring_key="intellis", table1_key="intellis"),
    dict(id=10, name="Medtronic InterStim", scoring_key="medtronicinterstim", table1_key="medtronicinterstim"),
    dict(id=11, name="Medtronic Percept PC/RC", scoring_key="medtronicpercept", table1_key="medtronicpercept"),
    dict(id=12, name="Mobia Medical Vivistim Paired VNS System", scoring_key="vivistim", table1_key="vivistim"),
    dict(id=13, name="Boston Scientific (Nalu) Neurostimulation System", scoring_key="nalu", table1_key="nalu"),
    dict(id=14, name="NeuroPace RNS System", scoring_key="neuropace", table1_key="neuropace"),
    dict(id=15, name="Neuros Medical Altius Nerve Stimulation System", scoring_key="altius", table1_key="altius"),
    dict(id=16, name="Globus Medical (Nevro) Senza SCS System", scoring_key="nevrosenza", table1_key="nevrosenza"),
    dict(id=17, name="Saluda Medical Evoke SCS System", scoring_key="saluda", table1_key="saluda"),
    dict(id=18, name="Abbott Infinity DBS System", scoring_key="abbottinfinity", table1_key="abbottinfinity"),
    dict(id=19, name="Synapse Biomedical NeuRx Diaphragm Pacing System", scoring_key="neurx", table1_key="neurx"),
    dict(id=20, name="Boston Scientific (Valencia) eCoin Peripheral Neurostimulator", scoring_key="ecoin", table1_key="ecoin"),
    dict(id=21, name="ZOLL remedē Phrenic Nerve Stimulator System", scoring_key="remed", table1_key="remed"),
    dict(id=22, name="SetPoint Medical SetPoint System", scoring_key="setpoint", table1_key="setpoint"),
    dict(id=23, name="Curonix Freedom SCS/PNS System", scoring_key="freedom", table1_key="freedom"),
    dict(id=24, name="Biotronik Prospera SCS System", scoring_key="prospera", table1_key="prospera"),
    dict(id=25, name="Medtronic (SPR) SPRINT PNS System", scoring_key="sprint", table1_key="sprint"),
]

# --------------------------------------------------------------------------------------
# 5. Figure 1 (PRISMA) counts
# --------------------------------------------------------------------------------------
# These are recorded counts from the original October 17, 2025 FDA database pull and its manual screening.
PRISMA_COUNTS = {
    "product_codes": 35,
    "records_screened": 416,
    "excluded_total": 331,
    "excluded_duplicate": 269,
    "excluded_pma_unverified": 45,
    "excluded_incorrect_device": 10,
    "excluded_incorrect_pma": 7,
    "systems_assessed": 85,
    "excluded_before_scoring": 64,       # leads and ancillary components
    "original_pull_systems": 21,
    "added_by_reference_matching": 4,    # SetPoint, Curonix Freedom, Biotronik Prospera, SPRINT
}