#!/usr/bin/env python3
"""
lyrics_batch_audit.py — T3-1 배치 감사 하니스 (가사워크플로우 보강안 Tier 3)

세션마다 수동 수행하던 배치 자가점검(크로스곡 오염/SP디렉티브/V1≠V2/1행섹션/
폼다양성/coherence 밴드)을 게이트로 코드화. corpus_quality_gate.py 철학 계승.

검사 항목 (N013/N014 자가점검 기준 그대로):
  1. coherence 밴드 분포 — <0.45 저 / 0.45~0.70 통제밴드 / >0.70 고
  2. 곡간(배치내) 가사 라인 Jaccard — >0.15 = 크로스곡 오염 FAIL
  3. 크로스배치 중첩 — history 디렉토리의 타 배치 곡 대비 Jaccard >0.15 WARN
     (history에는 미출고 드래프트/리롤 파일 포함 + 동일 코퍼스 검색이라 한계
      중첩은 구조적으로 발생. --fail-cross-batch 로 게이트 승격 가능)
  4. SP 디렉티브 누출 — is_sp_directive() 라인 검출 FAIL
  5. V1≠V2 — 동일 섹션타입 반복 간 텍스트 동일 FAIL
  6. 1행 코어섹션 — verse/pre_chorus/bridge 가창 1행 이하 FAIL
  7. 폼 다양성 / 제목 고유율 / 브래킷-SP 악기 일치율 — 리포트(게이트 아님)
  8. 곡내 자기반복 — 서로 다른 섹션타입에 동일 라인 출현(코러스 반복 제외) WARN

사용법:
  # 단일 배치 감사 (오프라인, exit 1 = hard fail 존재 → re-roll 대상)
  python3 scripts/lyrics_batch_audit.py audit data/lyrics_history/lyrics_batch_X.json
      [--history-dir data/lyrics_history] [--json out.json] [--jaccard 0.15]
  # N001~N014 coherence 분포 소급 측정 (DB, role_sunolanguage SELECT)
  python3 scripts/lyrics_batch_audit.py retro [--json out.json]
"""
import argparse
import itertools
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from corpus_quality_gate import is_sp_directive
from lyrics_validator import _parse_sections
from bracket_presets import extract_sp_instruments

BASE = Path(__file__).resolve().parent.parent
DEFAULT_HISTORY_DIR = BASE / "data" / "lyrics_history"

JACCARD_LIMIT = 0.15          # N013/N014 자가점검 기준 (이하=클린)
COH_BAND = (0.45, 0.70)       # coherence 통제밴드 [[project_suno_lyrics_drive_music]]
MIN_CORE_LINES = 2            # 코어섹션(verse/pre_chorus/bridge) 가창 최소 행수-1 초과 요구
CORE_SECTIONS = {"verse", "pre-chorus", "pre_chorus", "bridge"}

# N시리즈 gid 밴드 (retro용 — KANBAN/메모리 정본)
GID_BANDS = {
    "N001": (20311, 20320), "N002": (20321, 20330), "N003": (20341, 20350),
    "N004": (20351, 20360), "N005": (20361, 20370), "N006": (20371, 20380),
    "N007": (20381, 20390), "N008": (30001, 30010), "N009": (30011, 30020),
    "N010": (30021, 30030), "N011": (30031, 30040), "N012": (30041, 30050),
    "N013": (30051, 30060), "N014": (30061, 30070),
}


# ---------------------------------------------------------------- helpers

def vocal_lines(lyrics: str) -> list[str]:
    """가창 라인만 추출 — 브래킷 지문/빈줄 제외, 정규화."""
    out = []
    for line in lyrics.split("\n"):
        s = line.strip()
        if not s or s.startswith("["):
            continue
        out.append(re.sub(r"\s+", " ", s))
    return out


def jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def section_base(tag: str) -> str:
    return re.sub(r"\s*\d+$", "", tag.strip().lower()).replace("_", "-")


# ---------------------------------------------------------------- checks

def check_coherence(songs: list[dict]) -> dict:
    lo, hi = COH_BAND
    scores = []
    for s in songs:
        c = (s.get("lyrics_validation") or {}).get("coherence_score")
        if c is not None:
            scores.append((s.get("index"), s.get("title"), c))
    bands = {"low": [], "band": [], "high": []}
    for idx, title, c in scores:
        key = "low" if c < lo else ("band" if c <= hi else "high")
        bands[key].append({"index": idx, "title": title, "coherence": c})
    vals = [c for _, _, c in scores]
    return {
        "count": len(vals),
        "avg": round(sum(vals) / len(vals), 4) if vals else None,
        "min": min(vals) if vals else None,
        "max": max(vals) if vals else None,
        "band_limits": list(COH_BAND),
        "distribution": {k: len(v) for k, v in bands.items()},
        "low_songs": bands["low"],
        "high_songs": bands["high"],
    }


