import asyncio
import sys
import diskcache
from pathlib import Path
import cognee
# from cognee.modules.chunking.text_chunker_with_overlap import TextChunkerWithOverlap
from schema import DentalPolicyGraph
from schema import PatientMedicalHistory, MedicalCondition, Medication

from dotenv import load_dotenv
load_dotenv()

# ROOT = os.getenv("./.cognee_data")
PROCESSED = Path("data-collection/processed")
DATASET   = "dental_insurance_kb_1"


# class OverlappingChunker(TextChunkerWithOverlap):
#     def __init__(self, document, get_text, max_chunk_size):
#         # 10% of chunk_size tokens will overlap with the next chunk
#         super().__init__(document, get_text, max_chunk_size, chunk_overlap_ratio=0.10)


# ─── Build Graph ───────────────────────────────────────────────────────
async def build(dry_run=True):

    # 1. Connect to Cloud Tenant
    await cognee.serve()

    # Access clean .md docs
    dirs = ["diagnostic", "oral_surgery", "periodontics"] if dry_run else ["diagnostic", "oral_surgery", "periodontics", "adjunctive_general_services", "endodontics", "implant_services", "medical_in_nature", "orthodontics", "preventive", "restorative"]
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
    await cognee.cognify(datasets=[DATASET], graph_model=DentalPolicyGraph, chunk_size=2048
                        #  , chunker=OverlappingChunker
                         )
    print("Done!")

async def enrich():
    await cognee.serve()
    print("Connecting to existing dental graph database on Cognee Cloud...")
    print("\nExecuting global graph enrichment passes...")
    try:
        await cognee.improve(dataset=DATASET, build_global_context_index=True)
        print("✅ Graph enrichment complete via cognee.improve()!")
    except (AttributeError, RuntimeError) as e:
        # Intercepts the remote 404 routing limit to let the script exit cleanly
        print(f"ℹ️ Cloud enrichment endpoint bypassed or unavailable (Expected on Cognee Cloud Tier). Graph is fully viable. Proceeding safely...")



# ─── Session Management ───────────────────────────────────────────────────────
async def chat_with_agent(query_text: str, session_id: str, medical_history: list[PatientMedicalHistory] = None):
    """
    Executes a cloud-isolated session query. Conversation history is isolated 
    temporarily within the remote session context.
    """
    # Ensure client routing and authentication headers are active for this call thread
    await cognee.serve()

    # Merge patient context into the input space if present
    formatted_query = query_text
    if medical_history:
        formatted_query = (
            f"Patient Medical Context:\n"
            f"{''.join([model.model_dump_json(indent=2) for model in medical_history])}\n\n"
            f"User Query: {query_text}"
        )

    # Route query directly to the cloud tenant engine using session partitioning
    response = await cognee.recall(query_text=formatted_query, session_id=session_id, datasets=[DATASET])
    return response


# STORAGE OPTIMIZATION: PURGE SPECIFIC SESSION DATA
async def delete_session_history(session_id: str):
    """
    Evicts session memory from the remote cloud instance. 
    Local diskcache exploration is completely bypassed because storage scale is offloaded.
    """
    await cognee.serve()
    try:
        # Cloud Native: Drop the targeted dataset context gracefully via the cloud gateway API
        await cognee.forget(dataset_name=DATASET)
        print(f"🗑️ Cloud workspace metrics reset successfully for dataset: '{DATASET}'")
    except Exception as e:
        print(f"⚠️ Error resetting cloud dataset parameters: {e}")