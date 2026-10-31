"""Fail-closed behavior for the Gazebo-only avoidance prototype."""
import math
import tempfile
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import autonomous

class SensorTests(unittest.TestCase):
    def test_blocked_range_interrupts_forward(self):
        with tempfile.TemporaryDirectory() as temp:
            stop = Path(temp) / "stop"
            state = autonomous.SensorState()
            state.forward = True
            with patch.object(autonomous.walk_controller, "STOP_FILE", stop):
                state.scan(SimpleNamespace(ranges=[0.25], range_min=0.03))
                self.assertTrue(stop.exists())
    def test_requires_fresh_range_and_camera(self):
        state = autonomous.SensorState()
        state.scan(SimpleNamespace(ranges=[1.2], range_min=0.03))
        self.assertIsNone(state.reading())
        state.image(SimpleNamespace(width=2, height=2, data=bytes(12)))
        self.assertEqual(state.reading(), 1.2)
        state.camera_time = time.monotonic() - 4
        self.assertIsNone(state.reading())
    def test_invalid_ranges_never_report_clear(self):
        state = autonomous.SensorState()
        state.camera_time = time.monotonic()
        state.scan(SimpleNamespace(ranges=[math.nan, -1], range_min=0.03))
        self.assertIsNone(state.reading())

if __name__ == "__main__":
    unittest.main()