def check_cross_song(songs: list[dict], limit: float) -> list[dict]:
    """배치 내 곡간 라인셋 Jaccard — limit 초과 쌍 = 오염."""
    line_sets = [set(vocal_lines(s.get("lyrics", ""))) for s in songs]
    hits = []
    for i, j in itertools.combinations(range(len(songs)), 2):
        sim = jaccard(line_sets[i], line_sets[j])
        if sim > limit:
            hits.append({
                "pair": [songs[i].get("index"), songs[j].get("index")],
                "titles": [songs[i].get("title"), songs[j].get("title")],
                "jaccard": round(sim, 3),
                "shared_lines": sorted(line_sets[i] & line_sets[j])[:5],
            })
    return hits


def check_cross_batch(songs: list[dict], batch_path: Path,
                      history_dir: Path, limit: float) -> list[dict]:
    """타 배치 곡 대비 Jaccard — limit 초과 = 크로스배치 오염."""
    line_sets = [set(vocal_lines(s.get("lyrics", ""))) for s in songs]
    hits = []
    for other in sorted(history_dir.glob("lyrics_batch_*.json")):
        if other.resolve() == batch_path.resolve():
            continue
        try:
            others = json.loads(other.read_text())
        except (json.JSONDecodeError, OSError):
            continue
        if not isinstance(others, list):
            continue
        for o in others:
            o_set = set(vocal_lines(o.get("lyrics", "")))
            for i, mine in enumerate(line_sets):
                sim = jaccard(mine, o_set)
                if sim > limit:
                    hits.append({
                        "index": songs[i].get("index"),
                        "title": songs[i].get("title"),
                        "other_file": other.name,
                        "other_title": o.get("title"),
                        "jaccard": round(sim, 3),
                    })
    return hits


def check_sp_directive(songs: list[dict]) -> list[dict]:
    hits = []
    for s in songs:
        for line in vocal_lines(s.get("lyrics", "")):
            if is_sp_directive(line):
                hits.append({"index": s.get("index"), "title": s.get("title"),
                             "line": line})
    return hits


def check_verse_identity(songs: list[dict]) -> list[dict]:
    """동일 섹션타입 반복(verse 1 vs verse 2 등)이 텍스트까지 동일하면 FAIL."""
    hits = []
    for s in songs:
        groups = {}
        for tag, text in _parse_sections(s.get("lyrics", "")):
            base = section_base(tag)
            norm = "\n".join(vocal_lines(text))
            if norm:
                groups.setdefault(base, []).append(norm)
        for base, texts in groups.items():
            if base in ("chorus", "hook"):   # 코러스/훅 반복은 정상
                continue
            if len(texts) > 1 and len(set(texts)) < len(texts):
                hits.append({"index": s.get("index"), "title": s.get("title"),
                             "section": base})
    return hits


def check_thin_sections(songs: list[dict]) -> list[dict]:
    """코어섹션 가창 MIN_CORE_LINES 미만 = 1행섹션류 FAIL."""
    hits = []
    for s in songs:
        for tag, text in _parse_sections(s.get("lyrics", "")):
            if section_base(tag) in CORE_SECTIONS:
                n = len(vocal_lines(text))
                if 0 < n < MIN_CORE_LINES:
                    hits.append({"index": s.get("index"), "title": s.get("title"),
                                 "section": tag, "lines": n})
    return hits


def check_self_repeat(songs: list[dict]) -> list[dict]:
    """서로 다른 섹션타입에 같은 라인 재출현 (코러스 계열 제외) — WARN."""
    hits = []
    for s in songs:
        owner = {}
        for tag, text in _parse_sections(s.get("lyrics", "")):
            base = section_base(tag)
            for line in vocal_lines(text):
                owner.setdefault(line, set()).add(base)
        repeats = [l for l, secs in owner.items()
                   if len(secs - {"chorus", "outro", "hook"}) > 1]
        if repeats:
            hits.append({"index": s.get("index"), "title": s.get("title"),
                         "lines": repeats[:3], "count": len(repeats)})
    return hits


