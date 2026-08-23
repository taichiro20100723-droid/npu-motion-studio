from __future__ import annotations

import hashlib
import html
import re
from dataclasses import dataclass
from pathlib import Path

# The SVG poster is intentionally kept as one readable template; its long XML
# attributes are not Python source lines that need wrapping.
# ruff: noqa: E501


GLYPH_STYLES = ("alien", "rune", "signal", "cyber")
_STYLE_LABELS = {
    "alien": ("ALIEN", "#72f7e8", "#8b5cff", "#07151b"),
    "rune": ("RUNE", "#ffd56b", "#ff6a9f", "#1b0f17"),
    "signal": ("SIGNAL", "#8bb8ff", "#b36dff", "#0b1020"),
    "cyber": ("CYBER", "#ff6e9b", "#61f5ff", "#160b1a"),
}
_PALETTES = {
    "alien": "ȺƵƦƎØȜƟƧƸȢƩȽƱ",
    "rune": "ᚫᛇᚱᛟᚦᛉᚲᛞᛃᛒᛗᛏᛁ",
    "signal": "⌁⟟⟒⧖⫷⨳⟡◈⟁⌬⧉⟐",
    "cyber": "ΛƵΞØƧ∅ⱫɌƎ⟟◈ϟȻŦ",
}
_MARKS = ("", "\u0336", "\u0338", "\u035e", "\u0307", "\u0336\u0307")
_SAFE_TEXT = re.compile(r"\s+")


@dataclass(frozen=True, slots=True)
class GlyphAssets:
    glyph_text: str
    svg_text: str
    svg_path: Path
    text_path: Path
    font_path: Path | None
    font_format: str | None


def normalize_source(text: str) -> str:
    cleaned = _SAFE_TEXT.sub(" ", text.strip())
    return cleaned[:120]


def make_glyph_text(text: str, style: str = "alien") -> str:
    """Create a deterministic, copyable pseudo-alphabet from ordinary text."""
    if style not in GLYPH_STYLES:
        raise ValueError(f"unknown glyph style: {style}")
    source = normalize_source(text) or "NPU MOTION"
    palette = _PALETTES[style]
    output: list[str] = []
    for index, char in enumerate(source):
        if char == " ":
            output.append("  ")
            continue
        digest = hashlib.blake2s(
            f"{style}:{char}:{index}".encode(), digest_size=8
        ).digest()
        base = palette[digest[0] % len(palette)]
        mark_a = _MARKS[digest[1] % len(_MARKS)]
        mark_b = _MARKS[digest[2] % len(_MARKS)] if digest[3] % 3 == 0 else ""
        output.append(base + mark_a + mark_b)
    return "".join(output).strip()


