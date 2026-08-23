from npu_motion_studio.engines.openvino_lcm import _glyph_frame_prompt


def test_glyph_prompt_preserves_character_sheet_instead_of_removing_text() -> None:
    first = _glyph_frame_prompt("natural character morph", 1, 8)
    last = _glyph_frame_prompt("natural character morph", 7, 8)
    assert "one symbol per cell" in first
    assert "same character cells" in last
    assert "no extra objects" in first
    assert "no text" not in first
