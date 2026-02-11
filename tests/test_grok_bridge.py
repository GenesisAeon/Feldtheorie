"""Tests for integration.grok_bridge — layer monitor, safety hooks, metrics."""

from __future__ import annotations

import json

import numpy as np
import pytest

from integration.grok_bridge.layer_monitor import GrokLayerMonitor, LayerReading
from integration.grok_bridge.safety_hooks import GrokSafetyHooks, SafetyAlert, SafetyLevel
from integration.grok_bridge.metrics_collector import GrokMetricsCollector


# ===========================================================================
# Layer Monitor
# ===========================================================================


class TestGrokLayerMonitor:
    def test_record_reading(self) -> None:
        monitor = GrokLayerMonitor()
        arr = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        reading = monitor.record_reading("layer.0", arr)
        assert isinstance(reading, LayerReading)
        assert reading.layer_name == "layer.0"
        assert reading.sigma_phi > 0.0

    def test_get_readings_empty(self) -> None:
        monitor = GrokLayerMonitor()
        assert monitor.get_readings() == []

    def test_get_readings_filtered(self) -> None:
        monitor = GrokLayerMonitor()
        monitor.record_reading("layer.0", np.array([1.0, 2.0]))
        monitor.record_reading("layer.1", np.array([3.0, 4.0]))
        monitor.record_reading("layer.0", np.array([5.0, 6.0]))
        assert len(monitor.get_readings("layer.0")) == 2
        assert len(monitor.get_readings("layer.1")) == 1

    def test_get_latest(self) -> None:
        monitor = GrokLayerMonitor()
        monitor.record_reading("layer.0", np.array([1.0, 2.0]))
        monitor.record_reading("layer.0", np.array([10.0, 20.0]))
        latest = monitor.get_latest("layer.0")
        assert latest is not None
        assert latest.mean_activation == pytest.approx(15.0)

    def test_get_latest_missing(self) -> None:
        monitor = GrokLayerMonitor()
        assert monitor.get_latest("nonexistent") is None

    def test_sigma_phi_series(self) -> None:
        monitor = GrokLayerMonitor()
        for i in range(5):
            monitor.record_reading("layer.0", np.array([float(i + 1), float(i + 2)]))
        series = monitor.get_sigma_phi_series("layer.0")
        assert len(series) == 5

    def test_drift_report(self) -> None:
        monitor = GrokLayerMonitor()
        rng = np.random.default_rng(42)
        for _ in range(20):
            monitor.record_reading("enc.0", rng.normal(10, 2, size=50))
        report = monitor.get_drift_report("enc.0")
        assert report["n_readings"] == 20
        assert report["drift"] >= 0.0

    def test_drift_report_empty(self) -> None:
        monitor = GrokLayerMonitor()
        report = monitor.get_drift_report("missing")
        assert report["n_readings"] == 0

    def test_clear_history(self) -> None:
        monitor = GrokLayerMonitor()
        monitor.record_reading("layer.0", np.array([1.0, 2.0]))
        monitor.clear_history()
        assert monitor.get_readings() == []

    def test_max_history_enforced(self) -> None:
        monitor = GrokLayerMonitor(max_history=5)
        for i in range(10):
            monitor.record_reading("layer.0", np.array([float(i)]))
        assert len(monitor.get_readings()) == 5

    def test_constant_input_sigma_phi_zero(self) -> None:
        monitor = GrokLayerMonitor()
        reading = monitor.record_reading("layer.0", np.array([5.0, 5.0, 5.0]))
        assert reading.sigma_phi == pytest.approx(0.0)


# ===========================================================================
# Safety Hooks
# ===========================================================================


