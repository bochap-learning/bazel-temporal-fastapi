from typing import Optional
import os
from dataclasses import dataclass

@dataclass
class EnvConfig:
    vault_host: str
    vault_port: str
    vault_token: str
    vault_path: str
    localhost_override: Optional[str]
    vault_max_retries: int
    vault_retry_interval: int

"""
returns an EnvConfig that populates vault_host (overriden to localhost if IS_LOCAL is set to true), vault_port, vault_token, vault_path, localhost_override (set to "localhost" if IS_LOCAL is set to true else None") from environment variables, 
"""
def get_env_config() -> EnvConfig:
    return EnvConfig(
        vault_host="localhost" if os.getenv("IS_LOCAL", "0") == "1" else os.getenv("VAULT_HOST"),
        vault_port=os.getenv("VAULT_PORT"),
        vault_token=os.getenv("VAULT_TOKEN"),
        vault_path=os.getenv("VAULT_PATH"),
        localhost_override = "localhost" if os.getenv("IS_LOCAL", "0") == "1" else None,
        vault_max_retries = 10,
        vault_retry_interval = 5
    )