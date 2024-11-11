from temporalio.client import Client
from library.meta.config import EnvConfig
from library.storage.vault import Vault
from library.storage.postgres import Postgres
from library.storage.blob_minio import MinioClient

"""
    get temporal client using vault credentials with host overriden if host_override is provided
"""
async def get_temporal_client(vault: Vault, host_override: str) -> Client:
    host = host_override if host_override != None else vault.get_secret("temporal", "host")
    url = f"{host}:{vault.get_secret("temporal", "consoleport")}"
    return await Client.connect(url, namespace="default")

"""
    get postgres client using vault credentials with host overriden if host_override is provided
"""
def get_api_db_client(vault: Vault, host_override: str) -> Postgres:
    host = host_override if host_override != None else vault.get_secret("apipostgres", "host")
    user = vault.get_secret("apipostgres", "user")
    password = vault.get_secret("apipostgres", "password")
    db = vault.get_secret("apipostgres", "db")
    port = vault.get_secret("apipostgres", "port")
    conn = f"postgresql://{user}:{password}@{host}:{port}/{db}"
    print(conn)
    return Postgres(conn)

"""
    get vault client using env config with host overriden if host_override is provided
"""
def get_vault_client(config: EnvConfig) -> Vault:
    return Vault(config)

"""
    get minio client using vault credentials with host overriden if host_override is provided
"""
def get_minio_client(vault: Vault, host_override: str) -> MinioClient:
    host_with_override = host_override if host_override != None else vault.get_secret("minio", "host")
    host = vault.get_secret("minio", "host")
    protocol = vault.get_secret("minio", "protocol")
    port = vault.get_secret("minio", "httpport")
    access_key = vault.get_secret("minio", "user")
    secret_key = vault.get_secret("minio", "password")
    bucket = vault.get_secret("minio", "bucket")
    return MinioClient(
        protocol=protocol,
        host_with_override=host_with_override,
        host=host,
        port=port,
        access_key=access_key,
        secret_key=secret_key,
        bucket=bucket
    )