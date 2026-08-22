#!/usr/bin/env python3
"""w030_harmony_probe.py — 축 H(화성·전조) 코퍼스 실측. leomusic-trot W030 선조회 회신 근거.

발주: leomusic-trot 2026-08-22 (W030 5문항 + 회피목록 재판정).

★이 스크립트가 존재하는 이유 = 재현. 수치를 말로 옮기면 다음 사람이 못 고친다.

층 정의 (lexical_index.sqlite `entries.source`):
  입력층 = leomusic_sp_full   (우리가 Suno에 넣은 원본 SP 전문, 425곡)
  출력층 = suno_sp_full / sp_entity / bracket_entity (Suno 재분석 서술문, 530곡)
  스템   = stems_sp / stems_bracket (외부 업로드 분석, 94곡)
  ★입력층 **브라켓은 이 색인에 없다**(SP 전문만). 입력층 수치는 산문 한정.

★동음이의 필수 분리: `modulation`은 조성 전조와 **필터/LFO 모듈레이션**이 섞인다.
  스템의 modulation 히트 13곡 중 12곡이 필터 계열이었다 — 안 가르면 13배 오보.
★조회 어휘를 내가 짓는 한 「없음」과 「못 찾음」이 섞인다: 1차 스캔에서 `resolving to`를
  빼먹어 S018_16(유일한 성공 사례)을 미지시군으로 오분류했다. 아래 MOVE는 그 교정본.

사용: python3 scripts/w030_harmony_probe.py [--dump]
"""
from __future__ import annotations
import json, re, sqlite3, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEX = ROOT / "data/reanalysis_v2/lexical_index.sqlite"
MERGED = ROOT / "data/reanalysis_v2/merged_4values.json"

MOVE = re.compile(r"modulat\w*|key change|transpos\w*|shifting to|shifts to|resolving to|"
                  r"resolves to|moving to|moves to|settling into|settles into", re.I)
KEYNAME = re.compile(r"\b([A-G](?:#|b|♯|♭)?)\s*(major|minor|maj|m)\b", re.I)
TIMBRE = re.compile(r"filter|cutoff|\blfo\b|low-frequency oscillator|resonan|saw|reese|timbre|"
                    r"synth (bass|lead|pad|sequence|pulse)|drone|wow and flutter", re.I)
TONAL = re.compile(r"\bkey\b|\bkeys\b|major|minor|chorus|bridge|section|chromatic|harmonic|tonal", re.I)
EXCL = re.compile(r"sus chords|head voice|airy head|chest verses|swing groove|"
                  r"straight on chorus|chorus modulation|tape-warp", re.I)

# 입력층 전조 지시곡 — 위 규칙 스캔 후 육안 감사로 확정한 전수(감사 기록=회신 본문)
PRESCRIBED = {"1135","1146","1386","1396","1427","1445","1446","1507","1508","1535","1539","1547",
 "1553","1558","1580","1630","1644","1660","1733","1766","10021","10464","10466","10472","1100",
 "1107","1149","1399","1432","1433","1451","S018_16","123","133","1126","1485","1405","1414","1415","10469"}


def out_modulation(sp: str):
    """출력층 서술문에서 ★조성 전조 문장만 반환(음색 모듈레이션 배제)."""
    for s in re.split(r"(?<=[.])\s+", sp or ""):
        if MOVE.search(s) and TONAL.search(s) and not TIMBRE.search(s) and not EXCL.search(s):
            return s.strip()
    return None


def paired_contrast(dump=False):
    data = json.loads(MERGED.read_text(encoding="utf-8"))
    pres, base = [], []
    for m in data:
        if not (m["leomusic_original"].get("sp") or "").strip():
            continue                                  # 입력층 SP 없는 곡=짝 대조 불가
        hit = out_modulation(" ".join((r.get("sp") or "") for r in m["suno_reanalysis"]))
        (pres if str(m["song_id"]) in PRESCRIBED else base).append((m["song_id"], hit))
    ph = [(s, h) for s, h in pres if h]
    bh = [(s, h) for s, h in base if h]
    print("╔═ 짝지어진 대조 — 우리 생성곡 425곡(입력층 SP 보유분) ═╗")
    print(f"  전조 지시군   {len(pres):>3}곡 → 출력층 전조 서술 {len(ph)}곡 = {len(ph)/len(pres)*100:.1f}%")
    print(f"  미지시 기저군 {len(base):>3}곡 → 출력층 전조 서술 {len(bh)}곡 = {len(bh)/len(base)*100:.2f}%")
    for tag, rows in (("지시군", ph), ("기저군", bh)):
        for s, h in rows:
            print(f"    [{tag}] {s}: {h[:130]}")
    return len(pres), len(ph), len(base), len(bh)


def term_table(terms, title):
    con = sqlite3.connect(LEX)
    src = lambda s: con.execute("SELECT song_id, sentence FROM entries WHERE source=?", (s,)).fetchall()
    L = {k: src(k) for k in ("sp_entity", "bracket_entity", "suno_sp_full",
                             "leomusic_sp_full", "stems_sp", "stems_bracket")}
    print(f"\n{'='*94}\n{title}   (행=원행/중복제거 · ★곡 수가 주 지표)\n{'='*94}")
    print(f"{'표현':<22}{'출력 원행':>9}{'출력 제거행':>11}{'출력 곡':>8}{'입력 곡':>8}{'스템 곡':>8}")
    for t in terms:
        p = re.compile(r"(?<![a-z])" + re.escape(t) + r"(?![a-z])", re.I)
        def h(keys):
            r = [(s, x) for k in keys for s, x in L[k] if p.search(x or "")]
            return len(r), len({(s, x) for s, x in r}), len({s for s, _ in r})
        o_raw, o_ded, o_song = h(("sp_entity", "bracket_entity"))
        _, _, i_song = h(("leomusic_sp_full",))
        _, _, s_song = h(("stems_sp", "stems_bracket"))
        _, _, of_song = h(("suno_sp_full",))
        print(f"{t:<22}{o_raw:>9}{o_ded:>11}{max(o_song, of_song):>8}{i_song:>8}{s_song:>8}")


if __name__ == "__main__":
    paired_contrast("--dump" in sys.argv)
    term_table(["chord progression", "chord progressions", "modal", "suspended", "arco",
                "octave bounce", "programmed", "vintage", "timbales", "singalong", "sing-along"],
               "Q3 leomusic-trot 회피목록 재판정")
    term_table(["minor seventh", "major seventh", "seventh", "ninth", "diminished",
                "turnaround", "borrowed chord", "relative major", "added ninth", "suspended fourth"],
               "Q4 화성 색채 어휘")
