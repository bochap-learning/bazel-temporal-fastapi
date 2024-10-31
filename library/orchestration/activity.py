from typing import List
from temporalio import activity
from sqlalchemy import text
from sqlmodel import Session
from library.storage.postgres import Postgres
from library.orchestration.model import CustomSqlInput

class CustomSqlActivity:
    def __init__(self, db: Postgres) -> None:
        self.db = db        
    
    @activity.defn
    async def execute_sql(self, input: CustomSqlInput) -> None:
        activity.logger.info("Executing custom sql batch")
        with next(self.db.get_session()) as session:
            for statement in input.statements:
                session.execute(text(statement))
                session.commit()
        activity.logger.info("Completed custom sql batch")
        return