def render_glyph_svg(text: str, style: str = "alien") -> tuple[str, str]:
    """Return (copyable glyph text, animated vector SVG poster)."""
    if style not in GLYPH_STYLES:
        raise ValueError(f"unknown glyph style: {style}")
    source = normalize_source(text) or "NPU MOTION"
    glyph_text = make_glyph_text(source, style)
    label, accent, accent_two, background = _STYLE_LABELS[style]
    escaped_source = html.escape(source, quote=True)
    escaped_glyph = html.escape(glyph_text, quote=True)
    length = max(1, len(glyph_text.replace(" ", "")))
    font_size = max(42, min(138, round(850 / length)))
    digest = hashlib.blake2s(f"{style}:{source}".encode(), digest_size=8).hexdigest()
    seed = int(digest[:8], 16)
    skew = -7 - seed % 9
    drift = 12 + seed % 22
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="576" viewBox="0 0 1024 576" role="img" aria-labelledby="title desc">
  <title id="title">{escaped_glyph}</title>
  <desc id="desc">Animated {label.lower()} glyph poster generated from {escaped_source}</desc>
  <metadata data-source="{escaped_source}" data-style="{style}" data-glyph="{escaped_glyph}" />
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop stop-color="{background}"/>
      <stop offset=".54" stop-color="{accent_two}" stop-opacity=".34"/>
      <stop offset="1" stop-color="#05070c"/>
    </linearGradient>
    <linearGradient id="ink" x1="0" y1="0" x2="1" y2="0">
      <stop stop-color="{accent}"/>
      <stop offset=".5" stop-color="#fff"/>
      <stop offset="1" stop-color="{accent_two}"/>
    </linearGradient>
    <filter id="glow" x="-30%" y="-60%" width="160%" height="220%">
      <feGaussianBlur stdDeviation="14" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="noise"><feTurbulence type="fractalNoise" baseFrequency=".012" numOctaves="2" seed="{seed % 31}" result="n"/><feColorMatrix in="n" type="saturate" values="0"/><feComponentTransfer><feFuncA type="table" tableValues="0 .12"/></feComponentTransfer><feBlend in="SourceGraphic" mode="screen"/></filter>
    <pattern id="grid" width="42" height="42" patternUnits="userSpaceOnUse"><path d="M42 0H0V42" fill="none" stroke="#fff" stroke-opacity=".075"/></pattern>
  </defs>
  <rect width="1024" height="576" fill="url(#bg)"/>
  <rect width="1024" height="576" fill="url(#grid)" opacity=".64"/>
  <g opacity=".25" filter="url(#glow)">
    <circle cx="150" cy="126" r="115" fill="{accent}"/>
    <circle cx="850" cy="440" r="150" fill="{accent_two}"/>
  </g>
  <g transform="skewX({skew})" filter="url(#noise)">
    <text x="512" y="320" text-anchor="middle" font-family="'Segoe UI Symbol','Noto Sans Symbols 2',sans-serif" font-size="{font_size}" font-weight="800" letter-spacing="9" fill="none" stroke="{accent}" stroke-opacity=".25" stroke-width="3">{escaped_glyph}</text>
    <text x="512" y="320" text-anchor="middle" font-family="'Segoe UI Symbol','Noto Sans Symbols 2',sans-serif" font-size="{font_size}" font-weight="800" letter-spacing="9" fill="url(#ink)" filter="url(#glow)">
      {escaped_glyph}
      <animateTransform attributeName="transform" type="translate" values="0 0;{drift} -4;0 0" dur="3.8s" repeatCount="indefinite"/>
    </text>
    <text x="512" y="320" text-anchor="middle" font-family="'Segoe UI Symbol','Noto Sans Symbols 2',sans-serif" font-size="{font_size}" font-weight="800" letter-spacing="9" fill="none" stroke="#fff" stroke-opacity=".72" stroke-width="1">
      {escaped_glyph}
      <animate attributeName="opacity" values=".05;.82;.05" dur="2.7s" repeatCount="indefinite"/>
      <animateTransform attributeName="transform" type="translate" values="{-drift} 4;0 0;{drift} -4" dur="2.7s" repeatCount="indefinite"/>
    </text>
  </g>
  <path d="M80 454H944" stroke="{accent}" stroke-opacity=".48" stroke-width="2"><animate attributeName="x1" values="80;140;80" dur="4.1s" repeatCount="indefinite"/></path>
  <text x="80" y="92" fill="{accent}" font-family="monospace" font-size="18" letter-spacing="6">NPU / GLYPH STAGE / {label}</text>
  <text x="80" y="505" fill="#fff" fill-opacity=".62" font-family="monospace" font-size="14" letter-spacing="2">SOURCE: {escaped_source[:56]}</text>
  <text x="944" y="505" text-anchor="end" fill="#fff" fill-opacity=".44" font-family="monospace" font-size="14">LOCAL VECTOR</text>
