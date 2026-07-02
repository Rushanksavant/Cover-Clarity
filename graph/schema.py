from typing import List, Optional
from pydantic import Field
from cognee.infrastructure.engine import DataPoint

class GlobalFramework(DataPoint):
    plan_name: str = Field(..., description="The name of the insurance plan, e.g., 'Bronze PPO'.")
    deductible_rules: str = Field(..., description="Overarching network deductible and out-of-pocket metrics.")
    global_exclusions: List[str] = Field(default_factory=list, description="Plan-wide blanket exclusions like cosmetic or experimental clauses.")

class PolicyCategory(DataPoint):
    name: str = Field(..., description="The folder-derived category, e.g., 'diagnostic', 'oral_surgery', 'periodontics'.")

class PolicyCode(DataPoint):
    code: str = Field(..., description="Clean alphanumeric CDT code identifier ONLY (e.g., 'D4341').")
    description: str = Field(..., description="Clean nomenclature text explaining what procedure this code represents.")
    age_constraints: str = Field(default="All Ages", description="Specific patient age restrictions if explicitly noted for this code.")

class ClinicalRule(DataPoint):
    rule_text: str = Field(..., description="The literal medical necessity criteria, frequency limit, or coverage condition.")
    rule_type: str = Field(..., description="Must be exactly one of: 'Covered', 'NotCovered', 'Conditional', 'Experimental'.")
    frequency_limit: Optional[str] = Field(None, description="Extracted time intervals if applicable, e.g., 'Once every 6 months'.")
    subtle_nuances: List[str] = Field(default_factory=list, description="Fine-print administrative conditions or hidden loopholes.")

# 🚀 THE CONNECTIVITY ACCELERATOR: LATERAL RELATIONSHIP ENGINE
# This explicit linking block maps horizontal intersections across the entire dataset.
class PolicyLinkage(DataPoint):
    source_id: str = Field(..., description="The code or rule originating the connection (e.g., 'D0120').")
    target_id: str = Field(..., description="The target entity being intersected (e.g., 'D0150' or 'Bronze PPO').")
    relationship_type: str = Field(
        ..., 
        description="Must be exactly one of: 'BUNDLED_WITH', 'MUTUALLY_EXCLUSIVE_WITH', 'GOVERNED_BY_GLOBAL_POLICY', 'REQUIRED_BEFORE'."
    )
    explanation: str = Field(..., description="Contextual narrative explaining why these two items intersect.")

class DentalPolicyGraph(DataPoint):
    summary: str = Field(..., description="One sentence semantic summary of this document chunk.")
    global_frameworks: List[GlobalFramework] = Field(default_factory=list)
    categories: List[PolicyCategory] = Field(default_factory=list)
    codes: List[PolicyCode] = Field(default_factory=list)
    rules: List[ClinicalRule] = Field(default_factory=list)
    cross_links: List[PolicyLinkage] = Field(default_factory=list)