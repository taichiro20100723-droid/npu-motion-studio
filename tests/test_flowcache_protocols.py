import numpy as np

from npu_motion_studio.flowcache.protocols import (
    AnchorFrame,
    AnchorGenerationRequest,
    AnchorImageBackend,
    FlowCacheBackends,
    FrameInterpolationBackend,
    InpaintRepairBackend,
    InpaintRequest,
    InterpolationRequest,
)


class FakeAnchorBackend:
    backend_name = "fake-openvino"

    def generate_anchors(self, request: AnchorGenerationRequest) -> tuple[AnchorFrame, ...]:
        image = np.zeros((request.height, request.width, 3), dtype=np.uint8)
        return tuple(AnchorFrame(image, request.seed + index) for index in range(request.count))


class FakeInpaintBackend:
    backend_name = "fake-inpaint"

    def inpaint(self, request: InpaintRequest) -> np.ndarray:
        output = request.image.copy()
        output[request.mask] = 255
        return output


class FakeInterpolationBackend:
    backend_name = "fake-rife"

    def interpolate(self, request: InterpolationRequest) -> tuple[np.ndarray, ...]:
        return tuple(
            (request.first.astype(np.float32) + request.second.astype(np.float32)) / 2
            for _ in range(request.intermediate_count)
        )


def test_backend_protocols_are_runtime_replaceable() -> None:
    anchors = FakeAnchorBackend()
    inpaint = FakeInpaintBackend()
    interpolation = FakeInterpolationBackend()
    assert isinstance(anchors, AnchorImageBackend)
    assert isinstance(inpaint, InpaintRepairBackend)
    assert isinstance(interpolation, FrameInterpolationBackend)

    backends = FlowCacheBackends(anchors, inpaint, interpolation)
    frames = backends.anchors.generate_anchors(AnchorGenerationRequest("city", count=2))
    assert len(frames) == 2
    assert frames[1].seed == 1


def test_inpaint_and_interpolation_contracts_use_numpy_images() -> None:
    image = np.zeros((2, 2, 3), dtype=np.uint8)
    mask = np.array([[True, False], [False, False]])
    repaired = FakeInpaintBackend().inpaint(InpaintRequest(image, mask))
    assert repaired[0, 0].tolist() == [255, 255, 255]

    second = np.full_like(image, 100)
    middle = FakeInterpolationBackend().interpolate(
        InterpolationRequest(image, second, intermediate_count=1)
    )[0]
    np.testing.assert_allclose(middle, 50)
