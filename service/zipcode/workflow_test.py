import pytest
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker
from library.meta.config import (
    get_env_config
)
from library.client.factory import (
    get_api_db_client,
    get_vault_client,
    get_minio_client
)
from library.storage.blob_minio import (
    MinioClient
)
from library.orchestration.activity import CustomSqlActivity
from service.patient.shared import (
    get_patients_url
)
from service.patient.activity import ExtractAndGeneratePatientActivity
from service.zipcode.shared import ETL_ZIPCODE_TASK_QUEUE
from service.zipcode.model import (
    ETLZipcodeWorkflowInput,
)
from service.zipcode.workflow import ETLZipcodeWorkflow

@pytest.mark.asyncio
async def test_etl_zipcode_workflow_success():
    async with await WorkflowEnvironment.start_local() as env:
        zipcode = "02718"
        env_config = get_env_config()
        vault = get_vault_client(env_config)        
        blob = get_minio_client(vault, env_config.localhost_override)
        db = get_api_db_client(vault, env_config.localhost_override)
        async with Worker(
            env.client,
            task_queue = ETL_ZIPCODE_TASK_QUEUE,
            workflows = [ETLZipcodeWorkflow],
            activities = [
                ExtractAndGeneratePatientActivity(blob).extract_and_generate_patient,
                CustomSqlActivity(db).execute_sql
            ],
        ):
            await env.client.execute_workflow(
                ETLZipcodeWorkflow.run,
                ETLZipcodeWorkflowInput(get_patients_url(zipcode), zipcode, 0),
                id = ETLZipcodeWorkflow.get_workflow_id(zipcode),
                task_queue = ETL_ZIPCODE_TASK_QUEUE
            )