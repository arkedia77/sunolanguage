# 한국어 프래그먼트 영역변환 v0 (2026-07-12) — 글로서리 변환/가드 단위 테스트
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from reference_matcher import hangul_ratio, ko_mood_translate  # noqa: E402


def test_hangul_ratio():
    assert hangul_ratio("밤의 라가 — 자정의 명상") > 0.3
    assert hangul_ratio("Sitar with buzzing strings") == 0.0
    assert hangul_ratio("nangs — 사이키델릭의 순간적 확장") > 0.3


def test_glossary_translates_attested_targets():
    terms, unmapped = ko_mood_translate("고독과 평화, 명상의 시간", set())
    # 고독→solitary/lonely, 평화→peaceful, 명상→meditative 전부 attested 타깃
    assert "solitary" in terms and "peaceful" in terms and "meditative" in terms


def test_glossary_skips_existing_keywords():
    # 이미 mood_keywords에 있는 영어어는 중복 투입 금지
    terms, _ = ko_mood_translate("고독한 명상", {"meditative"})
    assert "meditative" not in terms
    assert "solitary" in terms


def test_deadzone_targets_not_emitted():
    # 달빛/우주/마법 = 글로서리 명시 빈 배열(dead-zone 타깃 부재) → 변환 0, 미등재 아님
    terms, unmapped = ko_mood_translate("달빛과 우주의 마법", set())
    assert terms == []
    assert "달빛" not in unmapped  # 등재돼 있으나 타깃 없음 — 미등재로 분류 금지


def test_unmapped_reported_honestly():
    _, unmapped = ko_mood_translate("시타르의 물결", set())
    assert "시타르" in unmapped or "물결" in unmapped
