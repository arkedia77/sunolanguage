#!/usr/bin/env python3
"""B192 10곡 SP를 v3 어휘/문법 기준으로 검토 (단어 수준).

v3 어휘 phrase를 토큰으로 분해해 '알려진 단어 집합'을 만든다.
각 SP의 단어 중 이 집합에도 없고 structural/stop도 아닌 것이 'novel 단어'.
이걸 곡별로 취합하고 Leo 확인용 표로 묶는다.

출력: docs/b192_sp_review.md
"""

from __future__ import annotations
import json, re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path("/Users/leo/sunolanguage")
B192_PATH = Path("/tmp/b192_sp.json")
PILOT_PATH = Path("/Users/leo/leomusic/06_GENERATION/B192_STEP6_7_8_pilot_v3.json")
V3_VOCAB_PATH = Path("/tmp/v3_vocab_all.json")
OUT = ROOT / "docs" / "b192_sp_review.md"

STATUS = {g: "✅ generated" for g in (1773, 1774, 1775)}
for g in (1776, 1777, 1778, 1779, 1780, 1781, 1782):
    STATUS[g] = "❌ pending (폐기)"

STOP = {
    "a","an","the","and","with","of","in","on","at","into","from","to","that","as",
    "is","are","has","have","be","been","was","were","it","its","their","them",
    "this","these","those","there","here","for","by","or","but","no","not","any",
    "each","all","some","every","more","most","less","very","quite","most",
    "throughout","before","after","during","while","against","between","through",
    "plays","play","played","playing","enter","enters","entering","entered",
    "builds","building","built","sustains","sustained","follows","followed","following",
    "rises","rising","doubled","layered","provides","provided","adds","added","layers",
    "enters","walks","punches","plucks","moving","delivering","maintaining","centered",
    "lifts","alternates","alternating","creates","creating","shifts","shifting",
    "transitions","transitioning","rolls","rolling","drives","driving","hits","hitting",
    "breathes","breathing","resonates","resonating","pulses","pulsing",
    "one","two","three","four","five","six","seven","eight","nine","ten","zero",
    "first","second","third","fourth","bar","bars","note","notes","beat","beats",
    "section","sections","line","lines","part","parts","phrase","phrases",
    # 구조 단어
    "verse","verses","chorus","choruses","bridge","intro","outro","interlude","pre","hook","hooks",
    "song","songs","track","tracks","music","musical",
    # 지시/단위
    "bpm","tempo","time","key","major","minor","korean","lyrics","minutes","long","must","sit","wide","forward","close","low","high","mid","full",
    "downbeat","upbeat","backbeat","rhythm","style","tone","pattern","delivery","chord","chords","sustain","register","articulation","phrasing",
    "male","female","vocal","vocals","voice","voices","harmonies","harmony",
    # 형용사 기본
    "bright","warm","soft","light","dry","clean","sparse","minimal","deep","rich","full","quiet","loud","thick","thin","heavy","tight","punchy","smooth","crisp","melodic","rhythmic","steady",
    # alphabet keys letter-pitches
    "c","d","e","f","g","a","b","ab","bb","eb","db","gb","cm","dm","em","fm","gm","am","bm",
    # 흔한 악기 형용사 — 단일 단어는 v3 모디파이어에서 대부분 커버될 것
}


def load_v3_vocab() -> dict:
    return json.loads(V3_VOCAB_PATH.read_text())


def v3_word_set(v: dict) -> set[str]:
    """v3 phrase들을 토큰화해 단어 수준 집합 구축."""
    out: set[str] = set()
    for cat in ("entities", "modifiers", "effects", "chords", "patterns"):
        for ph in v.get(cat, []):
            for tok in re.split(r"[^\w\-]+", ph.lower()):
                tok = tok.strip("-")
                if tok:
                    out.add(tok)
    return out


