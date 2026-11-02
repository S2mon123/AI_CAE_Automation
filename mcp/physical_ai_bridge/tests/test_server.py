import asyncio
import json
import os
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def test_real_stdio_process(tmp_path):
    async def run():
        env = dict(
            os.environ, PHYSICAL_AI_WORKSPACE=str(tmp_path), PYTHONPATH=str(Path(__file__).resolve().parents[1] / "src")
        )
        env.pop("PHYSICAL_AI_CONFIG", None)
        parameters = StdioServerParameters(command=sys.executable, args=["-m", "physical_ai.server"], env=env)
        async with stdio_client(parameters) as (read, write):
            async with ClientSession(read, write) as client:
                await client.initialize()
                tools = await client.list_tools()
                names = {tool.name for tool in tools.tools}
                assert len(names) == 15
                assert not {"plc_commit_write", "task_execute", "task_commit_deploy", "task_resume"} & names
                result = await client.call_tool("system_get_status", {})
                value = json.loads(result.content[0].text)
                assert value["code"] == "BRIDGE_NOT_CONFIGURED"
                stop = await client.call_tool("robot_request_process_stop", {})
                assert json.loads(stop.content[0].text)["standstill_observed"] is False
                export = await client.call_tool("report_export", {})
                path = json.loads(export.content[0].text)["path"]
                assert Path(path).is_file()
                context = {
                    "controller_identity": "STDIO_TEST_FIXTURE",
                    **{
                        key: "a" * 64
                        for key in (
                            "robotware_and_options_hash",
                            "profile_hash",
                            "station_hash",
                            "configuration_hash",
                            "tool_load_wobj_hash",
                            "dependencies_hash",
                        )
                    },
                    "tool": "tool0",
                    "wobj": "wobj0",
                    "anchor": {
                        "translation_mm": [400.0, 100.0, 500.0],
                        "quaternion": [1.0, 0.0, 0.0, 0.0],
                        "configuration": [0, 0, 0, 0],
                        "external_axes": [9e9] * 6,
                    },
                }
                created = await client.call_tool("task_create", {"spec": {"mode": "C", "context": context}})
                task_id = json.loads(created.content[0].text)["task_id"]
                rendered = await client.call_tool("task_render", {"task_id": task_id})
                assert json.loads(rendered.content[0].text)["state"] == "LOCAL_DRAFT"
                validated = await client.call_tool("task_validate", {"task_id": task_id})
                assert json.loads(validated.content[0].text)["status"] == "INCOMPLETE"
                prepared = await client.call_tool("task_prepare_execute", {"task_id": task_id})
                assert json.loads(prepared.content[0].text)["state"] == "BLOCKED"

    asyncio.run(run())
