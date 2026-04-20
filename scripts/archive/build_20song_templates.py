#!/usr/bin/env python3
"""Suno SP+가사 7-Slot 템플릿 해석서 (20곡) — leomusic2 참조용."""
import json, re
from collections import Counter
from pathlib import Path

merged = json.loads(Path("data/reanalysis_v2/merged_4values.json").read_text())

target_genres = {
    'Indie Pop': 2, 'City Pop': 2, 'Korean Ballad': 1, 'R&B': 1,
    'Hip-Hop': 1, 'Folk': 1, 'Synth Pop': 1, 'Funk Pop': 1,
    'Electro Pop': 1, 'Rock': 1, 'Indie Rock': 1, 'Jazz Pop': 1,
    'Electronic': 1, 'Acoustic Pop': 1, 'Lo-fi Pop': 1,
    'Acoustic Ballad': 1, 'Disco Pop': 1, 'Indie Folk': 1,
}

selected = []
genre_count = Counter()
for s in merged:
    g = s.get('genre', '')
    if g in target_genres and genre_count[g] < target_genres[g]:
        for sr in s.get('suno_reanalysis', []):
            sp = sr.get('sp', '')
            lyr = sr.get('lyrics', '')
            if len(sp) > 100 and len(lyr) > 100:
                selected.append(s)
                genre_count[g] += 1
                break
    if len(selected) >= 20:
        break

# --- 분류 도구 ---
GENRE_INDICATORS = re.compile(
    r"^(k-pop|k-indie|k-hip\s*hop|k-ballad|k-rock|k-r&b|"
    r"pop|rock|jazz|r&b|hip[- ]?hop|electronic|ambient|folk|"
    r"indie|ballad|soul|funk|disco|synth|city\s*pop|bossa|"
    r"punk|metal|blues|country|reggae|lo-?fi|boom\s*bap|"
    r"cinematic|orchestral|dream\s*pop|shoegaze|chillwave)", re.I)
DRUM_WORDS = {"drum","drums","kick","snare","hi-hat","hi-hats",
              "percussion","cymbal","shaker","tambourine","rimshot","backbeat","beat","beats"}
VOCAL_WORDS = {"vocal","vocals","singer","singing","voice",
               "baritone","tenor","soprano","alto","falsetto","rap","rapping"}
TEMPO_RE = re.compile(r"\b(tempo|bpm|key of|time signature|\d+/\d+\s*time)\b", re.I)
PRODUCTION_WORDS = {"production","mix","mixing","processed","mic","close-mic",
                    "room reverb","stereo","panning","compression","eq","sidechain"}
ARRANGEMENT_RE = re.compile(r"(arrangement|arrangement is|focusing on|interplay)", re.I)

SLOT_KR = {
    "genre_declaration": "장르 선언",
    "instrument_layers": "악기 레이어",
    "drums": "드럼/퍼커션",
    "vocals": "보컬",
    "tempo_key_time": "템포/조성/박자",
    "production": "프로덕션/믹스",
    "arrangement_summary": "어레인지먼트 총평",
}

SLOT_POS = {
    "genre_declaration": "첫 문장",
    "instrument_layers": "본문(복수)",
    "drums": "본문",
    "vocals": "본문",
    "tempo_key_time": "후반부",
    "production": "본문~후반",
    "arrangement_summary": "마지막",
}

SLOT_EXPLAIN = {
    "genre_declaration": "Suno가 곡의 장르를 한 문장으로 선언. 첫 문장 고정 위치.",
    "instrument_layers": "악기별 연주 패턴·이펙트·역할을 기술. 복수 문장, 순서 자유.",
    "drums": "킥·스네어·하이햇·셰이커 등 타격음 구성을 기술.",
    "vocals": "보컬 타입(음역·성별)·딜리버리(발성법)·프로세싱(이펙트)을 기술.",
    "tempo_key_time": "BPM·조성·박자를 기술. 고정 구문 패턴.",
    "production": "전체 믹스 특성·리버브 타입·마이크 배치 등 프로덕션 기술.",
    "arrangement_summary": "어레인지먼트의 밀도·핵심 상호작용을 총평.",
}

BRACKET_TYPE_KR = {
    "section": "섹션 태그",
    "vocal_direction": "보컬 지시",
    "instrument_or_arrangement": "악기/어레인지먼트 큐",
    "transition_cue": "전환 큐",
    "effect": "이펙트 큐",
}

SECTION_TAGS = {"intro","verse","pre-chorus","chorus","bridge","outro","hook","drop",
                "breakdown","interlude","instrumental","refrain","coda"}
