from typing import Any


class PriorityEngine:
    """
    Assign operational priorities to mission events.

    Priority represents how urgently an event should be
    considered by the mission decision system. It is not
    a physical probability or risk score.
    """

    PRIORITY_LEVELS = {
        "CRITICAL": 4,
        "HIGH": 3,
        "MEDIUM": 2,
        "LOW": 1,
    }

    DEFAULT_EVENT_PRIORITIES = {
        "SAFETY_DISTANCE_VIOLATION": "CRITICAL",
        "CRITICAL_CLOSE_APPROACH": "CRITICAL",
        "ORBITAL_CONJUNCTION": "HIGH",
        "ENVIRONMENTAL_ANOMALY": "HIGH",
        "COMPOUND_EVENT": "HIGH",
        "ANOMALY": "MEDIUM",
        "CLOSE_APPROACH": "MEDIUM",
    }

    def __init__(
        self,
        event_priorities: dict[str, str] | None = None,
    ):
        self.event_priorities = (
            event_priorities
            or self.DEFAULT_EVENT_PRIORITIES.copy()
        )

        for event_type, priority in self.event_priorities.items():
            if priority not in self.PRIORITY_LEVELS:
                raise ValueError(
                    f"Invalid priority '{priority}' "
                    f"for event '{event_type}'."
                )

    def get_priority(
        self,
        event: dict[str, Any],
    ) -> str:
        """
        Determine the operational priority of an event.
        """

        event_type = event.get("event_type")

        if event_type is None:
            return "LOW"

        return self.event_priorities.get(
            event_type,
            "LOW",
        )

    def assign_priority(
        self,
        event: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Add priority information to a single event.
        """

        priority = self.get_priority(event)

        prioritized_event = event.copy()

        prioritized_event["priority"] = priority
        prioritized_event["priority_value"] = (
            self.PRIORITY_LEVELS[priority]
        )

        return prioritized_event

    def prioritize(
        self,
        events: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Assign priorities to multiple events and return
        them ordered from highest to lowest priority.
        """

        prioritized_events = [
            self.assign_priority(event)
            for event in events
        ]

        prioritized_events.sort(
            key=lambda event: event["priority_value"],
            reverse=True,
        )

        return prioritized_events