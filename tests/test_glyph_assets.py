from pathlib import Path

from npu_motion_studio.glyph_assets import (
    create_glyph_assets,
    make_glyph_text,
    render_glyph_svg,
    render_source_sheet_svg,
)


def test_glyph_text_is_stable_and_style_sensitive() -> None:
    alien = make_glyph_text("NPU MOTION", "alien")
    assert alien
    assert alien == make_glyph_text(" NPU   MOTION ", "alien")
    assert alien != make_glyph_text("NPU MOTION", "rune")


def test_svg_is_an_animated_vector_asset() -> None:
    glyph_text, svg = render_glyph_svg("ROBOT → DOG", "cyber")
    assert glyph_text
    assert svg.startswith('<svg xmlns="http://www.w3.org/2000/svg"')
    assert "<animateTransform" in svg
    assert "data-source=" in svg
    assert "ROBOT → DOG" in svg


def test_source_sheet_keeps_original_characters_for_npu(tmp_path: Path) -> None:
    svg = render_source_sheet_svg("A B C 123", "alien")
    assert 'data-stage="npu-character-sheet"' in svg
    assert ">A</text>" in svg
    assert ">1</text>" in svg
    assert "THE NPU CHANGES THE SHAPES" in svg


def test_assets_include_downloadable_svg_text_and_font(tmp_path: Path) -> None:
    assets = create_glyph_assets(tmp_path, "NPU MOTION", "signal")
    assert assets.svg_path.is_file()
    assert assets.source_svg_path.is_file()
    assert assets.text_path.is_file()
    assert assets.svg_path.read_text(encoding="utf-8").startswith("<svg")
    assert "npu-character-sheet" in assets.source_svg_path.read_text(encoding="utf-8")
    assert assets.text_path.read_text(encoding="utf-8").strip() == assets.glyph_text
    # fontTools is a runtime dependency; this confirms the actual font export,
    # rather than only the optional SVG/TXT fallback, is wired up.
    assert assets.font_path is not None
    assert assets.font_path.is_file()
    assert assets.font_format == "ttf"