def load_declared_inferred() -> dict[int, set[str]]:
    pilot = json.loads(PILOT_PATH.read_text())
    out = {}
    for s in pilot["songs"]:
        gid = s["song_id"]
        terms: set[str] = set()
        for step in ("step6_voicing", "step7_sp"):
            v = s.get(step, {}) or {}
            for t in v.get("inferred_vocab_used", []) or []:
                terms.add(t.lower().strip())
        out[gid] = terms
    return out


def tokenize_sp(sp: str) -> list[str]:
    cleaned = re.sub(r"[^\w\s\-']", " ", sp.lower())
    return [t.strip("'-") for t in cleaned.split() if t.strip("'-")]


def main() -> None:
    v3 = load_v3_vocab()
    v3_words = v3_word_set(v3)
    declared = load_declared_inferred()
    songs = json.loads(B192_PATH.read_text())

    # 각 곡 novel token 추출
    per_song_novel: dict[int, Counter] = {}
    novel_global: dict[str, set[int]] = defaultdict(set)
    declared_tokens: dict[int, set[str]] = {}
    for s in songs:
        gid = s["gid"]
        inf = declared.get(gid, set())
        inf_words = set()
        for t in inf:
            for w in re.split(r"[^\w]+", t.lower()):
                w = w.strip("-")
                if w:
                    inf_words.add(w)
        declared_tokens[gid] = inf_words

        toks = tokenize_sp(s["sp"])
        novel = Counter()
        for t in toks:
            if len(t) < 3: continue
            if t.isdigit(): continue
            if t in STOP: continue
            if t in v3_words: continue
            if t in inf_words: continue  # 이미 선언된 inferred
            novel[t] += 1
        per_song_novel[gid] = novel
        for t in novel:
            novel_global[t].add(gid)

    # 출력
    lines = []
    lines.append("# B192 10곡 SP 검토 — v3 어휘/문법 준수 실측")
    lines.append("")
    lines.append(
        "sunolanguage가 배포한 v3 어휘와 문법을 기준으로, 각 SP에 (a) v3에도 없고 "
        "(b) 파일럿이 inferred_vocab_used로 선언하지도 않은 **novel 단어**가 뭔지 스캔. "
        "쓸데없이 들어간 건지, 확장 어휘로 추가할 가치가 있는지 Leo 판정 필요."
    )
    lines.append("")
    lines.append(
        f"**v3 어휘 범위**: phrase 총 {sum(len(v3[k]) for k in ['entities','modifiers','patterns','effects','chords'])}개 "
        f"(토큰화 시 유니크 단어 {len(v3_words)}개)"
    )
    lines.append("")

    # 1) 곡별 요약
    lines.append("## 1. 곡별 요약")
    lines.append("")
    lines.append("| gid | 제목 | 상태 | SP자 | novel단어 | declared inferred |")
    lines.append("|---:|---|---|---:|---:|---|")
    for s in songs:
        gid = s["gid"]
        inf = declared.get(gid, set())
        inf_str = ", ".join(sorted(inf)) if inf else "-"
        lines.append(
            f"| {gid} | {s['title']} | {STATUS.get(gid,'?')} | {len(s['sp'])} | "
            f"{len(per_song_novel[gid])} | {inf_str} |"
        )
    lines.append("")

    # 2) 전역 novel 단어 — 등장 곡 수 기준
    lines.append("## 2. Leo 확인 요청 — v3 밖 novel 단어 (선언 없이 SP에 투입됨)")
    lines.append("")
    lines.append(
        "**판정 요청**: 각 단어에 대해 ① Suno가 반응 가능한 정상 어휘인가 "
        "② v3 어휘에 추가할 확장 후보인가 ③ 쓸데없이 들어간 건가."
    )
    lines.append("")
    lines.append("### 2-1. 2곡 이상 등장 (공통 novel — 더원 규칙이 밀어넣는 상수 후보)")
    lines.append("")
    lines.append("| 단어 | 등장곡수 | 등장 gid | 성공/폐기 |")
    lines.append("|---|---:|---|---|")
    common = [(w, gids) for w, gids in novel_global.items() if len(gids) >= 2]
    common.sort(key=lambda x: (-len(x[1]), x[0]))
    for w, gids in common:
        good = sum(1 for g in gids if g in (1773,1774,1775))
        bad = len(gids) - good
        lines.append(f"| `{w}` | {len(gids)} | {', '.join(str(g) for g in sorted(gids))} | ✅{good}/❌{bad} |")
    lines.append("")

    # 3) 곡별 novel (각 곡만의 특이 어휘)
    lines.append("### 2-2. 곡별 고유 novel 단어 (해당 곡에만 등장)")
    lines.append("")
    for s in songs:
        gid = s["gid"]
        uniq = {w: c for w, c in per_song_novel[gid].items() if len(novel_global[w]) == 1}
        if not uniq: continue
        lines.append(f"**gid {gid} ({s['title']}) [{STATUS.get(gid,'?')}]**")
        lines.append("")
        for w, c in sorted(uniq.items()):
            lines.append(f"- `{w}` (×{c})")
        lines.append("")

    # 4) 선언된 inferred 목록 (추적성 확보된 것들)
    lines.append("## 3. 선언된 inferred_vocab (이미 추적 중)")
    lines.append("")
    lines.append(
        "이미 `inferred_vocab_used`로 명시 선언된 확장 어휘. 추적성은 확보됐지만 "
        "Suno 반응 보장은 없음 — 아래는 Leo 사전 승인 여부 확인 대상."
    )
    lines.append("")
    all_decl: dict[str, list[int]] = defaultdict(list)
    for gid, ts in declared.items():
        for t in ts:
            all_decl[t].append(gid)
    lines.append("| phrase | 등장곡수 | 등장 gid | 성공/폐기 |")
    lines.append("|---|---:|---|---|")
    for ph, gids in sorted(all_decl.items(), key=lambda x: (-len(x[1]), x[0])):
        good = sum(1 for g in gids if g in (1773,1774,1775))
        bad = len(gids) - good
        lines.append(f"| `{ph}` | {len(gids)} | {', '.join(str(g) for g in sorted(gids))} | ✅{good}/❌{bad} |")
    lines.append("")

    # 5) v3 10슬롯 문법 준수도
    lines.append("## 4. v3 10슬롯 문법 준수도 (휴리스틱 탐지)")
    lines.append("")
    SLOTS = {
        "genre": r"^[A-Z][\w\-/&\s]+?[,.]",
        "tempo_key_time": r"bpm.*?(4/4|3/4|6/8)|(4/4|3/4|6/8).*?key of|key of.*?bpm",
        "vocal_main": r"vocal.*?(delivery|tone|range)",
        "vocal_chorus": r"(backing|doubled|stacked|layered).*?harmon|harmon.*?(chorus|backing)",
        "instrument": r"\b(plays|sustains|strums|layers|follows|provides|rises|walks|punches|enters|plucks|alternates)\b",
        "drums": r"\bkick\b.*\bsnare\b|\bhi-hat\b",
        "arrangement": r"arrangement|builds gradually|full band|sparse|minimalist",
        "mixing": r"vocals?\s+(sit|placed|centered|forward|wide|close|upfront)",
        "effect_electronic": r"reverb|delay|chorus effect|compression|phaser|distortion|saturation",
        "effect_sound": r"(crowd|rain|field recording|noise|silence|vinyl|texture|footsteps|breaths|airplane|drone|chatter|murmur|ambient hum)",
    }
    lines.append("| gid | " + " | ".join(SLOTS.keys()) + " | 합계 |")
    lines.append("|---:" + "|---" * len(SLOTS) + "|---:|")
    for s in songs:
        row = [str(s["gid"])]
        cnt = 0
        low = s["sp"].lower()
        for slot, pat in SLOTS.items():
            hit = bool(re.search(pat, low, re.M))
            row.append("✓" if hit else "·")
            if hit: cnt += 1
        row.append(str(cnt))
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
