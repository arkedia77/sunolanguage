#!/usr/bin/env python3
"""326 clips 전수 정찰: SP 산문 + 가사 브래킷 raw 수집·분류.
출력:
  - recon_sp_sentences.json : Suno SP 문장 단위 raw 덤프
  - recon_sp_templates.json : Suno SP에 반복되는 구문 패턴 top N
  - recon_lyrics_brackets.json : 가사 내 모든 브래킷 내용 분류 초안
  - recon_summary.md : 수치 요약
"""
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

MERGED = Path("/Users/leo/sunolanguage/data/reanalysis_v2/merged_4values.json")
OUT_DIR = Path("/Users/leo/sunolanguage/data/reanalysis_v2")
merged = json.loads(MERGED.read_text())

# ---------- SP 정찰 ----------
sp_sentences = []  # {song_id, uuid, sentence}
sp_sentence_patterns = Counter()  # lemmatized template
sp_vocabulary_raw = Counter()  # every 1-3gram (alphabetic)
sp_opening_sentences = Counter()  # 첫 문장 장르 시그니처

# ---------- Lyrics brackets 정찰 ----------
bracket_entries = []  # {song_id, uuid, bracket_raw, bracket_norm, position, neighbor_text}
bracket_freq = Counter()
bracket_by_type_guess = defaultdict(Counter)  # 자동 타입 추측

# 브래킷 타입 추측 규칙 (책 매뉴얼 B용 초안)
SECTION_TAGS = {"intro","verse","pre-chorus","chorus","bridge","outro","hook","drop","breakdown","interlude","instrumental","refrain","coda","fade-out","fadeout","ending"}
VOCAL_DIR_WORDS = {"vocal","vocals","voice","sing","singing","whisper","whispered","breathy","harmoniz","ad-lib","adlib","falsetto","shout","shouted","rap","rapped","spoken"}
INSTRUMENT_WORDS = {"guitar","bass","drum","drums","synth","piano","keys","pad","pads","organ","rhodes","strings","violin","cello","flute","clarinet","harp","trumpet","sax","808","clap","claps","hat","hats","hi-hat","hi-hats","kick","snare","shaker","tambourine","chime","chimes","bell","bells","gong","orchestra","choir","saxophone"}
EFFECT_WORDS = {"reverb","delay","filter","compress","compression","distortion","saturat","tape","vinyl","chorus","flanger","phaser","autotune","auto-tune","vocoder","sidechain","side-chain","duck","ducking","eq","pan","panning","stereo","low-pass","high-pass","bit-crush","bitcrush","lo-fi","fade","swell","sweep"}
TRANSITION_WORDS = {"enter","enters","drop","drops","drop out","drops out","fade","fades","build","builds","swell","swells","cut","cuts","break","return","returns","pause","pauses"}

def guess_bracket_type(b_norm: str) -> list[str]:
    bl = b_norm.lower()
    types = []
    first_word = bl.split()[0] if bl else ""
    # 섹션 태그
    if any(s in bl for s in SECTION_TAGS) or re.match(r"^(verse|chorus)\s*\d*$", bl) or re.match(r"^pre-?chorus\s*\d*$", bl):
        types.append("section")
    # 보컬 디렉션
    if any(w in bl for w in VOCAL_DIR_WORDS):
        types.append("vocal_direction")
    # 악기/어레인지먼트
    if any(w in bl for w in INSTRUMENT_WORDS):
        types.append("instrument_or_arrangement")
    # 이펙트
    if any(w in bl for w in EFFECT_WORDS):
        types.append("effect")
    # 진입/퇴장 전이 큐
    if any(w in bl for w in TRANSITION_WORDS):
        types.append("transition_cue")
    if not types:
        types.append("uncategorized")
    return types

# SP 문장 분해 — prose sentences by period
def split_sentences(txt: str):
    if not txt:
        return []
    t = re.sub(r"\s+", " ", txt.strip())
    # naive period split; acceptable for prose SP
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", t) if s.strip()]

def normalize_bracket(raw: str) -> str:
    return re.sub(r"\s+", " ", raw.strip()).lower()

BRACKET_RE = re.compile(r"\[([^\[\]]{1,200})\]")

