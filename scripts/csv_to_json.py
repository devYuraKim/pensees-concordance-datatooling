import pandas as pd
import json
import re
import sys
from pathlib import Path

def parse_complex_ref(val):
    """
    Parses strings like '624, 204 bis' or '852-853' 
    into a list of structured objects.
    """
    if pd.isna(val):
        return []
    
    cleaned = str(val).strip().replace(".0", "")

    if cleaned in ['-', '']:
        return []

    results = []
    # Split multiple refs: "835, 192" -> ["835", "192"]
    parts = [p.strip() for p in cleaned.split(',')]
    
    for part in parts:
        # 1. Handle Ranges: "241-242" -> [241, 242]
        range_match = re.match(r'^(\d+)-(\d+)$', part)
        if range_match:
            start, end = map(int, range_match.groups())
            for num in range(start, end + 1):
                results.append({"refNumber": num, "refSuffix": None, "refRaw": str(num)})
            continue

        # 2. Handle Suffixes: "163 bis" -> {number: 163, suffix: "bis"}
        suffix_match = re.match(r'^(\d+)\s+(bis|ter)$', part, re.IGNORECASE)
        if suffix_match:
            num, suffix = suffix_match.groups()
            results.append({"refNumber": int(num), "refSuffix": suffix, "refRaw": part})
            continue

        # 3. Handle Pure Numbers: "599" -> {number: 599}
        if part.isdigit():
            results.append({"refNumber": int(part), "refSuffix": None, "refRaw": part})
            continue

        # 4. Fallback for Exceptions: "app. XIII"
        results.append({"refNumber": None, "refSuffix": None, "refRaw": part})
    
    return results

def transform_to_json(csv_path):
    df = pd.read_csv(csv_path)
    final_output = []

    # Extract references for each edition
    edition_map = {'B': 'BRU', 'L': 'LAF', 'LG': 'LEG'}
    
    for idx, row in df.iterrows():
        # --- 1. Handle Sellier Number (The "Anchor") ---
        s_val = str(row['S']).strip() if pd.notna(row['S']) else ""
        
        s_nums = []
        if s_val == "" or s_val == "-":
            s_nums = [None]  # Keep the row alive even if Sellier is empty
        elif '-' in s_val:
            try:
                start, end = map(int, s_val.split('-'))
                s_nums = list(range(start, end + 1))
            except ValueError:
                s_nums = [s_val] # Fallback for non-numeric ranges if they exist
        else:
            # Handle float strings like "1.0" coming from pandas
            try:
                s_nums = [int(float(s_val))]
            except ValueError:
                s_nums = [s_val]
 
        # --- 2. Parse Other Editions ---
        current_refs = []
        for col, code in edition_map.items():
            parsed_list = parse_complex_ref(row[col])
            for item in parsed_list:
                current_refs.append({
                    **item,
                    "edition": code
                })

        # --- 3. Flatten into Final Output ---
        for s_num in s_nums:
            final_output.append({
                "sellierNumber": s_num,
                "references": list(current_refs),
                "original_row_index": idx
            })        

    return final_output

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

# Usage
if __name__ == "__main__":
    input_path = sys.argv[1] if len(sys.argv) > 1 else "data/raw/data.csv"
    
    df = pd.read_csv(input_path)
    data = transform_to_json(input_path)
    
    # remove 'original_row_index' from every entry
    clean_data = []
    for entry in data:
        clean_entry = entry.copy()
        clean_entry.pop('original_row_index', None) # Remove it if it exists
        clean_data.append(clean_entry)
        
    input_file = Path(input_path)
    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)  # create if missing
    
    # --- JSON ---
    output_path = output_dir / f"{input_file.stem}.json"
    with open(output_path, "w") as f:
        json.dump(clean_data, f, indent=2)
    print(f"✅ JSON file saved to: {output_path}")
    
    # --- ANOMALY REPORT ---
    report_path = output_dir / f"{input_file.stem}_audit.md"
    run_data_audit(data, df, report_path)
    print(f"✅ Audit report saved to: {report_path}")