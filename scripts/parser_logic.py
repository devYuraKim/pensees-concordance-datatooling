import pandas as pd
import re

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
        suffix_match = re.match(r'^(\d+)\s+([a-zA-Z]+)$', part)
        if suffix_match:
            num, suffix = suffix_match.groups()
            results.append({"refNumber": int(num), "refSuffix": suffix.lower(), "refRaw": part})
            continue

        # 3. Handle Pure Numbers: "599" -> {number: 599}
        if part.isdigit():
            results.append({"refNumber": int(part), "refSuffix": None, "refRaw": part})
            continue

        # 4. Fallback for Exceptions: "app. XIII"
        results.append({"refNumber": None, "refSuffix": None, "refRaw": part})
    
    return results