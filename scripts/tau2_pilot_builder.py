#!/usr/bin/env python3
"""tau2_pilot_builder.py — τ 파일럿 2호 (kee 2호 GO 조건 4 반영, 07-17)

신 파이프라인(F1~F5, retro_rematch_tau10 재사용)으로 신규 10곡 층화 선정→매칭→SP 조립.

층화(kee 조건①): 앵커(고스코어) 3 + 중간대 6 + 공백검증 라벨 1 (성공 모수=앵커+중간 9, Y율≥5 + 앵커 Y 필수)
제외: 1호 사용 track(run6~15) / ref 모드미상·무템포(매칭불가 클래스 — 1호에서 배제 의미론 검증됨) / 하드패스 0곡
조립(1호 규칙 준용): 매처 산출 표현만(top-3 매칭곡의 네이티브 SP 문장), 창작 보정 금지, 보컬 문장 제외,
  템포·키 문장은 top1 것(F1/F2 통과라 모드 일치·BPM ±10% 보장), 브라켓=[Intro]/[Instrumental]/[Outro].

사용:
  python3 scripts/tau2_pilot_builder.py --select          # 층화 선정 리포트(드라이런)
  python3 scripts/tau2_pilot_builder.py --build           # 배치 JSON 생성 (data/tau_pilot/TAU2_batch.json)
  python3 scripts/tau2_pilot_builder.py --load-pg         # songs_test_lab 적재 (test_id 287~296)
"""
import argparse
import json
import os
import re
import sqlite3
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from retro_rematch_tau10 import (  # noqa: E402
    load_corpus_profiles, instr_idf, ref_profile, gate_song, LEX, MAIN, ROOT)

OUT = ROOT / "data" / "tau_pilot" / "TAU2_batch.json"
PILOT1_TRACKS = {77, 96, 25, 27, 1, 84, 37, 54, 66, 72}
TEST_ID_START = 287
VOCAL_RE = re.compile(r"\bvocal|voice|singer|belts|sung|sings\b", re.I)
# 중립 제목 — 원곡명 노출 금지(1호 규율: 원곡명은 note만, 생성 미사용 — 저작권/오염 리스크)
NEUTRAL_TITLES = ["떠오르는 잔향", "오래된 영사기", "흐르는 건반", "오후의 그루브", "새벽 도시의 맥박",
                  "반복의 축적", "잔잔한 파문", "느린 상승", "사막의 산책", "초록 바람"]
TEMPO_RE = re.compile(r"\bBPM\b|key of", re.I)


def load_song_sentences():
    """곡별 문장(슬롯 라벨 포함, 원문 순서). {song_id: [(slot, sentence), ...]}"""
    conn = sqlite3.connect(LEX)
    rows = conn.execute(
        "SELECT song_id, slot, sentence FROM entries WHERE source='sp_entity' ORDER BY id").fetchall()
    full = conn.execute(
        "SELECT song_id, sentence FROM entries WHERE source IN ('suno_sp_full','leomusic_sp_full') "
        "ORDER BY id").fetchall()
    conn.close()
    by_song, seen = {}, set()
    for sid, slot, sent in rows:
        k = (str(sid), sent)
        if k in seen:
            continue
        seen.add(k)
        by_song.setdefault(str(sid), []).append((slot or "", sent))
    fulltext = {}
    for sid, sent in full:
        fulltext.setdefault(str(sid), []).append(sent)
    return by_song, {k: " ".join(v) for k, v in fulltext.items()}


def rank_for_ref(ref, profiles, idf, med_idf, aliases, top=5):
    ranked = []
    for sid, cand in profiles.items():
        g = gate_song(ref, cand, idf, med_idf, aliases)
        if g["hard_pass"]:
            ranked.append({"song_id": sid, "soft": g["soft_composite"],
                           "f3": g["f3_genre"], "f4": g["f4_instruments"],
                           "f5a": g["f5a_curve"], "f5b": g["f5b_production"]})
    ranked.sort(key=lambda x: -x["soft"])
    return ranked[:top], len(ranked)


def corpus_instr_lexicon(profiles):
    """코퍼스 악기 엔티티 전체 → ref texture 검출용 어휘 (EXTRA_INSTR의 15개 협소 검출 정정)."""
    lex = set()
    for p in profiles.values():
        for e in p["instruments"]:
            lex.add(e)
            lex.update(w for w in e.split() if len(w) > 3)
    return {w for w in lex if len(w) > 3}


def detect_ref_instruments(tex: str, lexicon: set) -> set:
    t = tex.lower()
    return {w for w in lexicon if w in t}


