#!/usr/bin/env python3
"""
N시리즈 Echo Jaccard 측정

입력 SP (Serendipity Engine 생성) vs Suno 재분석 SP 비교.
sunomusic 재분석 결과 수신 후 실행.

사용:
    python3 scripts/measure_echo_n_series.py <reanalysis_json>

    reanalysis_json 형식 (키 형식 무관 — 아래 중 하나로 곡 식별):
      식별 키:  "batch_line"(예: "N001_01")  또는  "gid"/"global_id"/"id"(숫자)
      SP 필드:  "reanalysis_sp"  또는  "sp"  또는  "style_prompt"
    예) [{ "batch_line": "N001_01", "reanalysis_sp": "..." }, ...]
        [{ "gid": 20311, "sp": "..." }, ...]
    최상위가 dict 이면 {"songs": [...]} 형태도 허용.

스키마 점검 (DB 연결/매칭 없이 핸드오프 키 + 기대 스키마 출력):
    python3 scripts/measure_echo_n_series.py --check

출력: data/n_series_echo_analysis.json
"""
import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
HANDOFF = REPO / "data" / "n_series_handoff.json"
OUT = REPO / "data" / "n_series_echo_analysis.json"

STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "in", "on", "at", "of", "to", "for", "with", "by", "from", "into",
    "and", "or", "but", "not", "no", "as", "if", "this", "that", "these",
    "those", "it", "its", "which", "who", "what", "when", "where", "why",
    "how", "than", "then", "so", "do", "does", "did", "has", "have", "had",
    "can", "could", "will", "would", "should", "may", "might", "must",
    "also", "more", "most", "some", "any", "all", "both", "each", "every",
    "other", "another", "such", "same", "own",
    "up", "down", "out", "off", "over", "under", "again", "further", "too",
    "very", "just", "only", "there", "here",
}

HIGH_ECHO_THRESHOLD = 0.70

# 핸드오프 곡 식별에 쓰는 키 후보 (배치라인 우선, 숫자 gid 류 보조)
ID_KEYS = ["batch_line", "gid", "global_id", "id"]
# 재분석 SP 가 담길 수 있는 필드 후보
SP_FIELDS = ["reanalysis_sp", "sp", "style_prompt"]

# 어느 배치를 핸드오프에서 읽을지 (없으면 전체 배치 사용)
HANDOFF_BATCHES = ["N001", "N002"]


def reanalysis_sp_of(rec: dict) -> str:
    """재분석 레코드에서 SP 텍스트를 SP_FIELDS 순서로 추출."""
    for f in SP_FIELDS:
        v = rec.get(f)
        if v:
            return v
    return ""


def reanalysis_keys_of(rec: dict) -> list[str]:
    """재분석 레코드가 가진 식별 키를 모두 문자열로 (매칭 후보)."""
    keys = []
    for k in ID_KEYS:
        if k in rec and rec[k] not in (None, ""):
            keys.append(str(rec[k]))
    return keys


def build_original_index(handoff: dict) -> dict:
    """핸드오프 곡을 batch_line 과 숫자 gid 류 키 양쪽으로 색인.

    importer 가 어느 키로 보내든 매칭되도록 같은 곡을 여러 키에 등록한다.
    """
    batches = handoff.get("batches", {})
    names = HANDOFF_BATCHES if any(b in batches for b in HANDOFF_BATCHES) else list(batches.keys())
    index = {}
    for batch_name in names:
        for s in batches.get(batch_name, []):
            entry = {
                "batch_line": s.get("batch_line", ""),
                "sp": s.get("style_prompt", ""),
                "genre": s.get("genre", ""),
                "title": s.get("title", ""),
            }
            for k in ID_KEYS:
                if k in s and s[k] not in (None, ""):
                    index[str(s[k])] = entry
    return index


def tokenize(text: str) -> set[str]:
    if not text:
        return set()
    words = re.findall(r"[a-zA-Z][a-zA-Z\-]{2,}", text.lower())
    return {w for w in words if w not in STOPWORDS}


def jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 0.0
    return len(a & b) / len(a | b)