</svg>'''
    return glyph_text, svg


def _draw_notdef(pen: object) -> None:
    pen.moveTo((80, 0))
    pen.lineTo((80, 780))
    pen.lineTo((620, 780))
    pen.lineTo((620, 0))
    pen.closePath()
    pen.moveTo((150, 90))
    pen.lineTo((550, 90))
    pen.lineTo((550, 690))
    pen.lineTo((150, 690))
    pen.closePath()


def _draw_custom_glyph(pen: object, codepoint: int, style: str) -> None:
    digest = hashlib.blake2s(f"{style}:{codepoint}".encode(), digest_size=8).digest()
    left, right = 90, 710
    bottom, top = 0, 800
    pen.moveTo((left, bottom))
    pen.lineTo((left + 80 + digest[0] % 90, top))
    pen.lineTo((right - 70 - digest[1] % 100, top))
    pen.lineTo((right, bottom))
    pen.closePath()
    bars = 2 + digest[2] % 4
    for index in range(bars):
        y = 120 + index * (520 // max(1, bars - 1))
        offset = 25 + digest[(index + 3) % len(digest)] % 115
        pen.moveTo((left + offset, y))
        pen.lineTo((right - offset, y + 32 + digest[(index + 4) % len(digest)] % 42))
        pen.lineTo((right - offset - 40, y + 22))
        pen.lineTo((left + offset + 40, y - 10))
        pen.closePath()


def _build_ttf(path: Path, source: str, style: str) -> bool:
    try:
        from fontTools.fontBuilder import FontBuilder
        from fontTools.pens.ttGlyphPen import TTGlyphPen
    except ImportError:
        return False

    chars = list(dict.fromkeys(char for char in normalize_source(source) if char != " "))
    glyph_order = [".notdef", "space"] + [f"g{index:04x}" for index in range(len(chars))]
    glyphs: dict[str, object] = {}
    notdef_pen = TTGlyphPen(None)
    _draw_notdef(notdef_pen)
    glyphs[".notdef"] = notdef_pen.glyph()
    space_pen = TTGlyphPen(None)
    glyphs["space"] = space_pen.glyph()
    cmap: dict[int, str] = {32: "space"}
    metrics: dict[str, tuple[int, int]] = {".notdef": (800, 0), "space": (360, 0)}
    for index, char in enumerate(chars):
        glyph_name = glyph_order[index + 2]
        pen = TTGlyphPen(None)
        _draw_custom_glyph(pen, ord(char), style)
        glyphs[glyph_name] = pen.glyph()
        cmap[ord(char)] = glyph_name
        metrics[glyph_name] = (800, 0)

    builder = FontBuilder(1000, isTTF=True)
    builder.setupGlyphOrder(glyph_order)
    builder.setupCharacterMap(cmap)
    builder.setupGlyf(glyphs)
    builder.setupHorizontalMetrics(metrics)
    builder.setupHorizontalHeader(ascent=850, descent=-200)
    builder.setupOS2(
        sTypoAscender=850,
        sTypoDescender=-200,
        usWinAscent=850,
        usWinDescent=200,
    )
    builder.setupNameTable(
        {
            "familyName": "NPU Glyph Stage",
            "styleName": style.title(),
            "uniqueFontIdentifier": f"NPU Glyph Stage {style}",
            "fullName": f"NPU Glyph Stage {style.title()}",
            "psName": f"NPUGlyphStage-{style.title()}",
            "version": "Version 1.0",
        }
    )
    builder.setupPost()
    builder.setupMaxp()
    builder.save(path)
    return True


def create_glyph_assets(output_directory: Path, text: str, style: str) -> GlyphAssets:
    if style not in GLYPH_STYLES:
        raise ValueError(f"unknown glyph style: {style}")
    source = normalize_source(text) or "NPU MOTION"
    glyph_text, svg_text = render_glyph_svg(source, style)
    digest = hashlib.blake2s(f"{style}:{source}".encode(), digest_size=10).hexdigest()
    directory = output_directory / "glyphs"
    directory.mkdir(parents=True, exist_ok=True)
    svg_path = directory / f"{digest}.svg"
    text_path = directory / f"{digest}.txt"
    svg_path.write_text(svg_text, encoding="utf-8")
    text_path.write_text(glyph_text + "\n", encoding="utf-8")
    font_path = directory / f"{digest}-{style}.ttf"
    font_available = _build_ttf(font_path, source, style)
    if not font_available:
        font_path = None
    return GlyphAssets(
        glyph_text=glyph_text,
        svg_text=svg_text,
        svg_path=svg_path,
        text_path=text_path,
        font_path=font_path,
        font_format="ttf" if font_available else None,
    )
