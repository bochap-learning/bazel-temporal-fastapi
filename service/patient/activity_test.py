import pytest
from temporalio.testing import ActivityEnvironment
from library.meta.config import (
    get_env_config
)
from library.client.factory import (
    get_vault_client, get_minio_client
)
from library.storage.blob_minio import MinioClient
from service.patient.shared import get_patients_url
from service.patient.model import (
    ExtractAndGeneratePatientActivityInput,
)
from service.patient.activity import ExtractAndGeneratePatientActivity

@pytest.mark.asyncio
async def test_extract_and_generate_patient_activity_success_without_paging():
    zipcode = "02718"
    env_config = get_env_config()
    vault = get_vault_client(env_config)
    blob = get_minio_client(vault, env_config.localhost_override)
    activity_environment = ActivityEnvironment()
    activity = ExtractAndGeneratePatientActivity(blob)
    activity_input = ExtractAndGeneratePatientActivityInput(get_patients_url(zipcode), zipcode, 0)
    activity_output = await activity_environment.run(activity.extract_and_generate_patient, activity_input)
    assert activity_output.processed_records == 16
    assert activity_output.total_records == 16    
    assert activity_output.blob_path.endswith(f"{zipcode}-0/patient.csv")
    assert activity_output.next_url == None

@pytest.mark.asyncio
async def test_extract_and_generate_patient_activity_success_with_paging():    
    zipcode = "3999"
    env_config = get_env_config()
    vault = get_vault_client(env_config)
    blob = get_minio_client(vault, env_config.localhost_override)
    activity_environment = ActivityEnvironment()
    activity = ExtractAndGeneratePatientActivity(blob)
    activity_input = ExtractAndGeneratePatientActivityInput(get_patients_url(zipcode), zipcode, 0)
    activity_output = await activity_environment.run(activity.extract_and_generate_patient, activity_input)
    assert activity_output.processed_records == 50
    assert activity_output.total_records == 50    
    assert activity_output.blob_path.endswith(f"{zipcode}-0/patient.csv")
    assert activity_output.next_url.startswith("https://hapi.fhir.org/baseR5")
