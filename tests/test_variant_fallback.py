"""가사변형(별도 계보) 풀고갈 폴백 배선 회귀 잠금.

match_sp_differentiated(use_variants=True)가 정규 코퍼스 전 폴백 소진(theme_search=∅)
후에만 variant_search로 빈 섹션을 채우는지, 기본(off)에선 절대 호출 안 하는지,
코어섹션(verse/pre_chorus/bridge) ≥3행 집계 불변·비-네이티브 표기(song_id=0·
source='variation')를 검증. 네트워크/모델 없이 theme_search·variant_search 몽키패치.
"""
import lyrics_retriever as LR

SP = "genre: k-pop ballad, mood: melancholic tender"

# 상호 Jaccard가 낮은(중복가드 통과) 뚜렷이 다른 한국어 라인들
DISTINCT = [
    "창밖에 빗물이 흘러내려",
    "우산도 없이 걷던 그 밤",
    "네 이름을 조용히 불러본다",
    "돌아오지 않을 메아리처럼",
    "혼자 남겨진 거리 위에서",
]


def _mk(text, sid, section, cos=0.9):
    return {"score": 0.9, "source": "variation", "text": text,
            "source_song_id": sid, "original_text": text, "section_tag": section,
            "cosine_to_src": cos, "payload": {"variant_text": text, "section_tag": section},
            "point_id": sid}


def _variants_by_section(section_tag=None, **_):
    if section_tag in ("verse", "chorus", "bridge"):
        base = {"verse": 900, "chorus": 800, "bridge": 700}[section_tag]
        return [_mk(DISTINCT[i], base + i, section_tag) for i in range(len(DISTINCT))]
    return []


def test_variant_fallback_fills_core_and_marks_nonnative(monkeypatch):
    monkeypatch.setattr(LR, "theme_search", lambda *a, **k: [])       # 정규 코퍼스 완전 고갈
    monkeypatch.setattr(LR, "variant_search",
                        lambda q, section_tag=None, **k: _variants_by_section(section_tag))
    res = LR.match_sp_differentiated(
        SP, form=["verse", "chorus", "bridge"],
        client=object(), model=object(), use_variants=True)

    verse = res["verse_1"]
    assert verse, "풀고갈 시 verse가 변형으로 채워져야 함"
    p = verse[0]["payload"]
    assert p["source"] == "variation"
    assert p["song_id"] == 0, "비-네이티브(원장 오염 없음) 표기"
    lines = [l for l in p["text"].split("\n") if l.strip()]
    assert len(lines) >= LR.MIN_VERSE_LINES, "코어섹션 ≥3행 집계 불변"

    chorus = res["chorus_1"]
    assert chorus and chorus[0]["payload"]["source"] == "variation"


def test_variant_fallback_off_by_default(monkeypatch):
    monkeypatch.setattr(LR, "theme_search", lambda *a, **k: [])
    called = {"hit": False}

    def _spy(*a, **k):
        called["hit"] = True
        return []
    monkeypatch.setattr(LR, "variant_search", _spy)

    res = LR.match_sp_differentiated(
        SP, form=["verse", "chorus"], client=object(), model=object())  # use_variants 기본 False
    assert called["hit"] is False, "opt-in — 기본 경로는 변형 미참조"
    assert res["verse_1"] == [], "정규 고갈 시 빈 섹션(코어 1행/누출보다 빈 섹션)"


def test_variant_core_shortfall_returns_empty(monkeypatch):
    # 변형이 3행 미만이면 코어섹션은 채우지 않고 빈 섹션 유지(1행 방지 불변)
    monkeypatch.setattr(LR, "theme_search", lambda *a, **k: [])
    monkeypatch.setattr(LR, "variant_search",
                        lambda q, section_tag=None, **k:
                        [_mk(DISTINCT[0], 901, "verse")] if section_tag == "verse" else [])
    res = LR.match_sp_differentiated(
        SP, form=["verse"], client=object(), model=object(), use_variants=True)
    assert res["verse_1"] == [], "1행뿐인 변형으로 코어섹션 채우지 않음"
