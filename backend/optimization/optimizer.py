from dataclasses import dataclass
from typing import Any

from backend.mission.resource_manager import ResourceManager
from backend.optimization.actions import Action, ActionRegistry


@dataclass
class ActionEvaluation:
    """
    Result of evaluating one possible action.
    """

    action: Action
    applicable: bool
    resources_available: bool
    score: float
    reason: str


class ActionOptimizer:
    """
    Select the most suitable available action for
    the current mission event.

    This is a deterministic baseline optimizer.
    """

    PRIORITY_WEIGHTS = {
        "CRITICAL": 4.0,
        "HIGH": 3.0,
        "MEDIUM": 2.0,
        "LOW": 1.0,
    }

    ACTION_PREFERENCES = {
        "ORBIT_ADJUSTMENT": 4.0,
        "SAFE_MODE": 3.0,
        "REDUCE_ACTIVITY": 2.5,
        "REQUEST_MORE_DATA": 2.0,
        "MONITOR": 1.0,
    }

    def __init__(
        self,
        action_registry: ActionRegistry | None = None,
    ):
        self.action_registry = (
            action_registry
            or ActionRegistry()
        )

    def _priority_weight(
        self,
        priority: str,
    ) -> float:
        """Convert operational priority to a comparison weight."""

        return self.PRIORITY_WEIGHTS.get(
            priority,
            1.0,
        )

    def _action_preference(
        self,
        action_id: str,
    ) -> float:
        """Return the baseline preference for an action."""

        return self.ACTION_PREFERENCES.get(
            action_id,
            0.0,
        )

    def evaluate(
        self,
        event: dict[str, Any],
        resource_manager: ResourceManager,
    ) -> list[ActionEvaluation]:
        """
        Evaluate all actions applicable to an event.
        """

        event_type = event.get("event_type")

        if not event_type:
            return []

        priority = event.get(
            "priority",
            "LOW",
        )

        priority_weight = self._priority_weight(
            priority
        )

        actions = (
            self.action_registry
            .get_applicable_actions(event_type)
        )

        evaluations = []

        for action in actions:

            resources_available = (
                resource_manager.check_availability(
                    action.resource_requirements
                )
            )

            if not resources_available:
                evaluations.append(
                    ActionEvaluation(
                        action=action,
                        applicable=True,
                        resources_available=False,
                        score=float("-inf"),
                        reason=(
                            "Required mission resources "
                            "are unavailable."
                        ),
                    )
                )

                continue

            score = (
                priority_weight
                + self._action_preference(
                    action.action_id
                )
            )

            evaluations.append(
                ActionEvaluation(
                    action=action,
                    applicable=True,
                    resources_available=True,
                    score=score,
                    reason=(
                        "Action is applicable and "
                        "required resources are available."
                    ),
                )
            )

        evaluations.sort(
            key=lambda evaluation: evaluation.score,
            reverse=True,
        )

        return evaluations

    def select_action(
        self,
        event: dict[str, Any],
        resource_manager: ResourceManager,
    ) -> ActionEvaluation | None:
        """
        Select the highest-ranked feasible action.
        """

        evaluations = self.evaluate(
            event,
            resource_manager,
        )

        feasible = [
            evaluation
            for evaluation in evaluations
            if evaluation.resources_available
        ]

        if not feasible:
            return None

        return feasible[0]