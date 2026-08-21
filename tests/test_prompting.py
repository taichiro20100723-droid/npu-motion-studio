from pathlib import Path

from npu_motion_studio.prompting import (
    ActionKind,
    LocalPromptTranslator,
    classify_action,
    compact_prompt,
    contains_japanese,
    fallback_translate,
)


def test_detects_japanese_and_actions() -> None:
    assert contains_japanese("巨大ロボットが踊る")
    assert not contains_japanese("a robot dancing")
    assert classify_action("人物が激しくダンスする") == ActionKind.DANCE
    assert classify_action("空き地にビルを建てる") == ActionKind.BUILD
    assert classify_action("red car driving fast") == ActionKind.DRIVE
    assert classify_action("ビルが基礎から建っていく") == ActionKind.BUILD
    assert classify_action("赤い車が高速で走る") == ActionKind.DRIVE
    assert classify_action("ロボットが全速力で走り、脚を大きく動かす") == ActionKind.RUN


def test_fallback_translation_preserves_subject_and_action() -> None:
    result = fallback_translate("未来都市で巨大ロボットがダンスする")
    assert "giant robot" in result
    assert "futuristic city" in result
    assert "dance" in result


def test_translator_uses_fallback_without_local_model(tmp_path: Path) -> None:
    translator = LocalPromptTranslator(tmp_path / "missing")
    assert translator.translate("猫が走る") == fallback_translate("猫が走る")
    assert translator.translate("a cat running") == "a cat running"


def test_compact_prompt_preserves_subject_and_action_tail() -> None:
    text = "red robot " + "detail " * 40 + "dancing with both arms"
    result = compact_prompt(text, max_words=20)
    assert result.startswith("red robot")
    assert result.endswith("dancing with both arms")
    assert len(result.split()) == 20
