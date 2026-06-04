#!/usr/bin/env python3
"""전체 맵 + 매뉴얼 A/B 샘플 엔트리 생성."""
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

DIR = Path(__file__).resolve().parent.parent / "data/reanalysis_v2"
merged = json.loads((DIR / "merged_4values.json").read_text())
brackets = json.loads((DIR / "recon_lyrics_brackets.json").read_text())
OUT_MAP = Path(__file__).resolve().parent.parent / "docs/coverage_map.md"
OUT_A = Path(__file__).resolve().parent.parent / "docs/manual_A_sp_sample.md"
OUT_B = Path(__file__).resolve().parent.parent / "docs/manual_B_lyrics_sample.md"
OUT_MAP.parent.mkdir(exist_ok=True)

# ---------- 장르 정규화 ----------
def norm_genre(g: str | None) -> str:
    if not g:
        return "미정"
    g0 = g.split("/")[0].strip()
    # 공통 패밀리로 묶기
    pop = {"Indie Pop","City Pop","Synth Pop","Lo-fi Pop","Electro Pop","Dream Pop",
           "Acoustic Pop","Funk Pop","Disco Pop","Electropop","Alt-Pop","Bedroom Pop",
           "Pop","Dance Pop","K-Pop","K-POP","Art Pop","Pop Soul","Pop-Ballad",
           "Soft Indie","Soft Pop","Britpop","Baroque Pop","Chamber Pop","Chillwave",
           "Indie Synth Pop","Hyperpop","Indie R&B","Indie Folk","Indie Acoustic",
           "Electro-Pop","Electronic Pop","Ambient Folk Pop","Ambient Indie",
           "Indie Electronic","Synth-Driven Indie Electronic","Indie Pop Ballad",
           "Pluggnb","Emo Pop","Pop Punk","Punk Pop"}
    rnb = {"R&B","Soft R&B","Neo-Soul","Alt R&B","R&B Soul","Indie Soul","Soul Ballad",
           "K-R&B","Contemporary R&B","Lo-fi R&B","R&B Pop","Alternative R&B"}
    hh = {"Hip-Hop","K-Hip-Hop","Electro Hip-Hop"}
    rock = {"Indie Rock","Rock","Pop Rock","Alternative Rock","Shoegaze","Hard Rock",
            "Blues Rock","Folk Rock","Post-Punk","Synth-Punk","Garage Rock","Surf Rock",
            "Alternative","Alternative / Art Rock","Industrial","Minimal Techno"}
    electronic = {"Electronic","EDM","Ambient","Ambient Electronic","Ambient Piano",
                  "Ambient Ballad","Minimal Electronic Ambient","Ambient Neoclassical",
                  "Ethereal Ambient","Electronic Funk","Ambient / Post-Classical"}
    folk = {"Folk","Acoustic Folk","Narrative Folk","Acoustic Ballad","Piano Ballad",
            "Acoustic Indie","Acoustic Waltz","Indie Acoustic Ballad",
            "Lo-fi Acoustic Folk"}
    ballad = {"Korean Ballad","Ballad","Adult Contemporary","Modern Ballad Indie",
              "K-Pop Ballad","Orchestral Ballad"}
    jazz = {"Jazz Pop","Jazz","Soft Jazz","Jazz Ballad"}
    orch = {"Chamber Pop / Orchestral","Post-Rock / Cinematic","Post-Rock",
            "Neoclassical Cinematic"}
    if g0 in pop: return "Pop 계열"
    if g0 in rnb: return "R&B 계열"
    if g0 in hh: return "Hip-Hop 계열"
    if g0 in rock: return "Rock 계열"
    if g0 in electronic: return "Electronic/Ambient"
    if g0 in folk: return "Folk/Acoustic"
    if g0 in ballad: return "Ballad"
    if g0 in jazz: return "Jazz"
    if g0 in orch or "Cinematic" in g0 or "Orchestral" in g0: return "Orchestral/Cinematic"
    return "기타"

genre_group = defaultdict(list)
for s in merged:
    genre_group[norm_genre(s.get("genre"))].append(s)

# ---------- 카테고리 × 장르 매트릭스 ----------
KEYWORD_CATS = {
    "악기": [r"\b(guitar|guitars|bass|drums?|synth|synths|piano|keys|pads?|organ|rhodes|strings?|violin|cello|flute|clarinet|harp|trumpet|sax|saxophone|808s?|claps?|hats?|hi-hats?|kick|snare|shaker|tambourine|chimes?|bells?|gong|choir|orchestra)\b"],
    "주법/연주": [r"\b(arpeggiat\w+|fingerpick\w+|palm[- ]mut\w+|strumm\w+|syncopat\w+|swing|walking\s+(?:bass|pattern)|backbeat|sidechain|chugg\w+|tremolo)\b"],
    "프로덕션": [r"\b(reverb|delay|compress\w+|distort\w+|saturat\w+|vinyl\s+crackle|tape\s+hiss|side[- ]chain\w*|filter|low[- ]pass|high[- ]pass|bit[- ]crush\w*|autotune|vocoder|chorus|flanger|phaser|lo-?fi|wide\s+stereo)\b"],
    "무드/감정": [r"\b(warm|cold|bright|dark|intimate|raw|gentle|aggressive|sparse|dense|gritty|smooth|lush|dry|wet|haunting|dreamy|ethereal|airy|punchy|tight|loose|crisp|resonant|shimmering|driving|groovy|soulful|hypnotic|melancholic|nostalgic|tense|serene|playful)\b"],
    "템포/BPM": [r"\b\d{2,3}\s*bpm\b"],
    "조성/Key": [r"\bkey\s+of\s+[A-G][#b]?\s*(?:major|minor)\b", r"\b[A-G][#b]?\s+(?:major|minor)\b"],
    "보컬": [r"\b(male\s+vocals?|female\s+vocals?|baritone|tenor|soprano|alto|breathy|whispered|falsetto|rapped|shouted|spoken|ad-libs?|harmoniz\w+)\b"],
    "음색/텍스처": [r"\b(distort\w+|clean|resonant|crisp|metallic|warm|overdriven|gritty|bright|muffled|shimmering|hollow|muted)\b"],
    "하모니/화성": [r"\b(major|minor|seventh|ninth|diminished|augmented|suspended|pentatonic|blues\s+scale|modal|chromatic|key\s+change|modulation)\b"],
    "구조/다이내믹스": [r"\b(intro|verse|chorus|bridge|outro|breakdown|drop|build\s*up|crescendo|decrescendo|swell\w*|fade[- ]?in|fade[- ]?out|drone|ostinato|drop-?out)\b"],
    "시간서명": [r"\b\d+\s*/\s*\d+\s+time\b"],
    "장르 자칭": [r"\b(k[- ]?pop|j[- ]?pop|r\s*&?\s*b|hip[- ]hop|rock|jazz|folk|cinematic|orchestral|ambient|electronic)\b"],
}

