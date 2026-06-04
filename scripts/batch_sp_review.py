#!/usr/bin/env python3
"""배치 SP novel 단어 리포트 + 의심 phrase 추적 대시보드.

사용:
    python3 scripts/batch_sp_review.py B192               # DB에서 batch 조회
    python3 scripts/batch_sp_review.py --gid-range 1773 1782
    python3 scripts/batch_sp_review.py --json <path>      # 로컬 JSON 입력

산출:
    docs/reviews/{batch}_sp_review.md
    docs/reviews/suspicion_tracker.json (누적 추적)

비교 기준:
  1) v3 어휘(entities/modifiers/patterns/effects/chords 토큰 집합)
  2) Suno 재분석 corpus(326 clips) 전체 텍스트 — 실제 Suno가 쓰는 어휘 근거
"""

from __future__ import annotations
import argparse, configparser, json, re, sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
V3_PATH = ROOT / "data" / "reanalysis_v2"
SP_ENT = V3_PATH / "sp_entities_v3.json"
BR_ENT = V3_PATH / "bracket_entities_v3.json"
MERGED = V3_PATH / "merged_4values.json"
REVIEW_DIR = ROOT / "docs" / "reviews"
TRACKER = REVIEW_DIR / "suspicion_tracker.json"
DB_CONF = Path.home() / ".config" / "leofamily_music" / "db.conf"

