#!/usr/bin/env python3
"""
Suno SP + 가사 브래킷 슬롯 재분류 v2

슬롯 구조:
  1. 장르 선언
  2. 악기 레이어 (동적 — 곡에 등장하는 악기만큼 2-1, 2-2, ...)
  3. 드럼 (킥/스네어/하이햇/퍼커션 보조 + 필인/패턴)
  4. 보컬
     4-1. 메인보컬 (음역, 톤, 기법)
     4-2. 코러스/백킹 (더블링, 레이어드, 하모니, 애드립)
  5. 템포/조성/박자
  6. 믹싱 (마이킹, 스테레오, 패닝, 컴프레션, EQ)
  7. 전자 이펙터 (리버브, 딜레이, 코러스이펙트, 디스토션 등)
  8. 사운드 이펙트 (바이닐크랙클, 시계소리, 기계음 등)
  9. 편곡 총평 (원문 리스팅 + 악기값 복사)
 10. 없음 선언 (명시적 제외/퇴장)
"""
import json, re
from collections import Counter, defaultdict
from pathlib import Path

DATA = json.loads(Path("data/reanalysis_v2/merged_4values.json").read_text())

# ─────────────────────────────────────────────
# 악기 사전 (이름 → 정규식)
# synth bass ≠ bass guitar, synthesizer ≠ keyboard
# ─────────────────────────────────────────────
INSTRUMENTS = {
    "guitar": r"\bguitars?\b",
    "acoustic guitar": r"(?:fingerpicked |fingerstyle |strummed |nylon[- ]string |12-string )?acoustic guitar",
    "clean electric guitar": r"clean electric guitar",
    "electric guitar": r"(?:distorted |overdriven |palm-muted |arpeggiated )?electric guitar",
    "bass guitar": r"(?:electric |fingerstyle |fretless |clean electric )?bass(?:\s+guitar)?(?!\s*(?:synth|drum))",
    "slap bass": r"slap bass",
    "upright bass": r"upright bass",
    "synth bass": r"(?:synth[- ]?bass|bass synth|sub[- ]?bass(?:\s+synth)?)",
    "acoustic piano": r"(?:acoustic |grand )?piano",
    "electric piano": r"electric piano",
    "rhodes": r"rhodes",
    "organ": r"(?:electric |hammond |church )?organ",
    "keyboard": r"keyboard|keys(?!\s*of)",
    "synthesizer": r"(?:analog |digital |warm |bright |lush )?synth(?:esizer)?(?!\s*bass)",
    "pad": r"(?:synth |ambient |warm |lush |string )?pads?",
    "strings": r"(?:orchestral )?strings",
    "violin": r"violin",
    "cello": r"cello",
    "harp": r"harp",
    "flute": r"flute",
    "trumpet": r"(?:muted )?trumpet",
    "saxophone": r"(?:alto |tenor |soprano )?saxophone|sax\b",
    "trombone": r"trombone",
    "clarinet": r"clarinet",
    "brass": r"brass(?:\s+(?:section|stabs?|accents?|hits?))?",
    "harmonica": r"harmonica",
    "accordion": r"accordion",
    "ukulele": r"ukulele",
    "mandolin": r"mandolin",
    "banjo": r"banjo",
    "vibraphone": r"vibraphone",
    "glockenspiel": r"glockenspiel",
    "808": r"808",
}

DRUM_PARTS = re.compile(
    r"\b(drums?|kick(?:\s+drum)?|snare(?:\s+drum)?|hi-hat|hi-hats|cymbals?|"
    r"toms?|rimshot|cross-?stick|ghost\s+notes?|fills?|drum\s+fills?|"
    r"backbeat|drum\s+machine|drum\s+kit|drum\s+pattern|four-on-the-floor|"
    r"boom[- ]?bap|trap[- ]?beat|percussion|shaker|tambourine|cowbell|"
    r"woodblock|claps?|handclap|finger\s*snap|congas?|bongos?|maracas?|"
    r"cabasa|guiro|cajon|timbales?|ride\s+cymbal|crash\s+cymbal|shakers?|"
    r"open\s+hi-hat|closed\s+hi-hat|brushe?d?\s+snare|"
    r"beat(?:\s+pattern)?|groove)\b", re.I)

