from typing import Any


class ConflictEngine:
    """
    Detect conflicts between simultaneous mission events.

    This module identifies situations where multiple events
    may require competing or incompatible responses.
    It does not make the final mission decision.
    """

    CONFLICT_RULES = {
        (
            "ORBITAL_CONJUNCTION",
            "ENVIRONMENTAL_ANOMALY",
        ): "ORBITAL_AND_ENVIRONMENTAL_CONFLICT",

        (
            "ORBITAL_CONJUNCTION",
            "ANOMALY",
        ): "ORBITAL_AND_SYSTEM_ANOMALY",

        (
            "ORBITAL_CONJUNCTION",
            "COMPOUND_EVENT",
        ): "ORBITAL_AND_COMPOUND_EVENT",

        (
            "ENVIRONMENTAL_ANOMALY",
            "COMPOUND_EVENT",
        ): "ENVIRONMENTAL_AND_COMPOUND_EVENT",
    }

    def _normalize_pair(
        self,
        event_type_1: str,
        event_type_2: str,
    ) -> tuple[str, str]:
        """
        Create a consistent ordering for two event types.
        """

        return tuple(
            sorted(
                [event_type_1, event_type_2]
            )
        )

    def detect(
        self,
        events: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Detect conflicts between events.
        """

        conflicts = []

        for i in range(len(events)):
            for j in range(i + 1, len(events)):

                event1 = events[i]
                event2 = events[j]

                type1 = event1.get("event_type")
                type2 = event2.get("event_type")

                if not type1 or not type2:
                    continue

                pair = self._normalize_pair(
                    type1,
                    type2,
                )

                conflict_type = None

                for rule_pair, rule_name in self.CONFLICT_RULES.items():
                    normalized_rule = self._normalize_pair(
                        rule_pair[0],
                        rule_pair[1],
                    )

                    if pair == normalized_rule:
                        conflict_type = rule_name
                        break

                if conflict_type is None:
                    continue

                conflicts.append(
                    {
                        "conflict_type": conflict_type,
                        "event1": event1,
                        "event2": event2,
                        "description": (
                            f"Potential conflict between "
                            f"{type1} and {type2}."
                        ),
                    }
                )

        return conflicts

    def has_conflict(
        self,
        events: list[dict[str, Any]],
    ) -> bool:
        """
        Return True if at least one conflict exists.
        """

        return bool(self.detect(events))