def run_check(handoff: dict):
    """--check: 매칭 없이 핸드오프 식별 키 + 기대 재분석 스키마를 출력."""
    index = build_original_index(handoff)
    # batch_line 키만 추려 사람이 읽기 쉽게 (전체 키는 별도 표시)
    batch_lines = sorted({e["batch_line"] for e in index.values() if e["batch_line"]})
    print("=== 핸드오프 곡 식별 (--check) ===")
    print(f"색인된 곡: {len(batch_lines)}곡")
    print(f"등록된 식별 키 종류: {sorted({k for k in index})[:6]}{' ...' if len(index) > 6 else ''}")
    print(f"resolvable handoff batch_line 키: {batch_lines}")
    print()
    print("=== 기대 재분석(reanalysis) 스키마 ===")
    print(f"  식별 키(아무거나):  {ID_KEYS}   (batch_line 예: 'N001_01')")
    print(f"  SP 필드(아무거나):  {SP_FIELDS}")
    print("  최상위가 dict 이면 {\"songs\": [...]} 도 허용")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("reanalysis", nargs="?",
                        help="sunomusic 재분석 결과 JSON 경로")
    parser.add_argument("--check", action="store_true",
                        help="매칭 없이 핸드오프 키/기대 스키마만 출력 후 종료")
    args = parser.parse_args()

    handoff = json.loads(HANDOFF.read_text())

    if args.check:
        run_check(handoff)
        return
    if not args.reanalysis:
        parser.error("reanalysis JSON 경로가 필요합니다 (또는 --check 사용).")

    # batch_line + 숫자 gid 류 양쪽으로 색인 → importer 가 어느 키를 쓰든 매칭
    original_index = build_original_index(handoff)

    reanalysis = json.loads(Path(args.reanalysis).read_text())
    if isinstance(reanalysis, dict) and "songs" in reanalysis:
        reanalysis = reanalysis["songs"]

    per_song = []
    by_genre_sum = defaultdict(list)
    matched_keys = set()      # 매칭에 성공한 original_index 키 (중복 곡 방지용)
    unmatched_reanalysis = []  # 핸드오프에서 곡을 못 찾은 재분석 레코드
    empty_sp_skipped = 0       # 매칭됐으나 SP 비어 스킵

    for r in reanalysis:
        re_sp = reanalysis_sp_of(r)
        # 레코드가 가진 식별 키들 중 핸드오프에 있는 첫 키로 매칭
        orig = None
        used_key = None
        for k in reanalysis_keys_of(r):
            if k in original_index:
                orig = original_index[k]
                used_key = k
                break
        if orig is None:
            unmatched_reanalysis.append(r)
            continue
        if used_key in matched_keys:
            continue
        if not orig["sp"] or not re_sp:
            empty_sp_skipped += 1
            continue
        matched_keys.add(used_key)
        gid_str = orig["batch_line"] or used_key

        tokens_orig = tokenize(orig["sp"])
        tokens_re = tokenize(re_sp)
        j = jaccard(tokens_orig, tokens_re)
        overlap = tokens_orig & tokens_re
        orig_only = tokens_orig - tokens_re
        re_only = tokens_re - tokens_orig

        row = {
            "gid": gid_str,
            "batch_line": orig["batch_line"],
            "title": orig["title"],
            "genre": orig["genre"],
            "echo_jaccard": round(j, 4),
            "tokens_original": len(tokens_orig),
            "tokens_reanalysis": len(tokens_re),
            "tokens_overlap": len(overlap),
            "flag_high_echo": j >= HIGH_ECHO_THRESHOLD,
            "overlap_tokens": sorted(overlap)[:20],
            "original_only": sorted(orig_only)[:15],
            "reanalysis_only": sorted(re_only)[:15],
        }
        per_song.append(row)
        by_genre_sum[orig["genre"] or "(unknown)"].append(j)

    # 매칭 진단: 조용히 버리지 않고 카운트 보고
    print(f"[match] 재분석 {len(reanalysis)}건 → 매칭 {len(per_song)} / "
          f"미매칭 {len(unmatched_reanalysis)} / SP빈값 스킵 {empty_sp_skipped}")
    if unmatched_reanalysis:
        sample = []
        for r in unmatched_reanalysis[:10]:
            sample.append(reanalysis_keys_of(r) or list(r.keys())[:3])
        print(f"[match] 미매칭 재분석 식별키 샘플: {sample}")
        print("[match] → 위 키가 핸드오프 batch_line/gid 와 다릅니다. --check 로 기대 스키마 확인.")

    if not per_song:
        print("❌ 매칭된 곡이 없습니다. batch_line(예 'N001_01') 또는 gid 형식을 확인하세요 (--check).")
        return

    hist = Counter()
    for r in per_song:
        bin_idx = min(int(r["echo_jaccard"] * 10), 9)
        hist[bin_idx] += 1
    distribution = [
        {"range": f"{i/10:.1f}-{(i+1)/10:.1f}", "count": hist.get(i, 0)}
        for i in range(10)
    ]

    all_js = sorted(r["echo_jaccard"] for r in per_song)
    n = len(all_js)
    summary = {
        "n_songs": n,
        "mean_echo": round(sum(all_js) / n, 4),
        "median_echo": round(all_js[n // 2], 4),
        "p25_echo": round(all_js[n // 4], 4),
        "p75_echo": round(all_js[3 * n // 4], 4),
        "n_high_echo": sum(1 for r in per_song if r["flag_high_echo"]),
        "high_echo_threshold": HIGH_ECHO_THRESHOLD,
        "baseline_corpus_echo_mean": 0.076,
        "n_reanalysis_total": len(reanalysis),
        "n_unmatched_reanalysis": len(unmatched_reanalysis),
        "n_empty_sp_skipped": empty_sp_skipped,
    }

    out = {
        "summary": summary,
        "distribution": distribution,
        "per_song": per_song,
    }

    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2))
    print(f"✔ {OUT}")
    print()
    print("=== 요약 ===")
    for k, v in summary.items():
        print(f"  {k:28s} {v}")
    print()
    print("=== Echo Jaccard 분포 ===")
    for row in distribution:
        bar = "█" * row["count"]
        print(f"  {row['range']}  {row['count']:4d}  {bar}")
    print()
    print("=== 곡별 ===")
    sorted_songs = sorted(per_song, key=lambda r: -r["echo_jaccard"])
    for r in sorted_songs:
        print(f"  {r['echo_jaccard']:.3f}  {r['batch_line']:<12} {r['genre'][:40]}")


if __name__ == "__main__":
    main()
