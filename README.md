# Data Processing Tools

This repository contains tools to transform raw **concordance tables (CSV)** into a **normalized JSON dataset** suitable for relational database ingestion.

## Getting Started

To verify the parser, you can run the transformation on both the standard dataset and the edge-case dataset.

### 1. Process Normal Data

This dataset contains clean, one-to-one mappings between editions.

```bash
python3 scripts/csv_to_json.py data/raw/normal_data.csv
```

### 2. Process Edge Cases

This dataset stress-tests the parser against irregularities like ranges, suffixes, and non-numeric references.

```bash
python3 scripts/csv_to_json.py data/raw/edge_cases.csv
```

## Validation & Audit Reports

The tool generates two files in `data/processed/` for every CSV processed:

- **JSON Dataset**: The cleaned data ready for database ingestion (with internal metadata stripped).
- **Markdown Audit**: A human-readable report highlighting anomalies found in the source CSV.

### Comparing Results

We provide "expected" reference files so you can verify your output:

| Input File        | Expected JSON               | Expected Audit Report           |
| :---------------- | :-------------------------- | :------------------------------ |
| `normal_data.csv` | `normal_data.expected.json` | `normal_data_audit.expected.md` |
| `edge_cases.csv`  | `edge_cases.expected.json`  | `edge_cases_audit.expected.md`  |

### Audit Categories

The audit report automatically categorizes and displays the original CSV row for the following cases:

- **Sellier Missing**: Fragments that exist in other editions but are omitted by Sellier.
- **Incomplete Editions**: Rows missing one or more of the B, L, or LG references.
- **Ranges/Multi-refs**: Expansion of entries like `292-293` or `835, 192`.
- **Suffixes**: Detection of modifiers like `bis` or `ter`.
- **Non-Numeric**: Handling of references like `app. XIII`.
