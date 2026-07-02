import os
# CRITICAL: Must match the pipeline environment configuration
os.environ["ENABLE_BACKEND_ACCESS_CONTROL"] = "false"
os.environ["COGNEE_SKIP_CONNECTION_TEST"] = "true"

import asyncio
import cognee
from dotenv import load_dotenv

load_dotenv()

async def main():
    print("🔍 Querying Knowledge Graph...")
    
    # Try a slightly broader query keyword to maximize graph entity matches
    query = "List all extracted CDT codes and policy rules"
    
    results = await cognee.recall(query_text=query)
    print("\n💡 Search Results:")
    print(results)

if __name__ == "__main__":
    asyncio.run(main())