VOCAL_DIR_WORDS = {"vocal","vocals","voice","sing","singing","whisper","breathy",
                   "falsetto","shout","rap","rapped","spoken"}
INSTRUMENT_WORDS = {"guitar","bass","drum","drums","synth","piano","keys","pad","organ",
                    "rhodes","strings","violin","cello","flute","trumpet","sax","808",
                    "clap","hat","kick","snare","shaker","tambourine","bell","bells",
                    "orchestra","choir","saxophone"}
TRANSITION_WORDS = {"enter","enters","drop","drops","fade","fades","build","builds",
                    "swell","swells","cut","return","returns"}

def classify_sentence(sent, idx, total):
    sl = sent.lower()
    words_set = set(re.findall(r"[a-z\-']+", sl))
    if idx == 0 and GENRE_INDICATORS.search(sl):
        return "genre_declaration"
    if TEMPO_RE.search(sl) and not words_set & DRUM_WORDS:
        return "tempo_key_time"
    if ARRANGEMENT_RE.search(sl):
        return "arrangement_summary"
    if words_set & PRODUCTION_WORDS:
        return "production"
    if words_set & VOCAL_WORDS:
        return "vocals"
    if words_set & DRUM_WORDS:
        return "drums"
    return "instrument_layers"

def split_sentences(txt):
    if not txt:
        return []
    t = re.sub(r"\s+", " ", txt.strip())
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", t) if s.strip()]

BRACKET_RE = re.compile(r"\[([^\[\]]{1,200})\]")

def guess_bracket_type(b_norm):
    bl = b_norm.lower()
    if any(s in bl for s in SECTION_TAGS) or re.match(r"^(verse|chorus)\s*\d*$", bl):
        return "section"
    if any(w in bl for w in VOCAL_DIR_WORDS):
        return "vocal_direction"
    if any(w in bl for w in TRANSITION_WORDS):
        return "transition_cue"
    if any(w in bl for w in INSTRUMENT_WORDS):
        return "instrument_or_arrangement"
    return "instrument_or_arrangement"

def kr_interpret_sp(slot, sent):
    sl = sent.lower()
    if slot == "genre_declaration":
        return f"장르: {sent.rstrip('.')}"
    elif slot == "tempo_key_time":
        bpm = re.search(r"(\d+)\s*bpm", sl, re.I)
        key = re.search(r"key of\s+([a-g][#b]?\s*(?:major|minor))", sl, re.I)
        time = re.search(r"(\d+/\d+)\s*time", sl, re.I)
        parts = []
        if bpm: parts.append(f"템포 {bpm.group(1)} BPM")
        if key: parts.append(f"조성 {key.group(1)}")
        if time: parts.append(f"박자 {time.group(1)}")
        return ", ".join(parts) if parts else sent
    elif slot == "drums":
        return f"드럼: {sent.rstrip('.')}"
    elif slot == "vocals":
        return f"보컬: {sent.rstrip('.')}"
    elif slot == "arrangement_summary":
        return f"편곡: {sent.rstrip('.')}"
    elif slot == "production":
        return f"프로덕션: {sent.rstrip('.')}"
    else:
        return f"악기: {sent.rstrip('.')}"

# --- 문서 생성 ---
L = []
L.append("# Suno SP+가사 7-Slot 템플릿 해석서 (20곡)")
L.append("")
L.append("> leomusic2 참조용 · 2026-04-17 · sunolanguage v2 (326 clips)")
L.append("")

# --- Part 1: 사용법 ---
L.append("## Part 1: Suno의 두 채널 시스템")
L.append("")
L.append("Suno에게 곡을 만들라고 할 때, 두 가지 입력 채널이 있다:")
L.append("")
L.append("### 채널 A: SP (Style Prompt) — \"이 곡은 전체적으로 이런 곡이다\"")
L.append("")
L.append("산문 텍스트로 곡의 **전체 성격**을 기술. 7개 슬롯으로 구성:")
L.append("")
L.append("| # | 슬롯 | 위치 | 역할 |")
L.append("|---|------|------|------|")
for i, (slot_id, kr) in enumerate(SLOT_KR.items(), 1):
    L.append(f"| {i} | **{kr}** | {SLOT_POS[slot_id]} | {SLOT_EXPLAIN[slot_id]} |")
L.append("")
L.append("**SP가 답하는 질문**: \"어떤 장르? 어떤 악기? 어떤 드럼? 어떤 보컬? 얼마나 빠르게? 어떤 키? 어떤 믹스?\"")
L.append("")

