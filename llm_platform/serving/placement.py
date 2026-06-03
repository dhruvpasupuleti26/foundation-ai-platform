"""Execution placement resolution for local serving runtimes.

The platform needs a normalized way to express where a model should run.
Placements are intentionally capability-oriented rather than backend-specific so
the same deployment request shape can be reused across CUDA, Apple Metal MPS,
and plain CPU environments.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class PlacementAvailability:
    """Availability snapshot for runtime placements.

    Attributes:
        cpu: Whether CPU execution is available.
        cuda: Whether CUDA execution is available.
        mps: Whether Apple Metal Performance Shaders is available.
    """

    cpu: bool = True
    cuda: bool = False
    mps: bool = False

    def as_list(self) -> list[str]:
        """Return the available placements in deterministic order."""
        placements: list[str] = []
        if self.cuda:
            placements.append("cuda")
        if self.mps:
            placements.append("mps")
        if self.cpu:
            placements.append("cpu")
        return placements


def discover_placement_availability() -> PlacementAvailability:
    """Detect placement availability for the current process.

    Returns:
        Placement availability derived from the installed PyTorch runtime. If
        PyTorch is unavailable, CPU is treated as the only supported placement.
    """
    try:
        import torch
    except ImportError:
        return PlacementAvailability(cpu=True, cuda=False, mps=False)

    mps_backend = getattr(getattr(torch, "backends", None), "mps", None)
    return PlacementAvailability(
        cpu=True,
        cuda=bool(torch.cuda.is_available()),
        mps=bool(mps_backend and mps_backend.is_built() and mps_backend.is_available()),
    )


def resolve_placement(
    preferred: str | None,
    fallbacks: list[str] | None = None,
    availability: PlacementAvailability | None = None,
) -> str:
    """Resolve a usable placement from a preferred value and fallback list.

    Args:
        preferred: Preferred placement requested by the caller.
        fallbacks: Ordered fallback placement list.
        availability: Optional precomputed availability snapshot.

    Returns:
        The first supported placement in priority order.

    Raises:
        ValueError: If no requested placement is available.
    """
    availability = availability or discover_placement_availability()
    candidates = [candidate for candidate in [preferred, *(fallbacks or []), "cpu"] if candidate]
    available = set(availability.as_list())
    for candidate in candidates:
        normalized = candidate.lower()
        if normalized in available:
            return normalized
    raise ValueError(f"No requested placements are available. Requested={candidates}, available={availability.as_list()}")
