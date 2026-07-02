import os
os.environ.update({
    "OPENBLAS_NUM_THREADS": "1", "OMP_NUM_THREADS": "1",
    "COGNEE_SKIP_CONNECTION_TEST": "true",
    "ENABLE_BACKEND_ACCESS_CONTROL": "false",
    "CACHING": "true"
})

import asyncio
import sys
import diskcache
from pathlib import Path
import cognee
from dotenv import load_dotenv
from schema import DentalPolicyGraph
from schema import PatientMedicalHistory, MedicalCondition, Medication

load_dotenv()

ROOT = os.getenv("./.cognee_data")
PROCESSED = Path("data-collection/processed")
DATASET   = "dental_insurance_kb"


# ─── Build Graph ───────────────────────────────────────────────────────
async def build(dry_run=True):
    await cognee.prune.prune_data()
    await cognee.prune.prune_system(metadata=True)

    # Access clean .md docs
    dirs = ["diagnostic"] if dry_run else ["diagnostic", "oral_surgery", "periodontics"]
    files = [f for d in dirs for f in (PROCESSED / d).glob("*.md")]
    if (PROCESSED / "bronze-ppo.md").exists():
        files.append(PROCESSED / "bronze-ppo.md")

    # Start ingestion with Context Injection
    print(f"Ingesting {len(files)} files with category metadata injection...")
    for f in files:
        # Determine the category string dynamically based on the parent folder name
        folder_category = f.parent.name
        
        # Fallback handling for files like bronze-ppo.md that sit directly in the root 'processed' directory
        if folder_category == "processed":
            folder_category = "General"

        # Read the raw content of the markdown file
        with open(f, "r", encoding="utf-8") as file_handle:
            raw_content = file_handle.read()

        # Prepend the deterministic tracker header to the raw text block
        injected_content = f"SYSTEM_METADATA_CATEGORY: {folder_category}\n\n{raw_content}"

        print(f"   ↳ Ingesting Stream: {f.name} | Category Locked: [{folder_category}]")
        
        # Pass the injected text content directly into Cognee instead of the file path string
        await cognee.add(injected_content, dataset_name=DATASET)

    # Build graph
    print("Building knowledge graph...")
    await cognee.cognify(graph_model=DentalPolicyGraph, chunk_size=2048)
    print("Done!")

async def enrich():
    print("Connecting to existing dental graph database...")
    print("\nExecuting global graph enrichment passes...")
    try:
        await cognee.improve(dataset="dental_insurance_kb", build_global_context_index=True)
        print("✅ Graph enrichment complete via cognee.improve()!")
        
    except AttributeError:
        print("Method 'improve' not found. Falling back to legacy 'memify' pipeline...")
        await cognee.memify(dataset="dental_insurance_kb")
        print("✅ Graph enrichment complete via cognee.memify()!")



# ─── Session Management ───────────────────────────────────────────────────────
async def chat_with_agent(query_text: str, session_id: str, medical_history: [PatientMedicalHistory] = None):
    """
    Executes a session-isolated query. Turns are cached temporarily in the session
    context rather than polluting the core DATASET graph.
    """
    # Merge patient context into the input space if present
    formatted_query = query_text
    if medical_history:
        formatted_query = (
            f"Patient Medical Context:\n{medical_history.model_dump_json(indent=2)}\n\n"
            f"User Query: {query_text}"
        )
    # Cognee checks the short-term session cache first, then defaults to the graph dataset
    response = await cognee.recall(query_text=formatted_query, session_id=session_id, datasets=[DATASET])
    return response


# STORAGE OPTIMIZATION: PURGE SPECIFIC SESSION
def delete_session_history(session_id: str):
    """
    Evicts the specified session_id entries from the diskcache backend
    to stop unbounded growth of the local session storage footprint.
    """
    safe_root = os.getenv("DATA_ROOT_DIRECTORY") or os.getenv("COGNEE_DATA_DIR") or "./.cognee_data"
    cache_path = Path(safe_root).expanduser() / ".cognee_fs_cache" / "sessions_db"
    
    if not cache_path.exists():
        print("ℹ️ Cache folder does not exist. Nothing to clear.")
        return

    try:
        # Bind directly to Cognee's local diskcache backend
        cache = diskcache.Cache(str(cache_path))
        keys_to_evict = [key for key in cache if session_id in str(key)]
        
        for key in keys_to_evict:
            del cache[key]
            
        cache.close()
        print(f"🗑️ Successfully evicted {len(keys_to_evict)} storage records for session: '{session_id}'")
    except Exception as e:
        print(f"⚠️ Space optimization error handling diskcache: {e}")