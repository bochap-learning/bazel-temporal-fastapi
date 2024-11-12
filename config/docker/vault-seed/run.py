import asyncio
from dotenv import dotenv_values
import hvac
import http.server
import socketserver

class HealthCheckHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"OK")

async def seed_vault(max_retries=10, retry_interval=5):
    """Waits for Vault to be running and unsealed."""
    env_vars = dotenv_values(".env")
    vault_host = f"http://{env_vars.get("VAULT_HOST")}:{env_vars.get("VAULT_PORT")}"
    vault_token = env_vars.get("VAULT_TOKEN")
    vault_path = env_vars.get("VAULT_PATH")

    client = hvac.Client(url=vault_host, token=vault_token)
    for _ in range(max_retries):
        await asyncio.sleep(retry_interval)
        try:
            if client.sys.is_initialized() and client.sys.is_sealed():
                print("Vault is sealed, waiting for unseal...")
            elif client.sys.is_initialized() and not client.sys.is_sealed():
                print("Vault is running and unsealed!")
                secrets = {}
                for key, value in env_vars.items():
                    secret_path, secret_key = key.lower().split("_")
                    if secret_path == "vault": continue
                    if secret_path not in secrets:
                        secrets[secret_path] = {}
                    secrets[secret_path][secret_key] = value

                tasks = [
                    asyncio.create_task(write_secret(client, f"{vault_path}/{path}", value)) for path, value in secrets.items()
                ]
                responses = await asyncio.gather(*tasks)
                return True
        except hvac.exceptions.VaultError as e:
            print(f"Error connecting to Vault: {e}")

    raise Exception("Vault did not become available within the timeout.")

async def write_secret(client, vault_path, secret):
    """Writes a secret to Vault."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, client.secrets.kv.v2.create_or_update_secret, vault_path, secret)

async def main() -> None:
    await seed_vault()
    HOST, PORT = "localhost", 8000
    server = socketserver.TCPServer((HOST, PORT), HealthCheckHandler)    
    # Start the server in a separate thread
    asyncio.create_task(asyncio.to_thread(server.serve_forever))
    print(f"Server started on {PORT}. Press Ctrl+C to stop.")
    await asyncio.Event().wait()  # Wait forever

if __name__ == "__main__":
    asyncio.run(main())