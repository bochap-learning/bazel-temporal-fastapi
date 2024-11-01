# import pytest
# from temporalio.testing import WorkflowEnvironment
# from temporalio.worker import Worker
# from library.storage.blob_minio import (
#     MinioClient,
#     MinioStoreConfig
# )
# from library.storage.postgres import Postgres
# from library.orchestration.activity import CustomSqlActivity
# from service.patient.shared import (
#     get_patients_url
# )
# from service.patient.activity import ExtractAndGeneratePatientActivity
# from service.zipcode.shared import ETL_ZIPCODE_TASK_QUEUE
# from service.zipcode.model import (
#     ETLZipcodeWorkflowInput,
#     ETLZipcodeWorkflowResponse
# )
# from service.zipcode.workflow import ETLZipcodeWorkflow

# @pytest.mark.asyncio
# async def test_etl_zipcode_workflow_success():
#     async with await WorkflowEnvironment.start_local() as env:
#         zipcode = "02718"
#         bucket = "public-bucket"
#         config = MinioStoreConfig("http", "localhost", "9000", "bochap", "unsecure4convience", True)
#         blob = MinioClient(config)
#         db = Postgres("postgresql://bochap:unsecure4convience@localhost:5432/api")
#         async with Worker(
#             env.client,
#             task_queue = ETL_ZIPCODE_TASK_QUEUE,
#             workflows = [ETLZipcodeWorkflow],
#             activities = [
#                 ExtractAndGeneratePatientActivity(blob, bucket).extract_and_generate_patient,
#                 CustomSqlActivity(db).execute_sql
#             ],
#         ):
#             await env.client.execute_workflow(
#                 ETLZipcodeWorkflow.run,
#                 ETLZipcodeWorkflowInput(get_patients_url(zipcode), zipcode, 0),
#                 id = ETLZipcodeWorkflow.get_workflow_id(zipcode),
#                 task_queue = ETL_ZIPCODE_TASK_QUEUE
#             )