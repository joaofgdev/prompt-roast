"""Estado local, separado por agente, projeto e sessão."""
import hashlib
import json
import os
from pathlib import Path
import uuid

AGENTS = ("claude", "codex", "cursor", "gemini", "antigravity")


def state_root():
    override = os.environ.get("PROMPT_ROAST_STATE_DIR")
    base = Path(override) if override else Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local/state")) / "prompt-roast"
    return base.expanduser().absolute()


def identity(agent, project, session):
    if agent not in AGENTS:
        raise ValueError("agente desconhecido")
    if not session or len(session) > 256:
        raise ValueError("identificador de sessão inválido")
    project_hash = hashlib.sha256(str(Path(project).expanduser().resolve()).encode()).hexdigest()
    session_hash = hashlib.sha256(session.encode()).hexdigest()
    key = hashlib.sha256(f"{agent}\0{project_hash}\0{session_hash}".encode()).hexdigest()
    return project_hash, session_hash, key


def path_for(agent, project, session):
    return state_root() / (identity(agent, project, session)[2] + ".json")


def check_state_path(path):
    for part in (path, *path.parents):
        if part.is_symlink():
            raise ValueError(f"estado em link simbólico não é permitido: {part}")


def new_session(agent, project):
    session = str(uuid.uuid4())
    project_hash, session_hash, _ = identity(agent, project, session)
    root = state_root()
    check_state_path(root)
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    check_state_path(root)
    path = path_for(agent, project, session)
    data = {"schema_version": 1, "agent": agent, "project": project_hash,
            "session": session_hash, "tone": "normal", "scores": []}
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as out:
        json.dump(data, out, ensure_ascii=False, indent=2)
    return {"session": session, "state_dir": str(root)}


def lock_session_file(lock):
    import sys
    if sys.platform == "win32":
        import msvcrt
        lock.seek(0)
        msvcrt.locking(lock.fileno(), msvcrt.LK_LOCK, 1)
    else:
        import fcntl
        fcntl.flock(lock, fcntl.LOCK_EX)


def change_session(agent, project, session, operation):
    import tempfile

    path = path_for(agent, project, session)
    root = state_root()
    check_state_path(path)
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    lock_path = path.with_suffix(".lock")
    flags = os.O_RDWR | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(lock_path, flags, 0o600)
    with os.fdopen(fd, "r+") as lock:
        lock_session_file(lock)
        try:
            with path.open(encoding="utf-8") as file:
                data = json.load(file)
        except json.JSONDecodeError as exc:
            raise ValueError("histórico inválido; arquivo preservado") from exc
        if (not isinstance(data, dict) or data.get("schema_version") != 1
                or data.get("agent") != agent or data.get("tone") not in ("normal", "savage")
                or not isinstance(data.get("scores"), list)
                or not all(isinstance(entry, dict) for entry in data["scores"])):
            raise ValueError("histórico inválido ou versão desconhecida; arquivo preservado")
        result, changed = operation(data)
        if changed:
            temp_name = None
            try:
                with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=root, delete=False) as temp:
                    temp_name = temp.name
                    json.dump(data, temp, ensure_ascii=False, indent=2)
                    temp.flush()
                    os.fsync(temp.fileno())
                os.replace(temp_name, path)
            finally:
                if temp_name and os.path.exists(temp_name):
                    os.unlink(temp_name)
        return result


def record(agent, project, session, event_id, assessment):
    from datetime import datetime, timezone
    if not event_id or len(event_id) > 256:
        raise ValueError("identificador de evento inválido")
    from .scoring import evaluate
    result = evaluate(assessment["type"], *assessment["pillar_scores"], assessment["pattern"], assessment["butler_mode"])

    def add(data):
        for old in data["scores"]:
            if old.get("event_id") == event_id:
                if old.get("assessment") != result:
                    raise ValueError("identificador de evento já usado com outra avaliação")
                return old, False
        entry = {"event_id": event_id, "timestamp": datetime.now(timezone.utc).isoformat(), "assessment": result}
        data["scores"].append(entry)
        return entry, True
    return change_session(agent, project, session, add)


def statistics(agent, project, session):
    def read(data):
        values = [entry["assessment"]["score"] for entry in data["scores"]]
        recent = values[-5:]
        trend = None
        if len(values) >= 3:
            trend = "improving" if recent[-1] > recent[0] else "declining" if recent[-1] < recent[0] else "stable"
        return {"count": len(values), "average": round(sum(values) / len(values), 1) if values else None,
                "recent": recent, "trend": trend, "tone": data["tone"]}, False
    return change_session(agent, project, session, read)


def reset(agent, project, session):
    def clear(data):
        data["scores"] = []
        return {"reset": True, "tone": data["tone"]}, True
    return change_session(agent, project, session, clear)


def savage(agent, project, session, enabled):
    def set_tone(data):
        data["tone"] = "savage" if enabled else "normal"
        return {"tone": data["tone"]}, True
    return change_session(agent, project, session, set_tone)
