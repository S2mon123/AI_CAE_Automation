from __future__ import annotations

import asyncio
import os
import sys

from fastmcp import Client


async def run() -> None:
    config = {
        "mcpServers": {
            "robotstudio": {
                "transport": "stdio",
                "command": sys.executable,
                "args": ["-m", "robotstudio_mcp"],
                "env": dict(os.environ),
            }
        }
    }
    async with Client(config) as client:
        tools = await client.list_tools()
        resources = await client.list_resources()
        prompts = await client.list_prompts()
        if len(tools) < 20 or len(resources) < 8 or len(prompts) < 4:
            raise RuntimeError(
                f"Unexpected MCP surface: tools={len(tools)}, resources={len(resources)}, prompts={len(prompts)}"
            )
        print(f"stdio MCP OK: tools={len(tools)}, resources={len(resources)}, prompts={len(prompts)}")


if __name__ == "__main__":
    asyncio.run(run())
