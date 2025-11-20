#!/usr/bin/env python3
"""Quick test for single assessment."""

import logging
from src.config import Config
from src.observability import setup_logging
from src.sequential_orchestrator import ComplianceOrchestrator

setup_logging("INFO")
logger = logging.getLogger(__name__)

print("\n=== Quick Test: Single Assessment ===\n")

orchestrator = ComplianceOrchestrator()

system_info = {
    "system_name": "AutoLoan Approval System",
    "use_case": "Automated creditworthiness assessment for loan applications",
    "data_types": ["financial", "personal_data", "employment"],
    "decision_impact": "significant",
    "affected_groups": "Loan applicants",
    "autonomous_decision": True,
    "human_oversight": True,
    "error_consequences": "Severe - affects credit decisions",
}

try:
    result = orchestrator.assess_system(system_info)
    
    print(f"\n=== Results ===")
    print(f"State keys: {list(result.get('state', {}).keys())}")
    print(f"\nAssessment: {result.get('assessment', 'NOT FOUND')}")
    print(f"\nReport: {result.get('report', 'NOT FOUND')}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
