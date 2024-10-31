from typing import Any, Dict, Tuple
from service.observation.model import ExtractObservationActivityOutput

def _extract_model(patient_id: str, observation: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    if "resource" not in observation: return (False, None)
    resource = observation["resource"]
    if not resource.get("id", None): return (False, None)
    if not resource.get("resourceType", None): return (False, None)
    if not resource.get("status", None): return (False, None)
    return True, {
        "id": resource["id"],
        "resource_type": resource["resourceType"],
        "status": resource["status"],
        "patient_id": patient_id
    }

def extract_page(patient_id: str, response: Dict[str, Any]) -> ExtractObservationActivityOutput:
    if "entry" not in response:
        return ExtractObservationActivityOutput(False, None)
    for raw_record in response["entry"]:
        is_valid, record =  _extract_model(patient_id, raw_record)
        if not is_valid: continue
        return ExtractObservationActivityOutput(True, record)
    return ExtractObservationActivityOutput(False, None)