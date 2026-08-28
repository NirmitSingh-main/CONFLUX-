from typing import Any


class ResourceManager:
    """
    Track and manage resources available to the mission.
    """

    def __init__(
        self,
        resources: dict[str, float] | None = None,
    ):
        self.resources = resources or {}
        self.reserved: dict[str, float] = {}

        for name, amount in self.resources.items():
            if amount < 0:
                raise ValueError(
                    f"Resource '{name}' cannot be negative."
                )

    def get_available(
        self,
        resource: str,
    ) -> float:
        """
        Return the currently available amount of a resource.
        """

        total = self.resources.get(resource, 0.0)
        reserved = self.reserved.get(resource, 0.0)

        return total - reserved

    def check_availability(
        self,
        requirements: dict[str, float],
    ) -> bool:
        """
        Check whether all required resources are available.
        """

        for resource, amount in requirements.items():

            if amount < 0:
                raise ValueError(
                    f"Required amount for '{resource}' "
                    "cannot be negative."
                )

            if self.get_available(resource) < amount:
                return False

        return True

    def reserve(
        self,
        requirements: dict[str, float],
    ) -> bool:
        """
        Reserve resources if they are available.

        Returns:
            True if reservation succeeds,
            False otherwise.
        """

        if not self.check_availability(requirements):
            return False

        for resource, amount in requirements.items():
            self.reserved[resource] = (
                self.reserved.get(resource, 0.0)
                + amount
            )

        return True

    def release(
        self,
        resources: dict[str, float],
    ) -> None:
        """
        Release previously reserved resources.
        """

        for resource, amount in resources.items():

            if amount < 0:
                raise ValueError(
                    f"Released amount for '{resource}' "
                    "cannot be negative."
                )

            current = self.reserved.get(
                resource,
                0.0,
            )

            self.reserved[resource] = max(
                0.0,
                current - amount,
            )

    def get_status(self) -> dict[str, Any]:
        """
        Return the current resource status.
        """

        return {
            resource: {
                "total": total,
                "reserved": self.reserved.get(
                    resource,
                    0.0,
                ),
                "available": self.get_available(
                    resource
                ),
            }
            for resource, total in self.resources.items()
        }