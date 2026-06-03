"""System Telemetry."""
from collections import defaultdict
from typing import Dict, List, Any

class TelemetryTracker:
    def __init__(self):
        self._latencies = defaultdict(list)
        self._call_counts = defaultdict(int)
