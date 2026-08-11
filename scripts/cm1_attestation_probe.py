#!/usr/bin/env python3
"""CM-2026-0001(encore 조회) 회신 근거 실측 — 나레이션·음역·길이 어휘의 attested + uptake.

물음(encore 08-11): ⑴나레이션 구간을 생성으로 얻는 경로가 코퍼스에 있나 ⑵듀엣 화자분리
⑶최고음 A4를 넘지 않게 SP로 유도되나 ⑷길이에 기여하는 SP 어휘가 있나.

★설계 — 지난 오류 2건을 절차로 막는다:
  ⓐ같은 자로 잰다(08-04 오류): 요청층·관측층 **모두 동일한 소문자 부분문자열**로 계수.
    한쪽만 파서 정규화하면 `soft synth pads`↔`synthesizer`가 불일치로 잡힌다.
  ⓑ철자를 코퍼스에서 가져온다(08-09 거짓음성 2건): `mid-register`는 0건인데
    attested 형태는 `mid-range`였다. **내가 떠올린 철자로 0건을 내면 「없음」이 아니라 「안 봄」이다.**
  ⓒ★검정력을 같이 낸다: 「동시 0」은 uptake 부재의 증거가 아니다.
    기대 동시(요청n × 미요청군 기저율)가 3곡 미만이면 **판정 불가**로 찍는다.

층 정의(경계):
  관측층 suno_sp_full 497곡 = **Suno가 렌더 결과를 스스로 서술한 문장**. 오디오 측정이 아니다.
  요청층 leomusic_sp_full 425곡 = 우리가 쓴 SP. 쌍(둘 다 보유) 425곡.
  → 「관측에 안 났다」 = 「소리가 안 났다」가 아니라 **「Suno가 그 말을 안 했다」**.
"""
import json
import random
import re
import sqlite3
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DB = REPO / "data" / "reanalysis_v2" / "lexical_index.sqlite"
OUT = REPO / "data" / "exchange" / "cm1_narration_register_attestation.json"
SEED = 20260811
TRIALS = 2000

conn = sqlite3.connect(DB)


def texts(source):
    d = {}
    for sid, sent in conn.execute(
            "select song_id, sentence from entries where source=?", (source,)):
        d.setdefault(sid, []).append((sent or "").lower())
    return {k: " \n ".join(v) for k, v in d.items()}


REQ = texts("leomusic_sp_full")
OBS = texts("suno_sp_full")
PAIR = sorted(set(REQ) & set(OBS), key=str)
N = len(PAIR)


def uptake(term):
    t = term.lower()
    req = [s for s in PAIR if t in REQ[s]]
    both = sum(1 for s in req if t in OBS[s])
    n_not = N - len(req)
    base = (sum(1 for s in PAIR if t in OBS[s] and s not in set(req)) / n_not) if n_not else 0.0
    expected = len(req) * base
    pval = None
    if req and any(t in OBS[s] for s in PAIR):
        rnd = random.Random(SEED)
        obs = [1 if t in OBS[s] else 0 for s in PAIR]
        hits = sum(1 for _ in range(TRIALS)
                   if sum(obs[i] for i in rnd.sample(range(N), len(req))) >= both)
        pval = (hits + 1) / (TRIALS + 1)
    if not req:
        verdict = "요청 0곡 — ★안 해봄(부재 아님)"
    elif expected < 3:
        verdict = f"★검정력 부족(기대 {expected:.1f}곡) — 판정 불가"
    elif both == 0:
        verdict = "기대 대비 0 — uptake 부재 신호"
    elif both <= expected:
        verdict = "기저율과 동일 — ★요청이 확률을 못 올림"
    else:
        verdict = "uptake 있음 방향"
    return {
        "요청곡수": len(req), "동시": both,
        "미요청군_기저율": round(base, 3), "기대동시": round(expected, 1),
        "순열p": round(pval, 4) if pval is not None else None,
        "관측_attested_497곡중": sum(1 for v in OBS.values() if t in v),
        "판정": verdict,
    }


