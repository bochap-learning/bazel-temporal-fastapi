import asyncio
from temporalio.worker import Worker
from library.meta.config import (
    get_env_config
)
from library.client.factory import (
    get_temporal_client,
    get_api_db_client,
    get_vault_client,
    get_minio_client
)
from library.orchestration.activity import CustomSqlActivity
from service.patient.activity import ExtractAndGeneratePatientActivity
from service.observation.activity import (
    ExtractObservationActivity,
    LoadObservationActivity
)
from service.zipcode.shared import ETL_ZIPCODE_TASK_QUEUE
from service.zipcode.workflow import ETLZipcodeWorkflow


async def main():
    env_config = get_env_config()
    vault = get_vault_client(env_config)
    client = await get_temporal_client(vault, env_config.localhost_override)
    db = get_api_db_client(vault, env_config.localhost_override)
    blob = get_minio_client(vault, env_config.localhost_override)
    async with Worker(
        client,
        task_queue = ETL_ZIPCODE_TASK_QUEUE,
        workflows = [ETLZipcodeWorkflow],
        activities = [
            ExtractAndGeneratePatientActivity(blob).extract_and_generate_patient,
            CustomSqlActivity(db).execute_sql,
            ExtractObservationActivity().extract_observation,
            LoadObservationActivity(blob).load_observation
        ],
    ):
        print("Worker started, ctrl+c to exit.")       
        await asyncio.Future() # keep the worker running
    print("Shutting down")

            
if __name__ == "__main__":
    try:
        asyncio.run(main())    
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt received, shutting down...")