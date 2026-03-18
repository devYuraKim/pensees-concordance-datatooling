# Concordance Audit Report
Generated for: edge_cases_audit

## 1.Sellier Missing (1)
*Rows where the primary anchor (Sellier) is null.*
- Row 3: ` | 647 | 245 | 229`

## 2.Incomplete Editions (2)
*Rows missing one or more of B, L, or LG.*
- Row 2: `1 |   |   |  ` (S:1)
- Row 7: `310 | 446 bis | 278 | ` (S:310)

## 3.Ranges or Multi-refs (3)
*Entries containing '-' or ','.*
- Row 4: `241-242 | 599 | 309 | 195` — [S: 241-242]
- Row 6: `324 | 624, 204 bis | 292-293 | 275` — [B: 624, 204 bis]
- Row 9: `433 | 835, 192 | 852-853 | 691` — [B: 835, 192]

## 4.Suffixes (bis/ter) (3)
*Entries with specific edition modifiers.*
- Row 5: `228 | 163 bis | 197 | 183` — [BRU: 163 bis]
- Row 6: `324 | 624, 204 bis | 292-293 | 275` — [BRU: 204 bis]
- Row 7: `310 | 446 bis | 278 | ` — [BRU: 446 bis]

## 5.Non-Numeric Refs (1)
*Entries like 'app. XIII' with no digits.*
- Row 8: `419 | app. XIII | 830 | 678` — [BRU: app. XIII]
