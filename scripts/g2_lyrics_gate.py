#!/usr/bin/env python3
"""g2_lyrics_gate.py — 레오뮤직OS G2 가사게이트 v0 (S2→S3 관문).

발주: kee 2026-07-11 (주담당 sunolanguage, 리뷰 leomusic). LEO Tier2 GO.
스펙: 가사 체크리스트 5항목 PASS/FAIL (정량화 불요 v0).
  ①음절수(멜로디 대비) ②발음 난이도 ③금칙어 ④컨셉 일치 ⑤코퍼스 규격

G5 원칙 적용(3070 수출본 07-11):
  - 자연 기준선: 코퍼스 실측 분포만 사용 [MEASURED], 매직넘버 금지
  - Tukey fence: 곡 단위 개별 판정 = Q1-1.5·IQR ~ Q3+1.5·IQR (p10-p90 금지)
  - role enum: hard_fail(게이트 차단) / report_only(권고, verdict 미반영) 명시 구분
  - 정직 보류: 주관 항목은 outside_gate로 — 게이트 PASS가 보증하지 않음을 명시
  - 미측정=NOT_COMPARED 정직 표기 (멜로디 스펙 부재 시 ①은 기준선 대조만)

사용:
  # 자연 기준선 빌드 (songs DB generated 가사 실측 → data/g2_baseline.json)
  python3 scripts/g2_lyrics_gate.py build-baseline

  # 게이트 판정 (가사 파일 → JSON verdict, 여권 history[].gate 호환)
  python3 scripts/g2_lyrics_gate.py check lyrics.txt \
      --concept "왕의 고독, 밤의 궁궐" \
      --concept-keywords "고독,궁궐" \
      --melody-spec '{"syllables_per_line":[4,14]}' \
      --json

verdict 규칙: hard_fail 항목 중 하나라도 FAIL → 게이트 FAIL(여권 반송).
report_only 항목의 FAIL은 권고로만 표기.
"""
from __future__ import annotations
import argparse, json, os, re, sys, unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASELINE_PATH = ROOT / "data" / "g2_baseline.json"

# ---------------------------------------------------------------- 공통 유틸

HANGUL = re.compile(r"[가-힣]")
BRACKET_LINE = re.compile(r"^\s*\[[^\]]*\]\s*$")
SECTION_TAG = re.compile(r"^\s*\[(Intro|Verse|Chorus|Pre-Chorus|Bridge|Hook|Outro|Interlude|Instrumental|Build|Climax|Theme|Reprise|Main Riff|Refrain)[^\]]*\]\s*$", re.I)

# 겹받침 (복합 종성)
COMPLEX_CODA = set("ㄳㄵㄶㄺㄻㄼㄽㄾㄿㅀㅄ")
# 파열음/파찰음 초성 (경계 클러스터 근사)
HARD_ONSET = set("ㄱㄲㅋㄷㄸㅌㅂㅃㅍㅈㅉㅊ")
HARD_CODA = set("ㄱㄲㅋㄷㅌㅂㅍㅅㅆㅈㅊ")

CHO = "ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ"
JONG = " ㄱㄲㄳㄴㄵㄶㄷㄹㄺㄻㄼㄽㄾㄿㅀㅁㅂㅄㅅㅆㅇㅈㅊㅋㅌㅍㅎ"


