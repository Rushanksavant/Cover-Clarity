import os
os.environ.update({
    "OPENBLAS_NUM_THREADS": "1", "OMP_NUM_THREADS": "1",
    "COGNEE_SKIP_CONNECTION_TEST": "true",
    "ENABLE_BACKEND_ACCESS_CONTROL": "false",
    # "CACHING": "false"
})

import asyncio
from pathlib import Path
import cognee
from dotenv import load_dotenv
from schema import DentalPolicyGraph

load_dotenv()

PROCESSED = Path("data-collection/processed")
DATASET   = "dental_insurance_kb"


async def main(dry_run=True):
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
        await cognee.improve(
            dataset="dental_insurance_kb",
            build_global_context_index=True
        )
        print("✅ Graph enrichment complete via cognee.improve()!")
        
    except AttributeError:
        print("Method 'improve' not found. Falling back to legacy 'memify' pipeline...")
        # Legacy fallback also expects 'dataset'
        await cognee.memify(dataset="dental_insurance_kb")
        print("✅ Graph enrichment complete via cognee.memify()!")

async def prune_metadata():
    await cognee.prune.prune_system(graph=False, vector=False, metadata=True)

if __name__ == "__main__":
    import sys
    # Create graph
    # asyncio.run(main(dry_run="--full" not in sys.argv))

    # Creates a semantic index that acts as an entry-point for quries
    # asyncio.run(enrich())

    # Remove querying-history
    asyncio.run(prune_metadata())