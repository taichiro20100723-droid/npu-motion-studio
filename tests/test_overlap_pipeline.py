from npu_motion_studio.engines.overlap_pipeline import _interval_counts


def test_interval_counts_preserve_exact_video_frame_count() -> None:
    counts = _interval_counts(120, 11)
    assert len(counts) == 11
    assert sum(counts) + 1 == 120
    assert max(counts) - min(counts) <= 1


def test_interval_counts_support_loop_pair() -> None:
    counts = _interval_counts(64, 4)
    assert counts == (16, 16, 16, 15)
