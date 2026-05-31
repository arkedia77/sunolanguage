#!/usr/bin/env python3
"""
build_handoff.py — N시리즈 핸드오프 정규 Serializer

엔진 raw 출력(lyrics_engine batch → data/lyrics_history/lyrics_batch_*.json)을
sunomusic 핸드오프 고정 스키마(Option A = N005형, DB-ready)로 변환한다.

배경: N006에서 엔진 raw를 손으로 스트립 덤프 직송 → bpm/genre/creator 등 DB필드 누락 회귀.
이 스크립트가 raw → DB-ready 변환을 단일 경로로 고정해 스키마 드리프트를 종결한다.
(2026-05-30, sunomusic 회신으로 발각된 핸드오프 스키마 드리프트 대응)

사용법:
  python3 scripts/build_handoff.py <raw_batch.json> --batch N007 \\
      [--seed "K-Ballad piano emotional"] [--drift 0.6] [--market KR2] \\
      [--engine serendipity_engine_v2] [--energy Medium] \\
      [--out data/n007_handoff.json]

출력: {"batches": {batch_id: [songs...]}, "metadata": {...}}  (N005 최상위 구조와 동일)
"""
import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SCHEMA_VERSION = "optionA_v1"
SOURCE_PROJECT = "sunolanguage"
CREATOR = "sunolanguage"
LYRICIST = "lyrics_rag_v2"
DEFAULT_MARKET = "KR2"
DEFAULT_ENERGY = "Medium"
DEFAULT_ENGINE = "serendipity_engine_v2"

# Option A 고정 키 순서 (N005형). sunomusic insert_n_series.py 매핑 기준.
OPTION_A_KEYS = [
    "source_project", "batch", "batch_line", "batch_position",
    "title", "lyrics", "style_prompt", "status",
    "genre", "genre_mode", "bpm", "key_signature", "energy", "char_count",
    "song_form", "creator", "market", "agent", "lyricist",
    "theme", "sub_theme", "seed", "drift",
    "sp_validation", "lyrics_validation", "coherence",
    "bracket_sections", "genre_group",
]

# INSERT 차단되는 필수 키 (비면 에러)
REQUIRED_NONEMPTY = ["title", "lyrics", "style_prompt", "genre_group"]


def extract_genre(sp: str) -> str:
    """SP 오프닝에서 장르 구문 추출 (§1.10 SP 오프닝 문법: 첫 문장 = 장르).
    'Jazz trio ballad featuring a baritone...' → 'Jazz trio ballad'
    """
    if not sp:
        return ""
    first = re.split(r"[.\n]", sp.strip(), maxsplit=1)[0].strip()
    # featuring/with/over 앞까지가 장르 핵심
    cut = re.split(r"\s+(featuring|with|over|driven|led)\b", first, maxsplit=1,
                   flags=re.IGNORECASE)[0].strip()
    return (cut or first)[:120]


def derive_genre_mode(lyrics: str) -> str:
    """가사에 브래킷 외 실제 가사 행이 있으면 vocal, 없으면 instrumental."""
    if not lyrics:
        return "instrumental"
    for line in lyrics.splitlines():
        s = line.strip()
        if s and not s.startswith("["):
            return "vocal"
    return "instrumental"


def verdict_of(val) -> str:
    """validation dict/str → 'PASS'/'FAIL' 문자열."""
    if isinstance(val, dict):
        return val.get("verdict", "UNKNOWN")
    if isinstance(val, str):
        return val
    return "UNKNOWN"


def coherence_of(item: dict):
    """coherence는 lyrics_validation.coherence_score에서 추출."""
    lv = item.get("lyrics_validation")
    if isinstance(lv, dict) and "coherence_score" in lv:
        return round(float(lv["coherence_score"]), 4)
    if "coherence" in item and item["coherence"] is not None:
        return round(float(item["coherence"]), 4)
    return None


def map_song(item: dict, batch: str, position: int, *, market: str,
             energy: str, engine: str, seed: str, drift) -> dict:
    """엔진 raw item 1건 → Option A 곡 레코드 1건."""
    sp = item.get("sp") or item.get("style_prompt") or ""
    lyrics = item.get("lyrics") or ""
    title = item.get("title") or item.get("display_title") or item.get("temp_title") or ""

    return {
        "source_project": SOURCE_PROJECT,
        "batch": batch,
        "batch_line": f"{batch}_{position:02d}",
        "batch_position": position,
        "title": title,
        "lyrics": lyrics,
        "style_prompt": sp,
        "status": "pending",
        "genre": extract_genre(sp),
        "genre_mode": derive_genre_mode(lyrics),
        "bpm": item.get("bpm"),                  # 엔진 미생산 → None
        "key_signature": item.get("key_signature"),  # 엔진 미생산 → None
        "energy": item.get("energy") or energy,
        "char_count": item.get("sp_length") or len(sp),
        "song_form": item.get("song_form_type") or item.get("song_form") or "",
        "creator": CREATOR,
        "market": market,
        "agent": engine,
        "lyricist": LYRICIST,
        "theme": item.get("theme"),
        "sub_theme": item.get("sub_theme"),
        "seed": seed,
        "drift": drift,
        "sp_validation": verdict_of(item.get("sp_validation")),
        "lyrics_validation": verdict_of(item.get("lyrics_validation")),
        "coherence": coherence_of(item),
        "bracket_sections": item.get("bracket_sections"),
        "genre_group": item.get("genre_group"),
    }