def check_diversity(songs: list[dict]) -> dict:
    forms = [s.get("song_form_type") or " → ".join(s.get("song_form") or [])
             for s in songs]
    titles = [s.get("title") for s in songs]
    genre_groups = Counter(s.get("genre_group") for s in songs)
    return {
        "unique_forms": len(set(f for f in forms if f)),
        "songs": len(songs),
        "unique_titles": len(set(t for t in titles if t)),
        "dup_titles": [t for t, n in Counter(titles).items() if t and n > 1],
        "genre_groups": dict(genre_groups),
    }


def check_bracket_sp_match(songs: list[dict]) -> dict:
    """브래킷 지문 악기 ↔ SP 악기 일치율 (리포트 전용)."""
    matched = total = 0
    detail = []
    for s in songs:
        sp_inst = extract_sp_instruments(s.get("sp", ""))
        br_inst = set()
        for line in s.get("lyrics", "").split("\n"):
            t = line.strip()
            if t.startswith("[") and t.endswith("]"):
                br_inst |= extract_sp_instruments(t)
        if not br_inst:
            continue
        hit = len(br_inst & sp_inst)
        matched += hit
        total += len(br_inst)
        detail.append({"index": s.get("index"), "match": hit, "bracket": len(br_inst)})
    return {
        "match_rate": round(matched / total, 3) if total else None,
        "matched": matched, "total_bracket_instruments": total,
        "per_song": detail,
    }


# ---------------------------------------------------------------- audit

def audit_batch(batch_path: Path, history_dir: Path, limit: float,
                fail_cross_batch: bool = False) -> dict:
    songs = json.loads(batch_path.read_text())
    if not isinstance(songs, list):
        raise SystemExit(f"❌ 배치 파일이 곡 리스트가 아님: {batch_path}")

    cross_song = check_cross_song(songs, limit)
    cross_batch = (check_cross_batch(songs, batch_path, history_dir, limit)
                   if history_dir and history_dir.is_dir() else [])
    sp_leak = check_sp_directive(songs)
    v_ident = check_verse_identity(songs)
    thin = check_thin_sections(songs)

    fail_idx = sorted({h["index"] for hits in (sp_leak, v_ident, thin) for h in hits}
                      | {i for h in cross_song for i in h["pair"]}
                      | ({h["index"] for h in cross_batch} if fail_cross_batch
                         else set()))

    report = {
        "batch_file": batch_path.name,
        "songs": len(songs),
        "jaccard_limit": limit,
        "coherence": check_coherence(songs),
        "cross_song_contamination": cross_song,
        "cross_batch_contamination": cross_batch,
        "cross_batch_is_gate": fail_cross_batch,
        "sp_directive_leak": sp_leak,
        "identical_repeat_sections": v_ident,
        "thin_core_sections": thin,
        "self_repeat_warn": check_self_repeat(songs),
        "diversity": check_diversity(songs),
        "bracket_sp_match": check_bracket_sp_match(songs),
        "fail_list": fail_idx,
        "verdict": "FAIL" if fail_idx else "PASS",
    }
    return report


def print_report(r: dict):
    coh = r["coherence"]
    print(f"📋 배치 감사: {r['batch_file']} — {r['songs']}곡 → **{r['verdict']}**")
    print(f"  coherence: avg {coh['avg']} (min {coh['min']} / max {coh['max']}) "
          f"| 밴드분포 low {coh['distribution']['low']} / "
          f"band {coh['distribution']['band']} / high {coh['distribution']['high']}")
    div = r["diversity"]
    print(f"  폼 {div['unique_forms']}종/{div['songs']}곡 | "
          f"제목 고유 {div['unique_titles']}/{div['songs']}"
          + (f" (중복: {div['dup_titles']})" if div["dup_titles"] else ""))
    bsm = r["bracket_sp_match"]
    if bsm["match_rate"] is not None:
        print(f"  브래킷-SP 악기 일치율: {bsm['match_rate']:.0%} "
              f"({bsm['matched']}/{bsm['total_bracket_instruments']})")
    gates = [
        ("크로스곡 오염", r["cross_song_contamination"], True),
        ("크로스배치 중첩", r["cross_batch_contamination"], r["cross_batch_is_gate"]),
        ("SP 디렉티브 누출", r["sp_directive_leak"], True),
        ("동일반복 섹션(V1=V2류)", r["identical_repeat_sections"], True),
        ("1행 코어섹션", r["thin_core_sections"], True),
    ]
    for name, hits, is_gate in gates:
        mark = ("✅ 0건" if not hits
                else (f"❌ {len(hits)}건" if is_gate else f"⚠️ {len(hits)}건 (WARN)"))
        print(f"  {name}: {mark}")
        for h in hits[:5]:
            print(f"      {json.dumps(h, ensure_ascii=False)[:140]}")
    warns = r["self_repeat_warn"]
    if warns:
        print(f"  ⚠️ 곡내 섹션간 자기반복 {len(warns)}곡 (WARN, 게이트 아님)")
    if r["fail_list"]:
        print(f"  🔁 re-roll 대상 index: {r['fail_list']}")


