from datetime import datetime
from typing import Any


class CompoundEventDetector:
    """
    Detect compound mission events by correlating
    events produced by different intelligence modules.
    """

    def __init__(
        self,
        minimum_sources: int = 2,
    ):
        if minimum_sources < 2:
            raise ValueError(
                "Minimum sources must be at least 2."
            )

        self.minimum_sources = minimum_sources

    def detect(
        self,
        events: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Detect compound events from individual mission events.

        A compound event is created when multiple different
        sources report events during the same analysis cycle.
        """

        if not events:
            return []

        sources = set()

        for event in events:
            source = event.get("source")

            if source:
                sources.add(source)

        if len(sources) < self.minimum_sources:
            return []

        event_types = [
            event.get("event_type")
            for event in events
            if event.get("event_type")
        ]

        compound_event = {
            "event_type": "COMPOUND_EVENT",
            "timestamp": datetime.utcnow(),
            "sources": sorted(sources),
            "source_count": len(sources),
            "component_events": events,
            "event_types": event_types,
            "description": (
                "Multiple independent mission sources "
                "reported abnormal conditions."
            ),
        }

        return [compound_event]