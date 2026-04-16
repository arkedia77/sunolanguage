#!/usr/bin/env python3
"""Manual A (SP 산문 어휘) / Manual B (가사 브래킷) 샘플 엔트리 생성.
책 품질: 각 엔트리에 song_id + UUID + 실제 인용문 3건 포함."""
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

DIR = Path("/Users/leo/sunolanguage/data/reanalysis_v2")
merged = json.loads((DIR / "merged_4values.json").read_text())
OUT_A = Path("/Users/leo/sunolanguage/docs/manual_A_sp_sample.md")
OUT_B = Path("/Users/leo/sunolanguage/docs/manual_B_lyrics_sample.md")

# 인덱싱: term/bracket -> 인용 목록
def find_quotes_sp(term: str, max_q=3):
    regex = re.compile(r"[^.!?]*\b" + re.escape(term) + r"\b[^.!?]*[.!?]", re.IGNORECASE)
    quotes = []
    seen_songs = set()
    for s in merged:
        if len(quotes) >= max_q: break
        if s["song_id"] in seen_songs: continue
        for sr in s.get("suno_reanalysis", []):
            sp = sr.get("sp") or ""
            m = regex.search(sp)
            if m:
                quotes.append({"song_id": s["song_id"], "title": s["title"],
                               "genre": s.get("genre"), "uuid": sr.get("uuid"),
                               "quote": m.group().strip()})
                seen_songs.add(s["song_id"])
                break
    return quotes

def count_sp(term: str):
    regex = re.compile(r"\b" + re.escape(term) + r"\b", re.IGNORECASE)
    cnt = 0
    genres = Counter()
    for s in merged:
        g = s.get("genre") or "미정"
        for sr in s.get("suno_reanalysis", []):
            sp = sr.get("sp") or ""
            hits = len(regex.findall(sp))
            cnt += hits
            if hits:
                genres[g] += hits
    return cnt, genres

def count_in_leomusic_sp(term: str):
    regex = re.compile(r"\b" + re.escape(term) + r"\b", re.IGNORECASE)
    cnt = 0
    for s in merged:
        sp = (s["leomusic_original"].get("sp") or "")
        cnt += len(regex.findall(sp))
    return cnt

def variants(seed_root: str, candidates: list[str]):
    present = {}
    for v in candidates:
        c, _ = count_sp(v)
        if c:
            present[v] = c
    return present

