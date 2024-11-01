import pytest
from temporalio.testing import ActivityEnvironment
from library.meta.env import get_minio_configuration
from library.storage.blob_minio import MinioClient
from service.patient.shared import get_patients_url
from service.patient.model import (
    ExtractAndGeneratePatientActivityInput,
)
from service.patient.activity import ExtractAndGeneratePatientActivity

@pytest.mark.asyncio
async def test_extract_and_generate_patient_activity_success():
    config = get_minio_configuration()
    zipcode = "02718"
    bucket = config.bucket
    blob = MinioClient(config)
    activity_environment = ActivityEnvironment()
    activity = ExtractAndGeneratePatientActivity(blob, bucket)
    activity_input = ExtractAndGeneratePatientActivityInput(get_patients_url(zipcode), zipcode, 0)
    activity_output = await activity_environment.run(activity.extract_and_generate_patient, activity_input)
    assert activity_output.processed_records == 15
    assert activity_output.total_records == 15    
    assert activity_output.blob_path.endswith(f"{zipcode}-0/patient.csv")
    assert activity_output.next_url.startswith("https://hapi.fhir.org/baseR5")
