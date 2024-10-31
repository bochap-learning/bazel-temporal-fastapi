from typing import Optional, List
from dataclasses import dataclass
from sqlmodel import SQLModel, Field

class Patient(SQLModel):
    first_name: str = Field(index=True)
    gender: str
    birth_date: str

class PatientPersistent(Patient, table=True):
    __tablename__ = "patient"
    id: str = Field(primary_key=True)    

@dataclass
class ExtractAndGeneratePatientActivityInput:
    url: str
    zipcode: str
    page: int

@dataclass
class ExtractAndGeneratePatientActivityOutput:
    blob_path: str
    patient_ids: List[str]
    next_url: Optional[str]
    processed_records: int
    total_records: int

