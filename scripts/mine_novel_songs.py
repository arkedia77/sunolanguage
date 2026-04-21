#!/usr/bin/env python3
"""전체 DB에서 novel 단어 많이 포함한 generated 곡 추출 → 업로드 큐.

사용:
    python3 scripts/mine_novel_songs.py              # 기본: novel≥5, 상위 50
    python3 scripts/mine_novel_songs.py --min 3 --top 100

산출:
    docs/reviews/novel_song_mining.md   — Leo 검토용 랭킹
    data/reanalysis_v2/upload_queue.json — sunomusic 업로드 큐(후보)

필터:
  1) suno_generated = True (실제 Suno가 생성한 오디오 존재)
  2) 재분석 corpus(merged_4values.json, 318 clips) 밖의 곡만
  3) SP에 v3 어휘 + STOP 밖 단어 N개 이상

랭킹:
  novel_count desc, tie-break: SP 길이 desc
"""

from __future__ import annotations
import argparse, configparser, json, re, sys
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path("/Users/leo/sunolanguage")
V3 = ROOT / "data" / "reanalysis_v2"
SP_ENT = V3 / "sp_entities_v3.json"
BR_ENT = V3 / "bracket_entities_v3.json"
MERGED = V3 / "merged_4values.json"
REVIEW_DIR = ROOT / "docs" / "reviews"
QUEUE_OUT = V3 / "upload_queue.json"
DB_CONF = Path.home() / ".config" / "leofamily_music" / "db.conf"

STOP = set("""
a an the and with of in on at into from to that as is are has have be been was were it its their them
this these those there here for by or but no not any each all some every more most less very quite
throughout before after during while against between through plays play played playing enter enters entering entered
builds building built sustains sustained follows followed following rises rising doubled layered provides provided
adds added layers walks punches plucks moving delivering maintaining centered lifts alternates alternating
creates creating shifts shifting transitions transitioning rolls rolling drives driving hits hitting
breathes breathing resonates resonating pulses pulsing one two three four five six seven eight nine ten
zero first second third fourth bar bars note notes beat beats section sections line lines part parts
phrase phrases verse verses chorus choruses bridge intro outro interlude pre hook hooks song songs track
tracks music musical bpm tempo time key major minor korean lyrics minutes long must sit wide forward close
low high mid full downbeat upbeat backbeat rhythm style tone pattern delivery chord chords sustain register
articulation phrasing male female vocal vocals voice voices harmonies harmony bright warm soft light dry
clean sparse minimal deep rich quiet loud thick thin heavy tight punchy smooth crisp melodic rhythmic
steady c d e f g b ab bb eb db gb cm dm em fm gm am bm
""".split())


def load_v3_words() -> set[str]:
    words = set()
    for path in (SP_ENT, BR_ENT):
        for rec in json.loads(path.read_text()):
            for field in ("entity", "pattern"):
                v = rec.get(field, "") or ""
                if isinstance(v, str):
                    for tok in re.split(r"[^\w\-]+", v.lower()):
                        tok = tok.strip("-")
                        if tok:
                            words.add(tok)
            for field in ("modifiers", "effects", "chords"):
                for item in (rec.get(field) or []):
                    if isinstance(item, str):
                        for tok in re.split(r"[^\w\-]+", item.lower()):
                            tok = tok.strip("-")
                            if tok:
                                words.add(tok)
    return words


def load_reanalyzed_titles() -> set[str]:
    songs = json.loads(MERGED.read_text())
    return {s.get("title") for s in songs if s.get("title")}


def tokenize(sp: str) -> list[str]:
    cleaned = re.sub(r"[^\w\s\-']", " ", sp.lower())
    return [t.strip("'-") for t in cleaned.split() if t.strip("'-")]


NOISE_RE = re.compile(r"^(?:\d+[a-z]{1,2}|arc_[a-z0-9]|\d+(?:st|nd|rd|th))$")


def is_noise(t: str) -> bool:
    if not re.search(r"[a-z]", t):  # 한글/기호만 있는 토큰 제외
        return True
    if NOISE_RE.match(t):  # 마디 마커, arc 라벨, 서수
        return True
    return False


