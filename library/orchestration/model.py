from typing import List
from dataclasses import dataclass

@dataclass
class CustomSqlInput:
    statements: List[str]