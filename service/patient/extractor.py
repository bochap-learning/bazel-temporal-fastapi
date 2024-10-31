from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class PatientRecords:
    data: List[Dict[str, Any]]
    processed_records: int
    total_records: int

@dataclass
class PatientPage:
    records: PatientRecords
    next_url: Optional[str]

def _extract_models(response: Dict[str, Any]) -> PatientRecords:
    if "entry" not in response:
        return PatientRecords([], 0, 0)     
    records = []
    for raw_record in response["entry"]:
        is_valid, record =  _extract_model(raw_record)
        if not is_valid: continue
        records.append(record)

    return PatientRecords(records, len(records), len(response["entry"]))

def _extract_model(patient: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    if "resource" not in patient: return (False, None)
    resource = patient["resource"]
    if not resource.get("id", None): return (False, None)
    if not resource.get("gender", None): return (False, None)
    if not resource.get("birthDate", None): return (False, None)    
    name = resource.get("name", None)
    if not name: return (False, None)
    if not name[0].get("given", None): return (False, None)    
    return (True, {
        "id": resource["id"],
        "first_name": resource["name"][0]["given"][0],
        "gender": resource["gender"],
        "birth_date": resource["birthDate"] 
    })

def _extract_next_url(response: Dict[str, Any]) -> Optional[str]:
    if "link" not in response: return None
    links = response["link"]
    next_page = [ link["url"] for link in links if link["relation"] == "next" ]
    return None if len(next_page) == 0 else next_page[0]

def extract_page(response: Dict[str, Any]) -> PatientPage:
    return PatientPage(
        _extract_models(response),
        _extract_next_url(response)
    )
    