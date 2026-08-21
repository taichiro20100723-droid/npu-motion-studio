import pytest

from npu_motion_studio.flowcache.planner import FlowCacheCosts, plan_flowcache


def test_planner_selects_mode_anchor_targets_under_ten_seconds() -> None:
    fast = plan_flowcache(10, mode="fast")
    fun = plan_flowcache(10, mode="fun")
    wow = plan_flowcache(10, mode="wow")

    assert (fast.anchor_count, fun.anchor_count, wow.anchor_count) == (2, 3, 4)
    assert all(plan.deadline_feasible for plan in (fast, fun, wow))
    assert all(plan.estimated_seconds <= 9.5 for plan in (fast, fun, wow))
    assert any("external-interpolation" in pair.passes for pair in wow.pair_repairs)


def test_planner_degrades_anchors_as_deadline_shrinks() -> None:
    roomy = plan_flowcache(10, mode="wow")
    tight = plan_flowcache(4, mode="wow")
    impossible = plan_flowcache(1, mode="wow")

    assert roomy.anchor_count > tight.anchor_count
    assert tight.degraded
    assert impossible.anchor_count == 1
    assert not impossible.deadline_feasible
    assert impossible.fallback_transition == "smart-cut"


def test_planner_accounts_for_elapsed_time() -> None:
    fresh = plan_flowcache(10, elapsed_seconds=0, mode="fun")
    late = plan_flowcache(10, elapsed_seconds=7, mode="fun")
    assert late.available_seconds == 3
    assert late.anchor_count < fresh.anchor_count


def test_anchor_times_include_both_ends() -> None:
    plan = plan_flowcache(10, duration_seconds=6, mode="fun")
    assert plan.anchor_times == (0.0, 3.0, 6.0)


def test_planner_uses_measured_cost_override() -> None:
    slow_npu = FlowCacheCosts(first_anchor_seconds=3.0, additional_anchor_seconds=3.0)
    plan = plan_flowcache(10, mode="wow", costs=slow_npu)
    assert plan.anchor_count == 2
    assert plan.deadline_feasible
    assert plan.degraded


@pytest.mark.parametrize(
    "kwargs",
    [
        {"deadline_seconds": 0},
        {"deadline_seconds": 10, "duration_seconds": 0},
        {"deadline_seconds": 10, "elapsed_seconds": -1},
    ],
)
def test_planner_rejects_invalid_time(kwargs: dict[str, float]) -> None:
    with pytest.raises(ValueError):
        plan_flowcache(**kwargs)