VOCAL_MAIN_RE = re.compile(
    r"\b(vocal|vocals|voice|singer|singing|"
    r"baritone|tenor|soprano|alto|falsetto|"
    r"rap\b|rapping|rapper|spoken[- ]word|vocaliz\w+|"
    r"breathy|raspy|husky|nasal|airy|smoky|gritty|"
    r"chest\s+voice|head\s+voice|mixed\s+voice|"
    r"belting|belt\b|crooning|melisma\w*|vibrato|"
    r"syncopat\w+|laid[- ]?back|staccato|legato|"
    r"conversational|intimate|storytelling|"
    r"melodic\s+(?:singing|delivery|vocal)|"
    r"rhythmic\s+(?:singing|delivery|vocal|rap))\b", re.I)

VOCAL_CHORUS_RE = re.compile(
    r"\b(doubling|doubled|double[- ]?track\w*|"
    r"layered\s+vocal|vocal\s+layer|vocal\s+stack|"
    r"backing\s+vocal|background\s+vocal|"
    r"vocal\s+harmon\w+|harmonies|"
    r"choir|choral|unison|call[- ]and[- ]response|"
    r"ad[- ]?libs?|adlib)\b", re.I)

TEMPO_RE = re.compile(
    r"\b(tempo\b|bpm|\d+\s*bpm|key of|key is|key:|key\s*[A-G]|"
    r"key:\s*[A-G]|"
    r"time signature|\d+/\d+\s*time|in\s+\d+/\d+)\b", re.I)

MIXING_RE = re.compile(
    r"\b(close-mic\w*|mic\s+position\w*|stereo\s+imag\w*|"
    r"panning|panned|compression|compressor|"
    r"EQ\b|equali[sz]\w+|sidechain|"
    r"forward\s+in\s+the\s+mix|centered\s+in\s+the\s+mix|"
    r"sits?\s+forward|sits?\s+back\b|"
    r"in\s+the\s+mix|"
    r"high-?fidelity|lo-?fi\s+production|"
    r"analog\s+warmth|tape\s+saturation|"
    r"clean\s+production|polished\s+production|"
    r"processed|processing|"
    r"stereo\s+width|mono\b|"
    r"gain\s+stag\w*|headroom)\b", re.I)

EFFECT_ELECTRONIC_RE = re.compile(
    r"\b(reverb|delay|echo|chorus\s+effect|chorus\s+pedal|"
    r"light\s+chorus|with\s+chorus|and\s+chorus|subtle\s+chorus|"
    r"distort\w+|overdrive|overdriven|fuzz|"
    r"phaser|flanger|wah|tremolo\s+(?:effect|pedal)|"
    r"filter\s+sweep|high-?pass\s+filter|low-?pass\s+filter|"
    r"pitch\s+correction|auto[- ]?tune|"
    r"plate\s+reverb|room\s+reverb|hall\s+reverb|spring\s+reverb|"
    r"short\s+reverb|long\s+reverb|"
    r"slap-?back\s+delay|ping-?pong\s+delay|"
    r"feedback\s+(?:loop|swell))\b", re.I)

SOUND_EFFECT_RE = re.compile(
    r"\b(vinyl\s+crackle|record\s+scratch|static|noise\s+layer|"
    r"clock[- ]?tick\w*|machine\s+sound|mechanical|"
    r"ambient\s+(?:noise|sound|texture)|"
    r"sound\s+effect|wind|rain|thunder|"
    r"swoosh|riser|sweep|shutter|"
    r"tape\s+hiss|white\s+noise|"
    r"foley|water\s+drop\w*|dripping|hum\b|muffled)\b", re.I)

