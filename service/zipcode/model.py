from dataclasses import dataclass

@dataclass
class ETLZipcodeWorkflowInput:
    url: str
    zipcode: str
    page: int

@dataclass
class ETLZipcodeWorkflowResponse:
    workflow_id: int
    run_id: int    