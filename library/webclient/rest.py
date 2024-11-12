from typing import Any, Dict
from aiohttp import ClientSession, TCPConnector

async def get_to_json(url: str) -> Dict[str, Any]:
    async with ClientSession(connector=TCPConnector(verify_ssl=False)) as session:
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.json()