ARRANGEMENT_RE = re.compile(
    r"\b(arrangement\b|focusing\s+on|interplay\b|"
    r"sparse\b|dense\b|minimalist\b|lush\b|intimate\b|"
    r"wall[- ]of[- ]sound|full\s+band|stripped[- ]?back|"
    r"builds?\s+(?:from|to|into|toward)|crescendo|"
    r"transitions?\s+(?:from|to|into))\b", re.I)

ABSENCE_RE = re.compile(
    r"\b(no\s+percussion|no\s+drums?|no\s+bass|"
    r"without\s+(?:percussion|drum|bass|additional)|"
    r"(?:is\s+)?absent|stripped|drops?\s+out|"
    r"cuts?\s+out|fades?\s+out|stops?\s+briefly|"
    r"solo\s+(?:male|female|vocal|piano|guitar|violin|cello))\b", re.I)

GENRE_RE = re.compile(
    r"^(k-pop|k-indie|k-hip\s*hop|k-ballad|k-rock|k-r&b|"
    r"korean|j-rock|j-pop|"
    r"pop|rock|jazz|r&b|hip[- ]?hop|electronic|ambient|folk|"
    r"indie|ballad|soul|funk|disco|synth|city\s*pop|bossa|"
    r"punk|metal|blues|country|reggae|lo-?fi|boom\s*bap|"
    r"cinematic|orchestral|dream\s*pop|shoegaze|chillwave|"
    r"future\s*bass|trap|EDM|house|techno|dnb|drill)", re.I)


def classify_sp_sentence(sent, idx, total):
    """SP 문장 → 복수 슬롯 반환 (중복 허용)."""
    sl = sent.lower()
    slots = []

    # 1. 장르 (첫 문장)
    if idx == 0 and GENRE_RE.search(sl):
        slots.append("genre")

    # 2. 악기 (동적) — 구체적 매칭 우선, guitar 포괄은 다른 guitar 없을 때만
    found_instruments = []
    for inst_name, pat in INSTRUMENTS.items():
        if re.search(pat, sl, re.I):
            found_instruments.append(inst_name)
    guitar_specifics = {"acoustic guitar", "clean electric guitar", "electric guitar"}
    if "guitar" in found_instruments and set(found_instruments) & guitar_specifics:
        found_instruments = [i for i in found_instruments if i != "guitar"]
    if found_instruments:
        slots.append(("instruments", found_instruments))

    # 3. 드럼
    if DRUM_PARTS.search(sl):
        slots.append("drums")

    # 4-1. 메인보컬
    if VOCAL_MAIN_RE.search(sl):
        slots.append("vocal_main")

    # 4-2. 코러스/백킹
    if VOCAL_CHORUS_RE.search(sl):
        slots.append("vocal_chorus")

    # 5. 템포/조성/박자
    if TEMPO_RE.search(sl):
        slots.append("tempo_key_time")

    # 6. 믹싱
    if MIXING_RE.search(sl):
        slots.append("mixing")

    # 7. 전자 이펙터
    if EFFECT_ELECTRONIC_RE.search(sl):
        slots.append("effect_electronic")

    # 8. 사운드 이펙트
    if SOUND_EFFECT_RE.search(sl):
        slots.append("effect_sound")

    # 9. 편곡 총평
    if ARRANGEMENT_RE.search(sl):
        slots.append("arrangement")

    # 10. 없음 선언
    if ABSENCE_RE.search(sl):
        slots.append("absence")

    if not slots:
        slots.append("unclassified")

    return slots, found_instruments


# ─────────────────────────────────────────────
# 가사 브래킷 분류
# ─────────────────────────────────────────────
SECTION_RE_B = re.compile(
    r"^(intro|verse|pre-?chorus|chorus|bridge|outro|hook|drop|"
    r"breakdown|interlude|instrumental|refrain|coda|end)(?:\s*\d*)?$", re.I)

