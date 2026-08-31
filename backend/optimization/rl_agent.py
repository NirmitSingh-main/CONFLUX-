from typing import Any

from backend.mission.resource_manager import ResourceManager
from backend.optimization.actions import Action, ActionRegistry
from backend.optimization.optimizer import ActionOptimizer


class RLAgent:
    """
    Reinforcement-learning interface for CONFLUX.

    The current implementation provides a deterministic
    baseline policy. A trained RL policy can replace the
    selection method later without changing the rest of
    the architecture.
    """

    def __init__(
        self,
        action_registry: ActionRegistry | None = None,
        optimizer: ActionOptimizer | None = None,
    ):
        self.action_registry = (
            action_registry
            or ActionRegistry()
        )

        self.optimizer = (
            optimizer
            or ActionOptimizer(
                self.action_registry
            )
        )

    def build_state(
        self,
        mission_state: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Build the state representation used by the agent.
        """

        return {
            "mission_id": mission_state.get(
                "mission_id"
            ),
            "status": mission_state.get(
                "status",
                "NOMINAL",
            ),
            "active_events": mission_state.get(
                "active_events",
                [],
            ),
            "active_anomalies": mission_state.get(
                "active_anomalies",
                [],
            ),
            "affected_systems": mission_state.get(
                "affected_systems",
                [],
            ),
            "priorities": mission_state.get(
                "priorities",
                {},
            ),
            "conflicts": mission_state.get(
                "conflicts",
                [],
            ),
        }

    def select_action(
        self,
        mission_state: dict[str, Any],
        event: dict[str, Any],
        resource_manager: ResourceManager,
    ) -> Action | None:
        """
        Select an action for the current mission state.

        The current baseline delegates feasibility and
        deterministic ranking to the ActionOptimizer.
        """

        state = self.build_state(
            mission_state
        )

        # Keep the state available for a future trained policy.
        _ = state

        evaluation = self.optimizer.select_action(
            event,
            resource_manager,
        )

        if evaluation is None:
            return None

        return evaluation.action

    def evaluate_actions(
        self,
        mission_state: dict[str, Any],
        event: dict[str, Any],
        resource_manager: ResourceManager,
    ) -> list[dict[str, Any]]:
        """
        Evaluate candidate actions and return their
        decision information.
        """

        state = self.build_state(
            mission_state
        )

        _ = state

        evaluations = self.optimizer.evaluate(
            event,
            resource_manager,
        )

        return [
            {
                "action_id": evaluation.action.action_id,
                "name": evaluation.action.name,
                "score": evaluation.score,
                "applicable": evaluation.applicable,
                "resources_available": (
                    evaluation.resources_available
                ),
                "reason": evaluation.reason,
            }
            for evaluation in evaluations
        ]