STOP = set("""
a an the and with of in on at into from to that as is are has have be been was were it its their them this these those there here for by or but no not any each all some every more most less very quite throughout before after during while against between through plays play played playing enter enters entering entered builds building built sustains sustained follows followed following rises rising doubled layered provides provided adds added layers walks punches plucks moving delivering maintaining centered lifts alternates alternating creates creating shifts shifting transitions transitioning rolls rolling drives driving hits hitting breathes breathing resonates resonating pulses pulsing one two three four five six seven eight nine ten zero first second third fourth bar bars note notes beat beats section sections line lines part parts phrase phrases verse verses chorus choruses bridge intro outro interlude pre hook hooks song songs track tracks music musical bpm tempo time key major minor korean lyrics minutes long must sit wide forward close low high mid full downbeat upbeat backbeat rhythm style tone pattern delivery chord chords sustain register articulation phrasing male female vocal vocals voice voices harmonies harmony bright warm soft light dry clean sparse minimal deep rich quiet loud thick thin heavy tight punchy smooth crisp melodic rhythmic steady c d e f g b ab bb eb db gb cm dm em fm gm am bm
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
                        if tok: words.add(tok)
            for field in ("modifiers", "effects", "chords"):
                for item in (rec.get(field) or []):
                    if isinstance(item, str):
                        for tok in re.split(r"[^\w\-]+", item.lower()):
                            tok = tok.strip("-")
                            if tok: words.add(tok)
    return words


def load_suno_corpus_text() -> str:
    songs = json.loads(MERGED.read_text())
    texts = []
    for song in songs:
        for clip in (song.get("suno_reanalysis") or []):
            if isinstance(clip, dict):
                texts.append((clip.get("sp") or "") + "\n" + (clip.get("lyrics") or ""))
    return "\n\n".join(texts).lower()


def tokenize(sp: str) -> list[str]:
    cleaned = re.sub(r"[^\w\s\-']", " ", sp.lower())
    return [t.strip("'-") for t in cleaned.split() if t.strip("'-")]


def load_songs_from_db(batch: str | None, gid_range: tuple[int, int] | None) -> list[dict]:
    import psycopg2
    c = configparser.ConfigParser(); c.read(DB_CONF)
    cfg = dict(c["postgresql"])
    conn = psycopg2.connect(host=cfg["host"], port=int(cfg["port"]),
        dbname=cfg["dbname"], user=cfg["user"], password=cfg["password"])
    cur = conn.cursor()
    if batch:
        cur.execute("SELECT global_id, title, style_prompt, status, suno_generated "
                    "FROM songs WHERE batch=%s ORDER BY global_id;", (batch,))
    else:
        cur.execute("SELECT global_id, title, style_prompt, status, suno_generated "
                    "FROM songs WHERE global_id BETWEEN %s AND %s ORDER BY global_id;",
                    (gid_range[0], gid_range[1]))
    rows = cur.fetchall(); cur.close(); conn.close()
    return [{"gid": r[0], "title": r[1], "sp": r[2] or "", "status": r[3],
             "suno_generated": r[4]} for r in rows]


def count_in_corpus(word: str, corpus: str) -> int:
    return len(re.findall(r"(?:^|\W)" + re.escape(word.lower()) + r"(?:\W|$)", corpus))


def classify(word: str, corpus: str) -> str:
    cnt = count_in_corpus(word, corpus)
    if cnt == 0:
        return "🚨 Suno 0건 — 네이티브 아님"
    if cnt <= 2:
        return f"⚠️ Suno {cnt}건 — 희귀"
    return f"✓ Suno {cnt}건 — 네이티브"


def build_report(batch_id: str, songs: list[dict]) -> str:
    v3_words = load_v3_words()
    corpus = load_suno_corpus_text()

    per_song_novel: dict[int, Counter] = {}
    novel_global: dict[str, list[int]] = defaultdict(list)
    for s in songs:
        toks = tokenize(s["sp"])
        novel: Counter = Counter()
        for t in toks:
            if len(t) < 3 or t.isdigit(): continue
            if t in STOP or t in v3_words: continue
            novel[t] += 1
        per_song_novel[s["gid"]] = novel
        for t in novel:
            novel_global[t].append(s["gid"])

    lines = [f"# 배치 {batch_id} SP 검토 — v3 + Suno corpus 기준", ""]
    lines.append(f"생성일: {date.today().isoformat()}  ·  v3 토큰 {len(v3_words)} · "
                 f"Suno corpus {len(corpus):,}자 (326 clips)")
    lines.append("")

    # 곡별 요약
    lines.append("## 1. 곡별 요약")
    lines.append("")
    lines.append("| gid | 제목 | 상태 | SP자 | novel단어 |")
    lines.append("|---:|---|---|---:|---:|")
    for s in songs:
        status = "✅" if s.get("suno_generated") else "⏳" if s.get("status") == "pending" else "?"
        lines.append(f"| {s['gid']} | {s['title']} | {status} {s.get('status','?')} | "
                     f"{len(s['sp'])} | {len(per_song_novel[s['gid']])} |")
    lines.append("")

    # 전역 novel + Suno corpus 분류
    lines.append("## 2. novel 단어 — Suno corpus 교차 판정")
    lines.append("")
    lines.append("| 단어 | 곡수 | gid | Suno corpus |")
    lines.append("|---|---:|---|---|")
    sorted_novel = sorted(novel_global.items(), key=lambda x: (-len(x[1]), x[0]))
    for w, gids in sorted_novel[:80]:
        verdict = classify(w, corpus)
        gids_str = ", ".join(str(g) for g in sorted(set(gids)))
        lines.append(f"| `{w}` | {len(set(gids))} | {gids_str} | {verdict} |")
    lines.append("")

    # 의심 phrase 자동 감지 (Suno 0건인 단어)
    lines.append("## 3. Leo 확인 요청 — Suno 0건 단어 (네이티브 아님)")
    lines.append("")
    zero_words = [(w, gids) for w, gids in sorted_novel
                  if count_in_corpus(w, corpus) == 0]
    if zero_words:
        for w, gids in zero_words:
            gids_str = ", ".join(str(g) for g in sorted(set(gids)))
            lines.append(f"- `{w}` — 곡 {gids_str}")
    else:
        lines.append("- (없음)")
    lines.append("")

    return "\n".join(lines), zero_words


def update_tracker(batch_id: str, zero_words: list[tuple[str, list[int]]]) -> None:
    if TRACKER.exists():
        data = json.loads(TRACKER.read_text())
    else:
        data = {"entries": []}
    today = date.today().isoformat()
    for w, gids in zero_words:
        data["entries"].append({
            "word": w, "batch": batch_id,
            "gids": sorted(set(gids)),
            "detected_on": today,
            "suno_seen_in_reanalysis": False,
            "notes": "",
        })
    TRACKER.write_text(json.dumps(data, ensure_ascii=False, indent=2))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("batch", nargs="?", help="batch id (e.g. B192) — DB 조회")
    ap.add_argument("--gid-range", nargs=2, type=int, metavar=("FROM","TO"))
    ap.add_argument("--json", help="로컬 JSON 입력 (DB 미사용)")
    args = ap.parse_args()

    if args.json:
        songs = json.loads(Path(args.json).read_text())
        for s in songs:
            s.setdefault("status", "?")
            s.setdefault("suno_generated", False)
        batch_id = Path(args.json).stem
    elif args.batch:
        songs = load_songs_from_db(args.batch, None)
        batch_id = args.batch
    elif args.gid_range:
        songs = load_songs_from_db(None, tuple(args.gid_range))
        batch_id = f"gid{args.gid_range[0]}-{args.gid_range[1]}"
    else:
        ap.error("batch, --gid-range, or --json required")

    if not songs:
        sys.exit("no songs found")

    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    report, zero_words = build_report(batch_id, songs)
    out = REVIEW_DIR / f"{batch_id}_sp_review.md"
    out.write_text(report)
    update_tracker(batch_id, zero_words)
    print(f"wrote {out}")
    print(f"Suno 0건 단어 {len(zero_words)}개 추적 등록")


if __name__ == "__main__":
    main()