def decompose(ch: str):
    """한글 음절 → (초성, 종성) 자모. 비한글은 None."""
    o = ord(ch)
    if not (0xAC00 <= o <= 0xD7A3):
        return None
    idx = o - 0xAC00
    return CHO[idx // 588], JONG[idx % 28]


def vocal_lines(lyrics: str) -> list[str]:
    """브라켓 전용 행(섹션/디렉티브) 제외한 가창 행."""
    out = []
    for ln in lyrics.splitlines():
        s = ln.strip()
        if not s or BRACKET_LINE.match(s):
            continue
        out.append(s)
    return out


def sections(lyrics: str) -> list[tuple[str, list[str]]]:
    """[섹션태그] 기준 분할 → (태그, 가창행들)."""
    cur, buf, out = None, [], []
    for ln in lyrics.splitlines():
        s = ln.strip()
        if SECTION_TAG.match(s):
            if cur is not None:
                out.append((cur, buf))
            cur, buf = s.strip("[] \t"), []
        elif s and not BRACKET_LINE.match(s):
            buf.append(s)
    if cur is not None:
        out.append((cur, buf))
    return out


def line_metrics(line: str) -> dict:
    """행 단위 음절/발음 지표."""
    sylls = [ch for ch in line if HANGUL.match(ch)]
    n = len(sylls)
    coda = complex_c = cluster = 0
    prev_coda = " "
    for ch in sylls:
        cho, jong = decompose(ch)
        if jong != " ":
            coda += 1
        if jong in COMPLEX_CODA:
            complex_c += 1
        if prev_coda in HARD_CODA and cho in HARD_ONSET:
            cluster += 1
        prev_coda = jong
    return {
        "syllables": n,
        "coda_ratio": round(coda / n, 3) if n else 0.0,
        "complex_coda": complex_c,
        "cluster_per_10": round(cluster / n * 10, 2) if n else 0.0,
    }


def tukey(values: list[float]) -> dict:
    """Tukey fence. zero-inflated 분포(Q3=0)는 비영값 부분분포로 재계산 —
    fence 퇴화(hi=0 → 전건 오탐) 방지. 매직넘버 아님: 여전히 실측 분포 기반."""
    vs = sorted(values)
    if len(vs) < 4:
        return {"q1": None, "q3": None, "lo": None, "hi": None, "n": len(vs)}
    def pct(arr, p):
        k = (len(arr) - 1) * p
        f, c = int(k), min(int(k) + 1, len(arr) - 1)
        return arr[f] + (arr[c] - arr[f]) * (k - f)
    q1, q3 = pct(vs, 0.25), pct(vs, 0.75)
    zero_inflated = False
    if q3 == 0:
        nz = [v for v in vs if v > 0]
        if len(nz) >= 4:
            zero_inflated = True
            q1, q3 = pct(nz, 0.25), pct(nz, 0.75)
    iqr = q3 - q1
    out = {"q1": round(q1, 3), "q3": round(q3, 3),
           "lo": round(q1 - 1.5 * iqr, 3), "hi": round(q3 + 1.5 * iqr, 3), "n": len(vs)}
    if zero_inflated:
        out["zero_inflated_nonzero_fence"] = True
        out["lo"] = 0.0  # 0은 항상 정상 (비영값 fence는 상한 판정 전용)
    return out


# ---------------------------------------------------------------- 금칙어 (v0 기본)

FORBIDDEN_DEFAULT = [
    "씨발", "시발", "씨팔", "개새끼", "개새기", "병신", "지랄", "좆", "썅",
    "미친년", "미친놈", "느금", "니미", "엿먹", "꺼져라",
]
# 오탐 예외 (금칙어를 부분 포함하나 정상 단어)
FORBIDDEN_EXCEPTIONS = ["시발점", "시발역", "시발자동차"]


# ---------------------------------------------------------------- 5항목 체크

def check_syllables(lyrics: str, melody_spec: dict | None, baseline: dict | None) -> dict:
    """①음절수(멜로디 대비). 스펙 제공=hard / 부재=기준선 대조 NOT_COMPARED(권고)."""
    lines = vocal_lines(lyrics)
    per_line = [(ln, line_metrics(ln)["syllables"]) for ln in lines]
    if melody_spec and "syllables_per_line" in melody_spec:
        lo, hi = melody_spec["syllables_per_line"]
        bad = [{"line": ln, "syllables": s, "expected": [lo, hi]}
               for ln, s in per_line if s and not (lo <= s <= hi)]
        return {"id": 1, "name": "음절수(멜로디 대비)", "role": "hard_fail",
                "verdict": "FAIL" if bad else "PASS",
                "detail": {"basis": "melody_spec 제공 — 행당 음절 범위 대조",
                           "violations": bad[:10], "n_violations": len(bad)}}
    # 스펙 부재 — 코퍼스 자연 기준선 대조 (정직: 미비교 표기)
    detail = {"basis": "멜로디 스펙 부재 → NOT_COMPARED(멜로디 대비 판정 불가). 코퍼스 분포 대조 권고만"}
    if baseline:
        fence = baseline["fences"]["syllables"]
        out = [{"line": ln, "syllables": s} for ln, s in per_line
               if s and (s < fence["lo"] or s > fence["hi"])]
        detail["corpus_fence"] = fence
        detail["outliers"] = out[:10]
        detail["n_outliers"] = len(out)
    return {"id": 1, "name": "음절수(멜로디 대비)", "role": "report_only",
            "verdict": "NOT_COMPARED", "detail": detail}


def check_pronunciation(lyrics: str, baseline: dict | None) -> dict:
    """②발음 난이도 — 받침밀도/겹받침/경계클러스터 vs 코퍼스 Tukey fence (report_only)."""
    lines = vocal_lines(lyrics)
    flags = []
    if baseline:
        f_coda = baseline["fences"]["coda_ratio"]
        f_clus = baseline["fences"]["cluster_per_10"]
        for ln in lines:
            m = line_metrics(ln)
            if m["syllables"] < 2:
                continue
            reasons = []
            if f_coda["hi"] is not None and m["coda_ratio"] > f_coda["hi"]:
                reasons.append(f"받침밀도 {m['coda_ratio']}>{f_coda['hi']}")
            if f_clus["hi"] is not None and m["cluster_per_10"] > f_clus["hi"]:
                reasons.append(f"클러스터/10음절 {m['cluster_per_10']}>{f_clus['hi']}")
            if m["complex_coda"] >= 3:
                reasons.append(f"겹받침 {m['complex_coda']}행")
            if reasons:
                flags.append({"line": ln, "reasons": reasons})
        basis = f"코퍼스 실측 fence [MEASURED n={f_coda['n']}행]"
    else:
        basis = "기준선 파일 부재 — NOT_COMPARED"
    return {"id": 2, "name": "발음 난이도", "role": "report_only",
            "verdict": ("FAIL" if flags else "PASS") if baseline else "NOT_COMPARED",
            "detail": {"basis": basis, "flagged": flags[:10], "n_flagged": len(flags)}}


def check_forbidden(lyrics: str, extra: list[str] | None = None) -> dict:
    """③금칙어 (hard_fail). 기본 리스트+확장, 예외어 오탐 제거."""
    words = FORBIDDEN_DEFAULT + (extra or [])
    text = unicodedata.normalize("NFC", lyrics)
    hits = []
    for w in words:
        for m in re.finditer(re.escape(w), text):
            ctx = text[max(0, m.start() - 5):m.end() + 5]
            if any(exc in ctx for exc in FORBIDDEN_EXCEPTIONS):
                continue
            hits.append({"word": w, "context": ctx.replace("\n", " ")})
    return {"id": 3, "name": "금칙어", "role": "hard_fail",
            "verdict": "FAIL" if hits else "PASS",
            "detail": {"basis": f"기본 {len(FORBIDDEN_DEFAULT)}어+확장 {len(extra or [])}어, 예외 {len(FORBIDDEN_EXCEPTIONS)}어",
                       "hits": hits}}


def _nouns(text: str) -> set[str]:
    try:
        from kiwipiepy import Kiwi
    except ImportError:
        return set()
    kiwi = Kiwi()
    return {t.form for t in kiwi.tokenize(text) if t.tag in ("NNG", "NNP") and len(t.form) > 1}


def check_concept(lyrics: str, concept: str | None, concept_keywords: list[str] | None) -> dict:
    """④컨셉 일치. 명시 키워드 제공=hard(계약) / 자유서술=report_only. 은유는 outside_gate."""
    if not concept and not concept_keywords:
        return {"id": 4, "name": "컨셉 일치", "role": "report_only", "verdict": "NOT_COMPARED",
                "detail": {"basis": "컨셉 미제공 — 판정 불가(정직 표기)"}}
    vocal = " ".join(vocal_lines(lyrics))
    lyr_nouns = _nouns(vocal)
    if concept_keywords:
        # 명시 키워드 = S2 계약 — 표면 또는 명사 일치 1건 이상 요구 (hard)
        hit = [k for k in concept_keywords if k in vocal or k in lyr_nouns]
        miss = [k for k in concept_keywords if k not in hit]
        return {"id": 4, "name": "컨셉 일치", "role": "hard_fail",
                "verdict": "PASS" if hit else "FAIL",
                "detail": {"basis": "명시 concept_keywords 계약 — 최소 1개 구현 요구",
                           "hit": hit, "miss": miss,
                           "note": "은유적 구현(키워드 무겹침)은 outside_gate — FAIL 시 작사가 확인 후 keyword 갱신 또는 반송"}}
    c_nouns = _nouns(concept)
    overlap = sorted(c_nouns & lyr_nouns)
    return {"id": 4, "name": "컨셉 일치", "role": "report_only",
            "verdict": "PASS" if overlap else "FAIL",
            "detail": {"basis": "자유서술 컨셉 — 명사 겹침 권고 판정(은유 한계, outside_gate 병기)",
                       "concept_nouns": sorted(c_nouns)[:15], "overlap": overlap}}


INSTRUMENT_HINT = re.compile(
    r"\b(guitar|piano|drum|bass|synth|string|vocal|chorus|verse|solo|riff|melody|beat|reverb|BPM|fade|intro|outro)\b", re.I)


def check_format(lyrics: str) -> dict:
    """⑤코퍼스 규격 (hard_fail) — 누출/1행섹션/V1≡V2/브라켓형식/유니코드 위생."""
    problems = []
    # (a) 영어 디렉티브 누출 (가창행에 한글 없음 + 악기/제작 힌트)
    for ln in vocal_lines(lyrics):
        if not HANGUL.search(ln) and INSTRUMENT_HINT.search(ln):
            problems.append({"type": "english_directive_leak", "line": ln})
    # (b) 1행 섹션 (Intro/Outro/Interlude/Instrumental 등 연주섹션은 제외)
    for tag, lines in sections(lyrics):
        base = re.sub(r"\s*\d+$", "", tag).lower()
        if base in ("intro", "outro", "interlude", "instrumental", "build", "climax", "theme", "main riff"):
            continue
        if len(lines) == 1:
            problems.append({"type": "thin_section", "section": tag, "line": lines[0]})
    # (c) 동일 섹션명 완전중복 (V1≡V2)
    seen: dict[str, list[str]] = {}
    for tag, lines in sections(lyrics):
        base = re.sub(r"\s*\d+$", "", tag).lower()
        if base in ("chorus", "hook", "refrain"):  # 후렴 반복은 관용
            continue
        body = "\n".join(lines)
        if body and body in seen.get(base, []):
            problems.append({"type": "identical_sections", "section_base": base})
        seen.setdefault(base, []).append(body)
    # (d) 브라켓 형식 (미폐합)
    for ln in lyrics.splitlines():
        if ln.count("[") != ln.count("]"):
            problems.append({"type": "unbalanced_bracket", "line": ln.strip()})
    # (e) 유니코드 위생 (NFC 불일치·zero-width·전각영숫자)
    if unicodedata.normalize("NFC", lyrics) != lyrics:
        problems.append({"type": "not_nfc_normalized"})
    if re.search(r"[​‌‍﻿]", lyrics):
        problems.append({"type": "zero_width_chars"})
    return {"id": 5, "name": "코퍼스 규격", "role": "hard_fail",
            "verdict": "FAIL" if problems else "PASS",
            "detail": {"basis": "누출/1행섹션/V1≡V2/브라켓/유니코드 (배치간 오염은 lyrics_batch_audit 소관)",
                       "problems": problems[:20], "n_problems": len(problems)}}


OUTSIDE_GATE = [
    "감성·뉘앙스·시적 완성도 (Leo 청취 영역)",
    "멜로디 싱커페이션·프레이징 적합 (실청취 필요)",
    "가창 전달력·호흡 배치",
    "은유적 컨셉 구현 (키워드 무겹침 은유는 기계 판정 불가)",
]


# ---------------------------------------------------------------- 게이트 실행

def run_gate(lyrics: str, concept: str | None = None, concept_keywords: list[str] | None = None,
             melody_spec: dict | None = None, baseline: dict | None = None,
             forbidden_extra: list[str] | None = None) -> dict:
    items = [
        check_syllables(lyrics, melody_spec, baseline),
        check_pronunciation(lyrics, baseline),
        check_forbidden(lyrics, forbidden_extra),
        check_concept(lyrics, concept, concept_keywords),
        check_format(lyrics),
    ]
    hard_fails = [i for i in items if i["role"] == "hard_fail" and i["verdict"] == "FAIL"]
    return {
        "gate": "G2", "version": "v0",
        "verdict": "FAIL" if hard_fails else "PASS",
        "hard_fail_items": [i["name"] for i in hard_fails],
        "items": items,
        "outside_gate": OUTSIDE_GATE,
        "baseline_provenance": (baseline or {}).get("provenance", "기준선 미사용"),
    }


# ---------------------------------------------------------------- 기준선 빌드

def build_baseline() -> dict:
    import psycopg2
    conf = {}
    for ln in open(os.path.expanduser("~/.config/leofamily_music/db_sunolanguage.conf")):
        ln = ln.strip()
        if "=" in ln and not ln.startswith("#"):
            k, v = ln.split("=", 1)
            conf[k.strip()] = v.strip()
    c = psycopg2.connect(host=conf["DB_HOST"], port=conf.get("DB_PORT", 5432),
                         dbname=conf["DB_NAME"], user=conf["DB_USER"], password=conf.get("DB_PASSWORD", ""))
    cur = c.cursor()
    cur.execute("SELECT global_id, lyrics FROM songs WHERE status='generated' "
                "AND lyrics IS NOT NULL AND creator='sunolanguage' ORDER BY global_id")
    rows = cur.fetchall()
    c.close()
    syl, coda, clus = [], [], []
    n_lines = 0
    for _gid, ly in rows:
        for ln in vocal_lines(ly):
            m = line_metrics(ln)
            if m["syllables"] < 2:
                continue
            n_lines += 1
            syl.append(m["syllables"])
            coda.append(m["coda_ratio"])
            clus.append(m["cluster_per_10"])
    baseline = {
        "provenance": f"[MEASURED] songs DB status=generated creator=sunolanguage {len(rows)}곡/{n_lines}가창행 (Suno 생성성공 실증분)",
        "built_from_songs": len(rows),
        "n_vocal_lines": n_lines,
        "fences": {
            "syllables": tukey([float(x) for x in syl]),
            "coda_ratio": tukey(coda),
            "cluster_per_10": tukey(clus),
        },
    }
    return baseline


def main():
    ap = argparse.ArgumentParser(description="G2 가사게이트 v0")
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build-baseline", help="songs DB 실측 → data/g2_baseline.json")
    b.add_argument("--out", default=str(BASELINE_PATH))
    k = sub.add_parser("check", help="가사 파일 게이트 판정")
    k.add_argument("lyrics_file")
    k.add_argument("--concept", default=None)
    k.add_argument("--concept-keywords", default=None, help="쉼표구분 명시 키워드(제공 시 ④ hard)")
    k.add_argument("--melody-spec", default=None, help='JSON 예: {"syllables_per_line":[4,14]} (제공 시 ① hard)')
    k.add_argument("--baseline", default=str(BASELINE_PATH))
    k.add_argument("--forbidden-extra", default=None, help="추가 금칙어 파일(줄단위)")
    k.add_argument("--json", action="store_true", help="JSON만 출력(여권 기록용)")
    args = ap.parse_args()

    if args.cmd == "build-baseline":
        bl = build_baseline()
        Path(args.out).write_text(json.dumps(bl, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"baseline → {args.out}")
        print(json.dumps(bl["fences"], ensure_ascii=False, indent=2))
        print(bl["provenance"])
        return

    lyrics = Path(args.lyrics_file).read_text(encoding="utf-8")
    baseline = None
    if Path(args.baseline).exists():
        baseline = json.loads(Path(args.baseline).read_text(encoding="utf-8"))
    melody_spec = json.loads(args.melody_spec) if args.melody_spec else None
    ckw = [w.strip() for w in args.concept_keywords.split(",") if w.strip()] if args.concept_keywords else None
    extra = None
    if args.forbidden_extra:
        extra = [w.strip() for w in Path(args.forbidden_extra).read_text(encoding="utf-8").splitlines() if w.strip()]
    result = run_gate(lyrics, args.concept, ckw, melody_spec, baseline, extra)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"=== G2 v0 verdict: {result['verdict']} ===")
        for it in result["items"]:
            mark = {"PASS": "✅", "FAIL": "❌", "NOT_COMPARED": "➖"}[it["verdict"]]
            print(f"  {mark} [{it['id']}] {it['name']} ({it['role']}) — {it['verdict']}")
            if it["verdict"] == "FAIL":
                print(f"      {json.dumps(it['detail'], ensure_ascii=False)[:300]}")
        print(f"  outside_gate: {len(result['outside_gate'])}항목 (게이트 미보증 영역)")
    sys.exit(0 if result["verdict"] == "PASS" else 1)


if __name__ == "__main__":
    main()
