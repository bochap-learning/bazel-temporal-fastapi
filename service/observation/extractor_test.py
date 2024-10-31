import os
import json
from service.observation.extractor import _extract_model, extract_page

def test_extract_model_valid_observation() -> None:
    patient_id = "1119"
    target = {
        "resource": {
            "resourceType": "Observation",
            "id": "1120",
            "status": "final",
            "patient_id": patient_id
        }
    }
    is_valid, extracted = _extract_model(patient_id, target)
    assert is_valid == True
    assert extracted == {
        "id": "1120",
        "resource_type": "Observation",
        "status": "final",
        "patient_id": patient_id
    }

def test_extract_model_invalid_observation_with_missing_resource() -> None:
    patient_id = "1119"
    target = {}
    is_valid, extracted = _extract_model(patient_id, target)
    assert is_valid == False
    assert extracted == None    

def test_extract_model_invalid_observation_with_missing_id() -> None:
    patient_id = "1119"
    target = {
        "resource": {
            "resourceType": "Observation",
            "status": "final"
        }
    }
    is_valid, extracted = _extract_model(patient_id, target)
    assert is_valid == False
    assert extracted == None

def test_extract_model_invalid_observation_with_missing_resource_type() -> None:
    patient_id = "1119"
    target = {
        "resource": {
            "id": "1120",
            "status": "final"
        }
    }
    is_valid, extracted = _extract_model(patient_id, target)
    assert is_valid == False
    assert extracted == None

def test_extract_model_invalid_observation_with_missing_status() -> None:
    patient_id = "1119"
    target = {
        "resource": {
            "id": "1120",
            "status": "final"
        }
    }
    is_valid, extracted = _extract_model(patient_id, target)
    assert is_valid == False
    assert extracted == None

def test_extract_page_with_data() -> None:
    patient_id = "1119"
    cwd = os.path.dirname(__file__)
    with open(os.path.join(cwd, "data/test/observation_with_data.json"), "r") as file:
        response = json.load(file)
        page = extract_page(patient_id, response)
        expected_data = { "id": "1120", "resource_type": "Observation", "status": "final", "patient_id": patient_id }
        assert page.data == expected_data