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
    
    for _, row in df.iterrows():
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
                "references": list(current_refs)
            })        

    return final_output

# Usage
if __name__ == "__main__":
    input_path = sys.argv[1] if len(sys.argv) > 1 else "data/raw/data.csv"
    
    data = transform_to_json(input_path)
    
    # extract filename without extension
    input_file = Path(input_path)
    
    # target directory
    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)  # create if missing
    
    output_path = output_dir / f"{input_file.stem}.json"
    
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Saved to {output_path}")
    
    # --- ANOMALY REPORT ---
    null_sellier_rows = [
        (i, e['references']) 
        for i, e in enumerate(data) 
        if e['sellierNumber'] is None
    ]

    if null_sellier_rows:
        print(f"\n⚠️ Found {len(null_sellier_rows)} entries missing Sellier fragment number:")
        for idx, refs in null_sellier_rows: 
            ref_summary = ", ".join([f"{r['edition']}:{r['refRaw']}" for r in refs])
            # idx + 2 assumes a header row in the CSV
            print(f"  - Row {idx + 2}: [{ref_summary}]") 