import json
from jsonschema import Draft7Validator

def validate_json_data(json_data, schema_path):
    """
    Validates a dictionary or list against a JSON schema file.
    """
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema = json.load(f)
        
    validator = Draft7Validator(schema)
    errors = list(validator.iter_errors(json_data))
    
    if not errors:
        print("✅ Success: JSON Schema validation passed!")
        return True, []
    
    return False, errors
