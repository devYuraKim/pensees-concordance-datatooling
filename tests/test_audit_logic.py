import pytest
import pandas as pd
from pathlib import Path
from scripts.audit_logic import run_data_audit, generate_summary_table

# pytest tests/test_audit_logic.py -v    

@pytest.fixture
def mock_pipeline():
    """Returns a helper to run the audit on data where index matches DataFrame size."""
    def _run(data_list, df_dict):
        report_path = Path("test_report.md")
        # FIX: We ensure the DataFrame has enough rows to satisfy the indices in data_list
        df = pd.DataFrame(df_dict) 
        return data_list, df, report_path
    return _run

## --- SECTION TESTS ---

def test_section_1_sellier_missing(mock_pipeline, tmp_path):
    data, df, path = mock_pipeline(
        [{"original_row_index": 0, "sellierNumber": None, "references": []}],
        {"S": [""], "B": ["1"], "L": ["2"], "LG": ["3"]}
    )
    report_file = tmp_path / path
    run_data_audit(data, df, report_file)
    content = report_file.read_text()
    
    assert "## 1.Sellier Missing (1 rows)" in content
    assert "**Row 2**" in content 
    assert "[ empty | 1 | 2 | 3 ]" in content

def test_section_2_incomplete_editions(mock_pipeline, tmp_path):
    data, df, path = mock_pipeline(
        [{"original_row_index": 0, "sellierNumber": "10", "references": []}],
        {"S": ["10"], "B": [""], "L": ["-"], "LG": ["nan"]}
    )
    report_file = tmp_path / path
    run_data_audit(data, df, report_file)
    content = report_file.read_text()
    
    assert "## 2.Incomplete Editions (1 rows)" in content
    assert "`B, L, LG`" in content

def test_section_3_ranges_and_commas(mock_pipeline, tmp_path):
    data, df, path = mock_pipeline(
        [{"original_row_index": 0, "sellierNumber": "20", "references": []}],
        {"S": ["20"], "B": ["624, 204"], "L": ["10-15"], "LG": ["100"]}
    )
    report_file = tmp_path / path
    run_data_audit(data, df, report_file)
    content = report_file.read_text()
    
    assert "## 3.Ranges or Multi-refs" in content
    assert "B: 624, 204" in content or "L: 10-15" in content

def test_section_4_suffixes(mock_pipeline, tmp_path):
    data, df, path = mock_pipeline(
        [{
            "original_row_index": 0, 
            "sellierNumber": "30", 
            "references": [{"edition": "B", "refRaw": "163 bis"}]
        }],
        {"S": ["30"], "B": ["163 bis"], "L": ["1"], "LG": ["2"]}
    )
    report_file = tmp_path / path
    run_data_audit(data, df, report_file)
    content = report_file.read_text()
    
    assert "## 4.Suffixes (1 rows)" in content
    assert "B: 163 bis" in content

def test_section_5_non_numeric(mock_pipeline, tmp_path):
    data, df, path = mock_pipeline(
        [{
            "original_row_index": 0, 
            "sellierNumber": "40", 
            "references": [{"edition": "L", "refRaw": "app. XIII"}]
        }],
        {"S": ["40"], "B": ["1"], "L": ["app. XIII"], "LG": ["2"]}
    )
    report_file = tmp_path / path
    run_data_audit(data, df, report_file)
    content = report_file.read_text()
    
    assert "## 5.Non-Numeric Refs (1 rows)" in content
    assert "L: app. XIII" in content

def test_unique_row_counting_logic(mock_pipeline, tmp_path):
    data, df, path = mock_pipeline(
        [{"original_row_index": 0, "sellierNumber": "50-51", "references": []}],
        {"S": ["50-51"], "B": ["1"], "L": ["2"], "LG": [""]}
    )
    report_file = tmp_path / path
    run_data_audit(data, df, report_file)
    content = report_file.read_text()

    assert "| To Review (CSV Rows)| 1 |" in content
    assert "**Row 2**" in content

def test_summary_table_regex_bolding():
    # FIX: Added the missing keys to the report dict so generate_summary_table doesn't KeyError
    report = {
        "null_sellier": ["**Row 50**: [ context ]"],
        "missing_editions": [],
        "ranges_or_multi": [],
        "suffixes": [],
        "non_numeric": []
    }
    stats = {
        'total_records': 1, 'flagged_records': 1, 'missing_sellier': 1, 
        'incomplete_editions': 0, 'ranges_found': 0, 'suffixes_found': 0, 'non_numeric': 0
    }
    
    summary = generate_summary_table(stats, report)
    assert "| 50 |" in summary
    assert "**50**" in summary