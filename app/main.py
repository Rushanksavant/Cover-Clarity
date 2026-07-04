import os
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, FileResponse
from fastapi.staticfiles import StaticFiles
from jose import jwt, JWTError
import bcrypt
# from passlib.context import CryptContext
from pydantic import BaseModel
from dotenv import load_dotenv

from db_utils import (
    db_create_user, db_get_user, db_save_medical_history, db_get_medical_history,
    db_create_session, db_get_user_sessions, db_session_belongs_to_user,
)
from cognee_utils import (
    is_session_valid, chat, get_chat_history,
    history_to_markdown, history_to_pdf_bytes,
)

load_dotenv()

# ── App setup ────────────────────────────────────────────────────────────────

app = FastAPI(title="GraphRAG Chat API")

app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# pwd = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)

JWT_SECRET = os.environ["JWT_SECRET"]          # any random string in .env
JWT_ALGO = "HS256"
JWT_EXPIRE_HOURS = 24


# ── Auth helpers ─────────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password[:72].encode(), bcrypt.gensalt()).decode()

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain[:72].encode(), hashed.encode())

def make_token(user_id: str, username: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRE_HOURS)
    return jwt.encode(
        {"sub": user_id, "username": username, "exp": expire},
        JWT_SECRET, algorithm=JWT_ALGO,
    )


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


def current_user(authorization: str = None) -> dict:
    """FastAPI dependency — extracts user from Authorization header."""
    from fastapi import Header
    raise HTTPException(status_code=401, detail="Use get_current_user dependency")


from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

bearer = HTTPBearer()

def get_current_user(creds: HTTPAuthorizationCredentials = Depends(bearer)) -> dict:
    return decode_token(creds.credentials)


# ── Schemas ──────────────────────────────────────────────────────────────────

class AuthRequest(BaseModel):
    username: str
    password: str

class NewSessionRequest(BaseModel):
    label: str = ""

class ChatRequest(BaseModel):
    query: str


# ── Auth routes ──────────────────────────────────────────────────────────────

@app.post("/auth/signup")
async def signup(req: AuthRequest):
    if db_get_user(req.username):
        raise HTTPException(status_code=400, detail="Username already taken")

    user = db_create_user(req.username, hash_password(req.password))

    # Create a default session on sign-up
    session_id = f"{req.username}_default"
    db_create_session(user["id"], session_id, label="Default Session")

    token = make_token(user["id"], user["username"])
    return {"token": token, "default_session_id": session_id}


@app.post("/auth/login")
async def login(req: AuthRequest):
    user = db_get_user(req.username)
    if not user or not verify_password(req.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = make_token(user["id"], user["username"])

    # Return their sessions so frontend can restore state
    sessions = db_get_user_sessions(user["id"])
    return {"token": token, "sessions": sessions}


# ── Session routes ────────────────────────────────────────────────────────────

@app.get("/sessions")
async def list_sessions(user: dict = Depends(get_current_user)):
    return db_get_user_sessions(user["sub"])


@app.post("/sessions")
async def create_session(req: NewSessionRequest, user: dict = Depends(get_current_user)):
    session_id = f"{user['username']}_{uuid.uuid4().hex[:8]}"
    label = req.label or f"Session {datetime.now().strftime('%b %d %H:%M')}"
    record = db_create_session(user["sub"], session_id, label)
    return {"session_id": session_id, "label": label, "created_at": record["created_at"]}


@app.get("/sessions/{session_id}/valid")
async def check_session(session_id: str, user: dict = Depends(get_current_user)):
    if not db_session_belongs_to_user(user["sub"], session_id):
        raise HTTPException(status_code=403, detail="Session not found or expired in DB")
    valid = await is_session_valid(session_id)
    return {"valid": valid}


# ── Chat routes ───────────────────────────────────────────────────────────────

@app.post("/sessions/{session_id}/chat")
async def chat_endpoint(session_id: str, req: ChatRequest, user: dict = Depends(get_current_user)):
    if not db_session_belongs_to_user(user["sub"], session_id):
        raise HTTPException(status_code=403, detail="Session not found or expired")
    medical_history = db_get_medical_history(session_id)
    result = await chat(session_id, req.query, medical_history)
    return result  # {"answer": ..., "trace_ids": [...]}


@app.get("/sessions/{session_id}/history")
async def history_endpoint(session_id: str, user: dict = Depends(get_current_user)):
    if not db_session_belongs_to_user(user["sub"], session_id):
        raise HTTPException(status_code=403, detail="Session not found or expired")
    return await get_chat_history(session_id)


# ── Export route ─────────────────────────────────────────────────────────────

@app.get("/sessions/{session_id}/export/pdf")
async def export_pdf(session_id: str, user: dict = Depends(get_current_user)):
    if not db_session_belongs_to_user(user["sub"], session_id):
        raise HTTPException(status_code=403, detail="Forbidden")
    history = await get_chat_history(session_id)
    pdf_bytes = history_to_pdf_bytes(session_id, history, username=user["username"])
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={session_id}.pdf"},
    )



# ── Medical record routes ─────────────────────────────────────────────────────

@app.post("/sessions/{session_id}/medical-history")
async def save_medical_history(session_id: str, data: dict, user: dict = Depends(get_current_user)):
    if not db_session_belongs_to_user(user["sub"], session_id):
        raise HTTPException(status_code=403, detail="Forbidden")
    return db_save_medical_history(session_id, data)

@app.get("/sessions/{session_id}/medical-history")
async def get_medical_history(session_id: str, user: dict = Depends(get_current_user)):
    if not db_session_belongs_to_user(user["sub"], session_id):
        raise HTTPException(status_code=403, detail="Forbidden")
    return db_get_medical_history(session_id) or {}


# ── Serve frontend ────────────────────────────────────────────────────────────

@app.get("/")
async def serve_frontend():
    return FileResponse("./static/index.html")

@app.get("/health")
async def health():
    return {"status": "ok"}
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)