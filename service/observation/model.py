from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from sqlmodel import SQLModel, Field
from service.patient.model import PatientPersistent

class Observation(SQLModel):
    resource_type: str
    status: str

class ObservationPersistent(Observation, table=True):
    __tablename__ = "observation"
    id: str = Field(primary_key=True)    
    patient_id: str = Field(foreign_key=f"{PatientPersistent.__tablename__}.id")

@dataclass
class ExtractObservationActivityInput:
    patient_id: str

@dataclass
class ExtractObservationActivityOutput:
    has_data: bool
    data: Optional[Dict[str, Any]]

@dataclass
class LoadObservationActivityInput:
    data: List[Dict[str, Any]]
    zipcode: str
    page: int

@dataclass
class LoadObservationActivityOutput:
    blob_path: str    