# 카테고리별 hits / 고유
cat_stats_global = {}
for cat, pats in KEYWORD_CATS.items():
    regex = re.compile("|".join(pats), re.IGNORECASE)
    hits = 0
    uniq = Counter()
    for s in merged:
        for sr in s.get("suno_reanalysis", []):
            sp = sr.get("sp") or ""
            for m in regex.finditer(sp):
                hits += 1
                uniq[m.group(0).lower()] += 1
    cat_stats_global[cat] = {"hits": hits, "unique": len(uniq), "top": uniq.most_common(10)}

# 장르 그룹 × 카테고리 hits
cat_by_genre = defaultdict(lambda: defaultdict(int))
for gname, songs in genre_group.items():
    for cat, pats in KEYWORD_CATS.items():
        regex = re.compile("|".join(pats), re.IGNORECASE)
        for s in songs:
            for sr in s.get("suno_reanalysis", []):
                sp = sr.get("sp") or ""
                cat_by_genre[gname][cat] += len(regex.findall(sp))

# ---------- 맵 MD 생성 ----------
lines = [
    "# Suno 네이티브 어휘 — 전체 맵 (v2 초안)",
    "",
    f"- 곡(유니크 song_id): **{len(merged)}**",
    f"- Suno 재분석 clips: **{sum(len(s['suno_reanalysis']) for s in merged)}**",
    "- 출처: leomusic 생성곡 1분 컷 → Suno 앱 재업로드 → 자체 분석 SP+가사 수집",
    "",
    "## 1. 장르 그룹 × 곡수",
    "",
    "| 그룹 | 곡수 |",
    "|------|-----:|",
]
for g, items in sorted(genre_group.items(), key=lambda x: -len(x[1])):
    lines.append(f"| {g} | {len(items)} |")

lines += ["","## 2. 카테고리 전역 포화도 (Suno SP 내)","",
          "| 카테고리 | 총 출현 | 고유 표현 | 상위 예시 |","|----|---:|---:|---|"]
for cat, st in cat_stats_global.items():
    top = ", ".join(f"{t}({c})" for t, c in st["top"][:5])
    lines.append(f"| {cat} | {st['hits']} | {st['unique']} | {top} |")

lines += ["","## 3. 장르 그룹 × 카테고리 히트 매트릭스","",
          "| 장르 그룹 | " + " | ".join(KEYWORD_CATS.keys()) + " |",
          "|----|" + "|".join(["---:"] * len(KEYWORD_CATS)) + "|"]
for g in sorted(genre_group.keys(), key=lambda x: -len(genre_group[x])):
    row = [g]
    for cat in KEYWORD_CATS.keys():
        row.append(str(cat_by_genre[g][cat]))
    lines.append("| " + " | ".join(row) + " |")

# 가사 브래킷 맵
lines += ["","## 4. 가사 브래킷 시스템 (총 출현 / 고유)","",
          "| 추정 타입 | 출현 | 고유 | 상위 예시 |","|----|---:|---:|---|"]
for t, d in brackets["by_type_guess_counts"].items():
    total = sum(d.values())
    top = ", ".join(f"[{k}]({v})" for k, v in list(d.items())[:5])
    lines.append(f"| {t} | {total} | {len(d)} | {top} |")

lines += ["","## 5. 구멍 리스트 (우선 검토)","",
          "**장르 그룹별 얇은 영역**: 본 맵 §3에서 값이 0~5인 셀 — 해당 장르·카테고리는 현재 데이터로 매뉴얼 엔트리 생성 시 근거 부족. 추가 업로드 타겟 후보.",
          "",
          "**주요 공백 관찰**:"]
for g in ["Orchestral/Cinematic", "Jazz", "Rock 계열", "Electronic/Ambient", "Folk/Acoustic", "Ballad"]:
    if g in cat_by_genre:
        thin = [c for c in KEYWORD_CATS if cat_by_genre[g][c] < 5]
        if thin:
            lines.append(f"- **{g}** ({len(genre_group.get(g,[]))}곡): 얇은 카테고리 → {', '.join(thin)}")

OUT_MAP.write_text("\n".join(lines))
print(f"맵 생성: {OUT_MAP}")
print("\n".join(lines[:60]))
