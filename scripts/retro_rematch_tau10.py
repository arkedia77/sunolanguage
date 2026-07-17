#!/usr/bin/env python3
"""retro_rematch_tau10.py — 매칭 피처 재설계 v1의 1단계 소급 재현 (TAU10 판정문 = 골드셋)

설계: docs/matching_feature_redesign_v1.md (kee 검토 PASS 07-17)
대상: TAU06(run6 배제)·TAU07(run7 강등)·TAU08(run8 강등)·TAU09(run9 최상위 유지)

파이프라인(F1~F5):
  F1 스케일(하드): 'key of X major/minor' 정규 추출. ref 모드 미상(라가 등)=REF_UNKNOWN_BUCKET → 전 매칭 보류.
  F2 템포(하드밴드): BPM ±10%. ref 무템포=무템포 클래스 분리(유템포 코퍼스 배제).
  F3 장르(소프트): genre_aliases 정규화 토큰 자카드.
  F4 악기(소프트): IDF 가중 자카드 + 특징악기(고IDF) 부재 페널티.
  F5a 에너지 커브(소프트): 커브 형상 분류(rising_peak/arc/flat/wave) 일치도.
  F5b 믹싱 질감(소프트): production 키워드셋 자카드.
소프트 합성(v1 잠정 가중, 2호에서 조정): F3 .30 / F4 .30 / F5a .20 / F5b .20
증적: 구 top-5의 게이트별 스코어·신규 순위 + 신 top-3 → data/tau10_retro/retro_evidence.json

한계 정직 표기: F5a/F5b는 텍스트 프록시(실청감 아님). 코퍼스 프로필=lexical_index v3.2(496곡, run6~15와 동일 스냅샷).
"""
import json
import math
import re
import sqlite3
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEX = ROOT / "data" / "reanalysis_v2" / "lexical_index.sqlite"
MAIN = ROOT / "sunolang.db"
OUT_DIR = ROOT / "data" / "tau10_retro"

ANCHORS = {  # run_id: (TAU, 목표, LEO 노트 요지)
    6: ("TAU06", "배제", "시타르 안 씀·스케일(라가) 다름"),
    7: ("TAU07", "강등", "믹싱·이펙팅이 분위기 자체를 바꿈(사이키델릭→시티팝)"),
    8: ("TAU08", "강등", "점진 고조·강한 모티브 강조가 다름"),
    9: ("TAU09", "최상위 유지", "그나마 유사(오케스트럴)"),
}

SOFT_W = {"f3_genre": 0.30, "f4_instruments": 0.30, "f5a_curve": 0.20, "f5b_production": 0.20}
BPM_BAND = 0.10

MODE_RE = re.compile(r"key of ([A-G](?:#|b|♭|♯)?)[ -]*(major|minor)", re.I)
MODE_RE2 = re.compile(r"\b([A-G](?:#|b|♭|♯)?) (major|minor)\b", re.I)
BPM_RE = re.compile(r"(\d{2,3})\s*BPM", re.I)

CURVE_LEX = {
    "rise": ["build", "building", "builds", "swell", "crescendo", "riser", "rises",
             "escalat", "grows", "점점", "고조", "커지", "쌓"],
    "peak": ["climax", "peak", "triumphant", "explosive", "maximum", "폭발", "절정", "최대"],
    "fall": ["drop", "breakdown", "fades", "fade", "sparse outro", "여운", "잦아"],
    "flat": ["meditative", "steady throughout", "consistent", "hypnotic", "잔잔", "유지", "명상"],
}
PROD_LEX = [
    "phaser", "flanger", "flanging", "tape", "analog", "vintage", "compression", "compressed",
    "saturation", "saturated", "reverb", "hall", "plate", "room", "delay", "chorus effect",
    "distortion", "distorted", "overdriven", "lo-fi", "lofi", "clean", "gritty", "warm",
    "psychedelic", "panning", "modulation", "drone", "wide stereo", "close-mic", "close mic",
    "polished", "raw", "airy", "spacious", "intimate", "cinematic risers", "sub-bass", "sidechain",
]
# 레퍼런스 texture에서 악기 검출용 (코퍼스 엔티티 + 비서양 확장)
EXTRA_INSTR = ["sitar", "tabla", "tanpura", "sympathetic strings", "orchestra", "choir",
               "timpani", "brass", "strings", "synthesizer", "synth", "drum machine",
               "electronic percussion", "pad", "ostinato"]


