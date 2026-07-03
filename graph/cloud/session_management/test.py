import asyncio
from utilities import initialize_session, chat_with_agent, get_chat_history

SESSION_ID = "silver_hackathon_test_session_2"   # In prod: derive from user's DB record


async def chat_in_session(session_id):

    await initialize_session(SESSION_ID)

    print("\n[Turn 1]")
    r1 = await chat_with_agent(session_id, "check policy for root-canal?")
    print(f"Agent: {r1}")

    print("\n[Turn 2]")
    r2 = await chat_with_agent(session_id, "same for 16 year old.")
    print(f"Agent: {r2}")



async def get_session_history(session_id):
    print("\n📜 Chat History:")
    history = await get_chat_history(session_id)
    
    if not history:
        print("  No history found (session may have expired or never existed).")
        return

    for turn in history:
        print(f"  [{turn['time']}] Q: {turn['question']}")
        print(f"               A: {turn['answer']}")





if __name__ == "__main__":
    # asyncio.run(chat_in_session(SESSION_ID))
    asyncio.run(get_session_history(SESSION_ID))