def load_raw(path: Path):
    """raw 입력 로드. list거나 {songs|results|items: [...]} dict 모두 지원."""
    data = json.loads(path.read_text())
    if isinstance(data, list):
        return data, {}
    if isinstance(data, dict):
        meta = data.get("metadata", {})
        for k in ("songs", "results", "items"):
            if k in data and isinstance(data[k], list):
                return data[k], meta
    raise ValueError(f"인식 불가 raw 형식: {path}")


def validate(songs: list) -> list:
    """필수 키 검증. 위반 곡 목록 반환 (빈 리스트 = 통과)."""
    problems = []
    for s in songs:
        missing = [k for k in REQUIRED_NONEMPTY if not s.get(k)]
        if missing:
            problems.append((s.get("batch_line", "?"), missing))
    return problems


def main():
    ap = argparse.ArgumentParser(description="N시리즈 핸드오프 정규 Serializer (Option A)")
    ap.add_argument("raw", help="엔진 raw batch json (data/lyrics_history/lyrics_batch_*.json)")
    ap.add_argument("--batch", required=True, help="배치 ID (예: N007)")
    ap.add_argument("--seed", default="", help="생성 seed")
    ap.add_argument("--drift", type=float, default=None, help="drift 값")
    ap.add_argument("--market", default=DEFAULT_MARKET)
    ap.add_argument("--energy", default=DEFAULT_ENERGY)
    ap.add_argument("--engine", default=DEFAULT_ENGINE, help="agent/engine 이름")
    ap.add_argument("--patches", default="", help="콤마구분 패치 목록")
    ap.add_argument("--out", default=None, help="출력 경로 (기본 data/{batch소문자}_handoff.json)")
    args = ap.parse_args()

    raw_path = Path(args.raw)
    if not raw_path.is_absolute():
        raw_path = PROJECT_ROOT / raw_path
    if not raw_path.exists():
        sys.exit(f"❌ raw 파일 없음: {raw_path}")

    items, raw_meta = load_raw(raw_path)
    # raw 사이드카 metadata가 있으면 CLI 미지정값 보충
    seed = args.seed or raw_meta.get("seed", "")
    drift = args.drift if args.drift is not None else raw_meta.get("drift")
    engine = args.engine if args.engine != DEFAULT_ENGINE else raw_meta.get("engine", args.engine)

    songs = [
        map_song(item, args.batch, i + 1, market=args.market, energy=args.energy,
                 engine=engine, seed=seed, drift=drift)
        for i, item in enumerate(items)
    ]

    problems = validate(songs)
    if problems:
        print("❌ 필수 키 누락 — INSERT 차단됨:", file=sys.stderr)
        for line, missing in problems:
            print(f"   {line}: {missing}", file=sys.stderr)
        sys.exit(1)

    themes = sorted({s["theme"] for s in songs if s.get("theme")})
    patches = [p.strip() for p in args.patches.split(",") if p.strip()] or raw_meta.get("patches", [])

    out = {
        "batches": {args.batch: songs},
        "metadata": {
            "schema_version": SCHEMA_VERSION,
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "batch": args.batch,
            "count": len(songs),
            "engine": engine,
            "seed": seed,
            "drift": drift,
            "market": args.market,
            "themes": themes,
            "patches": patches,
            "clips_per_song": 2,
            "clips_note": "Suno Create당 2클립 (uuid1/uuid2). 4클립 필요시 배치별 명시.",
            "source_raw": raw_path.name,
        },
    }

    out_path = Path(args.out) if args.out else PROJECT_ROOT / "data" / f"{args.batch.lower()}_handoff.json"
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2))

    # 요약
    coh = [s["coherence"] for s in songs if s["coherence"] is not None]
    print(f"✅ {args.batch} 핸드오프 생성: {out_path}")
    print(f"   곡 수: {len(songs)} | 스키마: {SCHEMA_VERSION} ({len(OPTION_A_KEYS)}키)")
    print(f"   필수키 검증: PASS | SP검증 PASS: {sum(1 for s in songs if s['sp_validation']=='PASS')}/{len(songs)}"
          f" | 가사검증 PASS: {sum(1 for s in songs if s['lyrics_validation']=='PASS')}/{len(songs)}")
    if coh:
        print(f"   coherence avg: {sum(coh)/len(coh):.3f} | char_count avg: {sum(s['char_count'] for s in songs)//len(songs)}")
    print(f"   genre_group: {dict((g, sum(1 for s in songs if s['genre_group']==g)) for g in sorted({s['genre_group'] for s in songs}))}")


if __name__ == "__main__":
    main()
