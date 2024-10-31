import json
import os

from service.patient.extractor import _extract_model, _extract_next_url, extract_page, PatientPage

def test_extract_model_valid_patient() -> None:
    target = {
        "resource": {
            "id": "425",
            "name": [{
                "given": [ "Jérôme" ],
            }],
            "gender": "male",
            "birthDate": "1945-12-10"
        }
    }
    is_valid, extracted = _extract_model(target)
    assert is_valid == True
    assert extracted == {
        "id": "425",
        "first_name": "Jérôme",
        "gender": "male",
        "birth_date": "1945-12-10",
    }


def test_extract_model_invalid_patient_with_missing_resource() -> None:
    target = {}
    is_valid, extracted = _extract_model(target)
    assert is_valid == False
    assert extracted == None    

def test_extract_model_invalid_patient_with_missing_id() -> None:
    target = {
        "resource": {
            "name": [{
                "given": [ "Jérôme" ],
            }],
            "gender": "male",
            "birthDate": "1945-12-10"
        }
    }
    is_valid, extracted = _extract_model(target)
    assert is_valid == False
    assert extracted == None

def test_extract_model_invalid_patient_with_missing_name() -> None:
    target = {
        "resource": {
            "id": "425",
            "gender": "male",
            "birthDate": "1945-12-10"
        }
    }    
    is_valid, extracted = _extract_model(target)
    assert is_valid == False
    assert extracted == None

def test_extract_model_invalid_patient_with_empty_name() -> None:
    target = {
        "resource": {
            "id": "425",
            "name": [],
            "gender": "male",
            "birthDate": "1945-12-10"
        }
    }    
    is_valid, extracted = _extract_model(target)
    assert is_valid == False
    assert extracted == None

def test_extract_model_invalid_patient_with_missing_given() -> None:
    target = {
        "resource": {
            "id": "425",
            "name": [{}],
            "gender": "male",
            "birthDate": "1945-12-10"
        }
    }
    is_valid, extracted = _extract_model(target)
    assert is_valid == False
    assert extracted == None

def test_extract_model_invalid_patient_with_empty_given() -> None:
    target = {
        "resource": {
            "id": "425",
            "name": [{
                "given": [],
            }],
            "gender": "male",
            "birthDate": "1945-12-10"
        }
    }    
    is_valid, extracted = _extract_model(target)
    assert is_valid == False
    assert extracted == None    

def test_extract_model_invalid_patient_with_missing_gender() -> None:
    target = {
        "resource": {
            "id": "425",
            "name": [{
                "given": [ "Jérôme" ],
            }],
            "birthDate": "1945-12-10"
        }
    }    
    is_valid, extracted = _extract_model(target)
    assert is_valid == False
    assert extracted == None

def test_extract_model_invalid_patient_with_missng_birthdate() -> None:
    target = {
        "resource": {
            "id": "425",
            "name": [{
                "given": [ "Jérôme" ],
            }],
            "gender": "male",
        }
    }    
    is_valid, extracted = _extract_model(target)
    assert is_valid == False
    assert extracted == None

def test_extract_next_url_not_found() -> None:
    target = {
        "link": [
            {
                "relation": "self",
                "url": "https://hapi.fhir.org/baseR5/Patient?_count=5&_getpagesoffset=0&address-postalcode=02718"
            }
        ]
    }
    next_page = _extract_next_url(target)
    assert next_page == None

def test_extract_next_url_found() -> None:
    target = {
        "link": [
            {
                "relation": "self",
                "url": "https://hapi.fhir.org/baseR5/Patient?_count=5&_getpagesoffset=0&address-postalcode=02718"
            }, {
                "relation": "next",
                "url": "https://hapi.fhir.org/baseR5?_getpages=ec54982a-bc23-4b32-ae37-644c15cc97a1&_getpagesoffset=5&_count=5&_pretty=true&_bundletype=searchset"
            }
        ]
    }    
    next_page = _extract_next_url(target)
    assert next_page == "https://hapi.fhir.org/baseR5?_getpages=ec54982a-bc23-4b32-ae37-644c15cc97a1&_getpagesoffset=5&_count=5&_pretty=true&_bundletype=searchset"

def test_extract_page_with_next_url() -> None:
    cwd = os.path.dirname(__file__)
    with open(os.path.join(cwd, "data/test/patient_with_next_url.json"), "r") as file:
        response = json.load(file)
        page = extract_page(response)
        expected_data = [
            { "id": "425", "first_name": "Jérôme", "gender": "male", "birth_date": "1945-12-10" },
            { "id": "1002", "first_name": "Benny899sydd", "gender": "male", "birth_date": "1948-09-10" },
            { "id": "1003", "first_name": "Lenny", "gender": "male", "birth_date": "1948-09-10" },
            { "id": "1052", "first_name": "Lenny899", "gender": "male", "birth_date": "1948-09-10" },
            { "id": "1053", "first_name": "Lenny", "gender": "male", "birth_date": "1948-09-10" }
        ]
        assert page.records.processed_records == 5
        assert page.records.total_records == 5
        assert page.records.data == expected_data
        assert page.next_url == "https://hapi.fhir.org/baseR5?_getpages=ec54982a-bc23-4b32-ae37-644c15cc97a1&_getpagesoffset=5&_count=5&_pretty=true&_bundletype=searchset"

def test_extract_page_without_next_url() -> None:
    cwd = os.path.dirname(__file__)
    with open(os.path.join(cwd, "data/test/patient_without_next_url.json"), "r") as file:
        response = json.load(file)
        page = extract_page(response)
        expected_data = [
            { "id": "425", "first_name": "Jérôme", "gender": "male", "birth_date": "1945-12-10" },
            { "id": "1002", "first_name": "Benny899sydd", "gender": "male", "birth_date": "1948-09-10" },
            { "id": "1003", "first_name": "Lenny", "gender": "male", "birth_date": "1948-09-10" },
            { "id": "1052", "first_name": "Lenny899", "gender": "male", "birth_date": "1948-09-10" },
            { "id": "1053", "first_name": "Lenny", "gender": "male", "birth_date": "1948-09-10" }
        ]
        assert page.records.processed_records == 5
        assert page.records.total_records == 5
        assert page.records.data == expected_data
        assert page.next_url == None
