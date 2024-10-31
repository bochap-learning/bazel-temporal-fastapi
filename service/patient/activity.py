from typing import Any
from temporalio import activity
from sqlmodel import SQLModel, Session
from library.webclient.rest import get_to_json
from library.converter.memory import to_csv_stringio
from library.storage.postgres import Postgres
from library.storage.blob_minio import MinioClient
from service.patient.shared import PATIENT_HEADERS
from service.patient.model import (
    ExtractAndGeneratePatientActivityInput,
    ExtractAndGeneratePatientActivityOutput,
)
from service.patient.extractor import extract_page

class ExtractAndGeneratePatientActivity:
    def __init__(self, blob: MinioClient, bucket: str) -> None:
        self.blob = blob
        self.bucket = bucket

    @activity.defn
    async def extract_and_generate_patient(self, input: ExtractAndGeneratePatientActivityInput) -> ExtractAndGeneratePatientActivityOutput:
        activity.logger.info(f"Calling api at url: {input.url}")
        raw_patient = await get_to_json(input.url)
        activity.logger.info("Converting patient to csv")
        patient_page = extract_page(raw_patient)
        patient_stream = to_csv_stringio(PATIENT_HEADERS, patient_page.records.data)
        patient_ids = [record["id"] for record in patient_page.records.data]
        blob_path = self.blob.write_stringio(patient_stream, f"{input.zipcode}-{input.page}/patient.csv", self.bucket)
        return ExtractAndGeneratePatientActivityOutput(
            blob_path,
            patient_ids,
            patient_page.next_url,
            patient_page.records.processed_records,
            patient_page.records.total_records
        )
