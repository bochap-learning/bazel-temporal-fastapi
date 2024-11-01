from typing import Optional
import os
from dotenv import load_dotenv
from dataclasses import dataclass

load_dotenv()

@dataclass
class MinioStoreConfig:
    protocol: str
    host: str
    port: str
    access_key: str
    secret_key: str
    bucket: str    

def _get_localhost_override() -> Optional[str]:
    if os.getenv("IS_LOCAL", "0") == "1":
        return "localhost"
    return None


"""
host is overriden by localhost is "IS_LOCAL" enviromental variable is set to true
"""
def get_temporal_host() -> str:
    host = _get_localhost_override()
    if not host:
        host = os.getenv("TEMPORAL_HOST")
    return f"{host}:{os.getenv("TEMPORAL_CONSOLE_PORT")}"

"""
host is overriden by localhost is "IS_LOCAL" enviromental variable is set to true
"""
def get_minio_host(config: MinioStoreConfig) -> str:
    host = _get_localhost_override()
    if not host:
        host = config.host
    return f"{host}:{config.port}"

def get_object_path(config: MinioStoreConfig, object_name: str) -> str:
    return f"{config.protocol}://{config.host}:{config.port}/{config.bucket}/{object_name}"

"""
host is overriden by localhost is "IS_LOCAL" enviromental variable is set to true
"""
def get_api_db_conn() -> str:
    host = _get_localhost_override()
    if not host:
        host = os.getenv("API_POSTGRES_DOCKER_HOST")
    user = os.getenv("API_POSTGRES_USER")
    password = os.getenv("API_POSTGRES_PASSWORD")
    db = os.getenv("API_POSTGRES_DB")
    port = os.getenv("API_POSTGRES_PORT")
    return f"postgresql://{user}:{password}@{host}:{port}/{db}"

def get_minio_configuration() -> MinioStoreConfig:
    protocol = "http"
    host = os.getenv("MINIO_HOST")
    port = os.getenv("MINIO_HTTP_PORT")
    access_key = os.getenv("MINIO_ACCESS_KEY")
    secret_key = os.getenv("MINIO_SECRET_KEY")
    bucket = os.getenv("MINIO_BUCKET")
    return MinioStoreConfig(protocol, host, port, access_key, secret_key, bucket)