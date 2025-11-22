"""Unit tests for observability.py - MetricsCollector and TraceCollector."""

import pytest
import json
import tempfile
from pathlib import Path
from src.observability import MetricsCollector, TraceCollector


class TestMetricsCollector:
    """Test suite for MetricsCollector."""
    
    @pytest.fixture
    def metrics_collector(self):
        """Create a fresh MetricsCollector instance for testing."""
        return MetricsCollector()
    
    def test_initialization(self, metrics_collector):
        """Test that metrics collector initializes correctly."""
        assert metrics_collector.metrics == []
        assert metrics_collector.start_time is None
    
    def test_start_timer(self, metrics_collector):
        """Test that start_timer sets the start time."""
        metrics_collector.start_timer()
        assert metrics_collector.start_time is not None
        assert isinstance(metrics_collector.start_time, float)
    
    def test_record_metric_basic(self, metrics_collector):
        """Test recording a basic metric."""
        metrics_collector.record_metric("test_metric", 42)
        
        assert len(metrics_collector.metrics) == 1
        metric = metrics_collector.metrics[0]
        assert metric["metric_name"] == "test_metric"
        assert metric["value"] == 42
        assert "timestamp" in metric
    
    def test_record_metric_with_tags(self, metrics_collector):
        """Test recording a metric with tags."""
        metrics_collector.record_metric(
            "api_calls",
            5,
            tags={"endpoint": "/api/assess", "status": "success"}
        )
        
        assert len(metrics_collector.metrics) == 1
        metric = metrics_collector.metrics[0]
        assert metric["metric_name"] == "api_calls"
        assert metric["value"] == 5
        assert metric["tags"]["endpoint"] == "/api/assess"
        assert metric["tags"]["status"] == "success"
    
    def test_record_multiple_metrics(self, metrics_collector):
        """Test recording multiple metrics."""
        metrics_collector.record_metric("metric1", 10)
        metrics_collector.record_metric("metric2", 20)
        metrics_collector.record_metric("metric3", 30)
        
        assert len(metrics_collector.metrics) == 3
        assert metrics_collector.metrics[0]["value"] == 10
        assert metrics_collector.metrics[1]["value"] == 20
        assert metrics_collector.metrics[2]["value"] == 30
    
    def test_get_summary(self, metrics_collector):
        """Test getting metrics summary."""
        metrics_collector.record_metric("test1", 100)
        metrics_collector.record_metric("test2", 200)
        
        summary = metrics_collector.get_summary()
        
        assert "total_metrics" in summary
        assert summary["total_metrics"] == 2
        assert "metrics" in summary
        assert len(summary["metrics"]) == 2
    
    def test_get_summary_empty(self, metrics_collector):
        """Test getting summary with no metrics."""
        summary = metrics_collector.get_summary()
        
        assert summary["total_metrics"] == 0
        assert summary["metrics"] == []
    
    def test_elapsed_time_tracking(self, metrics_collector):
        """Test that elapsed time is tracked when timer is started."""
        import time
        
        metrics_collector.start_timer()
        time.sleep(0.1)  # Sleep for 100ms
        metrics_collector.record_metric("test_metric", 1)
        
        metric = metrics_collector.metrics[0]
        assert "elapsed_seconds" in metric
        assert metric["elapsed_seconds"] is not None
        assert metric["elapsed_seconds"] >= 0.1
    
    def test_save_metrics_to_file(self, metrics_collector):
        """Test saving metrics to JSON file."""
        metrics_collector.record_metric("test_metric", 42, tags={"env": "test"})
        
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test_metrics.json"
            metrics_collector.save_metrics(str(filepath))
            
            # Verify file was created
            assert filepath.exists()
            
            # Verify content
            with open(filepath) as f:
                data = json.load(f)
            
            assert data["total_metrics"] == 1
            assert data["metrics"][0]["metric_name"] == "test_metric"
            assert data["metrics"][0]["value"] == 42


