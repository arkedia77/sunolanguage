"""장르·보컬·분위기 선택 → Suno 스타일 프롬프트(SP) 조립.

원칙
- 분위기·악기·보컬 서술어는 **코퍼스 관측 어휘만** 쓴다: `sunolang.db` expr_concepts 를
  읽기 전용으로 열어 attested_count 를 그 자리에서 읽고, 문턱 미만·dead zone 은 거절한다.
  (수치를 이 파일에 옮겨 적지 않는다 — 값은 한 곳에서만.)
- 장르 라벨은 **요청층**이다(우리가 Suno에 달라고 쓰는 말이지, Suno가 그렇게 들었다는 관측이 아니다).
  그래서 provenance 에 layer=request 로 따로 적는다.
- SP 1000자 상한.
"""
import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parents[2] / "sunolang.db"
MIN_ATTESTED = 30
SP_MAX = 1000

# 장르: 화면 선택지 → 요청층 라벨 + 결합할 관측 어휘(악기·질감)
GENRES = {
    "ballad":   {"label": "발라드",   "request": "Korean pop ballad",       "terms": ["piano", "strings"]},
    "acoustic": {"label": "어쿠스틱", "request": "acoustic pop",            "terms": ["acoustic guitar"]},
    "trot":     {"label": "트로트",   "request": "Korean trot",             "terms": []},
    "gospel":   {"label": "가스펠",   "request": "gospel soul",             "terms": ["piano"]},
}
VOCALS = {
    "male":   {"label": "남성 보컬", "terms": ["male vocals"]},
    "female": {"label": "여성 보컬", "terms": ["female vocals"]},
}
# 목적(카드) → 분위기 관측 어휘
MOODS = {
    "birthday": ["bright", "warm"],
    "anniversary": ["warm", "intimate"],
    "thanks": ["warm", "gentle"],
    "cheer": ["bright"],
    "comfort": ["gentle", "soft", "intimate"],
    "parents": ["warm", "tender"],
}
TEMPO = {"birthday": 100, "anniversary": 76, "thanks": 80, "cheer": 110, "comfort": 70, "parents": 74}


def _lookup(terms):
    """terms → [(term, attested_count, category, dict_version)] ; 없거나 문턱 미만이면 예외."""
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    try:
        out = []
        for t in terms:
            row = con.execute(
                "select attested_count, category, dict_version, is_dead_zone from expr_concepts where suno_term=?",
                (t,),
            ).fetchone()
            if row is None:
                raise ValueError(f"코퍼스에 없는 어휘: {t!r}")
            cnt, cat, ver, dead = row
            if dead or cnt < MIN_ATTESTED:
                raise ValueError(f"관측 부족/데드존 어휘: {t!r} (attested={cnt}, dead={dead})")
            out.append({"term": t, "attested_count": cnt, "category": cat, "dict_version": ver, "layer": "observed"})
        return out
    finally:
        con.close()


def build_sp(occasion: str, genre: str, vocal: str) -> dict:
    g, v = GENRES[genre], VOCALS[vocal]
    mood = MOODS[occasion]
    observed = _lookup(mood + g["terms"] + v["terms"])
    words = {o["term"]: o["term"] for o in observed}
    parts = [
        f"{', '.join(words[m] for m in mood)} {g['request']}",
        f"{TEMPO[occasion]} BPM",
    ]
    if g["terms"]:
        parts.append(", ".join(words[t] for t in g["terms"]))
    parts.append(", ".join(words[t] for t in v["terms"]))
    parts.append("clear Korean lyrics, heartfelt gift song")
    sp = ", ".join(parts)
    if len(sp) > SP_MAX:
        raise ValueError(f"SP {len(sp)}자 > {SP_MAX}")
    return {
        "sp": sp,
        "sp_chars": len(sp),
        "provenance": observed
        + [{"term": g["request"], "layer": "request", "note": "장르 라벨=요청층(관측 아님)"},
           {"term": "clear Korean lyrics, heartfelt gift song", "layer": "request", "note": "용도 서술=요청층"}],
        "min_attested": MIN_ATTESTED,
    }


if __name__ == "__main__":
    import json
    for occ in MOODS:
        for gen in GENRES:
            r = build_sp(occ, gen, "female")
            print(occ, gen, r["sp_chars"], r["sp"])
    print(json.dumps(build_sp("birthday", "ballad", "male"), ensure_ascii=False, indent=1))