SECTION_PARTIAL_RE = re.compile(
    r"\b(intro|verse|pre-?chorus|bridge|outro|hook|drop|"
    r"breakdown|interlude|instrumental)\b", re.I)

def classify_bracket(text):
    """가사 브래킷 → 복수 슬롯."""
    bt = text.strip()
    bl = bt.lower()
    slots = []

    # 섹션 태그 (정확 매칭 우선)
    if SECTION_RE_B.match(bl):
        return ["section"], bt

    # "Chorus" 단독이면 섹션이지 이펙터가 아님
    if bl in ("chorus", "pre-chorus"):
        return ["section"], bt

    # 악기 — 구체적 매칭 우선
    found_inst = []
    for inst_name, pat in INSTRUMENTS.items():
        if re.search(pat, bl, re.I):
            found_inst.append(inst_name)
    guitar_specifics = {"acoustic guitar", "clean electric guitar", "electric guitar"}
    if "guitar" in found_inst and set(found_inst) & guitar_specifics:
        found_inst = [i for i in found_inst if i != "guitar"]
    if found_inst:
        slots.append(("instruments", found_inst))

    # 드럼
    if DRUM_PARTS.search(bl):
        slots.append("drums")

    # 보컬 메인
    if VOCAL_MAIN_RE.search(bl):
        slots.append("vocal_main")

    # 보컬 코러스
    if VOCAL_CHORUS_RE.search(bl):
        slots.append("vocal_chorus")

    # 전자 이펙터
    if EFFECT_ELECTRONIC_RE.search(bl):
        slots.append("effect_electronic")

    # 사운드 이펙트
    if SOUND_EFFECT_RE.search(bl):
        slots.append("effect_sound")

    # 전환 큐
    if re.search(r"\b(enters?|drops?\s|fades?|builds?|swells?|cuts?|returns?|intensif|crescendo|strip|"
                  r"resumes?|continues?|opens?\s+up|increases?|rings?\s+out|counts?\s+in|stops?|"
                  r"slide\b|flourish|scratche?s?)", bl):
        slots.append("transition")

    # 없음/퇴장
    if ABSENCE_RE.search(bl):
        slots.append("absence")

    # 편곡
    if re.search(r"(full\s+band|full\s+arrangement|full\s+electronic|half-time|arrangement)", bl):
        slots.append("arrangement")

    # 섹션 부분 매칭 (다른 것과 결합)
    if SECTION_PARTIAL_RE.search(bl) and "section" not in slots:
        slots.append("section")

    # 발음 지시
    if re.search(r"[a-z]+-[a-z]+", bl) or "unintelligible" in bl:
        slots.append("pronunciation")

    if not slots:
        slots.append("unclassified")

    return slots, bt


# ─────────────────────────────────────────────
# 전체 재분류 실행
# ─────────────────────────────────────────────
sp_results = []  # (song_id, genre, sent_idx, sentence, slots, instruments)
bracket_results = []  # (song_id, genre, bracket_text, slots)

# 슬롯별 통계
sp_slot_counts = Counter()
sp_slot_examples = defaultdict(list)
bracket_slot_counts = Counter()
bracket_slot_examples = defaultdict(list)

# 악기별 빈도 + 수식어 수집
instrument_freq = Counter()
instrument_modifiers = defaultdict(Counter)  # inst → modifier phrases

# 코드/보이싱 표현 수집 (악기 슬롯 내 수식어)
chord_expressions = Counter()

