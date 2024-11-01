from sqlmodel import SQLModel, create_engine, Session
from library.meta.metaclass import Singleton

class Postgres(metaclass=Singleton):
    def __init__(self, conn: str, echo: bool = False) -> None:
        self.engine = create_engine(conn, echo=echo)

    def register_schema(self) -> None:
        SQLModel.metadata.create_all(self.engine)

    def get_session(self) -> Session:
        with Session(self.engine) as session:
            yield session

    def copy_from_minio(table: str, path: str) -> str:
        return f"COPY {table} FROM PROGRAM 'curl {path}' csv header;"