class TestGrokSafetyHooks:
    def test_classify_stable(self) -> None:
        safety = GrokSafetyHooks()
        assert safety.classify(0.08) == SafetyLevel.STABLE

    def test_classify_warning(self) -> None:
        safety = GrokSafetyHooks()
        assert safety.classify(0.06) == SafetyLevel.WARNING

    def test_classify_critical(self) -> None:
        safety = GrokSafetyHooks()
        assert safety.classify(0.04) == SafetyLevel.CRITICAL

    def test_check_stable_returns_none(self) -> None:
        safety = GrokSafetyHooks()
        monitor = GrokLayerMonitor()
        reading = monitor.record_reading("layer.0", np.ones(100) * 16.0 + np.arange(100) * 0.001)
        # This has very low CV, so will be critical or warning
        # Use a reading that is stable
        reading_stable = LayerReading(
            layer_name="layer.0",
            sigma_phi=0.08,
            mean_activation=16.0,
            std_activation=1.28,
            timestamp=0.0,
            shape=(100,),
        )
        assert safety.check_safety_thresholds(reading_stable) is None

    def test_check_warning_returns_alert(self) -> None:
        safety = GrokSafetyHooks()
        reading = LayerReading(
            layer_name="layer.0",
            sigma_phi=0.06,
            mean_activation=16.0,
            std_activation=0.96,
            timestamp=0.0,
            shape=(100,),
        )
        alert = safety.check_safety_thresholds(reading)
        assert alert is not None
        assert alert.level == "warning"
        assert alert.should_shutdown is False

    def test_check_critical_triggers_shutdown(self) -> None:
        safety = GrokSafetyHooks()
        reading = LayerReading(
            layer_name="enc.0",
            sigma_phi=0.04,
            mean_activation=10.0,
            std_activation=0.4,
            timestamp=0.0,
            shape=(50,),
        )
        alert = safety.check_safety_thresholds(reading)
        assert alert is not None
        assert alert.level == "critical"
        assert alert.should_shutdown is True
        assert safety.shutdown_requested is True

    def test_check_none_reading(self) -> None:
        safety = GrokSafetyHooks()
        assert safety.check_safety_thresholds(None) is None

    def test_generate_alert_manual(self) -> None:
        safety = GrokSafetyHooks()
        alert = safety.generate_alert("warning", "test alert", "layer.0")
        assert alert.level == "warning"
        assert alert.message == "test alert"

    def test_alert_summary(self) -> None:
        safety = GrokSafetyHooks()
        safety.generate_alert("warning", "w1")
        safety.generate_alert("critical", "c1")
        summary = safety.get_alert_summary()
        assert summary["warnings"] == 1
        assert summary["criticals"] == 1
        assert summary["total"] == 2

    def test_reset_shutdown(self) -> None:
        safety = GrokSafetyHooks()
        safety.generate_alert("critical", "emergency")
        assert safety.shutdown_requested is True
        safety.reset_shutdown()
        assert safety.shutdown_requested is False

    def test_warning_callback_invoked(self) -> None:
        calls = []
        safety = GrokSafetyHooks()
        safety.set_warning_callback(lambda alert: calls.append(alert))
        reading = LayerReading(
            layer_name="x", sigma_phi=0.06,
            mean_activation=1.0, std_activation=0.06,
            timestamp=0.0, shape=(10,),
        )
        safety.check_safety_thresholds(reading)
        assert len(calls) == 1

    def test_critical_callback_invoked(self) -> None:
        calls = []
        safety = GrokSafetyHooks()
        safety.set_critical_callback(lambda alert: calls.append(alert))
        reading = LayerReading(
            layer_name="x", sigma_phi=0.03,
            mean_activation=1.0, std_activation=0.03,
            timestamp=0.0, shape=(10,),
        )
        safety.check_safety_thresholds(reading)
        assert len(calls) == 1

    def test_clear_alerts(self) -> None:
        safety = GrokSafetyHooks()
        safety.generate_alert("warning", "w")
        safety.clear_alerts()
        assert safety.get_alerts() == []


# ===========================================================================
# Metrics Collector
# ===========================================================================


class TestGrokMetricsCollector:
    def _make_collector(self) -> GrokMetricsCollector:
        monitor = GrokLayerMonitor()
        safety = GrokSafetyHooks()
        monitor._attached_layers = ["layer.0", "layer.1"]
        rng = np.random.default_rng(42)
        for _ in range(10):
            monitor.record_reading("layer.0", rng.normal(16, 1, size=50))
            monitor.record_reading("layer.1", rng.normal(20, 2, size=50))
        return GrokMetricsCollector(monitor=monitor, safety=safety)

    def test_take_snapshot(self) -> None:
        collector = self._make_collector()
        snap = collector.take_snapshot()
        assert snap.overall_sigma_phi > 0.0
        assert "layer.0" in snap.layers
        assert "layer.1" in snap.layers

    def test_dashboard_no_snapshots(self) -> None:
        monitor = GrokLayerMonitor()
        safety = GrokSafetyHooks()
        collector = GrokMetricsCollector(monitor=monitor, safety=safety)
        dash = collector.get_dashboard()
        assert dash["snapshot_count"] == 0

    def test_dashboard_with_snapshots(self) -> None:
        collector = self._make_collector()
        collector.take_snapshot()
        collector.take_snapshot()
        dash = collector.get_dashboard()
        assert dash["snapshot_count"] == 2
        assert "latest" in dash
        assert "sigma_phi_history" in dash

    def test_export_json(self, tmp_path) -> None:
        collector = self._make_collector()
        collector.take_snapshot()
        path = tmp_path / "metrics.json"
        collector.export_json(path)
        assert path.exists()
        data = json.loads(path.read_text())
        assert data["snapshot_count"] == 1

    def test_clear(self) -> None:
        collector = self._make_collector()
        collector.take_snapshot()
        collector.clear()
        assert collector.get_snapshots() == []

    def test_max_snapshots_enforced(self) -> None:
        collector = self._make_collector()
        collector.max_snapshots = 3
        for _ in range(5):
            collector.take_snapshot()
        assert len(collector.get_snapshots()) == 3