for song in merged:
    sid = song["song_id"]
    title = song.get("title")
    for sr in song.get("suno_reanalysis", []):
        uuid = sr.get("uuid")
        sp = sr.get("sp") or ""
        lyr = sr.get("lyrics") or ""
        # SP
        sents = split_sentences(sp)
        for idx, s in enumerate(sents):
            sp_sentences.append({"song_id": sid, "title": title, "uuid": uuid,
                                 "idx": idx, "sentence": s})
            if idx == 0:
                sp_opening_sentences[s[:120]] += 1
            # 구문 패턴: 단어 종류 치환으로 템플릿화 (간단형)
            tpl = re.sub(r"\b\d+\.?\d*\s*bpm\b", "<BPM>", s.lower())
            tpl = re.sub(r"\b(in\s+the\s+key\s+of\s+)[a-g][#b]?\s*(major|minor)\b", r"\1<KEY>", tpl)
            tpl = re.sub(r"\b[a-g][#b]?\s+(major|minor)\b", r"<KEY> \1", tpl)
            tpl = re.sub(r"\b\d+\b", "<NUM>", tpl)
            sp_sentence_patterns[tpl[:160]] += 1
        # 어휘 1-3gram (알파 2자 이상)
        toks = re.findall(r"[a-zA-Z][a-zA-Z\-']+", sp.lower())
        for w in toks:
            if len(w) > 2:
                sp_vocabulary_raw[w] += 1
        for i in range(len(toks) - 1):
            sp_vocabulary_raw[f"{toks[i]} {toks[i+1]}"] += 1
        for i in range(len(toks) - 2):
            sp_vocabulary_raw[f"{toks[i]} {toks[i+1]} {toks[i+2]}"] += 1
        # 가사 브래킷
        for m in BRACKET_RE.finditer(lyr):
            raw = m.group(1)
            norm = normalize_bracket(raw)
            if not norm:
                continue
            types = guess_bracket_type(norm)
            before = lyr[max(0, m.start()-40):m.start()]
            after = lyr[m.end():m.end()+40]
            bracket_entries.append({
                "song_id": sid, "title": title, "uuid": uuid,
                "raw": raw, "norm": norm, "types": types,
                "before_ctx": before.replace("\n"," "),
                "after_ctx": after.replace("\n"," "),
            })
            bracket_freq[norm] += 1
            for t in types:
                bracket_by_type_guess[t][norm] += 1

# dump
(OUT_DIR / "recon_sp_sentences.json").write_text(
    json.dumps(sp_sentences, ensure_ascii=False, indent=2))
(OUT_DIR / "recon_sp_templates.json").write_text(
    json.dumps(dict(sp_sentence_patterns.most_common(300)),
               ensure_ascii=False, indent=2))
(OUT_DIR / "recon_sp_ngrams.json").write_text(
    json.dumps(dict(sp_vocabulary_raw.most_common(1500)),
               ensure_ascii=False, indent=2))
(OUT_DIR / "recon_sp_openings.json").write_text(
    json.dumps(dict(sp_opening_sentences.most_common(100)),
               ensure_ascii=False, indent=2))
(OUT_DIR / "recon_lyrics_brackets.json").write_text(
    json.dumps({
        "entries_total": len(bracket_entries),
        "entries": bracket_entries,
        "top_frequencies": dict(bracket_freq.most_common(200)),
        "by_type_guess_counts": {k: dict(v.most_common())
                                 for k, v in bracket_by_type_guess.items()},
    }, ensure_ascii=False, indent=2))

# summary
total_clips = sum(len(s["suno_reanalysis"]) for s in merged)
lines = [
    "# 326 clips 정찰 요약",
    "",
    f"- 곡(유니크 song_id): {len(merged)}",
    f"- clips(Suno 재분석 샘플): {total_clips}",
    f"- SP 문장 수: {len(sp_sentences)}",
    f"- SP 고유 1-3gram (2자+ 알파): {len(sp_vocabulary_raw)}",
    f"- SP 템플릿(치환후): 고유 {len(sp_sentence_patterns)}",
    f"- 가사 브래킷 총 출현: {len(bracket_entries)}",
    f"- 가사 브래킷 고유 normalized: {len(bracket_freq)}",
    "",
    "## 가사 브래킷 자동 분류 추정 분포",
]
for t, c in sorted(bracket_by_type_guess.items(), key=lambda x: -sum(x[1].values())):
    lines.append(f"- **{t}**: 출현 {sum(c.values())} / 고유 {len(c)}")
lines.append("")
lines.append("## SP 템플릿 상위 10 (치환 정규화)")
for p, c in sp_sentence_patterns.most_common(10):
    lines.append(f"- ({c}) {p}")
(OUT_DIR / "recon_summary.md").write_text("\n".join(lines))
print("\n".join(lines))
