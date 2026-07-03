import sys
import asyncio
from executables import build, enrich

async def main():
    # Create Graph
    await build(dry_run="--full" not in sys.argv)
    
    # Creates a semantic index that acts as an entry-point for queries
    # await enrich()

if __name__ == "__main__":
    asyncio.run(main())