import numpy as np
import pytest

from npu_motion_studio.flowcache.fields import (
    DenseMotionField,
    bilinear_warp,
    correlated_noise_fields,
    disocclusion_mask,
    forward_backward_cycle_consistency_mask,
)


def constant_field(height: int, width: int, dx: float, dy: float) -> DenseMotionField:
    return DenseMotionField.from_components(
        np.full((height, width), dx, dtype=np.float32),
        np.full((height, width), dy, dtype=np.float32),
    )


def test_dense_motion_field_validates_and_is_immutable() -> None:
    field = DenseMotionField.zeros(2, 3)
    assert field.vectors.shape == (2, 3, 2)
    assert field.vectors.dtype == np.float32
    with pytest.raises(ValueError, match="shape"):
        DenseMotionField(np.zeros((2, 3), dtype=np.float32))
    with pytest.raises(ValueError, match="finite"):
        DenseMotionField(np.full((1, 1, 2), np.nan, dtype=np.float32))
    with pytest.raises(ValueError):
        field.vectors[0, 0, 0] = 1


def test_bilinear_warp_identity_and_half_pixel() -> None:
    image = np.array([[0.0, 10.0, 20.0]], dtype=np.float32)
    identity = DenseMotionField.zeros(1, 3)
    np.testing.assert_allclose(bilinear_warp(image, identity), image)

    shifted = constant_field(1, 3, 0.5, 0.0)
    np.testing.assert_allclose(
        bilinear_warp(image, shifted, border_mode="edge"),
        np.array([[5.0, 15.0, 20.0]], dtype=np.float32),
    )


def test_bilinear_warp_rgb_and_constant_border() -> None:
    image = np.arange(12, dtype=np.float32).reshape(2, 2, 3)
    outside = constant_field(2, 2, -4.0, 0.0)
    result = bilinear_warp(image, outside, border_mode="constant", border_value=7.0)
    assert result.shape == image.shape
    np.testing.assert_allclose(result, 7.0)


def test_forward_backward_cycle_consistency_detects_border_and_bad_inverse() -> None:
    forward = constant_field(3, 4, 1.0, 0.0)
    backward = constant_field(3, 4, -1.0, 0.0)
    consistent = forward_backward_cycle_consistency_mask(
        forward,
        backward,
        absolute_tolerance=0.01,
    )
    assert consistent[:, :-1].all()
    assert not consistent[:, -1].any()

    bad_backward = DenseMotionField.zeros(3, 4)
    bad = forward_backward_cycle_consistency_mask(
        forward,
        bad_backward,
        absolute_tolerance=0.01,
    )
    assert not bad.any()


def test_disocclusion_mask_finds_translation_hole() -> None:
    identity = disocclusion_mask(DenseMotionField.zeros(3, 4))
    assert not identity.any()

    translated = disocclusion_mask(constant_field(3, 4, 1.0, 0.0))
    assert translated[:, 0].all()
    assert not translated[:, 1:].any()


def test_correlated_noise_is_reproducible_and_has_expected_correlation() -> None:
    first = correlated_noise_fields(3, (128, 128), correlation=0.8, seed=42)
    second = correlated_noise_fields(3, (128, 128), correlation=0.8, seed=42)
    np.testing.assert_array_equal(first, second)
    observed = float(np.corrcoef(first[0].ravel(), first[1].ravel())[0, 1])
    assert observed == pytest.approx(0.8, abs=0.03)


def test_correlated_noise_accepts_motion_transport() -> None:
    fields = (DenseMotionField.zeros(8, 8), constant_field(8, 8, 1.0, 0.0))
    noise = correlated_noise_fields(
        2,
        (8, 8, 4),
        correlation=1.0,
        seed=7,
        motion_fields=fields,
    )
    assert noise.shape == (2, 8, 8, 4)
    np.testing.assert_allclose(noise[1, :, :-1], noise[0, :, 1:])


@pytest.mark.parametrize("correlation", [-0.1, 1.1])
def test_correlated_noise_rejects_invalid_correlation(correlation: float) -> None:
    with pytest.raises(ValueError, match="correlation"):
        correlated_noise_fields(2, (4, 4), correlation=correlation)