class TestTraceCollector:
    """Test suite for TraceCollector."""
    
    @pytest.fixture
    def trace_collector(self):
        """Create a fresh TraceCollector instance for testing."""
        return TraceCollector()
    
    def test_initialization(self, trace_collector):
        """Test that trace collector initializes correctly."""
        assert trace_collector.traces == []
    
    def test_record_trace_basic(self, trace_collector):
        """Test recording a basic trace."""
        trace_collector.record_trace(
            agent_name="TestAgent",
            action="test_action",
            status="success"
        )
        
        assert len(trace_collector.traces) == 1
        trace = trace_collector.traces[0]
        assert trace["agent"] == "TestAgent"
        assert trace["action"] == "test_action"
        assert trace["status"] == "success"
        assert "timestamp" in trace
    
    def test_record_trace_with_input_output(self, trace_collector):
        """Test recording trace with input and output data."""
        trace_collector.record_trace(
            agent_name="DataAgent",
            action="process_data",
            input_data={"key": "value"},
            output_data={"result": "processed"},
            status="success"
        )
        
        assert len(trace_collector.traces) == 1
        trace = trace_collector.traces[0]
        assert trace["input"]["key"] == "value"
        assert trace["output"]["result"] == "processed"
    
    def test_record_trace_with_error(self, trace_collector):
        """Test recording trace with error."""
        trace_collector.record_trace(
            agent_name="ErrorAgent",
            action="failing_action",
            status="error",
            error="Something went wrong"
        )
        
        assert len(trace_collector.traces) == 1
        trace = trace_collector.traces[0]
        assert trace["status"] == "error"
        assert trace["error"] == "Something went wrong"
    
    def test_record_multiple_traces(self, trace_collector):
        """Test recording multiple traces."""
        trace_collector.record_trace("Agent1", "action1", status="success")
        trace_collector.record_trace("Agent2", "action2", status="success")
        trace_collector.record_trace("Agent3", "action3", status="error", error="Failed")
        
        assert len(trace_collector.traces) == 3
        assert trace_collector.traces[0]["agent"] == "Agent1"
        assert trace_collector.traces[1]["agent"] == "Agent2"
        assert trace_collector.traces[2]["status"] == "error"
    
    def test_get_traces(self, trace_collector):
        """Test getting all recorded traces."""
        trace_collector.record_trace("Agent1", "action1", status="success")
        trace_collector.record_trace("Agent2", "action2", status="success")
        
        traces = trace_collector.get_traces()
        
        assert len(traces) == 2
        assert traces[0]["agent"] == "Agent1"
        assert traces[1]["agent"] == "Agent2"
    
    def test_get_traces_empty(self, trace_collector):
        """Test getting traces when none exist."""
        traces = trace_collector.get_traces()
        assert traces == []
    
    def test_save_traces_to_file(self, trace_collector):
        """Test saving traces to JSON file."""
        trace_collector.record_trace(
            agent_name="TestAgent",
            action="test_action",
            input_data={"test": "data"},
            status="success"
        )
        
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test_traces.json"
            trace_collector.save_traces(str(filepath))
            
            # Verify file was created
            assert filepath.exists()
            
            # Verify content
            with open(filepath) as f:
                data = json.load(f)
            
            assert len(data) == 1
            assert data[0]["agent"] == "TestAgent"
            assert data[0]["action"] == "test_action"
            assert data[0]["input"]["test"] == "data"
    
    def test_trace_ordering(self, trace_collector):
        """Test that traces are recorded in order."""
        import time
        
        trace_collector.record_trace("Agent1", "first", status="success")
        time.sleep(0.01)
        trace_collector.record_trace("Agent2", "second", status="success")
        time.sleep(0.01)
        trace_collector.record_trace("Agent3", "third", status="success")
        
        traces = trace_collector.get_traces()
        
        # Verify chronological order by checking timestamps
        assert len(traces) == 3
        assert traces[0]["action"] == "first"
        assert traces[1]["action"] == "second"
        assert traces[2]["action"] == "third"
        
        # Timestamps should be increasing
        t1 = traces[0]["timestamp"]
        t2 = traces[1]["timestamp"]
        t3 = traces[2]["timestamp"]
        assert t1 < t2 < t3


class TestObservabilityIntegration:
    """Test integration between metrics and trace collectors."""
    
    def test_combined_usage(self):
        """Test using both collectors together."""
        metrics = MetricsCollector()
        traces = TraceCollector()
        
        # Simulate workflow
        metrics.start_timer()
        traces.record_trace("Orchestrator", "start_assessment", status="success")
        
        metrics.record_metric("assessment_started", 1)
        traces.record_trace("Agent1", "process", status="success")
        
        metrics.record_metric("agents_completed", 1)
        traces.record_trace("Orchestrator", "complete_assessment", status="success")
        
        # Verify both collectors have data
        assert len(metrics.metrics) == 2
        assert len(traces.traces) == 3
    
    def test_save_both_to_directory(self):
        """Test saving both metrics and traces to same directory."""
        metrics = MetricsCollector()
        traces = TraceCollector()
        
        metrics.record_metric("test", 1)
        traces.record_trace("TestAgent", "test", status="success")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            metrics_file = Path(tmpdir) / "metrics.json"
            traces_file = Path(tmpdir) / "traces.json"
            
            metrics.save_metrics(str(metrics_file))
            traces.save_traces(str(traces_file))
            
            assert metrics_file.exists()
            assert traces_file.exists()


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
