#!/usr/bin/env python3
"""
N시리즈 Echo Jaccard 측정

입력 SP (Serendipity Engine 생성) vs Suno 재분석 SP 비교.
sunomusic 재분석 결과 수신 후 실행.

사용:
    python3 scripts/measure_echo_n_series.py <reanalysis_json>

    reanalysis_json 형식:
    [{ "gid": 20311, "reanalysis_sp": "...", ... }, ...]

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


def tokenize(text: str) -> set[str]:
    if not text:
        return set()
    words = re.findall(r"[a-zA-Z][a-zA-Z\-]{2,}", text.lower())
    return {w for w in words if w not in STOPWORDS}


def jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 0.0
    return len(a & b) / len(a | b)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("reanalysis", help="sunomusic 재분석 결과 JSON 경로")
    args = parser.parse_args()

    handoff = json.loads(HANDOFF.read_text())
    original_sps = {}
    for batch_name in ["N001", "N002"]:
        for s in handoff["batches"].get(batch_name, []):
            gid = None
            for key in ["gid", "global_id", "id"]:
                if key in s:
                    gid = s[key]
                    break
            if gid is None:
                gid = s["batch_line"]
            original_sps[str(gid)] = {
                "batch_line": s["batch_line"],
                "sp": s.get("style_prompt", ""),
                "genre": s.get("genre", ""),
                "title": s.get("title", ""),
            }

    reanalysis = json.loads(Path(args.reanalysis).read_text())
    if isinstance(reanalysis, dict) and "songs" in reanalysis:
        reanalysis = reanalysis["songs"]

    re_map = {}
    for r in reanalysis:
        gid = str(r.get("gid", r.get("global_id", r.get("id", ""))))
        re_map[gid] = r.get("reanalysis_sp", "")

    per_song = []
    by_genre_sum = defaultdict(list)

    for gid_str, orig in sorted(original_sps.items()):
        re_sp = re_map.get(gid_str, "")
        if not orig["sp"] or not re_sp:
            continue

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

    if not per_song:
        print("❌ 매칭된 곡이 없습니다. gid 형식을 확인하세요.")
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
