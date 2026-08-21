from __future__ import annotations

import math

import numpy as np
from PIL import Image

from npu_motion_studio.prompting import ActionKind

_DANCE_PHASES = (
    "feet planted, body preparing for the first beat",
    "full body stepping hard to the left, right arm raised high, legs clearly separated",
    "full body stepping hard to the right, left arm raised high, torso twisting",
    "deep rhythmic crouch, both arms spread wide, dynamic silhouette",
    "energetic upward jump, both feet off the ground, arms overhead",
    "landing into a wide stance, torso leaning forward, arms swinging down",
    "fast spin, clothing and hair trailing around the body",
    "strong final dance pose, full body visible, wide arms and legs",
)

_BUILD_PHASES = (
    "an empty prepared construction site with marked foundations",
    "foundation and first structural columns visibly appearing",
    "steel framework rising to one quarter of the final height",
    "half-built structure with cranes actively adding floors",
    "three-quarter height, walls and windows being installed",
    "nearly complete exterior with active construction equipment",
    "completed new building, clean facade, construction just finishing",
    "fully completed building in a dramatic hero view",
)


def frame_prompt(base_prompt: str, action: ActionKind, index: int, count: int) -> str:
    phase = 0.0 if count <= 1 else index / (count - 1)
    subject = base_prompt
    if action == ActionKind.DANCE:
        detail = _DANCE_PHASES[round(phase * (len(_DANCE_PHASES) - 1))]
        motion = f"the exact same subject and outfit, {detail}, energetic dance choreography"
    elif action == ActionKind.BUILD:
        detail = _BUILD_PHASES[round(phase * (len(_BUILD_PHASES) - 1))]
        subject = "fixed-camera cinematic time-lapse of one central futuristic building project"
        motion = (
            f"the exact same construction site over time, {detail}, "
            "clear structural progress in the center, cranes and workers active, "
            "do not show the completed central tower before the final phase"
        )
    elif action == ActionKind.DRIVE:
        position = ("left", "center-left", "center", "center-right", "far right")[
            min(4, round(phase * 4))
        ]
        motion = (
            f"the exact same vehicle now at the {position} of frame, racing fast, "
            "wheels spinning, suspension moving, strong background motion"
        )
    elif action == ActionKind.RUN:
        gait = ("push off", "long stride", "airborne stride", "foot strike")[index % 4]
        motion = f"the exact same subject, full-body running, {gait}, limbs clearly changing pose"
    elif action == ActionKind.FLY:
        motion = (
            f"the exact same subject flying dynamically, altitude phase {phase:.2f}, "
            "large visible movement through space"
        )
    elif action == ActionKind.TRANSFORM:
        motion = (
            f"the subject at transformation progress {round(phase * 100)} percent, "
            "origin anatomy and materials visibly becoming the requested destination form"
        )
    elif action == ActionKind.FLOW:
        motion = (
            f"the same scene at the next moment, flow phase {phase:.2f}, "
            "large organic motion in water fire smoke clouds and fabric"
        )
    else:
        motion = (
            f"the same scene at time phase {phase:.2f}, clear cinematic camera orbit, "
            "foreground and background move by different amounts"
        )
    return (
        f"{subject}, {motion}, coherent anatomy, consistent face, consistent colors, "
        "sharp cinematic frame, no text, no watermark"
    )


def strength_for(action: ActionKind, mode: str, *, has_input_image: bool) -> float:
    base = {"fast": 0.46, "fun": 0.64, "wow": 0.72}[mode]
    if action in {ActionKind.BUILD, ActionKind.TRANSFORM}:
        base += 0.08
    if action == ActionKind.BUILD:
        base = max(base, 0.72)
    if action == ActionKind.DANCE and has_input_image:
        base += 0.04
    return min(base, 0.78)


def warp_condition(image: Image.Image, action: ActionKind, index: int, count: int) -> Image.Image:
    import cv2

    source = np.ascontiguousarray(np.asarray(image.convert("RGB"), dtype=np.uint8))
    height, width = source.shape[:2]
    phase = 0.0 if count <= 1 else index / (count - 1)
    wave = math.sin(phase * math.tau)
    beat = math.sin(phase * math.tau * 2.0)

    if action in {ActionKind.FLOW, ActionKind.TRANSFORM}:
        grid_x, grid_y = np.meshgrid(
            np.arange(width, dtype=np.float32), np.arange(height, dtype=np.float32)
        )
        amplitude = 10.0 if action == ActionKind.FLOW else 6.0 + phase * 8.0
        grid_x += np.sin(grid_y / 24.0 + phase * math.tau).astype(np.float32) * amplitude
        grid_y += np.sin(grid_x / 37.0 - phase * math.tau).astype(np.float32) * amplitude * 0.5
        warped = cv2.remap(
            source,
            grid_x,
            grid_y,
            interpolation=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REFLECT_101,
        )
        return Image.fromarray(warped)

    if action == ActionKind.DANCE:
        angle, scale = wave * 10.0, 1.03 + abs(beat) * 0.035
        move_x, move_y = wave * 42.0, -abs(beat) * 26.0
    elif action == ActionKind.DRIVE:
        angle, scale = -wave * 2.0, 1.05
        move_x, move_y = (phase - 0.5) * 90.0, -abs(wave) * 5.0
    elif action == ActionKind.RUN:
        angle, scale = wave * 7.0, 1.04 + abs(beat) * 0.02
        move_x, move_y = wave * 40.0, -abs(beat) * 30.0
    elif action == ActionKind.FLY:
        angle, scale = wave * 6.0, 0.98 + phase * 0.1
        move_x, move_y = (phase - 0.5) * 50.0, -wave * 36.0
    elif action == ActionKind.BUILD:
        angle, scale = 0.0, 0.94 + phase * 0.1
        move_x, move_y = 0.0, (1.0 - phase) * 28.0
    else:
        angle, scale = wave * 2.5, 1.02 + phase * 0.04
        move_x, move_y = wave * 30.0, -phase * 12.0

    matrix = cv2.getRotationMatrix2D((width / 2.0, height / 2.0), angle, scale)
    matrix[0, 2] += move_x
    matrix[1, 2] += move_y
    warped = cv2.warpAffine(
        source,
        matrix,
        (width, height),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REFLECT_101,
    )
    return Image.fromarray(warped)
