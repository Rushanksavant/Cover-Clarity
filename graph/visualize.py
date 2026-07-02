import os
# Turn off the access control layer to bypass validation errors
os.environ["ENABLE_BACKEND_ACCESS_CONTROL"] = "false"
os.environ["COGNEE_SKIP_CONNECTION_TEST"] = "true"

import asyncio
from pathlib import Path
from cognee import visualize_graph
from dotenv import load_dotenv

load_dotenv()

async def main():
    print("📊 Generating interactive graph layout...")
    
    # FIX: Force the path to be absolute right from the start
    absolute_output_path = Path("./graph/dental_graph.html").resolve()
    
    # Pass the absolute string path to the visualizer
    await visualize_graph(str(absolute_output_path))
    
    print(f"\n✅ Success! Graph data compiled.")
    print(f"🚀 Open this file path directly in your browser:\n   file://{absolute_output_path}")

if __name__ == "__main__":
    asyncio.run(main())