from datetime import datetime
from typing import Any


class EventEngine:
    """
    Convert intelligence outputs into standardized
    mission events.
    """

    def __init__(self):
        self.events: list[dict[str, Any]] = []

    def _create_event(
        self,
        event_type: str,
        source: str,
        description: str,
        timestamp: datetime | None = None,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create and store a mission event."""

        event = {
            "event_type": event_type,
            "source": source,
            "timestamp": timestamp or datetime.utcnow(),
            "description": description,
            "data": data or {},
        }

        self.events.append(event)

        return event

    def process(
        self,
        intelligence_results: dict[str, dict[str, Any]],
        timestamp: datetime | None = None,
    ) -> list[dict[str, Any]]:
        """
        Convert intelligence results into mission events.
        """

        generated_events = []

        for source, result in intelligence_results.items():

            if not result:
                continue

            if result.get("anomaly_detected") is True:
                generated_events.append(
                    self._create_event(
                        event_type="ANOMALY",
                        source=source,
                        description=(
                            f"Anomaly detected by {source}."
                        ),
                        timestamp=timestamp,
                        data=result,
                    )
                )

            if result.get("environmental_anomaly") is True:
                generated_events.append(
                    self._create_event(
                        event_type="ENVIRONMENTAL_ANOMALY",
                        source=source,
                        description=(
                            f"Environmental anomaly detected "
                            f"by {source}."
                        ),
                        timestamp=timestamp,
                        data=result,
                    )
                )

            if result.get("collision_risk") is True:
                generated_events.append(
                    self._create_event(
                        event_type="ORBITAL_CONJUNCTION",
                        source=source,
                        description=(
                            "Orbital safety distance violation "
                            "detected."
                        ),
                        timestamp=timestamp,
                        data=result,
                    )
                )

            elif result.get("event_type") in {
                "CLOSE_APPROACH",
                "CRITICAL_CLOSE_APPROACH",
            }:
                generated_events.append(
                    self._create_event(
                        event_type="ORBITAL_CONJUNCTION",
                        source=source,
                        description=(
                            "Close orbital approach detected."
                        ),
                        timestamp=timestamp,
                        data=result,
                    )
                )

        return generated_events

    def get_events(self) -> list[dict[str, Any]]:
        """Return all generated mission events."""

        return self.events

    def clear_events(self) -> None:
        """Clear all stored mission events."""

        self.events.clear()