from dataclasses import dataclass
from typing import Any

from backend.mission.resource_manager import ResourceManager
from backend.optimization.actions import ActionRegistry


@dataclass
class SafetyValidation:
    """
    Result of validating a proposed mission action.
    """

    approved: bool
    action_id: str
    reasons: list[str]


class SafetyKernel:
    """
    Final safety gate for CONFLUX decisions.

    The safety kernel applies hard constraints and can
    reject an action proposed by the optimization layer.
    """

    def __init__(
        self,
        action_registry: ActionRegistry | None = None,
    ):
        self.action_registry = (
            action_registry
            or ActionRegistry()
        )

    def validate(
        self,
        action_id: str,
        event: dict[str, Any],
        resource_manager: ResourceManager,
        conflicts: list[dict[str, Any]] | None = None,
    ) -> SafetyValidation:
        """
        Validate a proposed action.

        An action is approved only when all required
        safety checks pass.
        """

        reasons = []

        action = self.action_registry.get(
            action_id
        )

        if action is None:
            return SafetyValidation(
                approved=False,
                action_id=action_id,
                reasons=[
                    "Action does not exist."
                ],
            )

        if not action.enabled:
            return SafetyValidation(
                approved=False,
                action_id=action_id,
                reasons=[
                    "Action is disabled."
                ],
            )

        event_type = event.get("event_type")

        if (
            event_type
            and event_type not in action.applicable_events
        ):
            return SafetyValidation(
                approved=False,
                action_id=action_id,
                reasons=[
                    (
                        f"Action '{action_id}' is not "
                        f"applicable to event "
                        f"'{event_type}'."
                    )
                ],
            )

        if not resource_manager.check_availability(
            action.resource_requirements
        ):
            reasons.append(
                "Required mission resources are unavailable."
            )

        if conflicts:
            for conflict in conflicts:
                conflict_type = conflict.get(
                    "conflict_type"
                )

                if conflict_type:
                    reasons.append(
                        f"Active mission conflict: "
                        f"{conflict_type}."
                    )

        if reasons:
            return SafetyValidation(
                approved=False,
                action_id=action_id,
                reasons=reasons,
            )

        return SafetyValidation(
            approved=True,
            action_id=action_id,
            reasons=[
                "All safety checks passed."
            ],
        )

    def validate_and_reserve(
        self,
        action_id: str,
        event: dict[str, Any],
        resource_manager: ResourceManager,
        conflicts: list[dict[str, Any]] | None = None,
    ) -> SafetyValidation:
        """
        Validate an action and reserve its resources
        if validation succeeds.
        """

        validation = self.validate(
            action_id=action_id,
            event=event,
            resource_manager=resource_manager,
            conflicts=conflicts,
        )

        if not validation.approved:
            return validation

        action = self.action_registry.get(
            action_id
        )

        if action is None:
            return SafetyValidation(
                approved=False,
                action_id=action_id,
                reasons=[
                    "Action does not exist."
                ],
            )

        reserved = resource_manager.reserve(
            action.resource_requirements
        )

        if not reserved:
            return SafetyValidation(
                approved=False,
                action_id=action_id,
                reasons=[
                    "Resources became unavailable "
                    "during reservation."
                ],
            )

        return SafetyValidation(
            approved=True,
            action_id=action_id,
            reasons=[
                "Safety checks passed and resources "
                "were reserved."
            ],
        )