# ========== Manual A — SP 샘플 엔트리 15개 ==========
SP_ENTRIES = [
    # 악기 카테고리
    {"term": "clean electric guitar", "cat": "악기/Instrument",
     "def": "왜곡 없이 맑은 음색의 일렉트릭 기타. Suno가 연주 묘사 시 가장 자주 사용하는 기타 디스크립터로, 주로 아르페지오·코드 연주와 함께 등장.",
     "variants": ["clean electric guitar","a clean electric guitar","clean guitar"]},
    {"term": "sub-bass synth", "cat": "악기/Instrument",
     "def": "20~60Hz 대역을 담당하는 저음 전용 신스. Suno는 'provides low-end weight', 'holds the foundation' 같은 기능 기술과 함께 사용.",
     "variants": ["sub-bass synth","a sub-bass synth","sub bass synth"]},
    {"term": "fingerpicked acoustic guitar", "cat": "악기/Instrument",
     "def": "손가락으로 현을 튕기는 어쿠스틱 기타 연주. Suno는 이 표현을 intimate/folk/ballad 계열에서 일관되게 사용, 악기+주법을 한 토큰으로 결합.",
     "variants": ["fingerpicked acoustic guitar","a fingerpicked acoustic guitar"]},
    # 주법
    {"term": "arpeggiated", "cat": "주법/Playing technique",
     "def": "코드를 동시에 울리지 않고 음을 하나씩 순차로 퍼뜨리는 연주. 기타/신스/피아노에 모두 적용. 'a repetitive arpeggiated pattern' 형태 자주 출현.",
     "variants": ["arpeggiated","arpeggio","arpeggiates"]},
    {"term": "syncopated", "cat": "주법/Playing technique",
     "def": "강박 대신 약박을 강조하여 리듬을 당김. Suno의 주법 어휘 중 최상위 빈도. 드럼/베이스/기타 모두에서 사용.",
     "variants": ["syncopated","syncopation"]},
    # 프로덕션
    {"term": "plate reverb", "cat": "프로덕션/Production",
     "def": "금속판 진동을 이용한 리버브. Suno는 보컬 처리 기술어로 반복 사용 — 특히 'moderate plate reverb', 'plate reverb on the vocals' 구문으로 정형화됨.",
     "variants": ["plate reverb","moderate plate reverb"]},
    {"term": "sidechain compression", "cat": "프로덕션/Production",
     "def": "외부 신호(보통 킥드럼) 레벨에 반응해 다른 트랙 볼륨을 자동 감쇠시키는 기법. Suno는 'sidechain compression from the kick' 형태로 사용.",
     "variants": ["sidechain compression","side-chain compression","sidechained"]},
    # 보컬
    {"term": "breathy female vocals", "cat": "보컬/Vocal",
     "def": "숨소리 결이 섞인 여성 보컬. Suno는 이 표현을 Pop/R&B/Indie의 intimate 계열에서 안정적으로 사용, 'intimate'·'centered in the mix' 등과 공기(共起).",
     "variants": ["breathy female vocals","breathy intimate female vocals","soft breathy female vocal"]},
    {"term": "baritone male vocal", "cat": "보컬/Vocal",
     "def": "중저음역 남성 보컬. Suno는 'baritone male vocal'을 팝·R&B·발라드에서 고정 어휘로 사용 (단수/복수 혼용).",
     "variants": ["baritone male vocal","baritone male vocals","a baritone male vocal"]},
    # 무드/음색
    {"term": "intimate", "cat": "무드/Mood",
     "def": "작은 공간/가까운 거리에서 속삭이듯 전달되는 질감을 가리키는 Suno의 핵심 무드 형용사. 보컬·편곡 양쪽에 동시 적용.",
     "variants": ["intimate","an intimate","intimate vocals"]},
    {"term": "crisp", "cat": "음색/Timbre",
     "def": "선명하고 에지가 살아있는 타격음·스네어·하이햇 묘사 시 Suno가 고정적으로 쓰는 형용사. 'crisp snare', 'crisp hi-hat' 형태.",
     "variants": ["crisp","crisp snare","crisp hi-hats"]},
    # 템포/키
    {"term": "72 BPM", "cat": "템포/Tempo",
     "def": "Suno 재분석에서 가장 자주 등장하는 BPM값. K-발라드·Indie Pop 샘플에서 집중 출현 — leomusic 생성곡 템포 분포 반영.",
     "variants": ["72 bpm","72bpm","at 72 bpm"]},
    {"term": "key of E Major", "cat": "조성/Key",
     "def": "Suno 재분석에서 최빈출 조성. 샘플 곡의 실제 key 분포를 반영하며 'The tempo is X BPM in the key of E Major' 구문에 고정 위치.",
     "variants": ["key of e major","in the key of e major"]},
    # 구조
    {"term": "4/4 time", "cat": "박자/Time signature",
     "def": "네박자. 원 기획 parsed schema에는 있었으나 v1 사전엔 빠져있던 필드. Suno SP에서 161회 출현, 전체 샘플 거의 전수가 4/4.",
     "variants": ["4/4 time","4/4"]},
    # 장르 자칭
    {"term": "K-Pop", "cat": "장르/Genre self-label",
     "def": "Suno가 첫 문장에서 장르 선언 시 가장 자주 내세우는 라벨. 'K-Pop ballad', 'K-Pop R&B ballad' 복합 형태로도 사용.",
     "variants": ["k-pop","k-pop ballad","k-pop r&b"]},
]

