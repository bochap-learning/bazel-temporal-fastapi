import pytest
from temporalio.testing import ActivityEnvironment
from service.observation.model import ExtractObservationActivityInput
from service.observation.activity import ExtractObservationActivity

@pytest.mark.asyncio
async def test_extract_observation_activity_with_data():
    patient_id = "1119"
    activity_environment = ActivityEnvironment()
    activity = ExtractObservationActivity()
    activity_input = ExtractObservationActivityInput(patient_id)
    activity_output = await activity_environment.run(activity.extract_observation, activity_input)
    assert activity_output.has_data == True
    assert activity_output.data == {'id': '1120', 'patient_id': '1119', 'resource_type': 'Observation', 'status': 'final'}

@pytest.mark.asyncio
async def test_extract_observation_activity_without_data():
    patient_id = "425"
    activity_environment = ActivityEnvironment()
    activity = ExtractObservationActivity()
    activity_input = ExtractObservationActivityInput(patient_id)
    activity_output = await activity_environment.run(activity.extract_observation, activity_input)
    assert activity_output.has_data == False
    assert activity_output.data == None