GROUPS = {
    "Q1_말하기": ["spoken-word", "spoken-word style", "spoken-word performance", "spoken",
                  "almost spoken", "narrative", "narration", "narrator", "monologue",
                  "voiceover", "recitative", "sprechgesang", "conversational",
                  "storytelling", "transitioning into", "transitioning to a"],
    "Q3_음역음색": ["baritone", "conversational baritone", "tenor", "conversational tenor",
                    "chest voice", "head voice", "falsetto", "belted",
                    "mid-range", "mid-register", "middle register",
                    "lower register", "low-register", "low register", "upper register",
                    "comfortable", "relaxed", "restrained", "understated",
                    "intimate", "close-mic", "soft", "warm", "deep", "powerful", "soaring"],
    "Q4_길이구조": ["outro", "intro", "interlude", "instrumental break", "bridge",
                    "extended", "short", "concise", "repeat", "fade out", "coda"],
}

KEY_A = re.compile(r'\b(?:in the )?key of\s+([a-g][#b♯♭]?\s*(?:major|minor|maj|min)?)')
KEY_B = re.compile(r'\b([a-g][#b]?)\s+(major|minor)\b')
BPM = re.compile(r'(\d{2,3})\s*bpm')


def keyset(t):
    return {m.group(1).strip() for m in KEY_A.finditer(t)} | {
        " ".join(m.groups()) for m in KEY_B.finditer(t)}


def numeric_compliance():
    """수치형 지시(키·BPM)의 준수율. ★관측층은 Suno 자체 분석기라 분석기 오차가 섞인다."""
    k_both = k_hit = 0
    for s in PAIR:
        kr, ko = keyset(REQ[s]), keyset(OBS[s])
        if kr and ko:
            k_both += 1
            k_hit += bool(kr & ko)
    exact = near = octave = other = 0
    for s in PAIR:
        a, b = BPM.search(REQ[s]), BPM.search(OBS[s])
        if not (a and b):
            continue
        r, o = int(a.group(1)), int(b.group(1))
        if r == o:
            exact += 1
        elif abs(r - o) <= 3:
            near += 1
        elif abs(r * 2 - o) <= 4 or abs(r - o * 2) <= 4:
            octave += 1
        else:
            other += 1
    bt = exact + near + octave + other
    return {
        "키": {"양층_명시": k_both, "문자열_일치": k_hit,
               "준수율": round(k_hit / k_both, 3) if k_both else None},
        "BPM": {"양층_명시": bt, "정확": exact, "±3": near,
                "배·반배_아티팩트": octave, "그외_불일치": other,
                "실질일치율(정확+±3)": round((exact + near) / bt, 3) if bt else None},
        "★교란": "관측 BPM·키는 Suno 자체 분석기 추정치다. 불일치에 렌더 미준수와 "
                 "분석기 오차가 섞여 있고 **본 실측은 둘을 분리하지 못한다.** 상한으로만 읽을 것.",
    }


result = {
    "생성": "scripts/cm1_attestation_probe.py",
    "설계": {
        "관측층": f"suno_sp_full {len(OBS)}곡 — Suno 자기 서술문(★오디오 아님)",
        "요청층": f"leomusic_sp_full {len(REQ)}곡 — 우리가 쓴 SP",
        "쌍": N,
        "자": "양층 동일 소문자 부분문자열(비대칭 계수 금지)",
        "순열": f"요청 라벨 셔플 {TRIALS}회, seed={SEED}",
        "★사전등록_없음": "본건은 조회 응답용 기술통계다. 가설 검정으로 인용하지 말 것 — "
                          "임계값을 미리 고정하지 않았다(08-04 골대 옮기기 재발 방지).",
    },
    "어휘": {g: {t: uptake(t) for t in ts} for g, ts in GROUPS.items()},
    "수치형_지시_준수": numeric_compliance(),
}

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(result, ensure_ascii=False, indent=1))
print(f"WROTE {OUT.relative_to(REPO)}")
for g, rows in result["어휘"].items():
    print(f"\n== {g}")
    for t, v in rows.items():
        print(f"  {t:24} 요청{v['요청곡수']:>4} 동시{v['동시']:>4} "
              f"기대{v['기대동시']:>5} attested{v['관측_attested_497곡중']:>4}  {v['판정']}")
print("\n== 수치형 지시")
print(json.dumps(result["수치형_지시_준수"], ensure_ascii=False, indent=1))