def render_sp_entry(e: dict) -> str:
    term = e["term"]
    cnt, genres = count_sp(term)
    leo_cnt = count_in_leomusic_sp(term)
    quotes = find_quotes_sp(term)
    var_counts = variants(term, e["variants"])
    lines = []
    lines.append(f"### {term}")
    lines.append(f"- **카테고리**: {e['cat']}")
    lines.append(f"- **정의**: {e['def']}")
    lines.append(f"- **Suno SP 출현**: {cnt}회 / **leomusic 원 SP 출현**: {leo_cnt}회")
    if genres:
        top_genres = ", ".join(f"{g}({c})" for g, c in genres.most_common(5))
        lines.append(f"- **장르 분포(상위5)**: {top_genres}")
    if var_counts:
        v_txt = " / ".join(f"`{k}`({v})" for k, v in sorted(var_counts.items(), key=lambda x: -x[1]))
        lines.append(f"- **변이형**: {v_txt}")
    diff = "Suno 고유 (leomusic 원 SP 미출현)" if leo_cnt == 0 and cnt > 0 else ("공통 어휘" if leo_cnt > 0 else "미검출")
    lines.append(f"- **leomusic↔Suno 관계**: {diff}")
    lines.append(f"- **검증 상태**: {'confirmed' if cnt >= 10 else ('plausible' if cnt >= 3 else 'single_occurrence')}")
    lines.append("- **인용문** (song_id · UUID · 장르):")
    for q in quotes:
        lines.append(f"  - #{q['song_id']:04d} *{q['title']}* · `{(q['uuid'] or '')[:8]}` · [{q['genre']}]")
        lines.append(f"    > {q['quote']}")
    return "\n".join(lines)

a_lines = [
    "# 매뉴얼 A — Suno가 SP에서 하는 것 (샘플 엔트리)",
    "",
    f"- 데이터 범위: 318곡 / 326 Suno 재분석 clips",
    "- 본 문서는 전체 매뉴얼의 **샘플 15 엔트리**. 전문가 3분 리뷰용 파일럿.",
    "- 각 엔트리는 정의·빈도·장르분포·변이형·leomusic 대응 관계·원문 인용 3건 포함",
    "",
    "## 엔트리 형식",
    "```",
    "### {term}",
    "- 카테고리",
    "- 정의",
    "- Suno SP 출현 / leomusic 원 SP 출현",
    "- 장르 분포(상위5)",
    "- 변이형",
    "- leomusic↔Suno 관계",
    "- 검증 상태 (confirmed ≥10 / plausible ≥3 / single_occurrence)",
    "- 인용문 3건 (song_id · UUID · 장르)",
    "```",
    "",
    "## 샘플 엔트리",
    "",
]
for e in SP_ENTRIES:
    a_lines.append(render_sp_entry(e))
    a_lines.append("")

OUT_A.write_text("\n".join(a_lines))
print(f"매뉴얼 A: {OUT_A} ({len(SP_ENTRIES)} entries)")

# ========== Manual B — 가사 브래킷 샘플 10 ==========
brackets = json.loads((DIR / "recon_lyrics_brackets.json").read_text())
bentries = brackets["entries"]

# normalized -> 여러 출현
by_norm = defaultdict(list)
for e in bentries:
    by_norm[e["norm"]].append(e)

def find_bracket_quotes(norm: str, max_q=3):
    occs = by_norm.get(norm, [])
    quotes = []
    seen_songs = set()
    for o in occs:
        if o["song_id"] in seen_songs: continue
        ctx = (o["before_ctx"] + f"[{o['raw']}]" + o["after_ctx"]).strip()
        quotes.append({"song_id": o["song_id"], "title": o["title"],
                       "uuid": o["uuid"], "context": ctx, "types": o["types"]})
        seen_songs.add(o["song_id"])
        if len(quotes) >= max_q: break
    return quotes

# 타입별 대표 브래킷 선정
TYPE_DEFS = {
    "section": "곡 구조 구분 태그 (Intro/Verse/Chorus/Bridge 등). Suno 재분석 가사에서 가장 안정된 브래킷 체계.",
    "vocal_direction": "보컬 퍼포먼스 지시 (톤/발성/숨결/강도). 구간 시작 부분 또는 특정 라인 위치에 삽입.",
    "instrument_or_arrangement": "악기 진입/레이어/어레인지먼트 큐. 'X enters', 'X comes in', 'layered with Y' 형태 다수.",
    "transition_cue": "구간 전환 큐 (enter/drop/fade/build/swell). 레이어 추가·제거 타이밍 명시.",
    "effect": "이펙트/프로세싱 큐 (reverb/delay/filter sweep 등). 순간적 처리 강조 용도.",
}

