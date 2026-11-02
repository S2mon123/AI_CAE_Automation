"""New v4 signed read-only RPC. Not wire-compatible with the retired v0.2 package."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
import uuid

PROTOCOL = "physical-ai/4.0"
MAX_BYTES = 1_048_576
READ_OPERATIONS = frozenset(("system.capabilities", "plc.state", "plc.read_bool"))


def encode(payload: dict, key: bytes, direction: str) -> bytes:
    if len(key) < 32 or direction not in ("request", "response"):
        raise ValueError("INVALID_PROTOCOL_KEY_OR_DIRECTION")
    content = base64.b64encode(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).decode("ascii")
    signature = hmac.new(key, f"{PROTOCOL}\n{direction}\n{content}".encode(), hashlib.sha256).hexdigest()
    return json.dumps({"protocol": PROTOCOL, "payload_b64": content, "signature": signature}).encode()


def decode(raw: bytes, key: bytes, direction: str, now: float | None = None) -> dict:
    if len(raw) > MAX_BYTES or len(key) < 32 or direction not in ("request", "response"):
        raise ValueError("INVALID_ENVELOPE")
    envelope = json.loads(raw)
    if set(envelope) != {"protocol", "payload_b64", "signature"} or envelope["protocol"] != PROTOCOL:
        raise ValueError("PROTOCOL_MISMATCH")
    content = envelope["payload_b64"]
    expected = hmac.new(key, f"{PROTOCOL}\n{direction}\n{content}".encode(), hashlib.sha256).hexdigest()
    if not isinstance(envelope["signature"], str) or not hmac.compare_digest(expected, envelope["signature"]):
        raise ValueError("BAD_SIGNATURE")
    payload = json.loads(base64.b64decode(content, validate=True))
    issued = payload.get("issued_at")
    if type(issued) is not int or abs((time.time() if now is None else now) - issued) > 30:
        raise ValueError("EXPIRED_SIGNATURE")
    for field in ("request_id", "nonce"):
        value = payload.get(field)
        if not isinstance(value, str) or len(value) != 32 or any(c not in "0123456789abcdef" for c in value):
            raise ValueError("INVALID_REQUEST_BINDING")
    return payload


class ReplayWindow:
    def __init__(self, capacity: int = 4096):
        self.seen: dict[str, float] = {}
        self.capacity = capacity

    def consume(self, payload: dict, now: float):
        self.seen = {key: expiry for key, expiry in self.seen.items() if expiry >= now}
        nonce = payload["nonce"]
        if nonce in self.seen:
            raise ValueError("REPLAY_REJECTED")
        if len(self.seen) >= self.capacity:
            raise ValueError("REPLAY_WINDOW_FULL")
        # Retain future-skewed requests for their complete acceptance interval.
        self.seen[nonce] = payload["issued_at"] + 30


def request(operation: str, parameters: dict) -> dict:
    if operation not in READ_OPERATIONS:
        raise ValueError("WRITE_OPERATION_NOT_EXPOSED")
    return {
        "request_id": uuid.uuid4().hex,
        "nonce": uuid.uuid4().hex,
        "issued_at": int(time.time()),
        "operation": operation,
        "parameters": parameters,
    }
