# `edge_cases` Audit Report

> **Note**: The audit report tracks **irregularities**, not necessarily errors. These are "points of interest" that may be perfectly valid for the dataset but should be manually verified to ensure no data was missed during entry.

## Summary

| Pipeline Stage           | Count | Status |
| :----------------------- | :---- | :----- |
| Processed (JSON Records) | 9     | ✅     |
| To Review (CSV Rows)     | 8     | ⚠️     |

&nbsp;

### To Review (CSV Rows) Breakdown

| Irregularity Type         | Count | Status | Row No.                    |
| :------------------------ | :---- | :----- | :------------------------- |
| Missing Sellier (Orphans) | 1     | ⚠️     | 3                          |
| Incomplete Editions       | 2     | ⚠️     | 2, 7                       |
| Expanded Ranges           | 3     | ⚠️     | 4, 6, 9                    |
| Suffixes                  | 3     | ⚠️     | 5, 6, 7                    |
| Non-Numeric References    | 1     | ⚠️     | 8                          |
| **TOTAL(unique rows)**    | **8** |        | **2, 3, 4, 5, 6, 7, 8, 9** |

&nbsp;

## Details (by CSV Row)

The following sections provide the specific context for each flagged row.

## 1.Sellier Missing (1 rows)

_Rows where the primary anchor (Sellier) is null._

- **Row 3**: [ empty | 647 | 245 | 229 ]

## 2.Incomplete Editions (2 rows)

_Rows missing one or more of B, L, or LG._

- **Row 2**: [ 1 | empty | empty | empty ] — `B, L, LG`
- **Row 7**: [ 310 | 446 bis | 278 | empty ] — `LG`

## 3.Ranges or Multi-refs (3 rows)

_Entries containing '-' or ','._

- **Row 4**: [ 241-242 | 599 | 309 | 195 ] — `S: 241-242`
- **Row 6**: [ 324 | 624, 204 bis | 292-293 | 275 ] — `B: 624, 204 bis`
- **Row 9**: [ 433 | 835, 192 | 852-853 | 691 ] — `B: 835, 192`

## 4.Suffixes (3 rows)

_Entries with specific edition modifiers('bis', 'ter', or 'note')._

- **Row 5**: [ 228 | 163 bis | 197 | 183 ] — `B: 163 bis`
- **Row 6**: [ 324 | 624, 204 bis | 292-293 | 275 ] — `B: 204 bis`
- **Row 7**: [ 310 | 446 bis | 278 | empty ] — `B: 446 bis`

## 5.Non-Numeric Refs (1 rows)

_Entries like 'app. XIII' with no digits._

- **Row 8**: [ 419 | app. XIII | 830 | 678 ] — `B: app. XIII`