for song in DATA:
    sid = song.get("song_id", 0)
    genre = song.get("genre", "")

    for sr in song.get("suno_reanalysis", []):
        sp = sr.get("sp", "")
        lyr = sr.get("lyrics", "")

        # SP 분류
        if sp:
            sents = [x.strip() for x in re.split(r"(?<=[.!?])\s+", sp.strip()) if x.strip()]
            for i, sent in enumerate(sents):
                slots, instruments = classify_sp_sentence(sent, i, len(sents))
                sp_results.append((sid, genre, i, sent, slots, instruments))

                for sl in slots:
                    slot_name = sl[0] if isinstance(sl, tuple) else sl
                    sp_slot_counts[slot_name] += 1
                    if len(sp_slot_examples[slot_name]) < 5:
                        sp_slot_examples[slot_name].append(sent[:120])

                for inst in instruments:
                    instrument_freq[inst] += 1

                # 코드/보이싱 추출
                for m in re.finditer(
                    r"(arpeggiated\s+chords?|sustained\s+chords?|power\s+chords?|"
                    r"jazz\s+chords?|block\s+chords?|open\s+chords?|"
                    r"chord\s+progressions?|jazz\s+voicings?|voicings?|"
                    r"harmonic\s+\w+|harmonies)", sent, re.I):
                    chord_expressions[m.group(0).lower().strip()] += 1

        # 가사 브래킷 분류
        if lyr:
            for m in re.finditer(r"\[([^\]]{1,200})\]", lyr):
                bt = m.group(1).strip()
                slots, _ = classify_bracket(bt)
                bracket_results.append((sid, genre, bt, slots))

                for sl in slots:
                    slot_name = sl[0] if isinstance(sl, tuple) else sl
                    bracket_slot_counts[slot_name] += 1
                    if len(bracket_slot_examples[slot_name]) < 5:
                        bracket_slot_examples[slot_name].append(bt[:100])


# ─────────────────────────────────────────────
# 출력: JSON + 요약 MD
# ─────────────────────────────────────────────
OUT_DIR = Path("data/reanalysis_v2")

# 1. SP 재분류 JSON
sp_json = []
for sid, genre, idx, sent, slots, instruments in sp_results:
    slot_names = []
    for sl in slots:
        if isinstance(sl, tuple):
            slot_names.append({"type": sl[0], "values": sl[1]})
        else:
            slot_names.append({"type": sl})
    sp_json.append({
        "song_id": sid, "genre": genre, "sent_idx": idx,
        "sentence": sent, "slots": slot_names, "instruments": instruments
    })
(OUT_DIR / "sp_slots_v2.json").write_text(json.dumps(sp_json, ensure_ascii=False, indent=2))

# 2. 브래킷 재분류 JSON
br_json = []
for sid, genre, bt, slots in bracket_results:
    slot_names = []
    for sl in slots:
        if isinstance(sl, tuple):
            slot_names.append({"type": sl[0], "values": sl[1]})
        else:
            slot_names.append({"type": sl})
    br_json.append({
        "song_id": sid, "genre": genre, "bracket": bt, "slots": slot_names
    })
(OUT_DIR / "bracket_slots_v2.json").write_text(json.dumps(br_json, ensure_ascii=False, indent=2))

# 3. 요약 MD
L = []
L.append("# Suno 슬롯 재분류 v2 — 결과 요약")
L.append("")
L.append(f"> 생성일: 2026-04-18 · SP {len(sp_results)}문장 · 브래킷 {len(bracket_results)}개")
L.append("")

L.append("## 슬롯 구조")
L.append("")
L.append("```")
L.append("1.  장르 선언           — 첫 문장, 100% 일관")
L.append("2.  악기 레이어 (동적)  — 곡에 등장하는 악기만큼 2-1, 2-2, ...")
L.append("3.  드럼                — 킥/스네어/하이햇/퍼커션 보조 + 필인/패턴")
L.append("4.  보컬")
L.append("    4-1. 메인보컬       — 음역, 톤, 기법 (syncopated, laid-back 등)")
L.append("    4-2. 코러스/백킹    — 더블링, 레이어드, 하모니, 애드립")
L.append("5.  템포/조성/박자      — BPM, key, time signature")
L.append("6.  믹싱                — 마이킹, 스테레오, 패닝, 컴프레션, EQ")
L.append("7.  전자 이펙터         — 리버브, 딜레이, 코러스이펙트, 디스토션 등")
L.append("8.  사운드 이펙트       — 바이닐크랙클, 기계음, 환경음 등")
L.append("9.  편곡 총평           — 원문 리스팅 (악기값은 슬롯2에 복사)")
L.append("10. 없음 선언           — 명시적 제외/퇴장 ('no percussion', 'drops out')")
L.append("```")
L.append("")
L.append("**원칙**: 하나의 표현이 복수 슬롯에 들어가는 것이 정상.")
L.append("규칙이 아니라 '가능성 높은 패턴'으로 기술.")
L.append("")

