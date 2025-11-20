"""Pytest configuration and shared fixtures."""

import pytest
import sys
import os
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


# ============================================================================
# Test Results Collection (stores actual test execution results in JSON)
# ============================================================================

class TestResultsCollector:
    """Collects test results during pytest execution and saves to JSON."""
    
    def __init__(self):
        self.results: List[Dict[str, Any]] = []
        self.start_time = None
        self.session_data = {
            "test_session_id": f"session_{int(time.time())}",
            "started_at": None,
            "finished_at": None,
            "duration_seconds": 0,
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "errors": 0
            },
            "tests": []
        }
    
    @pytest.hookimpl(tryfirst=True, hookwrapper=True)
    def pytest_runtest_makereport(self, item, call):
        """Hook to capture test execution results."""
        outcome = yield
        report = outcome.get_result()
        
        if report.when == "call":  # Only capture the actual test call
            test_result = {
                "test_id": item.nodeid,
                "test_name": item.name,
                "test_file": str(item.fspath.relative_to(project_root)),
                "test_class": item.parent.name if hasattr(item.parent, 'name') else None,
                "outcome": report.outcome,  # passed, failed, skipped
                "duration_seconds": round(report.duration, 4),
                "timestamp": datetime.now().isoformat(),
                "markers": [marker.name for marker in item.iter_markers()],
                "docstring": item.function.__doc__.strip() if item.function.__doc__ else None
            }
            
            # Add failure information
            if report.outcome == "failed":
                test_result["failure_info"] = {
                    "message": str(report.longrepr).split('\n')[0] if report.longrepr else "Unknown error",
                    "full_traceback": str(report.longrepr) if report.longrepr else None
                }
            
            # Add skip reason
            if report.outcome == "skipped":
                test_result["skip_reason"] = str(report.longrepr[2]) if len(report.longrepr) > 2 else "Unknown"
            
            self.results.append(test_result)
    
    @pytest.hookimpl(tryfirst=True)
    def pytest_sessionstart(self, session):
        """Called at start of test session."""
        self.start_time = time.time()
        self.session_data["started_at"] = datetime.now().isoformat()
    
    @pytest.hookimpl(trylast=True)
    def pytest_sessionfinish(self, session, exitstatus):
        """Called at end of test session - save results to JSON."""
        if self.start_time is None:
            return  # Session never started properly
            
        end_time = time.time()
        self.session_data["finished_at"] = datetime.now().isoformat()
        self.session_data["duration_seconds"] = round(end_time - self.start_time, 2)
        self.session_data["exit_status"] = exitstatus
        
        # Calculate summary statistics
        self.session_data["summary"]["total"] = len(self.results)
        for result in self.results:
            outcome = result["outcome"]
            if outcome == "passed":
                self.session_data["summary"]["passed"] += 1
            elif outcome == "failed":
                self.session_data["summary"]["failed"] += 1
            elif outcome == "skipped":
                self.session_data["summary"]["skipped"] += 1
        
        # Calculate success rate
        total = self.session_data["summary"]["total"]
        passed = self.session_data["summary"]["passed"]
        self.session_data["summary"]["success_rate"] = round((passed / total * 100) if total > 0 else 0, 2)
        
        # Add test results
        self.session_data["tests"] = self.results
        
        # Save to JSON file
        self._save_results()
    
    def _save_results(self):
        """Save test results to JSON file."""
        output_dir = Path("tests/results")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename based on timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"test_results_{timestamp}.json"
        
        # Also save as latest
        latest_file = output_dir / "test_results_latest.json"
        
        # Write JSON with pretty formatting
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.session_data, f, indent=2, ensure_ascii=False)
        
        with open(latest_file, 'w', encoding='utf-8') as f:
            json.dump(self.session_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n{'='*60}")
        print(f"📊 TEST RESULTS SAVED TO JSON")
        print(f"{'='*60}")
        print(f"📄 Timestamped: {output_file}")
        print(f"📄 Latest:      {latest_file}")
        print(f"\n✅ Summary:")
        print(f"   • Total:   {self.session_data['summary']['total']}")
        print(f"   • Passed:  {self.session_data['summary']['passed']} ✅")
        print(f"   • Failed:  {self.session_data['summary']['failed']} ❌")
        print(f"   • Skipped: {self.session_data['summary']['skipped']} ⏭️")
        print(f"   • Success: {self.session_data['summary']['success_rate']}%")
        print(f"   • Duration: {self.session_data['duration_seconds']}s")
        print(f"{'='*60}\n")


# Register the results collector
_results_collector = None


def pytest_configure(config):
    """Register our custom plugin."""
    global _results_collector
    _results_collector = TestResultsCollector()
    config.pluginmanager.register(_results_collector, "test_results_collector")


def pytest_unconfigure(config):
    """Unregister our custom plugin."""
    global _results_collector
    if _results_collector is not None:
        config.pluginmanager.unregister(_results_collector)


@pytest.fixture(scope="session")
def project_root_path():
    """Return the project root path."""
    return project_root


@pytest.fixture(scope="session")
def data_directory():
    """Return the data directory path."""
    return project_root / "data"


@pytest.fixture(scope="session")
def embeddings_cache_directory():
    """Return the embeddings cache directory path."""
    return project_root / "data" / "embeddings_cache"


@pytest.fixture
def sample_system_description():
    """Return a sample AI system description for testing."""
    return {
        "system_description": "AI system for automated decision-making",
        "use_case": "Testing purposes",
        "data_types": ["personal_data"],
        "autonomous_decision": True,
        "human_oversight": False
    }


@pytest.fixture
def prohibited_system_description():
    """Return a system description that should be classified as PROHIBITED."""
    return {
        "system_description": "Real-time biometric facial recognition system for mass surveillance and social scoring",
        "use_case": "Government social credit system",
        "data_types": ["biometric", "personal_data", "behavioral_data"],
        "autonomous_decision": True,
        "human_oversight": False,
        "decision_impact": "life-altering"
    }


@pytest.fixture
def high_risk_system_description():
    """Return a system description that should be classified as HIGH_RISK."""
    return {
        "system_description": "AI system for automated employment screening and hiring decisions",
        "use_case": "Recruitment and candidate evaluation",
        "data_types": ["personal_data", "employment_data", "educational_data"],
        "autonomous_decision": True,
        "human_oversight": True,
        "decision_impact": "significant"
    }


@pytest.fixture
def limited_risk_system_description():
    """Return a system description that should be classified as LIMITED_RISK."""
    return {
        "system_description": "Customer service chatbot that interacts with users",
        "use_case": "Automated customer support",
        "data_types": ["conversation_data"],
        "autonomous_decision": False,
        "human_oversight": True,
        "decision_impact": "minor"
    }


@pytest.fixture
def minimal_risk_system_description():
    """Return a system description that should be classified as MINIMAL_RISK."""
    return {
        "system_description": "Spam email filter",
        "use_case": "Email filtering and categorization",
        "data_types": ["email_content"],
        "autonomous_decision": True,
        "human_oversight": False,
        "decision_impact": "minimal"
    }


@pytest.fixture
def mock_api_key(monkeypatch):
    """Set mock API keys for testing."""
    monkeypatch.setenv("GOOGLE_API_KEY", "test_google_key_12345")
    monkeypatch.setenv("COHERE_API_KEY", "test_cohere_key_12345")


@pytest.fixture
def clear_api_keys(monkeypatch):
    """Clear API keys for testing error handling."""
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("COHERE_API_KEY", raising=False)


# Pytest configuration
def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (require API keys)"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests (no external dependencies)"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically."""
    for item in items:
        # Mark tests in test_evaluation.py that use asyncio
        if "asyncio" in item.keywords:
            item.add_marker(pytest.mark.asyncio)
        
        # Mark integration tests
        if "integration" in item.nodeid.lower() or "real_search" in item.name:
            item.add_marker(pytest.mark.integration)
        
        # Mark unit tests (default)
        if not any(marker in item.keywords for marker in ["integration", "slow"]):
            item.add_marker(pytest.mark.unit)