def norm_mode(key_text: str):
    if not key_text:
        return None
    m = MODE_RE.search(key_text) or MODE_RE2.search(key_text)
    return m.group(2).lower() if m else None


def curve_shape(text: str) -> str:
    t = text.lower()
    pos = {}
    for cls, kws in CURVE_LEX.items():
        idxs = [t.find(k) for k in kws if t.find(k) >= 0]
        if idxs:
            pos[cls] = min(idxs)
    if "rise" in pos and ("peak" in pos or "fall" not in pos):
        return "rising_peak" if "peak" in pos else "rising"
    if "rise" in pos and "fall" in pos:
        return "arc"
    if "flat" in pos and "rise" not in pos:
        return "flat"
    if "fall" in pos:
        return "falling"
    return "unknown"


def curve_score(ref: str, cand: str) -> float:
    if ref == "unknown" or cand == "unknown":
        return 0.3  # 판단 불가 — 중립 하향
    if ref == cand:
        return 1.0
    near = {("rising_peak", "rising"), ("rising", "rising_peak"), ("arc", "rising_peak"),
            ("rising_peak", "arc")}
    return 0.6 if (ref, cand) in near else 0.0


def prod_set(text: str) -> set:
    t = text.lower()
    return {k for k in PROD_LEX if k in t}


def jaccard(a: set, b: set) -> float:
    return len(a & b) / len(a | b) if (a | b) else 0.0


def genre_tokens(g: str, aliases: dict) -> set:
    t = re.sub(r"[/&,+·]", " ", (g or "").lower())
    toks = set(t.split())
    out = set(toks)
    for canon, alist in aliases.items():
        names = {canon.lower()} | {a.lower() for a in alist} if isinstance(alist, list) else {canon.lower()}
        if toks & {w for n in names for w in n.split()}:
            out.add(canon.lower())
    return out - {"", "music", "and", "with"}


def load_corpus_profiles():
    conn = sqlite3.connect(LEX)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT song_id, source, sentence, slot, entity, genre FROM entries "
        "WHERE source IN ('suno_sp_full','leomusic_sp_full','sp_entity') ORDER BY song_id, id").fetchall()
    profs = {}
    for r in rows:
        p = profs.setdefault(str(r["song_id"]), {"text": [], "instruments": set(), "genres": Counter()})
        if r["source"] in ("suno_sp_full", "leomusic_sp_full"):
            p["text"].append(r["sentence"])
        if r["slot"] == "instrument" and r["entity"]:
            p["instruments"].add(r["entity"].lower())
        if r["genre"]:
            p["genres"][r["genre"]] += 1
    out = {}
    for sid, p in profs.items():
        text = " ".join(p["text"])
        out[sid] = {
            "mode": norm_mode(text),
            "bpm": int(BPM_RE.search(text).group(1)) if BPM_RE.search(text) else None,
            "genre": p["genres"].most_common(1)[0][0] if p["genres"] else "",
            "instruments": p["instruments"],
            "curve": curve_shape(text),
            "prod": prod_set(text),
        }
    conn.close()
    return out


def instr_idf(profiles: dict) -> dict:
    n = len(profiles)
    df = Counter()
    for p in profiles.values():
        for i in p["instruments"]:
            df[i] += 1
    return {i: math.log(n / c) for i, c in df.items()}


def ref_profile(track_row, aliases) -> dict:
    tex = (track_row["texture_description"] or "") + " " + (track_row["spatial_character"] or "")
    curve_src = (track_row["emotion_curve"] or "") + " " + tex
    instr_lex = set(EXTRA_INSTR)
    ref_instr = {i for i in instr_lex if i in tex.lower()}
    return {
        "mode": norm_mode(track_row["key"] or ""),
        "key_raw": track_row["key"],
        "bpm": track_row["bpm"] or None,
        "genre": f"{track_row['genre']} {track_row['sub_genre'] or ''}",
        "instruments": ref_instr,
        "curve": curve_shape(curve_src),
        "prod": prod_set(tex),
    }