L.append("### 채널 B: 가사 브래킷 — \"시간 순서대로 뭐가 들어오고 빠지는가\"")
L.append("")
L.append("가사 텍스트 안에 `[...]` 브래킷을 삽입하여 **시간축 레이어링**을 컨트롤:")
L.append("")
L.append("| 브래킷 타입 | 역할 | 예시 |")
L.append("|------------|------|------|")
L.append("| **섹션 태그** | 곡 구간 선언 | `[Intro]`, `[Verse 1]`, `[Chorus]`, `[Bridge]` |")
L.append("| **악기/어레인지먼트 큐** | 해당 구간의 악기 편성 지정 | `[fingerpicked acoustic guitar]`, `[full band arrangement]` |")
L.append("| **보컬 지시** | 보컬 타입 전환 | `[breathy female vocals]`, `[male tenor vocals]` |")
L.append("| **전환 큐** | 악기 진입/퇴장 타이밍 | `[kick drum enters]`, `[bass drops out]` |")
L.append("| **이펙트 큐** | 순간적 프로세싱 | `[vocal harmony on '삭제']`, `[guitar feedback swell]` |")
L.append("")
L.append("**가사 브래킷이 답하는 질문**: \"Intro에서 뭐가 먼저 나와? Verse 1에서 보컬은? Chorus에서 뭐가 추가로 들어와?\"")
L.append("")

L.append("### 두 채널의 관계")
L.append("")
L.append("```")
L.append("SP:   \"이 곡에는 clean electric guitar, sub-bass synth, crisp snare가 있다\"")
L.append("       → 전체 팔레트 선언 (무엇이 있는가)")
L.append("")
L.append("가사:  [Intro] [arpeggiated clean electric guitar with chorus]")
L.append("       [Verse 1] [breathy female vocals] 가사... [kick drum enters]")
L.append("       [Chorus] [sub-bass synth enters, snare hits on 2 and 4]")
L.append("       → 시간축 시퀀싱 (언제 들어오는가)")
L.append("```")
L.append("")
L.append("**SP = 팔레트 / 가사 브래킷 = 타임라인.** 둘이 합쳐져야 완전한 곡 기술.")
L.append("")
L.append("---")
L.append("")

# --- Part 2: 20곡 템플릿 ---
L.append("## Part 2: 20곡 실제 템플릿")
L.append("")

count = 0
for song in selected:
    sr = song['suno_reanalysis'][0]
    sp = sr.get('sp', '')
    lyr = sr.get('lyrics', '')
    if not sp or not lyr:
        continue
    count += 1

    L.append(f"### [{count}/20] #{song['song_id']:04d} {song['title']} — {song.get('genre','미정')}")
    L.append("")

    # SP 원문
    L.append("#### SP 원문")
    L.append(f"> {sp}")
    L.append("")

    # SP 슬롯 분해
    L.append("#### SP → 7슬롯 분해")
    L.append("")
    sents = split_sentences(sp)
    for i, s in enumerate(sents):
        slot = classify_sentence(s, i, len(sents))
        kr = SLOT_KR[slot]
        interpret = kr_interpret_sp(slot, s)
        L.append(f"| **{kr}** | {s} |")
        L.append(f"| | *{interpret}* |")
    L.append("")

    # 가사 원문 + 브래킷 해석
    L.append("#### 가사 브래킷 시퀀스")
    L.append("")
    lyr_lines = lyr.split('\n')
    for ll in lyr_lines:
        ll = ll.strip()
        if not ll:
            continue
        brackets = BRACKET_RE.findall(ll)
        if brackets:
            bracket_parts = []
            for b in brackets:
                btype = guess_bracket_type(b.lower())
                type_kr = BRACKET_TYPE_KR.get(btype, "기타")
                bracket_parts.append(f"`[{b}]` ← {type_kr}")
            L.append("  ".join(bracket_parts))
        else:
            # 가사 라인 — 브래킷이 중간에 있을 수 있음
            inline_brackets = BRACKET_RE.findall(ll)
            if inline_brackets:
                display = ll
                for b in inline_brackets:
                    btype = guess_bracket_type(b.lower())
                    type_kr = BRACKET_TYPE_KR.get(btype, "기타")
                    display = display.replace(f"[{b}]", f"**[{b}]**←{type_kr}")
                L.append(f"  {display[:100]}")
            else:
                if len(ll) > 60:
                    L.append(f"  _{ll[:60]}..._")
                else:
                    L.append(f"  _{ll}_")
    L.append("")

    # SP↔가사 관계
    sp_lower = sp.lower()
    lyr_lower = lyr.lower()
    sp_insts = set(re.findall(
        r"((?:clean |acoustic |electric |slap |upright |fingerpicked )*"
        r"(?:guitar|bass|piano|synth|drum|trumpet|organ|rhodes|strings|pads?|saxophone))",
        sp_lower))
    lyr_brackets_all = BRACKET_RE.findall(lyr)
    lyr_insts = set()
    for b in lyr_brackets_all:
        found = re.findall(
            r"((?:clean |acoustic |electric |slap |upright |fingerpicked )*"
            r"(?:guitar|bass|piano|synth|drum|trumpet|organ|rhodes|strings|pads?|saxophone))",
            b.lower())
        lyr_insts.update(found)

    L.append("#### SP↔가사 악기 매칭")
    if sp_insts or lyr_insts:
        common = sp_insts & lyr_insts
        sp_only = sp_insts - lyr_insts
        lyr_only = lyr_insts - sp_insts
        if common:
            L.append(f"- **공통** (SP 기술 + 가사 큐): {', '.join(sorted(common))}")
        if sp_only:
            L.append(f"- **SP에만** (전체 톤, 진입 큐 없음): {', '.join(sorted(sp_only))}")
        if lyr_only:
            L.append(f"- **가사에만** (SP 미언급, 가사에서 직접 큐): {', '.join(sorted(lyr_only))}")
    else:
        L.append("- 악기 매칭 데이터 없음")
    L.append("")
    L.append("---")
    L.append("")

