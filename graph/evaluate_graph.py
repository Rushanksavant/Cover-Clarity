import os
# Bypasses the strict authentication layers and hanging connection lookups
os.environ["ENABLE_BACKEND_ACCESS_CONTROL"] = "false"
os.environ["COGNEE_SKIP_CONNECTION_TEST"] = "true"

import asyncio
import cognee
from dotenv import load_dotenv

load_dotenv()

async def run_evaluation():
    print("=" * 65)
    print("📊 COGNEE KNOWLEDGE GRAPH QUALITY EVALUATION SUITE")
    print("=" * 65)
    
    # 1. Fetching Graph Infrastructure Telemetry
    print("\n🔍 Fetching graph topology from local Kuzu storage...")
    try:
        # Pulls the raw node and edge configurations managed by Cognee
        nodes, edges = await cognee.get_memory_provenance_graph(include_memory=True)
        total_nodes = len(nodes)
        total_edges = len(edges)
    except Exception as e:
        print(f"❌ Error extracting graph topology: {e}")
        print("💡 Suggestion: Ensure your pipeline ran successfully and created the database.")
        return

    # 2. Fetch Schema Type Count Summaries
    print("🗂️ Analyzing entity type distributions...")
    try:
        inventory = await cognee.get_schema_inventory()
    except Exception as e:
        inventory = None

    # 3. Computing Graph Connectivity & Density
    # Higher ratio means entities collapse into shared, cross-linked concepts
    connectivity_ratio = total_edges / total_nodes if total_nodes > 0 else 0
    
    print("\n" + "-" * 45)
    print("📈 TOPOLOGICAL METRICS")
    print("-" * 45)
    print(f"• Total Extracted Graph Nodes: {total_nodes}")
    print(f"• Total Committed Graph Edges: {total_edges}")
    print(f"• Connectivity Density Ratio:  {connectivity_ratio:.2f} edges/node")
    
    quality_warnings = []
    if total_nodes == 0:
        quality_warnings.append("CRITICAL: The graph database is empty! Run your local_pipeline.py first.")
    elif connectivity_ratio < 1.0:
        quality_warnings.append("WARNING: Low connectivity ratio. Nodes are behaving like decoupled islands. Your multi-hop queries will degrade to standard vector searches.")
    elif connectivity_ratio >= 1.5:
        print("✨ Topology Quality: High-density mesh detected! Nodes are deeply cross-linked.")
    else:
        print("⚡ Topology Quality: Linear graph architecture found.")

    # 4. Executing Multi-Hop Functional Routing Probes
    print("\n" + "-" * 45)
    print("⚡ LIVE MULTI-HOP RECALL PROBES")
    print("-" * 45)
    
    probes = [
    # === CATEGORY 1: CODE-SPECIFIC FREQUENCY LIMITATIONS ===
    "How often can a patient receive comprehensive oral evaluations (D0150) under this plan?",
    "What are the explicit frequency limitations governing panoramic radiographic images?",
    "Is there a limit on the number of prophylaxis cleanings allowed within a single calendar year?",
    "What is the frequency rule governing periodontal scaling and root planing (D4341) per quadrant?",
    "How frequently are bitewing X-rays covered for adult patients?",
    "Are local anesthesia administrations limited by a specific maximum count per patient visit?",
    "What is the replacement frequency rule for major prosthodontic services or porcelain crowns?",
    "How many times can a palliative treatment for minor dental pain be billed per year?",
    "Is there a lifetime frequency limit on specific orthodontic or complex surgical procedures?",
    "What time interval must pass before a sealant procedure can be repeated on the exact same tooth?",

    # === CATEGORY 2: CLINICAL CRITERIA & MEDICAL NECESSITY ===
    "What specific clinical conditions or pocket depths are required to justify periodontal scaling (D4341)?",
    "Are diagnostic casts or intraoral photographs covered only under specific medical necessity clauses?",
    "What documentation, such as radiographic evidence or charting, is mandatory for partial or full denture approvals?",
    "Under what surgical conditions is an extraoral biopsy of osseous tissue covered by the policy?",
    "Does the plan require pre-authorization or specific clinical notes for complex surgical extractions (D7210)?",
    "What clinical criteria define a procedure as 'experimental' or 'investigational' in the oral surgery guidelines?",
    "Are tissue conditioning treatments covered only prior to the final denture fabrication step?",
    "What pocket depth metrics or bleeding indexes must be documented to qualify for periodontic maintenance (D4910)?",
    "What explicit clinical criteria govern the coverage of core buildups including pins?",
    "Is localized delivery of antimicrobial agents covered under standard periodontal intervention protocols?",

    # === CATEGORY 3: AGE DEMOGRAPHICS & DEPENDENT CONSTRAINTS ===
    "At what maximum age does a dependent child lose eligibility for pediatric dental benefits?",
    "Are fluoride varnish applications strictly limited to pediatric patients under a certain age constraint?",
    "Does the plan outline any specific age cutoffs or development limitations for space maintainers?",
    "Are there explicit age restrictions governing the coverage of dental sealants on permanent molars?",
    "Does orthognathic surgery or orthodontic coverage depend on the patient reaching a minimum age?",
    "Are full-mouth debridements (D4355) restricted or modified based on adult versus child classifications?",
    "What global age exceptions allow a disabled dependent to maintain coverage beyond age 26?",
    "Are nitrous oxide or general anesthesia benefits restricted by the patient's age group?",
    "Does the plan differentiate between pediatric and adult prophylaxis limits?",
    "What age limits apply to deep sedation or intravenous conscious sedation codes?",

    # === CATEGORY 4: BUNDLING, EXCLUSIVITY, & LATERAL CODE LINKS ===
    "Is a periodic oral evaluation (D0120) bundled into a comprehensive evaluation if performed on the same day?",
    "Can a full mouth debridement be billed concurrently with a standard prophylaxis scaling?",
    "Are local infiltrations or regional blocks considered mutually exclusive from the main surgical extraction code?",
    "What individual treatment codes are bundled into or considered part of a standard endodontic root canal therapy?",
    "Is an intraoral periapical radiograph collection bundled when a panoramic film is captured during the same visit?",
    "Can periodontic maintenance (D4910) be billed during the same encounter as regular prophylaxis (D1110)?",
    "Are post and core procedures mutually exclusive from standard crown cementation codes if performed separately?",
    "What rules prevent the simultaneous billing of emergency palliative care with definitive therapeutic procedures?",
    "Is a pulp vitality test bundled into a comprehensive diagnostic workup?",
    "Are surgical stent placements bundled into final implant placement procedures?",

    # === CATEGORY 5: GLOBAL PLAN RULES & NETWORK LIMITATIONS (BRONZE PPO) ===
    "What global exclusions apply to purely cosmetic dental modifications like teeth whitening?",
    "How do out-of-network deductibles differ from in-network deductibles under the Bronze PPO framework?",
    "What standard preventative services are entirely exempt from the individual annual deductible requirements?",
    "What is the plan's policy on out-of-pocket maximum caps for pediatric versus family tiers?",
    "Are dental implants globally excluded or covered as a major restorative tier item?",
    "How does the plan handle dental treatments resulting from an occupational injury or covered by worker's compensation?",
    "What is the co-insurance percentage split for basic diagnostic services versus major oral surgery?",
    "Are missing tooth clauses enforced for prosthetics placed after the plan's effective date?",
    "What global plan boundaries dictate coverage limits for emergency dental care received out of state?",
    "Are prescription medications or specialized oral rinses covered under this dental insurance framework?"
]
    
    successful_probes = 0
    for idx, probe in enumerate(probes, 1):
        print(f"Firing Probe #{idx}: '{probe}'")
        try:
            res = await cognee.recall(query_text=probe)
            res_str = str(res).lower()
            
            # Identify if context fails or returns generic fallback strings
            if "no conditional" in res_str or "no rules" in res_str or "no provided context" in res_str or len(res_str.strip()) < 40:
                print(f"  ❌ Probe Status: Disconnected path. LLM failed to bridge contexts.")
            else:
                print(f"  ✅ Probe Status: Path active. Context successfully synthesized.")
                successful_probes += 1
        except Exception as e:
            print(f"  ❌ Probe Status: Execution execution error ({e})")

    # 5. Render Hackathon Pitch Scorecard
    print("\n" + "=" * 65)
    print("🎯 FINAL PRODUCTION GRAPH SCORECARD")
    print("=" * 65)
    
    # Mathematical Heuristic Grade Matrix
    if total_nodes == 0:
        grade = "F (Empty Data Source Layers)"
    elif successful_probes == 0 and connectivity_ratio < 1.1:
        grade = "C- (Flat Vector RAG Fallback - Low Interconnectivity)"
    elif connectivity_ratio < 1.4:
        grade = "B (Good Quality, Medium Path Multi-Hop Depth)"
    else:
        grade = "A (Production Grade - Rich Structural Semantic Graph Mesh)"
        
    print(f"⭐️ Graph Intelligence Grade:  {grade}")
    print(f"📊 Query Trace Pass Rate:      {(successful_probes / len(probes)) * 100:.1f}%")
    print(f"🔗 Relationship Node Ratio:    {connectivity_ratio:.2f}")
    print("=" * 65)

if __name__ == "__main__":
    asyncio.run(run_evaluation())