import os
os.environ.update({
    "OPENBLAS_NUM_THREADS": "1", "OMP_NUM_THREADS": "1",
    "COGNEE_SKIP_CONNECTION_TEST": "true",
    "ENABLE_BACKEND_ACCESS_CONTROL": "false",
    "CACHING": "true"
})

import sys
import asyncio
from executables import build, enrich

async def main():
    # Create Graph
    await build(dry_run="--full" not in sys.argv)
    
    # Creates a semantic index that acts as an entry-point for queries
    await enrich()

if __name__ == "__main__":
    asyncio.run(main())