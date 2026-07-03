import asyncio
from schema import PatientMedicalHistory, MedicalCondition, Medication
# Redirecting import to look at your updated cloud executable architecture
from executables import chat_with_agent, delete_session_history

# Hardcoded session-id
session_id = "user_9921_eval_session"

# Mock a Hard-coded Medical History
sample_patient_history = PatientMedicalHistory(
    patient_id="PATIENT_9921",
    age=45,
    chronic_conditions=[
        MedicalCondition(condition_name="Hypertension", severity="Mild"),
        MedicalCondition(condition_name="Dental Anxiety", severity="Severe", notes="Requires sedation alternatives")
    ],
    current_medications=[
        Medication(name="Lisinopril", dosage="10mg", frequency="Once daily")
    ],
    allergies=["Penicillin"]
)

async def chat(session_id = session_id):
    # Isolated Query Run 1 (Turn includes background context)
    print("\n--- Sending Turn 1 ---")
    reply_1 = await chat_with_agent(
        query_text="Is a root canal covered under my profile status?",
        session_id=session_id,
        medical_history=sample_patient_history
    )
    print(f"Agent Response:\n{reply_1}")
    
    # Isolated Query Run 2 (Turn relies on short-term session context)
    print("\n--- Sending Turn 2 (Context Check) ---")
    reply_2 = await chat_with_agent(
        query_text="What about alternative options for my sedation limits?",
        session_id=session_id
        # No need to re-pass history; it's captured in the short-term session thread context
    )
    print(f"Agent Response:\n{reply_2}")
    
async def delete_chat_history(session_id = session_id):
    # Evict storage footprint safely
    print(f"\n--- Optimizing Storage footprint for session: {session_id} ---")
    await delete_session_history(session_id)

if __name__ == "__main__":
    # Orchestrating the async flows sequentially inside an event loop execution block
    async def main():
        ## Demo chat simulation
        await chat()
        
        ## Deleting chat-sessions safely without wiping out the permanent graph topology
        await delete_chat_history("user_9921_eval_session")
        await delete_chat_history("system_quality_eval_session") # evaluation probes session
        
    asyncio.run(main())