def f4_score(ref_i: set, cand_i: set, idf: dict, med_idf: float):
    """IDF 가중 자카드 + 특징악기 부재 페널티. 반환 (score, detail)."""
    def w(i):
        return idf.get(i, med_idf * 1.5)  # 코퍼스 무존재 악기(시타르 등)=희소 최상 가중
    def hit(ri):
        return any(ri in ci or ci in ri for ci in cand_i)
    inter = sum(w(i) for i in ref_i if hit(i))
    union = sum(w(i) for i in ref_i) + sum(idf.get(i, med_idf) for i in cand_i
                                           if not any(i in ri or ri in i for ri in ref_i))
    base = inter / union if union else 0.0
    missing = [i for i in ref_i if w(i) >= med_idf and not hit(i)]
    penalty = min(0.5, 0.15 * len(missing))
    return max(0.0, base - penalty), {"missing_signature_instruments": missing, "penalty": round(penalty, 3)}


def gate_song(ref: dict, cand: dict, idf: dict, med_idf: float, aliases: dict) -> dict:
    r = {}
    # F1 스케일 (하드)
    if ref["mode"] is None:
        r["f1"] = "REF_UNKNOWN_BUCKET"  # 라가 등 — 전 매칭 보류
    elif cand["mode"] is None:
        r["f1"] = "HOLD(코퍼스 모드 미상)"
    else:
        r["f1"] = "PASS" if ref["mode"] == cand["mode"] else f"EXCLUDE(모드 {cand['mode']}≠{ref['mode']})"
    # F2 템포 (하드밴드)
    if not ref["bpm"]:
        r["f2"] = "REF_NO_TEMPO_CLASS"  # 무템포 클래스 — 유템포 코퍼스 배제
    elif not cand["bpm"]:
        r["f2"] = "HOLD(코퍼스 BPM 미상)"
    else:
        lo, hi = ref["bpm"] * (1 - BPM_BAND), ref["bpm"] * (1 + BPM_BAND)
        r["f2"] = "PASS" if lo <= cand["bpm"] <= hi else f"EXCLUDE(BPM {cand['bpm']}∉[{lo:.0f},{hi:.0f}])"
    # 소프트
    r["f3_genre"] = round(jaccard(genre_tokens(ref["genre"], aliases), genre_tokens(cand["genre"], aliases)), 3)
    f4, f4d = f4_score(ref["instruments"], cand["instruments"], idf, med_idf)
    r["f4_instruments"], r["f4_detail"] = round(f4, 3), f4d
    r["f5a_curve"] = round(curve_score(ref["curve"], cand["curve"]), 3)
    r["f5b_production"] = round(jaccard(ref["prod"], cand["prod"]), 3)
    r["soft_composite"] = round(sum(SOFT_W[k] * r[k] for k in SOFT_W), 4)
    r["hard_pass"] = r["f1"] == "PASS" and r["f2"] == "PASS"
    return r


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    aliases = json.loads((ROOT / "rag" / "genre_aliases.json").read_text()) if (ROOT / "rag" / "genre_aliases.json").exists() else {}
    profiles = load_corpus_profiles()
    idf = instr_idf(profiles)
    med_idf = sorted(idf.values())[len(idf) // 2] if idf else 1.0

    main_db = sqlite3.connect(MAIN)
    main_db.row_factory = sqlite3.Row
    evidence = {"provenance": "retro_rematch_tau10.py — 코퍼스=lexical_index v3.2(496곡, run6~15 동일 스냅샷), "
                              "레퍼런스=tracks 테이블 실측 필드. 가중=v1 잠정(F3 .3/F4 .3/F5a .2/F5b .2), "
                              "F5a/F5b=텍스트 프록시(실청감 아님) 정직 표기.",
                "runs": {}}
    all_pass = True
    for run_id, (tau, goal, note) in ANCHORS.items():
        tr = main_db.execute(
            "SELECT t.* FROM match_runs mr JOIN reference_items ri ON ri.id=mr.reference_item_id "
            "JOIN tracks t ON t.id=ri.track_id WHERE mr.id=?", (run_id,)).fetchone()
        ref = ref_profile(tr, aliases)
        old_top = main_db.execute(
            "SELECT corpus_song_id, ROUND(SUM(score),4) rrf FROM match_results "
            "WHERE run_id=? AND channel='fused' AND corpus_song_id IS NOT NULL "
            "GROUP BY corpus_song_id ORDER BY rrf DESC LIMIT 5", (run_id,)).fetchall()

        old_detail = []
        for rank, row in enumerate(old_top, 1):
            sid = str(row["corpus_song_id"])
            cand = profiles.get(sid)
            if not cand:
                old_detail.append({"old_rank": rank, "song_id": sid, "error": "프로필 없음(인덱스 밖)"})
                continue
            g = gate_song(ref, cand, idf, med_idf, aliases)
            old_detail.append({"old_rank": rank, "song_id": sid, "old_rrf": row["rrf"],
                               "cand_profile": {"mode": cand["mode"], "bpm": cand["bpm"],
                                                "genre": cand["genre"], "curve": cand["curve"],
                                                "n_instruments": len(cand["instruments"])},
                               "gates": g})
        # 신 파이프라인 top-3 (하드게이트 통과분 소프트 순)
        new_ranked = []
        if ref["mode"] is not None and ref["bpm"]:
            for sid, cand in profiles.items():
                g = gate_song(ref, cand, idf, med_idf, aliases)
                if g["hard_pass"]:
                    new_ranked.append({"song_id": sid, "soft": g["soft_composite"], "gates": g})
            new_ranked.sort(key=lambda x: -x["soft"])
        new_rank_of = {e["song_id"]: i + 1 for i, e in enumerate(new_ranked)}

        # 목표 판정
        if goal == "배제":
            achieved = ref["mode"] is None  # REF_UNKNOWN_BUCKET → 전 매칭 보류
            verdict_note = "F1 REF_UNKNOWN_BUCKET(라가=서양 모드 미상) → 전 코퍼스 매칭 보류=배제 달성" if achieved else "미달성"
        elif goal == "강등":
            olds = [d for d in old_detail if "gates" in d]
            demoted = all((not d["gates"]["hard_pass"]) or
                          (new_rank_of.get(d["song_id"], 10**6) > d["old_rank"]) for d in olds)
            achieved = demoted and bool(olds)
            verdict_note = "구 top-5 전건: 하드게이트 탈락 또는 신 순위 하락"
        else:  # 최상위 유지
            old1 = str(old_top[0]["corpus_song_id"]) if old_top else None
            nr = new_rank_of.get(old1)
            achieved = nr is not None and nr <= 3
            verdict_note = f"구 1위 {old1} → 신 순위 {nr} (top-3 이내={achieved})"
        all_pass &= achieved
        evidence["runs"][tau] = {
            "run_id": run_id, "reference": {"title": tr["title"], "artist": tr["artist"],
                                            "key_raw": ref["key_raw"], "mode": ref["mode"],
                                            "bpm": ref["bpm"], "genre": ref["genre"].strip(),
                                            "curve": ref["curve"], "instruments": sorted(ref["instruments"]),
                                            "prod": sorted(ref["prod"])},
            "leo_note": note, "goal": goal,
            "old_top5_gated": old_detail,
            "new_top3": [{"song_id": e["song_id"], "soft": e["soft"],
                          "f3": e["gates"]["f3_genre"], "f4": e["gates"]["f4_instruments"],
                          "f5a": e["gates"]["f5a_curve"], "f5b": e["gates"]["f5b_production"]}
                         for e in new_ranked[:3]],
            "n_hard_pass_candidates": len(new_ranked),
            "achieved": achieved, "verdict_note": verdict_note,
        }
        print(f"{tau} [{goal}] → {'✅' if achieved else '❌'} {verdict_note}")

    evidence["all_pass"] = all_pass
    out = OUT_DIR / "retro_evidence.json"
    out.write_text(json.dumps(evidence, ensure_ascii=False, indent=1))
    print(f"\n전건 정합: {all_pass} → {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
