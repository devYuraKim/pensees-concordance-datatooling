import re

def generate_summary_table(stats, report):
    """Creates two separate summary tables: High-level Scope and Category Breakdown."""
    
    # Store all found row numbers to calculate the final unique list
    all_row_nums = set()
    
    def get_row_nums(key):
        nums = []
        for item in report[key]:
            match = re.search(r'Row (\d+)', item)
            if match:
                val = match.group(1)
                nums.append(val)
                all_row_nums.add(int(val)) # Add to master set as int for sorting
        
        unique_nums = sorted(list(set(nums)), key=int)
        return ", ".join(unique_nums) if unique_nums else "-"
    
    # Table 1: High-level Scope
    table = [
        "## Summary",
        "",
        "| Pipeline Stage | Count | Status |",
        "| :--- | :--- | :--- |",
        f"| Processed (JSON Records) | {stats['total_records']} | ✅ |",
        f"| To Review (CSV Rows)| {stats['flagged_records']} | {'⚠️' if stats['flagged_records'] > 0 else '✅'} |",
        "&nbsp;",
        "### To Review (CSV Rows) Breakdown",
        "",
        "| Irregularity Type | Count | Status | Row No. |",
        "| :--- | :--- | :--- | :--- |"
    ]
    
# Table 2: Category Breakdown
    metrics = [
        ("Missing Sellier (Orphans)", stats['missing_sellier'], get_row_nums("null_sellier")),
        ("Incomplete Editions", stats['incomplete_editions'], get_row_nums("missing_editions")),
        ("Expanded Ranges", stats['ranges_found'], get_row_nums("ranges_or_multi")),
        ("Suffixes", stats['suffixes_found'], get_row_nums("suffixes")),
        ("Non-Numeric References", stats['non_numeric'], get_row_nums("non_numeric")),
    ]

    for label, count, rows in metrics:
        icon = "⚠️" if count > 0 else "✅"
        table.append(f"| {label} | {count} | {icon} | {rows} |")
        
    # Final "Footer" Row (Total Issues Found)
    sorted_total_rows = ", ".join(map(str, sorted(list(all_row_nums))))
    table.append(f"| **TOTAL(unique rows)** | **{stats['flagged_records']}** | | **{sorted_total_rows}** |")
    
    return "\n".join(table)

def run_data_audit(data, df, report_path):
    """
    Categorizes irregularities and saves a detailed Markdown report.
    """
    report = {
        "null_sellier": [],
        "missing_editions": [],
        "ranges_or_multi": [],
        "suffixes": [],
        "non_numeric": []
    }
    
    # Track which CSV rows already flagged for each category
    # to avoid duplicates caused by flattened ranges
    seen_rows = {key: set() for key in report.keys()}
    all_flagged_rows = set()
    
    for entry in data:
        # Use the stored index to find the original CSV data
        row_idx = entry.get('original_row_index')
        if row_idx is None:
            # Skip entries that don't have an index (or handle them as errors)
            continue
        
        row_num = row_idx + 2  # Adjust for 0-index and header row
        vals = [str(v).strip() if str(v).strip() != "" else "empty" for v in df.iloc[row_idx].fillna("empty")]
        row_context = " | ".join(vals)
        line_label = f"**Row {row_num}**: [ {row_context} ]  "

        edition_map = {"BRU": "B", "LAF": "L", "LEG": "LG", "SEL": "S"}
        s_num = entry['sellierNumber']
        refs = entry['references']
        
        # 1. Sellier Missing
        if s_num is None and row_idx not in seen_rows["null_sellier"]:
            report["null_sellier"].append(line_label)
            seen_rows["null_sellier"].add(row_idx)
            all_flagged_rows.add(row_idx)

        # 2. Incomplete Editions
        required_cols = {"B", "L", "LG"}
        original_row = df.iloc[row_idx]
        
        missing_ones = [
            col for col in required_cols 
            if str(original_row.get(col, "")).strip() in ["", "nan", "-"]
        ]
        
        if missing_ones and row_idx not in seen_rows["missing_editions"]:
            missing_str = ", ".join(sorted(missing_ones))
            report["missing_editions"].append(f"{line_label} — `{missing_str}`")
            seen_rows["missing_editions"].add(row_idx)
            all_flagged_rows.add(row_idx)

        # 3. Ranges or Multi-refs
        if row_idx not in seen_rows["ranges_or_multi"]:
            for col in ['S', 'B', 'L', 'LG']:
                val = str(original_row.get(col, ""))
                if '-' in val or ',' in val:
                    report["ranges_or_multi"].append(f"{line_label} — `{col}: {val}`")
                    seen_rows["ranges_or_multi"].add(row_idx)
                    all_flagged_rows.add(row_idx)
                    break
        
        for r in refs:
            raw = str(r['refRaw'])
            ed_short = edition_map.get(r['edition'], r['edition'])
            
            # 4. Suffixes
            if re.search(r'bis|ter|note', raw, re.I) and row_idx not in seen_rows["suffixes"]:
                report["suffixes"].append(f"{line_label} — `{ed_short}: {raw}`")
                seen_rows["suffixes"].add(row_idx)
                all_flagged_rows.add(row_idx)
            
            # 5. Non-numeric
            if not any(char.isdigit() for char in raw) and raw not in ['-', ''] and row_idx not in seen_rows["non_numeric"]:
                report["non_numeric"].append(f"{line_label} — `{ed_short}: {raw}`")
                seen_rows["non_numeric"].add(row_idx)
                all_flagged_rows.add(row_idx)

    stats = {
            'total_records': len(data),
            'flagged_records': len(all_flagged_rows),
            'missing_sellier': len(report["null_sellier"]),
            'incomplete_editions': len(report["missing_editions"]),
            'ranges_found': len(report["ranges_or_multi"]),
            'suffixes_found': len(report["suffixes"]),
            'non_numeric': len(report["non_numeric"])
        }
    
    display_name = report_path.stem.replace('_audit', '').replace('-audit', '')
    # Construct Markdown Content
    md = [
        f"# `{display_name}` Audit Report",
        "",
        "> **Note**: The audit report tracks **irregularities**, not necessarily errors. These are \"points of interest\" that may be perfectly valid for the dataset but should be manually verified to ensure no data was missed during entry.",
        "",

        generate_summary_table(stats, report),
        "&nbsp;",
        "",
        "## Details (by CSV Row)",
        "The following sections provide the specific context for each flagged row.",
        ""
    ]
    
    sections = [
        ("1.Sellier Missing", "null_sellier", "Rows where the primary anchor (Sellier) is null."),
        ("2.Incomplete Editions", "missing_editions", "Rows missing one or more of B, L, or LG."),
        ("3.Ranges or Multi-refs", "ranges_or_multi", "Entries containing '-' or ','."),
        ("4.Suffixes", "suffixes", "Entries with specific edition modifiers('bis', 'ter', or 'note')."),
        ("5.Non-Numeric Refs", "non_numeric", "Entries like 'app. XIII' with no digits.")
    ]

    for title, key, desc in sections:
        md.append(f"## {title} ({len(report[key])} rows)")
        md.append(f"*{desc}*")
        if report[key]:
            for item in report[key]:
                md.append(f"- {item}")
        else:
            md.append("- No issues found.")
        md.append("")

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))