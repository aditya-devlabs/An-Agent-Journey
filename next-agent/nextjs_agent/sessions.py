import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from nextjs_agent.config import SESSIONS_DIR


def create_session() -> dict:
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    session = {
        "id": str(uuid.uuid4()),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "messages": [],
    }
    return session


def save_session(session: dict):
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    session["updated_at"] = datetime.now(timezone.utc).isoformat()
    path = SESSIONS_DIR / f"{session['id']}.json"
    path.write_text(json.dumps(session, indent=2))


def load_session(session_id: str) -> dict | None:
    path = SESSIONS_DIR / f"{session_id}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text())


def list_sessions() -> list[dict]:
    if not SESSIONS_DIR.exists():
        return []
    sessions = []
    for path in sorted(
        SESSIONS_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True
    ):
        session = json.loads(path.read_text())
        sessions.append(
            {
                "id": session["id"],
                "created_at": session.get("created_at", ""),
                "updated_at": session.get("updated_at", ""),
                "message_count": len(session.get("messages", [])),
            }
        )
    return sessions


def get_session_path(session_id: str) -> Path:
    return SESSIONS_DIR / f"{session_id}.json"


def session_exists(session_id: str) -> bool:
    return get_session_path(session_id).exists()


def get_latest_sessions(n: int = 5) -> list[dict]:
    return list_sessions()[:n]


def delete_session(session_id: str) -> bool:
    path = get_session_path(session_id)
    if not path.exists():
        return False
    path.unlink()
    return True
