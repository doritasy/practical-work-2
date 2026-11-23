"""SQLite storage for sessions, instructions and responses."""

import os
import time
from typing import Any

from pony.orm import Database, PrimaryKey, Required, Optional, db_session

db = Database()
REPORT_WINDOW_MINUTES = 6


class Session(db.Entity):
    """Session entity."""

    uid = PrimaryKey(int)
    created = Required(int)


class Instruction(db.Entity):
    """Instruction entity."""

    uid = PrimaryKey(int)
    created = Required(int)
    payload = Optional(str)
    session = Required(int)
    description = Optional(str)
    tags = Optional(str)


class Response(db.Entity):
    """Response entity."""

    uid = PrimaryKey(int)
    created = Required(int)
    output = Optional(str)
    stage = Optional(str)
    error = Optional(str)
    instruction = Required(int)
    cache_hit = Required(int)
    duration = Required(int)


def init_db() -> None:
    """Initialize the database."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, "database.sqlite")
    print(f"Creating database at: {db_path}")
    db.bind(provider="sqlite", filename=db_path, create_db=True)
    db.generate_mapping(create_tables=True)


@db_session
def add_session(uid: int, data: dict[str, Any]) -> dict[str, Any]:
    """Add a session record."""
    existing = Session.get(uid=uid)
    if existing:
        return {"uid": existing.uid, "created": existing.created}
    obj = Session(uid=uid, created=data.get("created", int(time.time())))
    return {"uid": obj.uid, "created": obj.created}


@db_session
def pop_session(uid: int) -> bool:
    """Remove a session by uid."""
    obj = Session.get(uid=uid)
    if obj:
        obj.delete()
        return True
    return False


@db_session
def get_sessions() -> list[dict[str, Any]]:
    """Return all sessions."""
    return [{"uid": s.uid, "created": s.created} for s in Session.select()]


@db_session
def update_session(uid: int, data: dict[str, Any]) -> dict[str, Any] | None:
    """Update session data."""
    obj = Session.get(uid=uid)
    if obj:
        if "created" in data:
            obj.created = data["created"]
        return {"uid": obj.uid, "created": obj.created}
    return None


@db_session
def add_instruction(uid: int, data: dict[str, Any]) -> dict[str, Any]:
    """Add an instruction record."""
    existing = Instruction.get(uid=uid)
    if existing:
        return {
            "uid": existing.uid,
            "created": existing.created,
            "payload": existing.payload or "",
            "session": existing.session,
            "description": existing.description or "",
            "tags": existing.tags or "",
        }
    obj = Instruction(
        uid=uid,
        created=data.get("created", int(time.time())),
        payload=data.get("payload", ""),
        session=data.get("session", 0),
        description=data.get("description", ""),
        tags=data.get("tags", ""),
    )
    return {
        "uid": obj.uid,
        "created": obj.created,
        "payload": obj.payload or "",
        "session": obj.session,
        "description": obj.description or "",
        "tags": obj.tags or "",
    }


@db_session
def pop_instruction(uid: int) -> bool:
    """Remove an instruction by uid."""
    obj = Instruction.get(uid=uid)
    if obj:
        obj.delete()
        return True
    return False


@db_session
def get_instructions(session_id: int) -> list[dict[str, Any]]:
    """Get instructions belonging to a session."""
    return [
        {
            "uid": i.uid,
            "created": i.created,
            "payload": i.payload or "",
            "session": i.session,
            "description": i.description or "",
            "tags": i.tags or "",
        }
        for i in Instruction.select(lambda x: x.session == session_id)
    ]


@db_session
def update_instruction(
    uid: int, data: dict[str, Any]
) -> dict[str, Any] | None:
    """Update instruction data."""
    obj = Instruction.get(uid=uid)
    if obj:
        for key, value in data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return {
            "uid": obj.uid,
            "created": obj.created,
            "payload": obj.payload or "",
            "session": obj.session,
            "description": obj.description or "",
            "tags": obj.tags or "",
        }
    return None


@db_session
def add_response(uid: int, data: dict[str, Any]) -> dict[str, Any]:
    """Add a response record."""
    existing = Response.get(uid=uid)
    if existing:
        return {
            "uid": existing.uid,
            "created": existing.created,
            "output": existing.output or "",
            "stage": existing.stage or "",
            "error": existing.error or "",
            "instruction": existing.instruction,
            "cache_hit": existing.cache_hit,
            "duration": existing.duration,
        }
    obj = Response(
        uid=uid,
        created=data.get("created", int(time.time())),
        output=data.get("output", ""),
        stage=data.get("stage", ""),
        error=data.get("error", ""),
        instruction=data.get("instruction", 0),
        cache_hit=data.get("cache_hit", 0),
        duration=data.get("duration", 0),
    )
    return {
        "uid": obj.uid,
        "created": obj.created,
        "output": obj.output or "",
        "stage": obj.stage or "",
        "error": obj.error or "",
        "instruction": obj.instruction,
        "cache_hit": obj.cache_hit,
        "duration": obj.duration,
    }


@db_session
def get_responses(instruction_id: int) -> list[dict[str, Any]]:
    """Get responses for an instruction."""
    return [
        {
            "uid": r.uid,
            "created": r.created,
            "output": r.output or "",
            "stage": r.stage or "",
            "error": r.error or "",
            "instruction": r.instruction,
            "cache_hit": r.cache_hit,
            "duration": r.duration,
        }
        for r in Response.select(lambda x: x.instruction == instruction_id)
    ]


@db_session
def get_report() -> list[dict[str, Any]]:
    """Get report of recent responses."""
    now = int(time.time())
    threshold = now - REPORT_WINDOW_MINUTES * 60
    result = []
    for resp in Response.select(lambda r: r.created > threshold):
        instr = Instruction.get(uid=resp.instruction)
        if instr:
            result.append({"description": instr.description or ""})
    return result