B_ENTRIES = [
    {"norm": "intro", "type": "section"},
    {"norm": "verse 1", "type": "section"},
    {"norm": "chorus", "type": "section"},
    {"norm": "pre-chorus", "type": "section"},
    {"norm": "bridge", "type": "section"},
    {"norm": "breathy female vocals", "type": "vocal_direction"},
    {"norm": "kick drum enters", "type": "instrument_or_arrangement"},
    {"norm": "arpeggiated clean electric guitar with chorus", "type": "instrument_or_arrangement"},
    {"norm": "plate reverb", "type": "effect"},
    {"norm": "drum kit enters", "type": "instrument_or_arrangement"},
]

def render_b_entry(e: dict) -> str:
    norm = e["norm"]
    t = e["type"]
    occs = by_norm.get(norm, [])
    total = len(occs)
    genres = Counter()
    for o in occs:
        sid = o["song_id"]
        song = next((s for s in merged if s["song_id"] == sid), None)
        if song:
            genres[song.get("genre") or "미정"] += 1
    q = find_bracket_quotes(norm)
    lines = []
    lines.append(f"### [{norm}]")
    lines.append(f"- **타입**: {t} — {TYPE_DEFS[t]}")
    lines.append(f"- **총 출현**: {total}회 (고유 {total and len(set(o['song_id'] for o in occs))}곡)")
    if genres:
        top = ", ".join(f"{g}({c})" for g, c in genres.most_common(5))
        lines.append(f"- **장르 분포(상위5)**: {top}")
    lines.append(f"- **검증 상태**: {'confirmed' if total >= 10 else ('plausible' if total >= 3 else 'single_occurrence')}")
    lines.append("- **인용 문맥** (앞뒤 40자 포함):")
    for qq in q:
        lines.append(f"  - #{qq['song_id']:04d} *{qq['title']}* · `{(qq['uuid'] or '')[:8]}`")
        ctx = qq["context"].replace("\n", " ↵ ")[:180]
        lines.append(f"    > ...{ctx}...")
    return "\n".join(lines)

b_lines = [
    "# 매뉴얼 B — Suno가 가사에서 하는 것 (샘플 엔트리)",
    "",
    "- 데이터 범위: 318곡 / 326 Suno 재분석 clips / **2,282개 가사 브래킷**",
    "- Suno는 가사 내부 `[...]` 브래킷으로 **구간별 연출 지시**를 남김 — SP 산문과 별개의 언어 시스템",
    "- 본 문서는 전체 매뉴얼의 **샘플 10 엔트리** + 자동 1차 타입 분류",
    "",
    "## 추정 타입 체계 (1차 초안)",
    "",
    "| 타입 | 정의 |",
    "|------|------|",
]
for t, d in TYPE_DEFS.items():
    b_lines.append(f"| {t} | {d} |")

b_lines += ["", "## 타입별 출현/고유 분포 (자동 분류)", "",
            "| 타입 | 출현 | 고유 | 비고 |", "|----|---:|---:|----|"]
for t, d in brackets["by_type_guess_counts"].items():
    note = {"section":"가장 안정", "instrument_or_arrangement":"가장 다양 (600 고유)",
            "transition_cue":"순간 큐 위주", "vocal_direction":"",
            "effect":"", "uncategorized":"타입 규칙 보완 필요"}.get(t,"")
    b_lines.append(f"| {t} | {sum(d.values())} | {len(d)} | {note} |")

b_lines += ["", "## 샘플 엔트리", ""]
for e in B_ENTRIES:
    b_lines.append(render_b_entry(e))
    b_lines.append("")

OUT_B.write_text("\n".join(b_lines))
print(f"매뉴얼 B: {OUT_B} ({len(B_ENTRIES)} entries)")
