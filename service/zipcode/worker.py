import asyncio
from temporalio.client import Client
from temporalio.worker import Worker
from library.orchestration.activity import CustomSqlActivity
from library.storage.blob_minio import (
    MinioClient,
    MinioStoreConfig
)
from library.storage.postgres import Postgres
from service.patient.activity import ExtractAndGeneratePatientActivity
from service.observation.activity import (
    ExtractObservationActivity,
    LoadObservationActivity
)
from service.zipcode.shared import ETL_ZIPCODE_TASK_QUEUE
from service.zipcode.workflow import ETLZipcodeWorkflow


async def main():
    client = await Client.connect("localhost:7233", namespace="default")
    zipcode = "02718"
    bucket = "public-bucket"
    config = MinioStoreConfig("http", "localhost", "9000", "bochap", "unsecure4convience", True)
    blob = MinioClient(config)
    db = Postgres("postgresql://bochap:unsecure4convience@localhost:5432/api")
    worker = Worker(
        client,
        task_queue = ETL_ZIPCODE_TASK_QUEUE,
        workflows = [ETLZipcodeWorkflow],
        activities = [
            ExtractAndGeneratePatientActivity(blob, bucket).extract_and_generate_patient,
            CustomSqlActivity(db).execute_sql,
            ExtractObservationActivity().extract_observation,
            LoadObservationActivity(blob, bucket).load_observation
        ],
    )
    print("Started worker...")
    await worker.run()
            
if __name__ == "__main__":
    asyncio.run(main())