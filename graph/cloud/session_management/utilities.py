import os
import httpx
os.environ["CACHING"] = "true"
os.environ["SELF_IMPROVEMENT"] = "false"

import cognee
from dotenv import load_dotenv

load_dotenv()

COGNEE_URL = os.getenv("COGNEE_SERVICE_URL")
COGNEE_API_KEY = os.getenv("COGNEE_API_KEY")

COGNEE_EMAIL = os.getenv("COGNEE_EMAIL")
COGNEE_PASSWORD = os.getenv("COGNEE_PASSWORD")


DATASET = "dental_insurance_kb_1"
_cognee_initialized = False


## 1.
async def initialize_cognee():
    """Connect to Cognee Cloud once per process."""
    global _cognee_initialized
    if not _cognee_initialized:
        await cognee.serve()
        _cognee_initialized = True


## 2.
async def initialize_session(session_id: str) -> str:
    """Establish Cognee Cloud connection and return session_id."""
    await initialize_cognee()
    print(f"🚀 Session '{session_id}' ready on Cognee Cloud.")
    return session_id


## 3.
async def is_session_valid(session_id: str) -> bool:
    """Returns True if session exists on Cognee Cloud, False if expired/deleted."""
    headers = {"X-Api-Key": COGNEE_API_KEY}

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{COGNEE_URL}/api/v1/sessions/{session_id}",
            headers=headers,
        )
        return resp.status_code == 200


## 4.
async def chat_with_agent(session_id: str, query: str) -> str:
    """Query the GraphRAG dataset with session-scoped conversational memory."""

    if not await is_session_valid(session_id):
        return f"Session '{session_id}' has expired. Please start a new session."
    
    await initialize_cognee()

    results = await cognee.recall(
        query_text=query,
        session_id=session_id,
        datasets=[DATASET],
    )

    if not results:
        return "No applicable policy context found for your query."

    return "\n".join(str(r) for r in results) if isinstance(results, list) else str(results)


## 5.
async def get_chat_history(session_id: str, last_n: int = None) -> list[dict]:
    """Fetch chat history directly from Cognee Cloud REST API."""

    if not await is_session_valid(session_id):
        print(f"⚠️ Session '{session_id}' has expired or does not exist.")
        return []
  
    headers = {"X-Api-Key": COGNEE_API_KEY}

    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{COGNEE_URL}/api/v1/sessions/{session_id}", headers=headers)
        resp.raise_for_status()
        data = resp.json()

    # print(data)
    qas = data.get("qas", [])
    if last_n:
        qas = qas[-last_n:]

    return [
        {"time": e["time"], "question": e["question"], "answer": e["answer"]} for e in qas
        ]