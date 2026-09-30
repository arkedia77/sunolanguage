"""장르·보컬·분위기 선택 → Suno 스타일 프롬프트(SP) 조립.

원칙
- 분위기·악기·보컬 서술어는 **코퍼스 관측 어휘만** 쓴다: `sunolang.db` expr_concepts 를
  읽기 전용으로 열어 attested_count 를 그 자리에서 읽고, 문턱 미만·dead zone 은 거절한다.
  (수치를 이 파일에 옮겨 적지 않는다 — 값은 한 곳에서만.)
- 장르 라벨은 **요청층**이다(우리가 Suno에 달라고 쓰는 말이지, Suno가 그렇게 들었다는 관측이 아니다).
  그래서 provenance 에 layer=request 로 따로 적는다.
- SP 1000자 상한.

배포(2026-09-30): SP 는 목적×장르×보컬의 **결정론 함수**다 ⇒ 전 조합을 미리 계산해
`sp_presets.json` 으로 동봉하면 공개 호스트(leoserver)에 **코퍼스 DB 를 올리지 않아도 된다**.
  - DB 가 있으면 **DB 가 정본**이고 프리셋은 쓰지 않는다(여기서 재는 게 항상 우선).
  - DB 가 없으면 프리셋을 읽는다. 없는 조합이면 **거절**한다(조용히 지어내지 않는다).
  - ⛔자를 두 벌 두지 않으려고 `--verify` 를 둔다: 프리셋 전건을 DB 로 다시 계산해 **한 글자라도
    다르면 실패**. 프리셋 생성(`--emit`)은 DB 가 있어야만 된다.
"""
import json
import sqlite3
from pathlib import Path

import templates

DB = Path(__file__).resolve().parents[2] / "sunolang.db"
PRESETS = Path(__file__).resolve().parent / "sp_presets.json"
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
# 목적(카드) → 분위기 관측 어휘 · BPM — ★정본은 templates.py 하나뿐(여기 복제하지 않는다)
MOODS = templates.MOODS
TEMPO = templates.TEMPO


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


def preset_key(occasion: str, genre: str, vocal: str) -> str:
    return f"{occasion}|{genre}|{vocal}"


def _from_presets(occasion: str, genre: str, vocal: str) -> dict:
    """DB 가 없는 배포용 — 미리 계산해 둔 조합을 읽는다. 없으면 거절."""
    if not PRESETS.is_file():
        raise ValueError(f"코퍼스 DB({DB.name})도 프리셋({PRESETS.name})도 없습니다 — SP 를 만들 수 없습니다")
    key = preset_key(occasion, genre, vocal)
    data = json.loads(PRESETS.read_text(encoding="utf-8"))
    if key not in data:
        raise ValueError(f"프리셋에 없는 조합: {key} (DB 없이는 새 조합을 만들 수 없습니다)")
    out = dict(data[key])
    out["from_presets"] = True   # ★어디서 온 값인지 남긴다
    return out


def build_sp(occasion: str, genre: str, vocal: str) -> dict:
    if occasion not in MOODS:
        raise ValueError(f"없는 템플릿: {occasion!r}")
    if not DB.is_file():
        return _from_presets(occasion, genre, vocal)
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


def all_combos():
    return [(o, g, v) for o in MOODS for g in GENRES for v in VOCALS]


def _emit():
    if not DB.is_file():
        raise SystemExit(f"⛔ 프리셋 생성은 DB 가 있어야 합니다: {DB}")
    out = {preset_key(o, g, v): build_sp(o, g, v) for o, g, v in all_combos()}
    PRESETS.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"✅ {PRESETS.name} — {len(out)}조합 ({PRESETS.stat().st_size:,}바이트)")


def _verify():
    """프리셋 == DB 재계산. ★한 글자라도 다르면 실패(자가 두 벌이 되는 걸 여기서 막는다)."""
    if not DB.is_file():
        raise SystemExit(f"⛔ 대조는 DB 가 있어야 합니다: {DB}")
    if not PRESETS.is_file():
        raise SystemExit(f"⛔ 프리셋이 없습니다: {PRESETS}")
    data = json.loads(PRESETS.read_text(encoding="utf-8"))
    combos = all_combos()
    missing = [preset_key(*c) for c in combos if preset_key(*c) not in data]
    extra = [k for k in data if k not in {preset_key(*c) for c in combos}]
    diff = []
    for o, g, v in combos:
        k = preset_key(o, g, v)
        if k in data and data[k]["sp"] != build_sp(o, g, v)["sp"]:
            diff.append(k)
    bad = bool(missing or extra or diff)
    print(("❌" if bad else "✅") + f" 대조 {len(combos)}조합 — 누락 {len(missing)} · 잉여 {len(extra)} · 불일치 {len(diff)}")
    for k in (missing + extra + diff)[:10]:
        print("   ", k)
    raise SystemExit(1 if bad else 0)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="SP 조립 · 프리셋 생성/대조")
    ap.add_argument("--emit", action="store_true", help=f"전 조합을 {PRESETS.name} 으로 (DB 필요)")
    ap.add_argument("--verify", action="store_true", help="프리셋 == DB 재계산 대조 (DB 필요)")
    a = ap.parse_args()
    if a.emit:
        _emit()
    elif a.verify:
        _verify()
    else:
        for o, g, v in all_combos():
            r = build_sp(o, g, v)
            print(f"{o:12s} {g:9s} {v:7s} {r['sp_chars']:4d}  {r['sp']}")