L.append("---")
L.append("")
L.append("## SP 슬롯별 분포")
L.append("")
L.append("| 슬롯 | 빈도 | 비율 |")
L.append("|------|------|------|")
total_sp = len(sp_results)
for slot, count in sp_slot_counts.most_common():
    pct = count / total_sp * 100
    L.append(f"| {slot} | {count} | {pct:.1f}% |")
L.append("")

L.append("### SP 슬롯별 예시")
L.append("")
for slot in ["genre", "instruments", "drums", "vocal_main", "vocal_chorus",
             "tempo_key_time", "mixing", "effect_electronic", "effect_sound",
             "arrangement", "absence", "unclassified"]:
    examples = sp_slot_examples.get(slot, [])
    if examples:
        L.append(f"**{slot}**:")
        for ex in examples:
            L.append(f"- `{ex}`")
        L.append("")

L.append("---")
L.append("")
L.append("## 악기 빈도 (SP)")
L.append("")
L.append("| # | 악기 | 빈도 |")
L.append("|---|------|------|")
for i, (inst, count) in enumerate(instrument_freq.most_common(), 1):
    L.append(f"| {i} | {inst} | {count} |")
L.append("")

L.append("---")
L.append("")
L.append("## 코드/보이싱 표현 (악기 슬롯 내 수식어)")
L.append("")
L.append("| 표현 | 빈도 |")
L.append("|------|------|")
for expr, count in chord_expressions.most_common():
    L.append(f"| {expr} | {count} |")
L.append("")
L.append("> 코드/보이싱은 독립 슬롯이 아닌 악기 레이어의 수식어로 등장.")
L.append("")

L.append("---")
L.append("")
L.append("## 가사 브래킷 슬롯별 분포")
L.append("")
L.append("| 슬롯 | 빈도 | 비율 |")
L.append("|------|------|------|")
total_br = len(bracket_results)
for slot, count in bracket_slot_counts.most_common():
    pct = count / total_br * 100
    L.append(f"| {slot} | {count} | {pct:.1f}% |")
L.append("")

L.append("### 브래킷 슬롯별 예시")
L.append("")
for slot in ["section", "instruments", "drums", "vocal_main", "vocal_chorus",
             "transition", "effect_electronic", "effect_sound", "arrangement",
             "absence", "pronunciation", "unclassified"]:
    examples = bracket_slot_examples.get(slot, [])
    if examples:
        L.append(f"**{slot}**:")
        for ex in examples:
            L.append(f"- `[{ex}]`")
        L.append("")