# --- Part 3: 패턴 요약 + 체크리스트 ---
L.append("## Part 3: 공통 패턴 + leomusic2 체크리스트")
L.append("")
L.append("### SP 작성 규칙")
L.append("1. **첫 문장 = 장르 선언** (100% 일관). 'K-Pop/K-Indie/K-Hip Hop' + 하위장르 조합.")
L.append("2. **각 악기 = 독립 문장**. `{악기} plays/performs/provides {패턴} with {이펙트}.`")
L.append("3. **드럼 = 독립 문장**. 'The drums consist of {킥} and {스네어} with {레이어}.'")
L.append("4. **보컬 = 독립 문장**. 음역(baritone/tenor) + 딜리버리(breathy/intimate) + 프로세싱(plate reverb).")
L.append("5. **템포/조성 = 후반부**. 'The tempo is <BPM> in the key of <KEY>.' 변이형 한정.")
L.append("6. **어레인지먼트 총평 = 마지막** (선택). 'The arrangement is sparse, focusing on...'")
L.append("")
L.append("### 가사 작성 규칙")
L.append("1. **[Intro]로 시작** + 메인 악기 큐. 예: `[Intro]\\n[fingerpicked acoustic guitar]`")
L.append("2. **각 섹션 = [섹션 태그] + [보컬/악기 큐]** 쌍으로 시작.")
L.append("   - `[Verse 1]\\n[breathy male vocals]` → 이 구간의 보컬 타입 지정")
L.append("3. **가사 중간에 [전환 큐]** 삽입으로 레이어 추가.")
L.append("   - `가사 텍스트 [kick drum enters] 가사 계속` → 킥드럼 진입 시점")
L.append("4. **SP에서 언급한 악기가 가사에서도 진입** (교차 일관성).")
L.append("5. **Chorus에서 악기 추가**, Bridge에서 악기 제거가 전형적 패턴.")
L.append("")
L.append("### SP 생성 체크리스트")
L.append("- [ ] 첫 문장에 장르 선언?")
L.append("- [ ] 각 악기를 독립 문장으로? (패턴 + 이펙트)")
L.append("- [ ] 드럼 구성 별도 문장?")
L.append("- [ ] 보컬 타입·딜리버리·프로세싱?")
L.append("- [ ] 후반부에 템포/조성/박자?")
L.append("- [ ] 어레인지먼트 총평? (선택)")
L.append("")
L.append("### 가사 생성 체크리스트")
L.append("- [ ] [Intro]로 시작 + 악기 큐?")
L.append("- [ ] 각 섹션 [태그] + [악기/보컬 큐] 쌍?")
L.append("- [ ] 가사 중간 [X enters] 전환 큐?")
L.append("- [ ] SP 악기와 가사 브래킷 교차 확인?")
L.append("- [ ] Chorus 확장 / Bridge 축소 패턴?")

OUT = Path("docs/slot_template_20songs.md")
OUT.write_text('\n'.join(L))
print(f"생성: {OUT} ({len(L)} lines, {count}곡)")
