import time
import hvac
from library.meta.metaclass import (
    Singleton
)
from library.meta.config import (
    EnvConfig
)

class Vault(metaclass=Singleton):
    def __init__(
        self, config: EnvConfig
    ) -> None:
        """Waits for Vault to be running and unsealed."""
        self.client = Vault.__get_client(config)
        self.root = config.vault_path

    def __get_client(config: EnvConfig) -> hvac.Client:
        vault_addr = f"http://{config.vault_host}:{config.vault_port}"
        client = hvac.Client(url=vault_addr, token=config.vault_token)
        for _ in range(config.vault_max_retries):
            try:
                if client.sys.is_initialized() and client.sys.is_sealed():
                    print("Vault is sealed, waiting for unseal...")
                elif client.sys.is_initialized() and not client.sys.is_sealed():
                    print("Vault is running and unsealed!")
                    return client
            except hvac.exceptions.VaultError as e:
                print(f"Error connecting to Vault: {e}")
            time.sleep(config.vault_retry_interval)
        raise Exception("Vault did not become available within the timeout.")

    def get_secret(self, path: str, key: str) -> str:
        read_response = self.client.secrets.kv.read_secret_version(path=f"{self.root}/{path}")
        return read_response["data"]["data"][key]


# if __name__ == "__main__":
#     vault = Vault(
#         VaultConfig(
#             vault_host="vault",
#             vault_port=8200,
#             vault_token="unsecure4convience",
#             vault_path="supersecretlocation",
#             vault_max_retries=10, 
#             vault_retry_interval=5,
#             is_local=True
#         )
#     )
#     print(vault.get_secret("minio", "bucket"))

            
        