L.append("---")
L.append("")
L.append("## 가사 브래킷 실사용 가이드")
L.append("")
L.append("### 기본 문법: `[...]`")
L.append("")
L.append("Suno 가사에서 `[대괄호]`는 **비가사 지시문**을 의미합니다.")
L.append("가사가 아닌 모든 음악적 지시는 대괄호 안에 넣습니다.")
L.append("")
L.append("### 브래킷 용도별 패턴")
L.append("")
L.append("#### 1. 섹션 구분")
L.append("```")
L.append("[Intro]")
L.append("[Verse 1]")
L.append("[Pre-Chorus]")
L.append("[Chorus]")
L.append("[Bridge]")
L.append("[Outro]")
L.append("[Instrumental]")
L.append("[Breakdown]")
L.append("```")
L.append("- 대문자 시작이 관례")
L.append("- 단독 한 줄에 배치")
L.append("")
L.append("#### 2. 악기 큐 (진입/퇴장/변경)")
L.append("```")
L.append("[fingerpicked acoustic guitar]           ← 구간 시작 시 악기 지정")
L.append("[clean electric guitar enters]            ← 진입 타이밍")
L.append("[bass guitar enters with a slide]         ← 진입 + 주법")
L.append("[synth pads swell]                        ← 변화")
L.append("[guitar stops briefly]                    ← 일시 중단")
L.append("[piano melodic fill]                      ← 필인")
L.append("```")
L.append("")
L.append("#### 3. 드럼 큐")
L.append("```")
L.append("[kick drum enters]                        ← 킥 진입")
L.append("[shaker enters]                           ← 퍼커션 보조 진입")
L.append("[drum fill]                               ← 필인")
L.append("[drums fade out]                          ← 퇴장")
L.append("[soft kick drum, brushed snare]           ← 드럼 편성 지정")
L.append("```")
L.append("")
L.append("#### 4. 보컬 지시")
L.append("```")
L.append("[breathy female vocals]                   ← 메인보컬 톤+성별")
L.append("[male tenor vocals]                       ← 메인보컬 음역")
L.append("[male vocals enter]                       ← 보컬 진입")
L.append("[whispered vocals]                        ← 기법 전환")
L.append("[vocal harmony on '사랑']                 ← 코러스/하모니")
L.append("[layered vocals]                          ← 레이어드")
L.append("[ad-lib]                                  ← 애드립")
L.append("```")
L.append("")
L.append("#### 5. 이펙트/전환")
L.append("```")
L.append("[guitar feedback swell]                   ← 사운드 이펙트")
L.append("[vinyl crackle]                           ← 환경 이펙트")
L.append("[piano chords intensify]                  ← 다이내믹 전환")
L.append("[full band arrangement]                   ← 편곡 전환")
L.append("[instrumental fade out]                   ← 페이드 아웃")
L.append("```")
L.append("")
L.append("#### 6. 가사 중간 삽입")
L.append("```")
L.append("서랍 깊은 곳에 누런 봉투 하나 [muted trumpet enters]")
L.append("접힌 자국 사이로 번진 마음 [piano chords intensify]")
L.append("```")
L.append("- 가사 텍스트 사이에 브래킷을 넣으면 **해당 시점**에 이벤트 발생")
L.append("- 줄 끝에 붙이는 것이 가장 흔한 패턴")
L.append("")
L.append("### SP ↔ 가사 브래킷 관계")
L.append("")
L.append("| SP (팔레트) | 가사 브래킷 (타임라인) |")
L.append("|------------|----------------------|")
L.append("| 곡 전체에 이런 악기가 있다 | 이 구간에서 이 악기가 들어온다 |")
L.append("| 전체 톤/성격 선언 | 시점별 변화 지시 |")
L.append("| 산문 텍스트 | `[대괄호]` 지시문 |")
L.append("")
L.append("**SP에서 선언한 악기가 가사에서 진입하는 것이 가장 높은 확률의 패턴.**")
L.append("SP에 없는 악기를 가사에서 직접 큐하는 것도 가능하지만 빈도가 낮음.")
L.append("")

