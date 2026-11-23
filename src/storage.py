"""In-memory storage for sessions, instructions and responses."""

import time
from typing import Any

sessions: dict[int, dict[str, Any]] = {}
instructions: dict[int, dict[str, Any]] = {}
responses: dict[int, dict[str, Any]] = {}


def add_session(uid: int, data: dict[str, Any]) -> dict[str, Any]:
    """Add a session record."""
    sessions[uid] = {"uid": uid, "created": data.get("created", int(time.time()))}
    return sessions[uid]


def pop_session(uid: int) -> bool:
    """Remove a session by uid."""
    return sessions.pop(uid, None) is not None


def get_sessions() -> list[dict[str, Any]]:
    """Return all sessions."""
    return list(sessions.values())


def update_session(uid: int, data: dict[str, Any]) -> dict[str, Any] | None:
    """Update session data."""
    if uid not in sessions:
        return None
    sessions[uid].update(data)
    return sessions[uid]


def add_instruction(uid: int, data: dict[str, Any]) -> dict[str, Any]:
    """Add an instruction record."""
    record = {
        "uid": uid,
        "created": data.get("created", int(time.time())),
        "payload": data.get("payload", ""),
        "session": data.get("session", 0),
        "description": data.get("description", ""),
        "tags": data.get("tags", ""),
    }
    instructions[uid] = record
    return record


def pop_instruction(uid: int) -> bool:
    """Remove an instruction by uid."""
    return instructions.pop(uid, None) is not None


def get_instructions(session_id: int) -> list[dict[str, Any]]:
    """Get instructions belonging to a session."""
    return [
        i for i in instructions.values() if i["session"] == session_id
    ]


def update_instruction(uid: int, data: dict[str, Any]) -> dict[str, Any] | None:
    """Update instruction data."""
    if uid not in instructions:
        return None
    instructions[uid].update(data)
    return instructions[uid]


def add_response(uid: int, data: dict[str, Any]) -> dict[str, Any]:
    """Add a response record."""
    record = {
        "uid": uid,
        "created": data.get("created", int(time.time())),
        "output": data.get("output", ""),
        "stage": data.get("stage", ""),
        "error": data.get("error", ""),
        "instruction": data.get("instruction", 0),
        "cache_hit": data.get("cache_hit", 0),
        "duration": data.get("duration", 0),
    }
    responses[uid] = record
    return record


def get_responses(instruction_id: int) -> list[dict[str, Any]]:
    """Get responses for an instruction."""
    return [
        r for r in responses.values() if r["instruction"] == instruction_id
    ]


def get_report() -> list[dict[str, Any]]:
    """Get report of recent responses."""
    now = int(time.time())
    threshold = now - 6 * 60
    result = []
    for resp in responses.values():
        if resp.get("created", 0) > threshold:
            instr = instructions.get(resp.get("instruction"))
            if instr:
                result.append({"description": instr.get("description", "")})
    return result
