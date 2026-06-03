from __future__ import annotations

from llm_platform.serving.placement import PlacementAvailability, resolve_placement


def test_resolve_placement_prefers_requested_backend():
    placement = resolve_placement(
        preferred="mps",
        fallbacks=["cpu"],
        availability=PlacementAvailability(cpu=True, cuda=False, mps=True),
    )

    assert placement == "mps"


def test_resolve_placement_falls_back_to_cpu():
    placement = resolve_placement(
        preferred="cuda",
        fallbacks=["mps", "cpu"],
        availability=PlacementAvailability(cpu=True, cuda=False, mps=False),
    )

    assert placement == "cpu"
