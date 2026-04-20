#!/usr/bin/env python3
"""
R2 — echo 측정

leomusic 원 SP가 이미 Suno 모방 어휘로 작성되어 있어,
Suno 재분석이 자기 어휘를 재사용하는지(echo) 검증 필요.

지표: song_id별 Jaccard(leomusic_sp_tokens, suno_sp_tokens)

출력: data/reanalysis_v2/echo_analysis.json
  - per_song: song_id, title, genre, echo_jaccard, flag_high_echo(≥0.7)
  - distribution: 히스토그램 (10 bin)
  - by_genre: 장르별 평균 echo율
  - top_echo, bottom_echo: 양 끝 10곡
"""
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
IN = REPO / "data" / "reanalysis_v2" / "merged_4values.json"
OUT = REPO / "data" / "reanalysis_v2" / "echo_analysis.json"

# 빈도 높은 불용어 — echo 측정의 노이즈. 음악 어휘는 유지.
STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "in", "on", "at", "of", "to", "for", "with", "by", "from", "into",
    "and", "or", "but", "not", "no", "as", "if", "this", "that", "these",
    "those", "it", "its", "which", "who", "what", "when", "where", "why",
    "how", "than", "then", "so", "do", "does", "did", "has", "have", "had",
    "can", "could", "will", "would", "should", "may", "might", "must",
    "also", "more", "most", "some", "any", "all", "both", "each", "every",
    "other", "another", "such", "same", "own", "own",
    "up", "down", "out", "off", "over", "under", "again", "further", "too",
    "very", "just", "only", "there", "here",
}

HIGH_ECHO_THRESHOLD = 0.70


def tokenize(text: str) -> set[str]:
    """SP 텍스트 → 의미 토큰 집합."""
    if not text:
        return set()
    words = re.findall(r"[a-zA-Z][a-zA-Z\-]{2,}", text.lower())
    return {w for w in words if w not in STOPWORDS}


def jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 0.0
    return len(a & b) / len(a | b)


def main():
    data = json.loads(IN.read_text())
    per_song = []
    by_genre_sum = defaultdict(list)

    for song in data:
        lo_sp = (song.get("leomusic_original") or {}).get("sp") or ""
        sr_list = song.get("suno_reanalysis") or []
        suno_sp = " ".join(sr.get("sp", "") for sr in sr_list if sr.get("sp"))

        if not lo_sp or not suno_sp:
            continue

        tokens_lo = tokenize(lo_sp)
        tokens_su = tokenize(suno_sp)
        j = jaccard(tokens_lo, tokens_su)
        overlap = tokens_lo & tokens_su
        lo_only = tokens_lo - tokens_su
        su_only = tokens_su - tokens_lo

        row = {
            "song_id": song.get("song_id"),
            "title": song.get("title"),
            "genre": song.get("genre", ""),
            "echo_jaccard": round(j, 4),
            "tokens_leomusic": len(tokens_lo),
            "tokens_suno": len(tokens_su),
            "tokens_overlap": len(overlap),
            "flag_high_echo": j >= HIGH_ECHO_THRESHOLD,
            "top_overlap_tokens": sorted(overlap)[:20],
            "suno_unique_tokens_sample": sorted(su_only)[:20],
        }
        per_song.append(row)
        by_genre_sum[row["genre"] or "(unknown)"].append(j)

    # 히스토그램 (10 bin: 0.0-0.1, ..., 0.9-1.0)
    hist = Counter()
    for r in per_song:
        bin_idx = min(int(r["echo_jaccard"] * 10), 9)
        hist[bin_idx] += 1
    distribution = [
        {"range": f"{i/10:.1f}-{(i+1)/10:.1f}", "count": hist.get(i, 0)}
        for i in range(10)
    ]

    # 장르별 평균
    by_genre = []
    for g, js in sorted(by_genre_sum.items(), key=lambda x: -len(x[1])):
        if len(js) >= 3:
            avg = sum(js) / len(js)
            by_genre.append({
                "genre": g,
                "n_songs": len(js),
                "avg_echo": round(avg, 4),
                "min_echo": round(min(js), 4),
                "max_echo": round(max(js), 4),
            })

    # 양 끝
    sorted_asc = sorted(per_song, key=lambda r: r["echo_jaccard"])
    top_echo = [r for r in reversed(sorted_asc)][:10]
    bottom_echo = sorted_asc[:10]

    all_js = [r["echo_jaccard"] for r in per_song]
    all_js.sort()
    n = len(all_js)
    summary = {
        "n_songs": n,
        "mean_echo": round(sum(all_js) / n, 4) if n else 0,
        "median_echo": round(all_js[n // 2], 4) if n else 0,
        "p25_echo": round(all_js[n // 4], 4) if n else 0,
        "p75_echo": round(all_js[3 * n // 4], 4) if n else 0,
        "n_high_echo": sum(1 for r in per_song if r["flag_high_echo"]),
        "high_echo_threshold": HIGH_ECHO_THRESHOLD,
    }

    out = {
        "summary": summary,
        "distribution": distribution,
        "by_genre": by_genre,
        "top_echo": [
            {k: r[k] for k in ("song_id", "title", "genre", "echo_jaccard")}
            for r in top_echo
        ],
        "bottom_echo": [
            {k: r[k] for k in ("song_id", "title", "genre", "echo_jaccard")}
            for r in bottom_echo
        ],
        "per_song": per_song,
    }

    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2))

    # 리포트
    print(f"✔ echo_analysis.json 작성: {OUT}")
    print()
    print("=== 요약 ===")
    for k, v in summary.items():
        print(f"  {k:22s} {v}")
    print()
    print("=== Echo Jaccard 분포 (10 bin) ===")
    for row in distribution:
        bar = "█" * row["count"]
        print(f"  {row['range']}  {row['count']:4d}  {bar}")
    print()
    print("=== 장르별 평균 echo (n≥3) ===")
    for row in by_genre[:15]:
        print(f"  {row['avg_echo']:.3f}  n={row['n_songs']:3d}  {row['genre']}")
    print()
    print("=== TOP echo (echo 높음 — 책 근거에서 제외 후보) ===")
    for r in top_echo[:5]:
        print(f"  {r['echo_jaccard']:.3f}  [{r['song_id']}] {r['title']}  ({r['genre']})")
    print()
    print("=== BOTTOM echo (echo 낮음 — Suno 네이티브 어휘 근거) ===")
    for r in bottom_echo[:5]:
        print(f"  {r['echo_jaccard']:.3f}  [{r['song_id']}] {r['title']}  ({r['genre']})")


if __name__ == "__main__":
    main()
