import asyncio
from temporalio.client import Client
from temporalio.worker import Worker
from library.meta.env import get_minio_configuration, get_api_db_conn, get_temporal_host
from library.orchestration.activity import CustomSqlActivity
from library.storage.blob_minio import MinioClient
from library.storage.postgres import Postgres
from service.patient.activity import ExtractAndGeneratePatientActivity
from service.observation.activity import (
    ExtractObservationActivity,
    LoadObservationActivity
)
from service.zipcode.shared import ETL_ZIPCODE_TASK_QUEUE
from service.zipcode.workflow import ETLZipcodeWorkflow


async def main():
    client = await Client.connect(get_temporal_host(), namespace="default")
    config = get_minio_configuration()
    bucket = config.bucket
    blob = MinioClient(config)
    db = Postgres(get_api_db_conn())
    async with Worker(
        client,
        task_queue = ETL_ZIPCODE_TASK_QUEUE,
        workflows = [ETLZipcodeWorkflow],
        activities = [
            ExtractAndGeneratePatientActivity(blob, bucket).extract_and_generate_patient,
            CustomSqlActivity(db).execute_sql,
            ExtractObservationActivity().extract_observation,
            LoadObservationActivity(blob, bucket).load_observation
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