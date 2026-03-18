# `normal_data` Audit Report

> **Note**: The audit report tracks **irregularities**, not necessarily errors. These are "points of interest" that may be perfectly valid for the dataset but should be manually verified to ensure no data was missed during entry.

## Summary

| Pipeline Stage | Count | Status |
| :--- | :--- | :--- |
| Processed (JSON Records) | 9 | ✅ |
| To Review (CSV Rows)| 0 | ✅ |
&nbsp;
### To Review (CSV Rows) Breakdown

| Irregularity Type | Count | Status | Row No. |
| :--- | :--- | :--- | :--- |
| Missing Sellier (Orphans) | 0 | ✅ | - |
| Incomplete Editions | 0 | ✅ | - |
| Expanded Ranges | 0 | ✅ | - |
| Suffixes | 0 | ✅ | - |
| Non-Numeric References | 0 | ✅ | - |
| **TOTAL(unique rows)** | **0** | | **** |
&nbsp;

## Details (by CSV Row)
The following sections provide the specific context for each flagged row.

## 1.Sellier Missing (0 rows)
*Rows where the primary anchor (Sellier) is null.*
- No issues found.

## 2.Incomplete Editions (0 rows)
*Rows missing one or more of B, L, or LG.*
- No issues found.

## 3.Ranges or Multi-refs (0 rows)
*Entries containing '-' or ','.*
- No issues found.

## 4.Suffixes (0 rows)
*Entries with specific edition modifiers('bis', 'ter', or 'note').*
- No issues found.

## 5.Non-Numeric Refs (0 rows)
*Entries like 'app. XIII' with no digits.*
- No issues found.
