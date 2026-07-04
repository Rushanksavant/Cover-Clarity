import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

_client: Client = None

def get_db() -> Client:
    global _client
    if _client is None:
        _client = create_client(
            os.environ["SUPABASE_URL"],
            os.environ["SUPABASE_SERVICE_KEY"],
        )
    return _client


# ── Users ──────────────────────────────────────────────────────────────────

def db_create_user(username: str, password_hash: str) -> dict:
    res = get_db().table("users").insert({
        "username": username,
        "password_hash": password_hash,
    }).execute()
    return res.data[0]


def db_get_user(username: str) -> dict | None:
    res = get_db().table("users").select("*").eq("username", username).execute()
    return res.data[0] if res.data else None


# ── Sessions ────────────────────────────────────────────────────────────────

def db_create_session(user_id: str, session_id: str, label: str) -> dict:
    res = get_db().table("sessions").insert({
        "user_id": user_id,
        "session_id": session_id,
        "label": label,
    }).execute()
    return res.data[0]


def db_get_user_sessions(user_id: str) -> list[dict]:
    """Returns all non-expired sessions for a user, newest first."""
    res = (
        get_db().table("sessions")
        .select("*")
        .eq("user_id", user_id)
        .gt("expires_at", "now()")          # filter expired
        .order("created_at", desc=True)
        .execute()
    )
    return res.data


def db_session_belongs_to_user(user_id: str, session_id: str) -> bool:
    res = (
        get_db().table("sessions")
        .select("id")
        .eq("user_id", user_id)
        .eq("session_id", session_id)
        .gt("expires_at", "now()")
        .execute()
    )
    return len(res.data) > 0



# ── Medical History ─────────────────────────────────────────────────────────

def db_save_medical_history(session_id: str, data: dict) -> dict:
    res = get_db().table("medical_history").upsert({
        "session_id": session_id,
        "data": data,
    }).execute()
    return res.data[0]

def db_get_medical_history(session_id: str) -> dict | None:
    res = get_db().table("medical_history").select("*").eq("session_id", session_id).execute()
    return res.data[0]["data"] if res.data else None