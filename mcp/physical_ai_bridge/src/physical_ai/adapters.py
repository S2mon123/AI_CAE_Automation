from __future__ import annotations

import base64
import ipaddress
import json
import os
import subprocess
import urllib.request
from pathlib import Path
from urllib.parse import urlsplit

from physical_ai.protocol import MAX_BYTES, decode, encode, request


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError("BRIDGE_REDIRECT_FORBIDDEN")


class BridgeReader:
    def __init__(self, config: dict):
        self.config = config
        parsed = urlsplit(config["url"])
        address = ipaddress.ip_address(parsed.hostname or "")
        private = any(
            address in network
            for network in (
                ipaddress.ip_network("10.0.0.0/8"),
                ipaddress.ip_network("172.16.0.0/12"),
                ipaddress.ip_network("192.168.0.0/16"),
                ipaddress.ip_network("127.0.0.0/8"),
            )
        )
        if parsed.scheme != "http" or not private or parsed.path != "/rpc" or parsed.query or parsed.fragment:
            raise ValueError("BRIDGE_REQUIRES_EXPLICIT_PRIVATE_IPV4_RPC_URL")
        if parsed.username or parsed.password or not parsed.port:
            raise ValueError("BRIDGE_URL_INVALID")
        for field in ("bridge_id", "ams_net_id", "ads_port", "key_file"):
            if not config.get(field):
                raise ValueError("BRIDGE_TARGET_NOT_CONFIGURED:" + field)
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())

    def call(self, operation: str, parameters: dict | None = None) -> dict:
        payload = request(operation, parameters or {})
        key = base64.b64decode(Path(self.config["key_file"]).read_text().strip(), validate=True)
        req = urllib.request.Request(
            self.config["url"],
            data=encode(payload, key, "request"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        # Exactly one attempt. No redirects, proxy inheritance, or speculative fallback backend.
        with self.opener.open(req, timeout=5) as response:
            raw = response.read(MAX_BYTES + 1)
        result = decode(raw, key, "response")
        if any(result.get(field) != payload[field] for field in ("request_id", "nonce")):
            raise ValueError("RESPONSE_REQUEST_MISMATCH")
        expected = {field: self.config[field] for field in ("bridge_id", "ams_net_id", "ads_port")}
        if result.get("target") != expected:
            raise ValueError("BRIDGE_TARGET_IDENTITY_MISMATCH")
        return result


class AbbReader:
    def __init__(self, config: dict):
        self.config = config

    def call(self, operation: str, signal: str | None = None) -> dict:
        if operation not in ("status", "inventory", "io"):
            raise ValueError("ABB_READ_OPERATION_REQUIRED")
        executable = Path(self.config["proxy_executable"])
        config_file = Path(self.config["proxy_config"])
        if not executable.is_absolute() or not config_file.is_absolute():
            raise ValueError("EXPLICIT_ABSOLUTE_PROXY_PATHS_REQUIRED")
        command = [str(executable), str(config_file), operation]
        if operation == "io":
            if not signal or len(signal) > 80 or not all(c.isalnum() or c == "_" for c in signal):
                raise ValueError("EXPLICIT_SIGNAL_NAME_REQUIRED")
            command.append(signal)
        result = subprocess.run(
            command,
            capture_output=True,
            timeout=20,
            shell=False,
            encoding="utf-8",
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        if len(result.stdout) > MAX_BYTES:
            raise ValueError("ABB_RESPONSE_TOO_LARGE")
        if result.returncode != 0:
            # Do not propagate arbitrary SDK exception strings, usernames or credentials.
            raise ValueError("ABB_PROXY_READ_FAILED")
        response = json.loads(result.stdout)
        if response.get("controller_identity") != self.config["controller_identity"]:
            raise ValueError("ABB_CONTROLLER_IDENTITY_MISMATCH")
        if response.get("source") not in ("ABB_LIVE", "ROBOTSTUDIO_VC"):
            raise ValueError("ABB_INVALID_SOURCE")
        return response
