# Neuromodulation Data-Governance Analysis Code

Code that reads the data workbooks and produces the figures, tables, and summary statistics. Each system was scored 1 (low concern), 2 (some concern) or 3 (high concern) on 24 disclosure criteria, which are grouped into seven governance dimensions.

## Contents
```
run_all.py                   Runs every step (or those given with --only) and writes outputs/
config.py                    paths, criteria and dimensions, system names, colors, PRISMA counts
data_io.py                   reads and validates the input workbooks into a Dataset object
analysis.py                  statistics functions
results_summary.py           Quick results summary written to results_summary.txt
figures/                     fig1_prisma.py, fig2_heatmap.py, fig3_criteria_bars.py
tables/                      table1 ... table5, tableS1, tableS2 modules; style.py (shared table style, PNG/PDF saving)
inputs/                      input files (see Inputs below)
outputs/                     files produced by `python run_all.py --with-ifu`
```

## Requirements

Python 3.9 or newer; the packages `pandas`, `numpy`, `matplotlib`, `openpyxl`, `Pillow`, `great_tables` and `selenium`;
and Google Chrome, which `great_tables` uses to render tables to PNG and PDF. Tables are set in Times New Roman.

## Usage

Run from inside this folder:

```bash
python run_all.py                       # every step, Company Policy scoring matrix
python run_all.py --with-ifu            # also the matrix-dependent outputs for the IFU matrix, in <out>/IFU/
python run_all.py --only fig2,table2    # selected steps only
python run_all.py --out some/folder     # write somewhere else (default: outputs/)
```

Step names: `fig1`, `fig2`, `fig3`, `table1`, `table2`, `table3`, `table4`, `table5`, `tableS1`, `tableS2`, `summary`.

## Outputs

| Item | Step | Module | Files |
|---|---|---|---|
| Figure 1: PRISMA flow diagram | `fig1` | `figures/fig1_prisma.py` | `figure1_PRISMA.png/.pdf` |
| Figure 2: concern heatmap with total-score column | `fig2` | `figures/fig2_heatmap.py` | `figure2_disclosure_concern_heatmap_by_manufacturer.*` |
| Figure 3: highest-concern criteria (panels A and B) | `fig3` | `figures/fig3_criteria_bars.py` | `figure3_highest_concern_criteria.*` |
| Table 1: system characteristics | `table1` | `tables/table1_characteristics.py` | `table1_device_characteristics.*` |
| Table 2: domain scores overall and by type | `table2` | `tables/table2_domain_scores.py` | `table2_domain_concern_scores.*` |
| Table 3: top-6 criteria by type | `table3` | `tables/table3_top_criteria.py` | `table3_top_criteria_by_type.*` |
| Table 4: qualitative themes | `table4` | `tables/table4_themes.py` | `table4_disclosure_themes.*` |
| Table 5: consent checklist (two versions) | `table5` | `tables/table5_consent_checklist.py` | `table5_consent_checklist_with/without_new_question.*` |
| Supplementary Table S1: scoring rubric | `tableS1` | `tables/tableS1_rubric.py` | `tableS1_rubric.*` |
| Supplementary Table S2: full score matrix | `tableS2` | `tables/tableS2_scores.py` | `tableS2_heatmap_scores_criteria_rows_compact_horizontal.*` |
| Quoted numbers | `summary` | `results_summary.py` | `results_summary.txt` |

`.png` and `.pdf` versions are written for every figure and table. Each figure and table module also writes the data it
displays to `source_data/` as CSV (or Excel for Table 5). With `--with-ifu`, Figures 2 and 3, Tables 2, 3 and S2 and the
summary are produced for the IFU matrix as well, with the suffix `_IFU` in the file names.

## Definitions

* **Score**: 1 = low concern (clear, specific disclosure), 2 = some concern (partial or ambiguous), 3 = high concern
  (absent or insufficient).
* **Dimension score**: the mean of a system's scores over the criteria in a governance dimension. The dimensions are
  Transparency (criteria 1-4), Data Collection Purpose (5-9), Data Minimization (10-12), User Control and Rights (13-16),
  Third-Party Data Sharing (17), Data Security (18-23) and Breach Notification (24).
* **Total score**: a system's sum over the 24 criteria (range 24-72). A criterion's total score is its sum over the 25
  systems (maximum 75).
* **Neuromodulation type**: DBS, SCS, VNS, RNS or Peripheral. A system typed "SCS, Peripheral" is counted in both groups in
  the type-level statistics and is listed under its first type in Table 1.
* **Highest-concern criteria**: ranked by criterion total score, then by number of systems scoring 3. Criteria tied with
  the last one shown are all kept, so Figure 3 can show more than ten bars.
* **Scoring matrices**: the workbook holds two matrices. *Company Policy* scores the manufacturers' privacy policies and is
  the matrix used for all figures and tables in the paper. *IFU* scores each device's instructions for use and is
  available as an option.

## Inputs

All inputs are in `inputs/`. Paths are set in `config.py`.

| File | Content |
|---|---|
| `scoring_workbook.xlsx` | sheets "Scoring Matrix (Company Policy)" and "Scoring Matrix (IFU)" (25 systems x 24 criteria, scores 1-3, scorer notes, system key) (the workbook also holds system-selection sheets, "Included Devices", "Neuromod Devices" and "Filtered (417)", which the code does not read) |
| `neuromodtable.xlsx` | system characteristics: manufacturer, regulatory identifiers, indication, type, digital-ecosystem features |
| `themes_text.xlsx` | text of Table 4 (themes) |
| `checklist_text.xlsx` | text of Table 5 (consent checklist) |
| `rubric_text.xlsx` | text of Table S1 (scoring rubric: one row per criterion with definition, indicators and the High Risk, Low Risk and Some Concerns descriptions) |

## Notes on the data

* **Figure 1** uses recorded counts from the October 17, 2025 FDA database pull and manual screening (35 product codes,
  416 records screened, 331 excluded, 85 systems assessed, 64 excluded before scoring, 21 + 4 = 25). They are stored in
  `config.PRISMA_COUNTS`.
* **Tables 4 and 5** contain authored tables that are then formatted by the code.
* **Table S1** contains authored text (the rubric); the code again formats it. The three risk-level descriptions of each criterion are combined in one column.
* **System names** in figures and tables combine manufacturer and product name and are defined in `config.SYSTEMS`.