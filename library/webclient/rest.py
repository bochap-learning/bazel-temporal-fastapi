from typing import Any, Dict
import certifi
import ssl
from aiohttp import ClientSession, TCPConnector

async def get_to_json(url: str) -> Dict[str, Any]:
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    async with ClientSession(connector=TCPConnector(ssl=ssl_context)) as session:
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.json()