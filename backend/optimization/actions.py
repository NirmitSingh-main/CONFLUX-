from dataclasses import dataclass, field


@dataclass
class Action:
    """
    Represents an action that CONFLUX can consider.
    """

    action_id: str
    name: str
    description: str

    resource_requirements: dict[str, float] = field(
        default_factory=dict
    )

    applicable_events: list[str] = field(
        default_factory=list
    )

    enabled: bool = True


class ActionRegistry:
    """
    Registry of actions available to the CONFLUX
    decision-making system.
    """

    def __init__(self):
        self.actions: dict[str, Action] = {}

        self._register_default_actions()

    def register(self, action: Action) -> None:
        """Register a new action."""

        if action.action_id in self.actions:
            raise ValueError(
                f"Action '{action.action_id}' is already registered."
            )

        self.actions[action.action_id] = action

    def _register_default_actions(self) -> None:
        """Register the actions used by the CONFLUX prototype."""

        self.register(
            Action(
                action_id="MONITOR",
                name="Continue Monitoring",
                description=(
                    "Continue monitoring the affected condition "
                    "without taking an active intervention."
                ),
                applicable_events=[
                    "ANOMALY",
                    "CLOSE_APPROACH",
                    "ENVIRONMENTAL_ANOMALY",
                    "COMPOUND_EVENT",
                ],
            )
        )

        self.register(
            Action(
                action_id="REQUEST_MORE_DATA",
                name="Request More Data",
                description=(
                    "Collect additional observations before "
                    "making an operational decision."
                ),
                applicable_events=[
                    "ANOMALY",
                    "ENVIRONMENTAL_ANOMALY",
                    "COMPOUND_EVENT",
                ],
            )
        )

        self.register(
            Action(
                action_id="REDUCE_ACTIVITY",
                name="Reduce Spacecraft Activity",
                description=(
                    "Reduce non-essential spacecraft activity "
                    "to limit exposure to an abnormal condition."
                ),
                resource_requirements={
                    "power": 0.0,
                },
                applicable_events=[
                    "THERMAL_ANOMALY",
                    "ENVIRONMENTAL_ANOMALY",
                    "COMPOUND_EVENT",
                ],
            )
        )

        self.register(
            Action(
                action_id="ORBIT_ADJUSTMENT",
                name="Perform Orbit Adjustment",
                description=(
                    "Perform a planned orbital maneuver to "
                    "address an orbital conjunction."
                ),
                resource_requirements={
                    "fuel": 10.0,
                },
                applicable_events=[
                    "ORBITAL_CONJUNCTION",
                    "CLOSE_APPROACH",
                    "CRITICAL_CLOSE_APPROACH",
                    "SAFETY_DISTANCE_VIOLATION",
                ],
            )
        )

        self.register(
            Action(
                action_id="SAFE_MODE",
                name="Enter Safe Mode",
                description=(
                    "Place the spacecraft into a predefined "
                    "safe operational configuration."
                ),
                applicable_events=[
                    "ANOMALY",
                    "THERMAL_ANOMALY",
                    "ENVIRONMENTAL_ANOMALY",
                    "COMPOUND_EVENT",
                ],
            )
        )

    def get(self, action_id: str) -> Action | None:
        """Return an action by its ID."""

        return self.actions.get(action_id)

    def get_all(self) -> list[Action]:
        """Return all registered actions."""

        return list(self.actions.values())

    def get_applicable_actions(
        self,
        event_type: str,
    ) -> list[Action]:
        """Return enabled actions applicable to an event."""

        return [
            action
            for action in self.actions.values()
            if action.enabled
            and event_type in action.applicable_events
        ]

    def disable(self, action_id: str) -> None:
        """Disable an action."""

        action = self.get(action_id)

        if action is None:
            raise ValueError(
                f"Action '{action_id}' does not exist."
            )

        action.enabled = False

    def enable(self, action_id: str) -> None:
        """Enable an action."""

        action = self.get(action_id)

        if action is None:
            raise ValueError(
                f"Action '{action_id}' does not exist."
            )

        action.enabled = True