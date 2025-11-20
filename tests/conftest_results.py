"""Pytest plugin to capture test results and save to JSON."""

import pytest
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any


class TestResultsCollector:
    """Collects test results during pytest execution."""
    
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
                "errors": 0,
                "xfailed": 0,
                "xpassed": 0
            },
            "tests": []
        }
    
    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_makereport(self, item, call):
        """Hook to capture test execution results."""
        outcome = yield
        report = outcome.get_result()
        
        if report.when == "call":  # Only capture the actual test call, not setup/teardown
            test_result = {
                "test_id": item.nodeid,
                "test_name": item.name,
                "test_file": str(item.fspath),
                "test_class": item.parent.name if hasattr(item.parent, 'name') else None,
                "outcome": report.outcome,  # passed, failed, skipped
                "duration_seconds": round(report.duration, 4),
                "timestamp": datetime.now().isoformat(),
                "markers": [marker.name for marker in item.iter_markers()],
                "docstring": item.function.__doc__.strip() if item.function.__doc__ else None
            }
            
            # Add failure information if test failed
            if report.outcome == "failed":
                test_result["failure_info"] = {
                    "message": str(report.longrepr),
                    "exception_type": report.longrepr.reprcrash.message if hasattr(report.longrepr, 'reprcrash') else None,
                    "traceback": str(report.longrepr) if report.longrepr else None
                }
            
            # Add skip reason if test was skipped
            if report.outcome == "skipped":
                test_result["skip_reason"] = report.longrepr[2] if len(report.longrepr) > 2 else "Unknown"
            
            self.results.append(test_result)
    
    def pytest_sessionstart(self, session):
        """Called at start of test session."""
        self.start_time = time.time()
        self.session_data["started_at"] = datetime.now().isoformat()
    
    def pytest_sessionfinish(self, session, exitstatus):
        """Called at end of test session - save results to JSON."""
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
        
        print(f"\n📊 Test results saved to:")
        print(f"   • {output_file}")
        print(f"   • {latest_file}")
        print(f"\n✅ {self.session_data['summary']['passed']}/{self.session_data['summary']['total']} tests passed")
        print(f"   Success rate: {self.session_data['summary']['success_rate']}%")


# Register the plugin
collector = TestResultsCollector()


def pytest_configure(config):
    """Register our custom plugin."""
    config.pluginmanager.register(collector, "test_results_collector")


def pytest_unconfigure(config):
    """Unregister our custom plugin."""
    config.pluginmanager.unregister(collector)
