import asyncio
from temporalio import workflow
from temporalio.client import Client

with workflow.unsafe.imports_passed_through():
    from datetime import timedelta
    from library.orchestration.model import CustomSqlInput
    from library.orchestration.activity import CustomSqlActivity
    from library.storage.postgres import Postgres
    from service.patient.shared import (
        CREATE_PATIENT_TABLE_PRODUCTION,
        CREATE_PATIENT_TABLE_TEMP,
        MERGE_PATIENT_TABLE_TEMP_TO_TABLE_PRODUCTION,
        TRUNCATE_PATIENT_TABLE_TEMP,
        PATIENT_TABLE_TEMP_NAME,
        get_patients_url
    )
    from service.patient.model import (
        ExtractAndGeneratePatientActivityInput,
        ExtractAndGeneratePatientActivityOutput,
    )
    from service.patient.activity import (
        ExtractAndGeneratePatientActivity
    )
    from service.observation.shared import (
        CREATE_OBSERVATION_TABLE_PRODUCTION,
        CREATE_OBSERVATION_TABLE_TEMP,
        MERGE_OBSERVATION_TABLE_TEMP_TO_TABLE_PRODUCTION,
        TRUNCATE_OBSERVATION_TABLE_TEMP,
        OBSERVATION_TABLE_TEMP_NAME,
        get_observation_url
    )
    from service.observation.model import (
        ExtractObservationActivityInput,
        ExtractObservationActivityOutput,
        LoadObservationActivityInput,
        LoadObservationActivityOutput,
    )
    from service.observation.activity import (
        ExtractObservationActivity,
        LoadObservationActivity
    )
    from service.zipcode.shared import ETL_ZIPCODE_TASK_QUEUE
    from service.zipcode.model import (
        ETLZipcodeWorkflowInput,
        ETLZipcodeWorkflowResponse
    )

@workflow.defn
class ETLZipcodeWorkflow:
    def get_workflow_id(zipcode: str) -> str:
        return f"extract-{zipcode}-patient-observation"
    
    @workflow.run
    async def run(self, input: ETLZipcodeWorkflowInput) -> None:
        workflow.logger.info(f"Start patient extraction workflow for zip: {input.zipcode}")
        workflow.logger.info("Extracting patient as csv")
        extractPatientInput = ExtractAndGeneratePatientActivityInput(
            input.url,
            input.zipcode,
            input.page
        )
        extractPatientOutput: ExtractAndGeneratePatientActivityOutput = await workflow.execute_activity_method(
            ExtractAndGeneratePatientActivity.extract_and_generate_patient,
            extractPatientInput,
            start_to_close_timeout=timedelta(seconds=30),
        )
        
        workflow.logger.info("Generate production patient schema")
        await workflow.execute_activity_method(
            CustomSqlActivity.execute_sql,
            CustomSqlInput(CREATE_PATIENT_TABLE_PRODUCTION),
            start_to_close_timeout=timedelta(seconds=5),
        )

        workflow.logger.info("Merge patient into prod")
        merge_sql: List[str] = [
            CREATE_PATIENT_TABLE_TEMP,
            Postgres.copy_from_minio(PATIENT_TABLE_TEMP_NAME, extractPatientOutput.blob_path),
            MERGE_PATIENT_TABLE_TEMP_TO_TABLE_PRODUCTION,
            TRUNCATE_PATIENT_TABLE_TEMP             # Adding this to make sure the table is cleared as SQLAlchemy uses connection pooling that doesn't clean up the temp tables
        ]
        await workflow.execute_activity_method(
            CustomSqlActivity.execute_sql,
            CustomSqlInput(merge_sql),
            start_to_close_timeout=timedelta(seconds=30),
        )
        workflow.logger.info(f"Loaded {extractPatientOutput.processed_records} patient{ "s" if extractPatientOutput.processed_records ==  0 or extractPatientOutput.processed_records > 1 else "" }")

        workflow.logger.info("Extracting observations")
        observation_records = []
        patient_ids = extractPatientOutput.patient_ids
        while patient_ids:
            subtasks = []
            for _ in range(min(len(patient_ids), 5)):
                patient_id = patient_ids.pop()
                extractObservationActivityInput = ExtractObservationActivityInput(patient_id)
                subtasks.append(asyncio.create_task(
                    workflow.execute_activity(
                        ExtractObservationActivity.extract_observation, 
                        extractObservationActivityInput, 
                        start_to_close_timeout=timedelta(seconds=30)
                    )
                ))
            extractObservationActivityOutputs = await asyncio.gather(*subtasks)
            for extractObservationActivityOutput in extractObservationActivityOutputs:
                if not extractObservationActivityOutput.has_data: continue
                observation_records.append(extractObservationActivityOutput.data)                    
        
        workflow.logger.info("Loading observations as csv")
        loadObservationActivityOutput: LoadObservationActivityOutput = await workflow.execute_activity_method(
            LoadObservationActivity.load_observation,
            LoadObservationActivityInput(observation_records, input.zipcode, input.page),
            start_to_close_timeout=timedelta(seconds=30),
        )
        
        workflow.logger.info("Generate production observation schema")
        await workflow.execute_activity_method(
            CustomSqlActivity.execute_sql,
            CustomSqlInput(CREATE_OBSERVATION_TABLE_PRODUCTION),
            start_to_close_timeout=timedelta(seconds=5),
        )

        workflow.logger.info("Merge patient into prod")
        merge_sql: List[str] = [
            CREATE_OBSERVATION_TABLE_TEMP,
            Postgres.copy_from_minio(OBSERVATION_TABLE_TEMP_NAME, loadObservationActivityOutput.blob_path),
            MERGE_OBSERVATION_TABLE_TEMP_TO_TABLE_PRODUCTION,
            TRUNCATE_OBSERVATION_TABLE_TEMP             # Adding this to make sure the table is cleared as SQLAlchemy uses connection pooling that doesn't clean up the temp tables
        ]
        await workflow.execute_activity_method(
            CustomSqlActivity.execute_sql,
            CustomSqlInput(merge_sql),
            start_to_close_timeout=timedelta(seconds=30),
        )
        workflow.logger.info(f"Loaded {len(observation_records)} observation{ "s" if len(observation_records) ==  0 or len(observation_records) > 1 else "" }")

        if extractPatientOutput.next_url:
            new_input = ETLZipcodeWorkflowInput(extractPatientOutput.next_url, input.zipcode, input.page + 1)
            workflow.continue_as_new(new_input)

    
async def start_workflow(host: str, zipcode: str):
    client = await Client.connect(host)
    input = ETLZipcodeWorkflowInput(
        get_patients_url(zipcode),
        zipcode,
        0
    )
    handle = await client.start_workflow(
        ETLZipcodeWorkflow.run,
        input,
        id = ETLZipcodeWorkflow.get_workflow_id(zipcode),
        task_queue = ETL_ZIPCODE_TASK_QUEUE
    )
    return ETLZipcodeWorkflowResponse(handle.id, handle.result_run_id)