def novel_tokens(sp: str, v3: set[str]) -> Counter:
    novel: Counter = Counter()
    for t in tokenize(sp):
        if len(t) < 3 or t.isdigit():
            continue
        if t in STOP or t in v3:
            continue
        if is_noise(t):
            continue
        novel[t] += 1
    return novel


def load_generated_songs() -> list[dict]:
    import psycopg2
    c = configparser.ConfigParser()
    c.read(DB_CONF)
    cfg = dict(c["postgresql"])
    conn = psycopg2.connect(
        host=cfg["host"], port=int(cfg["port"]),
        dbname=cfg["dbname"], user=cfg["user"], password=cfg["password"]
    )
    cur = conn.cursor()
    cur.execute(
        "SELECT global_id, batch, title, style_prompt "
        "FROM songs "
        "WHERE suno_generated = True AND style_prompt IS NOT NULL AND length(style_prompt) > 0 "
        "ORDER BY global_id;"
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [
        {"gid": r[0], "batch": r[1], "title": r[2], "sp": r[3]}
        for r in rows
    ]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--min", type=int, default=5, help="minimum novel word count per song")
    ap.add_argument("--top", type=int, default=50, help="top N songs to queue")
    args = ap.parse_args()

    v3 = load_v3_words()
    reanalyzed = load_reanalyzed_titles()
    songs = load_generated_songs()

    print(f"generated 곡 {len(songs)}, v3 토큰 {len(v3)}, 재분석 완료 {len(reanalyzed)}곡")

    scored = []
    for s in songs:
        if s["title"] in reanalyzed:
            continue  # 이미 재분석된 곡 제외
        novel = novel_tokens(s["sp"], v3)
        if sum(novel.values()) < args.min:
            continue
        scored.append({
            "gid": s["gid"],
            "batch": s["batch"],
            "title": s["title"],
            "sp_len": len(s["sp"]),
            "novel_count": sum(novel.values()),
            "novel_unique": len(novel),
            "novel_words": sorted(novel.keys()),
        })

    scored.sort(key=lambda x: (-x["novel_unique"], -x["sp_len"]))
    top = scored[: args.top]

    # 큐 JSON
    queue = {
        "generated_at": date.today().isoformat(),
        "filter": f"suno_generated=True AND novel_unique>={args.min}, title 기준 재분석 corpus 제외",
        "total_candidates": len(scored),
        "queued": len(top),
        "items": top,
    }
    QUEUE_OUT.write_text(json.dumps(queue, ensure_ascii=False, indent=2))

    # 마크다운 리포트
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    out = REVIEW_DIR / "novel_song_mining.md"
    lines = [
        "# 업로드 큐 — novel-word 기반 Suno 재분석 후보",
        "",
        f"생성: {date.today().isoformat()} · generated 곡 {len(songs)} · "
        f"재분석 완료 {len(reanalyzed)} · 후보 {len(scored)} · 큐 상위 {len(top)}",
        "",
        f"필터: `suno_generated=True` · novel 유니크 ≥ {args.min} · 재분석 corpus 외 곡만",
        "",
        "| rank | gid | batch | title | SP자 | novel U/총 | 대표 novel(최대 15개) |",
        "|---:|---:|---|---|---:|---|---|",
    ]
    for i, s in enumerate(top, 1):
        words_show = ", ".join(f"`{w}`" for w in s["novel_words"][:15])
        if len(s["novel_words"]) > 15:
            words_show += f" … +{len(s['novel_words'])-15}"
        lines.append(
            f"| {i} | {s['gid']} | {s['batch']} | {s['title']} | {s['sp_len']} | "
            f"{s['novel_unique']}/{s['novel_count']} | {words_show} |"
        )
    lines.append("")
    lines.append(f"JSON 큐: `data/reanalysis_v2/upload_queue.json` ({len(top)}곡)")
    out.write_text("\n".join(lines))

    print(f"wrote {out}")
    print(f"wrote {QUEUE_OUT} — {len(top)}곡 큐")


if __name__ == "__main__":
    main()
