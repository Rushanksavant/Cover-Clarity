import re
from pathlib import Path

PROCESSED_BASE_DIR = Path("./data-collection/processed")
BRONZE_PPO_PATH = PROCESSED_BASE_DIR / "bronze-ppo.md"



def is_mobile_duplicate_table(table_lines: list) -> bool:
    """
    Checks if a table block is a mobile-responsive duplicate.
    Responsive mobile tables repeat the column headers ('Documentation required', etc.)
    inside the first cell of alternating rows.
    """
    for idx, line in enumerate(table_lines):
        # Split the markdown row into cells
        cells = [c.strip().replace("*", "") for c in line.split("|")]
        if len(cells) > 1:
            first_cell = cells[1]
            # If a row's first column contains a header string as its value, it's a mobile layout
            if first_cell in ["Documentation required", "Medical necessity criteria", "Pathologic criteria"]:
                # Ensure it's treated as a row value, not the genuine top header line
                if first_cell == "Documentation required" or idx > 1:
                    return True
    return False



def clean_cpb_content(content: str) -> str:
    """
    Removes standard Aetna boilerplates, academic references, 
    and legal disclaimers from Clinical Policy Bulletins.
    """
    # 1. Strip the generic 'Important note' section up until the actual 'Policy' heading
    content = re.sub(r"## Important note.*?## Policy", "## Policy", content, flags=re.DOTALL)
    
    # 2. Slice off everything from the references section onwards
    # This automatically drops references, copyrights, and website footers in one clean cut
    cutoff_markers = [
        "## The above policy is based on the following references:",
        "## **The above policy is based on the following references:**",
        "## Legal notices"
    ]
    
    for marker in cutoff_markers:
        if marker in content:
            content = content.split(marker)[0]
        
    # 3. Clean up ghost headers leftover from removed web elements (e.g., '### \n\n')
    content = re.sub(r"### \s*\n", "", content)

    # 4. Filter out duplicate responsive table layouts line-by-line
    lines = content.splitlines()
    sanitized_lines = []
    current_table_lines = []
    in_table = False

    for line in lines:
        if line.strip().startswith("|"):
            in_table = True
            current_table_lines.append(line)
        else:
            if in_table:
                # Evaluate the collected table block before writing it back
                if not is_mobile_duplicate_table(current_table_lines):
                    sanitized_lines.extend(current_table_lines)
                current_table_lines = []
                in_table = False
            sanitized_lines.append(line)

    # Catch any trailing table block at EOF
    if in_table and not is_mobile_duplicate_table(current_table_lines):
        sanitized_lines.extend(current_table_lines)

    return "\n".join(sanitized_lines).strip()



def enrich_bronze_ppo():
    """Injects explicit PNS and UCR fee schedule logic into the benefit profile."""
    if not BRONZE_PPO_PATH.exists():
        print("⚠️ bronze-ppo.md not found in processed directory. Skipping enrichment.")
        return
        
    with open(BRONZE_PPO_PATH, "r", encoding="utf-8") as f:
        content = f.read()


    network_override_text = """
---
## Global Network Rules Override

### 1. In-Network Application (PNS)
* All diagnostic, basic, and major service tiers listed in this document apply **strictly** to In-Network participating providers matching the PPOII and ExtendSM networks.

### 2. Out-of-Network (OON) Coinsurance Penalty
* Any service rendered by a non-participating provider is subject to a **30% penalty reduction** relative to the plan's baseline coinsurance coverage.

### 3. UCR Fee Schedule Baseline
* Out-of-Network plan payments are calculated under the Usual, Customary, and Reasonable (UCR) framework, pegged specifically to the **70th percentile of prevailing charges** for the geographic area. The patient maintains full liability for balance billing limits above this threshold.
        """
    if network_override_text[-300:] == content[-300:]:
        print("⏩ bronze-ppo.md is already enriched. Skipping.")
        return
    else:
        with open(BRONZE_PPO_PATH, "a", encoding="utf-8") as f:
            f.write(network_override_text)
        print("💎 Enriched bronze-ppo.md with explicit PNS & UCR baseline parameters.")



def run_workspace_cleanup():
    if not PROCESSED_BASE_DIR.exists():
        print(f"❌ Processed directory '{PROCESSED_BASE_DIR}' does not exist.")
        return

    print("🧼 Purging boilerplate, references, and copyrights from markdown files...")
    cleaned_count = 0

    # Clean all parsed CPBs recursively across nested folders
    for md_path in PROCESSED_BASE_DIR.rglob("*.md"):
        if md_path.name == "bronze-ppo.md":
            continue
            
        with open(md_path, "r", encoding="utf-8") as f:
            raw_content = f.read()
            
        cleaned_content = clean_cpb_content(raw_content)
        
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(cleaned_content)
        cleaned_count += 1

    print(f"✅ Successfully sanitized {cleaned_count} Clinical Policy Bulletins.")
    
    # Enrich the insurance benefit sheet
    enrich_bronze_ppo()



if __name__ == "__main__":
    run_workspace_cleanup()