"""Inspect disk XML and stage a proposal. Never invoke COM or activate a target."""

from __future__ import annotations

import hashlib
import xml.etree.ElementTree as ET


def inspect_tsm(data: bytes) -> dict:
    if len(data) > 8_388_608:
        raise ValueError("FILE_TOO_LARGE")
    # Decode before filtering so UTF-16 cannot bypass the DTD restriction.
    text = data.decode("utf-16") if data.startswith((b"\xff\xfe", b"\xfe\xff")) else data.decode("utf-8-sig")
    if "<!DOCTYPE" in text.upper() or "<!ENTITY" in text.upper():
        raise ValueError("XML_DTD_FORBIDDEN")
    root = ET.fromstring(text)
    records = []
    nodes = 0

    def walk(node: ET.Element, owners: tuple[str, ...]):
        nonlocal nodes
        nodes += 1
        if nodes > 50000 or len(owners) > 100:
            raise ValueError("XML_LIMIT_EXCEEDED")
        tag = node.tag.split("}")[-1]
        context = owners + (tag + (":" + node.attrib["Name"] if "Name" in node.attrib else ""),)
        if "link" in tag.lower() or "mapping" in tag.lower():
            records.append({"element": tag, "attributes": dict(node.attrib), "context": list(owners)})
        for child in node:
            walk(child, context)

    walk(root, ())
    return {
        "source": "FILE_CONFIGURATION",
        "source_sha256": hashlib.sha256(data).hexdigest(),
        "root_element": root.tag,
        "mapping_records": records,
        "nodes": nodes,
        "runtime_consistency": "UNKNOWN",
        "free_bits": "UNKNOWN",
        "note": "Raw mapping records only; missing records never imply a free bit or active Runtime match.",
    }


def link_proposal(data: bytes, from_path: str, to_path: str, bit_count: int) -> dict:
    if not from_path.strip() or not to_path.strip() or from_path == to_path:
        raise ValueError("TWO_DISTINCT_EXPLICIT_PATHS_REQUIRED")
    if type(bit_count) is not int or not 1 <= bit_count <= 32:
        raise ValueError("INVALID_BIT_COUNT")
    inspected = inspect_tsm(data)
    return {
        "source": "LOCAL_PROPOSAL",
        "base_sha256": inspected["source_sha256"],
        "operation": "LinkVariables",
        "from_path": from_path,
        "to_path": to_path,
        "bit_count": bit_count,
        "status": "DRAFT",
        "applied_to_copy": False,
        "activation_authorized": False,
        "blockers": [
            "DUAL_END_OCCUPANCY_UNKNOWN",
            "BYTE_AND_ARRAY_OVERLAPS_UNCHECKED",
            "ABB_GROUP_SIGNALS_UNCHECKED",
            "TC2_COM_STAGE_NOT_IMPLEMENTED",
        ],
        "diff": {
            "before": inspected["mapping_records"],
            "proposed_addition": {"from": from_path, "to": to_path, "bits": bit_count},
        },
    }
