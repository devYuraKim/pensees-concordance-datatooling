import pytest
from scripts.csv_to_json import parse_complex_ref, transform_to_json

@pytest.mark.parametrize("input_val, expected", [
    # Case: Simple Number
    ("599", [{"refNumber": 599, "refSuffix": None, "refRaw": "599"}]),
    
    # Case: Suffix (bis/ter)
    ("163 bis", [{"refNumber": 163, "refSuffix": "bis", "refRaw": "163 bis"}]),
    
    # Case: Range (Should expand into atomic units)
    ("241-242", [
        {"refNumber": 241, "refSuffix": None, "refRaw": "241"},
        {"refNumber": 242, "refSuffix": None, "refRaw": "242"}
    ]),
    
    # Case: Multiple References
    ("835, 192", [
        {"refNumber": 835, "refSuffix": None, "refRaw": "835"},
        {"refNumber": 192, "refSuffix": None, "refRaw": "192"}
    ]),
    
    # Case: Exception (Appendix/Text)
    ("app. XIII", [{"refNumber": None, "refSuffix": None, "refRaw": "app. XIII"}]),
    
    # Case: Null/Empty
    ("-", []),
    (None, [])
])
def test_parse_complex_ref(input_val, expected):
    assert parse_complex_ref(input_val) == expected
    
def test_transform_to_json():
    result = transform_to_json("data/raw/test.csv")

    assert isinstance(result, list)
    assert len(result) > 0

    first = result[0]
    assert "sellierNumber" in first
    assert "references" in first