L.append("---")
L.append("")
L.append("## 경계 단어 정리")
L.append("")
L.append("### 복수 슬롯에 걸리는 단어")
L.append("")
L.append("| 단어 | 의미 A | 의미 B | 판별 기준 |")
L.append("|------|--------|--------|-----------|")
L.append("| bass | 베이스 기타 (악기) | bass drum (드럼) | 'bass guitar/line/plays' → 악기, 'bass drum' → 드럼 |")
L.append("| bass | 베이스 기타 | synth bass (별도 악기) | 'synth bass/sub-bass' → synth bass |")
L.append("| chorus | 섹션 태그 | 코러스 이펙트 | 대문자 단독 `[Chorus]` → 섹션, 'light chorus' → 이펙터 |")
L.append("| close-mic | 보컬 기법 | 믹싱 기법 | 양쪽 슬롯에 중복 등록 |")
L.append("| pitch correction | 보컬 프로세싱 | 전자 이펙터 | 양쪽 슬롯에 중복 등록 |")
L.append("| vibrato | 보컬 기법 | 이펙터 (tremolo와 혼용) | 보컬 문맥 → 보컬, 악기 문맥 → 이펙터 |")
L.append("| reverb | 믹싱 요소 | 전자 이펙터 | 양쪽 슬롯에 중복 등록 |")
L.append("| fills | 드럼 필인 | 악기 melodic fill | 'drum fill' → 드럼, 'melodic fill' → 악기 |")
L.append("| groove | 드럼 패턴 | 템포/느낌 | 'drum groove' → 드럼, 'mid-tempo groove' → 템포 |")
L.append("| solo | 없음 선언 (solo = 다른 건 없음) | 연주 기법 | 'solo vocal' → 없음선언, 'guitar solo' → 악기 |")
L.append("")

L.append("### 별도 악기로 구분해야 하는 것")
L.append("")
L.append("| 같은 카테고리 아님 | 이유 |")
L.append("|-------------------|------|")
L.append("| bass guitar ≠ synth bass | 음색·역할·주법 완전히 다름 |")
L.append("| synthesizer ≠ keyboard | keyboard=물리악기(keys), synthesizer=소리합성 |")
L.append("| acoustic piano ≠ electric piano | 음색·표현 범위 다름 |")
L.append("| acoustic guitar ≠ electric guitar | 주법·이펙트 체인 다름 |")
L.append("| clean electric guitar ≠ distorted electric guitar | 이펙트 유무로 캐릭터 분리 |")
L.append("")

# 통계 요약
L.append("---")
L.append("")
L.append("## 수치 요약")
L.append("")
L.append(f"- SP 문장: {len(sp_results)}개")
L.append(f"- 가사 브래킷: {len(bracket_results)}개")
L.append(f"- 고유 악기: {len(instrument_freq)}종")
L.append(f"- 코드/보이싱 표현: {len(chord_expressions)}종 (총 {sum(chord_expressions.values())}회)")
L.append(f"- SP 미분류: {sp_slot_counts.get('unclassified', 0)}개")
L.append(f"- 브래킷 미분류: {bracket_slot_counts.get('unclassified', 0)}개")

Path("docs/slot_reclassify_v2.md").write_text("\n".join(L))
print(f"완료:")
print(f"  SP 재분류: {OUT_DIR / 'sp_slots_v2.json'} ({len(sp_results)} entries)")
print(f"  브래킷 재분류: {OUT_DIR / 'bracket_slots_v2.json'} ({len(bracket_results)} entries)")
print(f"  요약 문서: docs/slot_reclassify_v2.md ({len(L)} lines)")
print()
print("=== SP 슬롯 분포 ===")
for slot, count in sp_slot_counts.most_common():
    print(f"  {count:4d}  {slot}")
print()
print("=== 브래킷 슬롯 분포 ===")
for slot, count in bracket_slot_counts.most_common():
    print(f"  {count:4d}  {slot}")
print()
print(f"=== 악기 TOP 15 ===")
for inst, c in instrument_freq.most_common(15):
    print(f"  {c:4d}  {inst}")
print()
print(f"=== 미분류 SP ===")
for sid, genre, idx, sent, slots, insts in sp_results:
    if any((s == "unclassified" if isinstance(s, str) else False) for s in slots):
        print(f"  [{sid:04d}] {sent[:100]}")
print()
print(f"=== 미분류 브래킷 ===")
for sid, genre, bt, slots in bracket_results:
    if any((s == "unclassified" if isinstance(s, str) else False) for s in slots):
        print(f"  [{sid:04d}] [{bt[:80]}]")
