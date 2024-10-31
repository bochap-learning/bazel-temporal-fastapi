from typing import Any
from temporalio import activity
from sqlmodel import SQLModel
from library.webclient.rest import get_to_json
from library.converter.memory import to_csv_stringio
from library.storage.postgres import Postgres
from library.storage.blob_minio import MinioClient
from service.observation.shared import (OBSERVATION_HEADERS, get_observation_url)
from service.observation.model import (
    ExtractObservationActivityInput,
    ExtractObservationActivityOutput,
    LoadObservationActivityInput,
    LoadObservationActivityOutput
)
from service.observation.extractor import extract_page

class ExtractObservationActivity:
    @activity.defn
    async def extract_observation(self, input: ExtractObservationActivityInput) -> ExtractObservationActivityOutput:
        url = get_observation_url(input.patient_id)
        activity.logger.info(f"Calling api at url: {url}")
        raw_observation = await get_to_json(url)
        activity.logger.info("Converting observation to key value pairs")
        return extract_page(input.patient_id, raw_observation)
    
class LoadObservationActivity:
    def __init__(self, blob: MinioClient, bucket: str) -> None:
        self.blob = blob
        self.bucket = bucket

    @activity.defn
    async def load_observation(self, input: LoadObservationActivityInput) -> LoadObservationActivityOutput:
        activity.logger.info("Converting observation to csv")
        observation_stream = to_csv_stringio(OBSERVATION_HEADERS, input.data)
        blob_path = self.blob.write_stringio(observation_stream, f"{input.zipcode}-{input.page}/observations.csv", self.bucket)
        return LoadObservationActivityOutput(blob_path)