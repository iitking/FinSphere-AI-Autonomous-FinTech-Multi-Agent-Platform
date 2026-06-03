"""
System Telemetry & Performance Metrics.
Tracks agent call frequencies, execution latency percentiles, and guardrail interventions.
"""

from __future__ import annotations

import time
from collections import defaultdict
from typing import Dict, List


class TelemetryTracker:
    def __init__(self):
        self._latencies: Dict[str, List[float]] = defaultdict(list)
        self._call_counts: Dict[str, int] = defaultdict(int)
        self._guardrail_blocks: int = 0

    def record_call(self, agent_name: str, latency: float):
        self._latencies[agent_name].append(latency)
        self._call_counts[agent_name] += 1

    def record_guardrail_block(self):
        self._guardrail_blocks += 1

    def summary(self) -> Dict[str, Any]:
        return {
            "total_agent_calls": sum(self._call_counts.values()),
            "by_agent": dict(self._call_counts),
            "guardrail_interceptions": self._guardrail_blocks,
        }


telemetry = TelemetryTracker()