# ---------------------------------------------------------------- retro (DB)

def get_conn():
    import psycopg2
    conf = {}
    conf_path = os.path.expanduser("~/.config/leofamily_music/db_sunolanguage.conf")
    with open(conf_path) as f:
        for line in f:
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                conf[k.strip()] = v.strip().strip('"')
    return psycopg2.connect(
        host=conf["DB_HOST"], port=conf["DB_PORT"], dbname=conf["DB_NAME"],
        user=conf["DB_USER"], password=conf["DB_PASSWORD"])


def retro_coherence() -> dict:
    """N001~N014 coherence 분포 소급 — songs(creator='sunolanguage') 직접 조회."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT global_id, coherence FROM songs "
        "WHERE creator = 'sunolanguage' AND global_id IS NOT NULL "
        "ORDER BY global_id")
    rows = cur.fetchall()
    conn.close()

    lo, hi = COH_BAND
    out = {}
    for batch, (g0, g1) in GID_BANDS.items():
        vals = [float(c) for g, c in rows if g0 <= g <= g1 and c is not None]
        nulls = sum(1 for g, c in rows if g0 <= g <= g1 and c is None)
        if not vals and not nulls:
            continue
        out[batch] = {
            "gid_band": [g0, g1], "n": len(vals), "null": nulls,
            "avg": round(sum(vals) / len(vals), 4) if vals else None,
            "min": min(vals) if vals else None,
            "max": max(vals) if vals else None,
            "low": sum(1 for v in vals if v < lo),
            "band": sum(1 for v in vals if lo <= v <= hi),
            "high": sum(1 for v in vals if v > hi),
        }
    all_vals = [float(c) for _, c in rows if c is not None]
    return {
        "band_limits": [lo, hi],
        "total_rows": len(rows), "with_coherence": len(all_vals),
        "overall_avg": round(sum(all_vals) / len(all_vals), 4) if all_vals else None,
        "batches": out,
    }


def print_retro(r: dict):
    lo, hi = r["band_limits"]
    print(f"📊 N시리즈 coherence 소급 분포 (통제밴드 {lo}~{hi}) — "
          f"{r['with_coherence']}/{r['total_rows']}행 측정, 전체 avg {r['overall_avg']}")
    print(f"  {'배치':<6} {'n':>3} {'avg':>7} {'min':>6} {'max':>6} "
          f"{'low':>4} {'band':>5} {'high':>5} {'null':>5}")
    for b, s in r["batches"].items():
        print(f"  {b:<6} {s['n']:>3} {s['avg'] or '-':>7} {s['min'] or '-':>6} "
              f"{s['max'] or '-':>6} {s['low']:>4} {s['band']:>5} {s['high']:>5} "
              f"{s['null']:>5}")


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description="T3-1 배치 감사 하니스")
    sub = ap.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("audit", help="단일 배치 감사 (오프라인)")
    a.add_argument("batch", type=Path)
    a.add_argument("--history-dir", type=Path, default=DEFAULT_HISTORY_DIR)
    a.add_argument("--jaccard", type=float, default=JACCARD_LIMIT)
    a.add_argument("--fail-cross-batch", action="store_true",
                   help="크로스배치 중첩을 WARN이 아닌 게이트로 승격")
    a.add_argument("--json", type=Path, help="리포트 JSON 저장 경로")

    rt = sub.add_parser("retro", help="N001~N014 coherence 분포 소급 (DB)")
    rt.add_argument("--json", type=Path)

    args = ap.parse_args()

    if args.cmd == "audit":
        report = audit_batch(args.batch, args.history_dir, args.jaccard,
                             fail_cross_batch=args.fail_cross_batch)
        print_report(report)
        if args.json:
            args.json.write_text(json.dumps(report, ensure_ascii=False, indent=2))
            print(f"  💾 {args.json}")
        sys.exit(1 if report["fail_list"] else 0)

    if args.cmd == "retro":
        report = retro_coherence()
        print_retro(report)
        if args.json:
            args.json.write_text(json.dumps(report, ensure_ascii=False, indent=2))
            print(f"  💾 {args.json}")


if __name__ == "__main__":
    main()
