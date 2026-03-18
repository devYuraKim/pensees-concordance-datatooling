# `normal_data` Audit Report

> **Note on Irregularities**: This report flags "points of interest" rather than confirmed errors. While some may be data entry mistakes, others (like ranges or suffixes) are inherent to the concordance scholarship. Please manually verify these rows to ensure the mapping aligns with the source editions.

## Summary

| Pipeline Stage           | Count | Status |
| :----------------------- | :---- | :----- |
| Processed (JSON Records) | 9     | ✅     |
| To Review (CSV Rows)     | 0     | ✅     |

&nbsp;

### To Review (CSV Rows) Breakdown

| Irregularity Type         | Count | Status | Row No.  |
| :------------------------ | :---- | :----- | :------- |
| Missing Sellier (Orphans) | 0     | ✅     | -        |
| Incomplete Editions       | 0     | ✅     | -        |
| Expanded Ranges           | 0     | ✅     | -        |
| Suffixes                  | 0     | ✅     | -        |
| Non-Numeric References    | 0     | ✅     | -        |
| **TOTAL(unique rows)**    | **0** |        | \*\*\*\* |

&nbsp;

## Details (by CSV Row)

The following sections provide the specific context for each flagged row.

## 1.Sellier Missing (0 rows)

_Rows where the primary anchor (Sellier) is null._

- No issues found.

## 2.Incomplete Editions (0 rows)

_Rows missing one or more of B, L, or LG._

- No issues found.

## 3.Ranges or Multi-refs (0 rows)

_Entries containing '-' or ','._

- No issues found.

## 4.Suffixes (0 rows)

_Entries with specific edition modifiers('bis', 'ter', or 'note')._

- No issues found.

## 5.Non-Numeric Refs (0 rows)

_Entries like 'app. XIII' with no digits._

- No issues found.