def classify_and_rank():
    aliases_p = ROOT / "rag" / "genre_aliases.json"
    aliases = json.loads(aliases_p.read_text()) if aliases_p.exists() else {}
    profiles = load_corpus_profiles()
    idf = instr_idf(profiles)
    med_idf = sorted(idf.values())[len(idf) // 2] if idf else 1.0
    lexicon = corpus_instr_lexicon(profiles)

    main_db = sqlite3.connect(MAIN)
    main_db.row_factory = sqlite3.Row
    tracks = main_db.execute(
        "SELECT * FROM tracks WHERE texture_description IS NOT NULL AND texture_description != '' "
        "ORDER BY id").fetchall()
    cands = []
    for tr in tracks:
        if tr["id"] in PILOT1_TRACKS:
            continue
        ref = ref_profile(tr, aliases)
        if ref["mode"] is None or not ref["bpm"]:
            continue  # 매칭불가 클래스(모드미상/무템포) — 배제 의미론은 1호 검증
        tex = (tr["texture_description"] or "") + " " + (tr["spatial_character"] or "")
        ref["instruments"] = ref["instruments"] | detect_ref_instruments(tex, lexicon)
        top, n_pass = rank_for_ref(ref, profiles, idf, med_idf, aliases)
        if not top:
            continue
        cands.append({"track_id": tr["id"], "title": tr["title"], "artist": tr["artist"],
                      "genre": tr["genre"], "ref": ref, "top": top, "n_pass": n_pass,
                      "top_soft": top[0]["soft"], "top_f4": top[0]["f4"],
                      "ref_instr_detected": len(ref["instruments"])})
    softs = sorted(c["top_soft"] for c in cands)
    q75 = softs[int(len(softs) * 0.75)]
    q25 = softs[int(len(softs) * 0.25)]
    for c in cands:
        # 공백검증 = ref 악기 검출됐는데도 코퍼스 최상 후보 F4=0 (진짜 편성 공백)
        if c["top_f4"] == 0.0 and c["ref_instr_detected"] >= 2:
            c["stratum"] = "공백검증(편성 F4=0)"
        elif c["top_soft"] >= q75:
            c["stratum"] = "고스코어 앵커"
        elif c["top_soft"] >= q25:
            c["stratum"] = "중간대"
        else:
            c["stratum"] = "저스코어"
    return cands, {"q25": q25, "q75": q75, "n_candidates": len(cands)}


def select_10(cands):
    """앵커 3 + 중간대 6 + 공백라벨 1, 장르 다양성 우선."""
    def diverse(pool, n):
        picked, genres = [], set()
        for c in sorted(pool, key=lambda x: -x["top_soft"]):
            if len(picked) >= n:
                break
            if c["genre"] not in genres:
                picked.append(c)
                genres.add(c["genre"])
        for c in sorted(pool, key=lambda x: -x["top_soft"]):  # 장르 다양성 부족 시 보충
            if len(picked) >= n:
                break
            if c not in picked:
                picked.append(c)
        return picked
    anchors = diverse([c for c in cands if c["stratum"] == "고스코어 앵커"], 3)
    mids = diverse([c for c in cands if c["stratum"] == "중간대"], 6)
    gaps = sorted([c for c in cands if c["stratum"].startswith("공백")], key=lambda x: -x["top_soft"])[:1]
    return anchors + mids + gaps


def assemble_sp(song_ids, by_song, fulltext):
    """top-3 매칭곡 네이티브 문장으로 SP 조립 (매처 산출만·창작 금지·보컬 제외)."""
    top1 = song_ids[0]
    sents = []
    t1 = by_song.get(top1, [])
    t1_text = fulltext.get(top1, "")
    first = t1_text.split(". ")[0].strip() if t1_text else ""
    if first and not VOCAL_RE.search(first):
        sents.append(first if first.endswith(".") else first + ".")
    def find_sent(pattern, sid=None):
        rx = re.compile(pattern, re.I)
        rows = by_song.get(sid, []) if sid else t1
        text = fulltext.get(sid, "") if sid else t1_text
        hit = next((s for _sl, s in rows if rx.search(s) and not VOCAL_RE.search(s)), None)
        if not hit:
            hit = next((s.strip() + "." for s in text.split(".")
                        if rx.search(s) and not VOCAL_RE.search(s)), None)
        return hit
    # BPM 문장과 key 문장이 분리된 곡 대비 — 둘 다 확보 (축 자체검증 요건).
    # key 폴백 사다리: top1 'key of' → top1 모드문장('E minor' 정형) → top2/3 'key of' (전부 매처 산출 원문)
    bpm_sent = find_sent(r"\bBPM\b")
    key_sent = (find_sent(r"key of")
                or find_sent(r"\b[A-G][#b♭♯]? (major|minor)\b")
                or next((find_sent(r"key of", sid) for sid in song_ids[1:3]
                         if find_sent(r"key of", sid)), None))
    tempo = " ".join(dict.fromkeys(s for s in [bpm_sent, key_sent] if s)) or None
    instr, prod = [], []
    for sid in song_ids[:3]:
        for slot, s in by_song.get(sid, []):
            if VOCAL_RE.search(s) or s in sents or s in instr or s in prod:
                continue
            if slot == "instrument" and len(instr) < 4:
                instr.append(s)
            elif slot == "production" and len(prod) < 2:
                prod.append(s)
    parts = sents + instr + prod + ([tempo] if tempo else [])
    sp = " ".join(p if p.endswith(".") else p + "." for p in parts)
    return sp[:900]


def build():
    cands, stats = classify_and_rank()
    sel = select_10(cands)
    by_song, fulltext = load_song_sentences()
    songs = []
    for i, c in enumerate(sel):
        sp = assemble_sp([t["song_id"] for t in c["top"]], by_song, fulltext)
        songs.append({
            "pos": i + 1, "test_id": TEST_ID_START + i, "tau": f"TAU{16 + i}",
            "track_id": c["track_id"],
            "original": f"{c['title']} — {c['artist']} ({c['genre']})",
            "stratum": c["stratum"], "top_soft": c["top_soft"], "n_hard_pass": c["n_pass"],
            "in_success_denominator": not c["stratum"].startswith("공백"),
            "matched_songs": c["top"][:3],
            "ref_axes": {"mode": c["ref"]["mode"], "bpm": c["ref"]["bpm"],
                         "curve": c["ref"]["curve"], "instruments": sorted(c["ref"]["instruments"])},
            "title": f"TAU{16 + i} {NEUTRAL_TITLES[i % len(NEUTRAL_TITLES)]}",
            "sp": sp, "sp_len": len(sp),
            "bracket": "[Intro]\n\n[Instrumental]\n\n[Outro]",
        })
    batch = {
        "batch": "TAU2", "designed": "2026-07-17", "n": len(songs),
        "concept": "τ 파일럿 2호 — 신 파이프라인(F1~F5, 재설계 v1) 매칭 산출 SP 조립 인스트루멘탈. "
                   "kee 2호 GO 조건 4 반영(공백라벨 1곡 모수분리·Y율≥5/9·앵커Y 필수·문항 2개 SPEC)",
        "assembly_rule": "1호 준용 — 매처 산출 표현만(top-3 매칭곡 네이티브 SP 문장), 창작 보정 금지, "
                         "보컬 문장 제외, 템포·키=top1(F1 모드일치·F2 ±10% 보장), 브라켓 lyrics 우회",
        "strata_stats": stats,
        "success_criteria": "공백라벨 제외 9곡 중 Y≥5 + 고스코어 앵커 3곡 중 Y 필수(재붕괴 시 즉시 중단)",
        "songs": songs,
    }
    OUT.write_text(json.dumps(batch, ensure_ascii=False, indent=1))
    print(f"→ {OUT.relative_to(ROOT)}")
    for s in songs:
        print(f"  {s['tau']} #{s['test_id']} [{s['stratum']}] soft={s['top_soft']:.3f} "
              f"pass={s['n_hard_pass']:3d} sp={s['sp_len']}자 | {s['original'][:50]}")
    return batch


def load_pg():
    import psycopg2
    batch = json.loads(OUT.read_text())
    conf = {}
    for ln in open(os.path.expanduser("~/.config/leofamily_music/db_sunolanguage.conf")):
        ln = ln.strip()
        if "=" in ln and not ln.startswith("#"):
            k, v = ln.split("=", 1)
            conf[k.strip()] = v.strip()
    c = psycopg2.connect(host=conf["DB_HOST"], port=conf.get("DB_PORT", 5432),
                         dbname=conf["DB_NAME"], user=conf["DB_USER"],
                         password=conf.get("DB_PASSWORD", ""))
    cur = c.cursor()
    for s in batch["songs"]:
        cur.execute(
            "INSERT INTO songs_test_lab (test_id, source_project, creator, batch, batch_position, "
            "title, lyrics, style_prompt, genre, status, note) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (test_id) DO NOTHING",
            (s["test_id"], "sunolanguage", "sunolanguage", "TAU2", s["pos"], s["title"],
             s["bracket"], s["sp"], "instrumental", "experimental",
             f"원곡(생성 미사용): {s['original']} | {s['stratum']} | soft={s['top_soft']}"))
    c.commit()
    cur.execute("SELECT test_id, title, status FROM songs_test_lab WHERE batch='TAU2' ORDER BY test_id")
    for r in cur.fetchall():
        print(r)
    c.close()


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--select", action="store_true")
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--load-pg", action="store_true")
    a = ap.parse_args()
    if a.select:
        cands, stats = classify_and_rank()
        print(json.dumps(stats, ensure_ascii=False))
        from collections import Counter
        print(Counter(c["stratum"] for c in cands))
        for c in select_10(cands):
            print(f"  [{c['stratum']}] soft={c['top_soft']:.3f} #{c['track_id']} {c['title']} — {c['artist']} ({c['genre']})")
    elif a.build:
        build()
    elif a.load_pg:
        load_pg()
    else:
        ap.print_help()
