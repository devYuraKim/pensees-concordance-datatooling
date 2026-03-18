import re

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
    
    for entry in data:
        # Use the stored index to find the original CSV data
        row_idx = entry.get('original_row_index')
        if row_idx is None:
            # Skip entries that don't have an index (or handle them as errors)
            continue
        
        row_num = row_idx + 2  # Adjust for 0-index and header row
        raw_values = df.iloc[row_idx].fillna("").astype(str).values
        row_context = " | ".join(raw_values)
        line_label = f"Row {row_num}: `{row_context}`"

        s_num = entry['sellierNumber']
        refs = entry['references']
        
        # 1. Sellier Missing
        if s_num is None and row_idx not in seen_rows["null_sellier"]:
            report["null_sellier"].append(line_label)
            seen_rows["null_sellier"].add(row_idx)

        # 2. Incomplete Editions
        found_editions = {r['edition'] for r in refs}
        if len(found_editions) < 3 and row_idx not in seen_rows["missing_editions"]:
            report["missing_editions"].append(f"{line_label} (S:{s_num})")
            seen_rows["missing_editions"].add(row_idx)

        # 3. Ranges or Multi-refs
        if row_idx not in seen_rows["ranges_or_multi"]:
            original_row = df.iloc[row_idx]
            for col in ['S', 'B', 'L', 'LG']:
                val = str(original_row[col])
                if '-' in val or ',' in val:
                    report["ranges_or_multi"].append(f"{line_label} — [{col}: {val}]")
                    seen_rows["ranges_or_multi"].add(row_idx)
                    break
        
        for r in refs:
            raw = str(r['refRaw'])
            
            # 4. Suffixes
            if re.search(r'bis|ter', raw, re.I) and row_idx not in seen_rows["suffixes"]:
                report["suffixes"].append(f"{line_label} — [{r['edition']}: {raw}]")
                seen_rows["suffixes"].add(row_idx)
            
            # 5. Non-numeric
            if not any(char.isdigit() for char in raw) and raw not in ['-', ''] and row_idx not in seen_rows["non_numeric"]:
                report["non_numeric"].append(f"{line_label} — [{r['edition']}: {raw}]")
                seen_rows["non_numeric"].add(row_idx)

    # Construct Markdown Content
    md = [f"# Concordance Audit Report\nGenerated for: {report_path.stem}\n"]
    
    sections = [
        ("1.Sellier Missing", "null_sellier", "Rows where the primary anchor (Sellier) is null."),
        ("2.Incomplete Editions", "missing_editions", "Rows missing one or more of B, L, or LG."),
        ("3.Ranges or Multi-refs", "ranges_or_multi", "Entries containing '-' or ','."),
        ("4.Suffixes (bis/ter)", "suffixes", "Entries with specific edition modifiers."),
        ("5.Non-Numeric Refs", "non_numeric", "Entries like 'app. XIII' with no digits.")
    ]

    for title, key, desc in sections:
        md.append(f"## {title} ({len(report[key])})")
        md.append(f"*{desc}*")
        if report[key]:
            md.extend([f"- {item}" for item in report[key]])
        else:
            md.append("- No issues found.")
        md.append("")

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))