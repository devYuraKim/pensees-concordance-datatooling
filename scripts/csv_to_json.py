import json
import sys
import pandas as pd
from pathlib import Path

from validate_json import validate_json_data
from parser_logic import parse_complex_ref
from audit_logic import run_data_audit

def transform_to_json(df):
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

# Usage
if __name__ == "__main__":
    input_file = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/raw/data.csv")    
    
    df = pd.read_csv(input_file, encoding='utf-8')
    data = transform_to_json(df)
    
    REPORT_DIR = Path("data/processed/reports")
    JSON_DIR = Path("data/processed/json")
    # Create them if they are missing
    for folder in [REPORT_DIR, JSON_DIR]:
        folder.mkdir(parents=True, exist_ok=True)
    
    # remove 'original_row_index' from every entry
    clean_data = []
    for entry in data:
        clean_entry = entry.copy()
        clean_entry.pop('original_row_index', None) # Remove it if it exists
        clean_data.append(clean_entry)
    
    schema_file = Path(__file__).parent.parent / "schemas" / "concordance_schema.json"
    is_valid, errors = validate_json_data(clean_data, schema_file)
    
    if is_valid:
        # --- JSON /processed/json---
        output_path = JSON_DIR / f"{input_file.stem}.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(clean_data, f, indent=2)
        print(f"✅ Success: JSON file saved to: {output_path}")
        # --- AUDIT /processed/reports ---
        report_path = REPORT_DIR / f"{input_file.stem}_audit.md"
        run_data_audit(data, df, report_path)
        print(f"✅ Success: Audit report saved to: {report_path}")
    else:
        # 1. Create a mapping of {index: [list_of_errors]}
        error_map = {}
        for error in errors:
            if error.path:
                idx = error.path[0]
                msg = f"{error.message} (Field: {error.path[1] if len(error.path) > 1 else '?'})"
                error_map.setdefault(idx, []).append(msg)

        # 2. Get unique sorted indices
        failed_indices = sorted(error_map.keys())
        
        # 3. Filter the original DataFrame
        error_df = df.iloc[failed_indices].copy()
        
        # 4. Add the "Source_CSV_Row" for cross reference purpose
        error_df.insert(0, 'Source_CSV_Row', [i + 2 for i in failed_indices])
        
        # 5. Add the "Error_Description" column
        error_df['Error_Description'] = ["; ".join(error_map[i]) for i in failed_indices]
        
        # 6. Save to CSV
        error_csv_path = REPORT_DIR / f"{input_file.stem}_FIX_ME.csv"
        error_df.to_csv(error_csv_path, index=False)
        
        print(f"❌ Error: JSON Validation failed.")
        print(f"   {len(failed_indices)} rows contain errors that must be fixed.")
        print(f"   Location: {error_csv_path}")
        print("🛠️  ACTION REQUIRED:")
        print("   1. Open the file above.")
        print("   2. Fix the issues in your ORIGINAL CSV.")
        print("   3. RUN THIS SCRIPT AGAIN.")
    
