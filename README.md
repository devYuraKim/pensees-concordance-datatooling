This repository contains small data processing tools that transform raw concordance tables (CSV) into a normalized JSON dataset suitable for ingestion into relational databases.

## Edge Case Demonstration

This repository includes a sample dataset designed to stress-test the parser against real-world irregularities (ranges, suffixes like "bis", and non-numeric references).

Run the following command to generate the transformed output:

```bash
python3 scripts/csv_to_json.py data/raw/edgecases.csv
```

The output will be saved to `data/processed/`.

Inspect the result to see how each reference is normalized into structured fields (`refNumber`, `refSuffix`, `refRaw`), including:

- Expansion of ranges (e.g. `292-293`, `835,192`)
- Parsing of suffixes (e.g. `163 bis`)
- Handling of non-numeric references (e.g. `app. XIII`)

A reference output is provided in `data/processed/edgecases.expected.json` for comparison.
