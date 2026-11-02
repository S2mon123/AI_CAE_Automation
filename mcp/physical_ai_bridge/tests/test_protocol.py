import base64
import json
import os
import subprocess

import pytest

from physical_ai.adapters import BridgeReader
from physical_ai.protocol import ReplayWindow, decode, encode, request

KEY = b"test-only-never-install-this-key!" * 2


def test_signatures_replay_and_direction():
    payload = request("plc.state", {})
    wire = encode(payload, KEY, "request")
    assert decode(wire, KEY, "request") == payload
    with pytest.raises(ValueError):
        decode(wire, KEY, "response")
    with pytest.raises(ValueError):
        decode(wire, b"x" * 32, "request")
    with pytest.raises(ValueError):
        decode(wire, KEY, "request", now=payload["issued_at"] + 31)
    envelope = json.loads(wire)
    envelope["payload_b64"] = base64.b64encode(b"{}").decode()
    with pytest.raises(ValueError):
        decode(json.dumps(envelope).encode(), KEY, "request")
    replay = ReplayWindow()
    replay.consume(payload, payload["issued_at"])
    with pytest.raises(ValueError, match="REPLAY"):
        replay.consume(payload, payload["issued_at"])


def test_replay_future_skew_retained():
    window = ReplayWindow(capacity=1)
    first = request("plc.state", {})
    first["issued_at"] = 120
    window.consume(first, 100)
    with pytest.raises(ValueError, match="REPLAY"):
        window.consume(first, 145)


@pytest.mark.parametrize("operation", ["plc.write_bool", "plc.toggle", "plc.force", "task_execute", "start", "stop"])
@pytest.mark.parametrize("value", [True, False])
def test_all_write_semantics_absent(operation, value):
    with pytest.raises(ValueError, match="WRITE_OPERATION"):
        request(operation, {"alias": "start", "value": value})


@pytest.mark.parametrize(
    "url",
    [
        "http://example.com:8766/rpc",
        "http://8.8.8.8:8766/rpc",
        "http://192.168.1.1:8766/anything",
        "http://u:p@192.168.1.1:8766/rpc",
        "http://127.0.0.1:8766/rpc?write=1",
    ],
)
def test_bridge_endpoint_scope(url):
    with pytest.raises(ValueError):
        BridgeReader({"url": url})


def test_csharp_wire_contract(tmp_path):
    executable = os.environ.get("PHYSICAL_AI_BRIDGE_TEST_EXE")
    if not executable:
        pytest.skip("Set PHYSICAL_AI_BRIDGE_TEST_EXE to locally compiled x86 bridge for interop test")
    key = tmp_path / "test.key"
    key.write_text(base64.b64encode(KEY).decode())
    payload = request("system.capabilities", {})
    wire = tmp_path / "request.json"
    wire.write_bytes(encode(payload, KEY, "request"))
    result = subprocess.run([executable, "--protocol-test", str(key), str(wire), "interop"], capture_output=True)
    assert result.returncode == 0, result.stderr
    response = decode(result.stdout, KEY, "response")
    assert response["request_id"] == payload["request_id"] and response["nonce"] == payload["nonce"]
    assert response["source"] == "TEST_DOUBLE"
    wire.write_bytes(encode(payload, b"x" * 32, "request"))
    assert (
        subprocess.run([executable, "--protocol-test", str(key), str(wire), "interop"], capture_output=True).returncode
        != 0
    )


@pytest.mark.parametrize("fault", ["target", "nonce", "signature", "timeout"])
def test_client_rejects_wrong_response_without_retry(tmp_path, fault):
    key_file = tmp_path / "test.key"
    key_file.write_text(base64.b64encode(KEY).decode())
    target = {"bridge_id": "test", "ams_net_id": "1.2.3.4.5.6", "ads_port": 801}
    reader = BridgeReader({**target, "url": "http://127.0.0.1:8766/rpc", "key_file": str(key_file)})

    class Response:
        def __init__(self, body):
            self.body = body

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def read(self, limit):
            return self.body[:limit]

    class Transport:
        calls = 0

        def open(self, req, timeout):
            self.calls += 1
            if fault == "timeout":
                raise TimeoutError("fixture")
            incoming = decode(req.data, KEY, "request")
            response = {**incoming, "target": target.copy(), "ok": True}
            if fault == "target":
                response["target"]["ams_net_id"] = "6.5.4.3.2.1"
            if fault == "nonce":
                response["nonce"] = "0" * 32
            return Response(encode(response, b"x" * 32 if fault == "signature" else KEY, "response"))

    transport = Transport()
    reader.opener = transport
    with pytest.raises((ValueError, TimeoutError)):
        reader.call("plc.state")
    assert transport.calls == 1
