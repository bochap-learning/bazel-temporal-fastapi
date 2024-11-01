from typing import Optional
from fastapi import FastAPI, status
from pydantic import BaseModel
from sqlmodel import select
from library.meta.env import get_api_db_conn, get_temporal_host
from library.storage.postgres import Postgres
from service.zipcode.workflow import start_workflow
from service.patient.model import Patient, PatientPersistent
from service.observation.model import Observation, ObservationPersistent



app = FastAPI()
db = Postgres(get_api_db_conn())

class LoadZipcodeRequest(BaseModel):
    zipcode: str

@app.get("/")
async def root():
    return { "message": "Hello World" }

@app.get("/patients/{patient_id}")
async def get_patient(patient_id: str) -> Optional[Patient]:
    with next(db.get_session()) as session:
        return session.get(PatientPersistent, patient_id)

@app.get("/patients")
async def get_patient_by_first_name(first_name: str) -> Optional[Patient]:
    with next(db.get_session()) as session:
        statement = select(PatientPersistent).where(PatientPersistent.first_name == first_name)
        results = session.exec(statement)
        return results.first()

@app.get("/observations")
async def get_observations_by_patient_id(patient_id: str) -> Optional[Observation]:
    with next(db.get_session()) as session:
        statement = select(ObservationPersistent).where(ObservationPersistent.patient_id == patient_id)
        results = session.exec(statement)
        return results.first()

@app.post("/zipcode", status_code=status.HTTP_204_NO_CONTENT)
async def load_zipcode(request: LoadZipcodeRequest):
    response = await start_workflow(get_temporal_host(), request.zipcode)
    print(f"Started workflow. Workflow ID: {response.workflow_id}, RunID {response.run_id}")
