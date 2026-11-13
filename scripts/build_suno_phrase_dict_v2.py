#!/usr/bin/env python3
"""build_suno_phrase_dict_v2.py — 수노말 사전 v2.0 (구 단위 · 채널 분리 · 먹힘 근거 칸) — encore 11-11 210058·210149·210303·212748 (LEO 지시).

★단일 Writer: sunolang.db `suno_phrase_dict` 를 쓰는 것은 이 파일 하나. `suno_emitted_terms`(v1.2 · build_suno_emitted_v1.py)는 건드리지 않는다.
채널(합산 0 — 칸마다 따로 센다 · 단위 = 곡):
  V+  Variety 고쳐 쓴 SP 에서 Suno 가 **더한** 구(보낸 SP 에 없고 Suno 저장 tags 에 있음) — Suno 가 쓴 것 확정
  V-  Suno 가 **뺀** 구(보낸 SP 에 있고 그 곡 모든 클립 tags 에 없음)
  HS  홈 곡 중 Suno 가 썼다고 볼 근거가 있는 문장 — 설명 모드(gpt_description_prompt 있음) · task=agentic_thinking
  HU  홈 곡 나머지(올린 사람 입력 · 저자 모름)
  HD  홈 곡 display_tags(Suno 화면 표시 태그)
  LS  Suno 가 오디오를 듣고 쓴 말 = tracks.suno_prompt(녹음 인식 79곡) — «들리면 이 말로 부른다» 역방향 근거(upload 문장은 저자 못 가려 HU)
  AG  우리 agentic 리믹스 클립 Suno tags(PG suno_clip_style gen_method=agentic_remix) — Suno 가 쓴 것 확정
  OD  우리 클립 display_tags(PG · Suno 화면 표시 태그 · 곡 단위 global_id)
  LEO LEO 문장 4(실명·곡명 든 구 뺌)
  ⛔Enhance·Inspire 자동 스타일 = 식별 칸 없음(PG·홈 둘 다) → 미측정
먹힘 근거: effect_pair(효과 대조 짝 · 교락 표기) / test_result(한 칸 짝 시험 PH2 · n=2) / listen_layer(LS 곡 수) / render_example(나온 클립·곡 id — 나옴 ≠ 들림).
쓰기 = data/suno_phrase_dict_v2/dict.json · sunolang.db suno_phrase_dict(DROP→CREATE). 생성 0 · 네트워크 0.
"""
import collections, hashlib, json, re, sqlite3, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
AC = Path.home() / "agent-comm-sunolanguage/projects"
REFS = AC / "sunomusic/attachments/SUNO_HOME_REFS_20261111/refs.json"
VAR = AC / "sunomusic/attachments/SUNO_HOME_REFS_20261111/variety_rewrites.json"
ACE = [AC / "sunomusic/attachments/acelang_collect_v2_20261113.jsonl", AC / "sunomusic/attachments/acelang_pilot_20261113.jsonl"]  # ✦ 출력(encore 235637 OK)
VERSION = "suno_phrase v2.2 (2026-11-14 · V± 하이픈 정규화 · ACE 칸)"

LEO = [  # encore 210058 «LEO 문장 4개» · 2·3 은 leomusic_encore_20261111_193153·193333 축자
    "Flamenco-Pop Fast Rumba, Hard-Struck Spanish Guitars With Cross-Accented Cajón, Fierce Palmas And Stomps Dropping Into Silence For A Half-Time Breakdown, Virtuosic Guitar Solo Into The Driving Final Refrain; Polished Wide-Stereo Live Mix, Dense Mastering, Controlled Limiting, Clean Powerful Bass And Stadium Ambience; Fast, Syncopated Groove; Upfront Close-Miked Gritty, Raspy Female Chest Voice, Shifting From Playful, Intimate Spoken Delivery To Explosive Belts And Fiery Melismas, With Crowd Chants And Jaleos Answering The Refrain.",
    "Futuristic K-Pop Hyperpop Edm With Aggressive Cyber Energy, Massive Cinematic Production, Explosive Beat Switches, Distorted Synth Bass, Industrial Electronic Textures, Powerful Female Vocals, Charismatic Giselle And Karina Rap With Sharp Fast-Flow Delivery, Confident Girl-Crush Attitude, Addictive “Whole Different Animal” Hook, Chant-Heavy Chorus, Huge Stadium Energy, Punchy Trap Drums, Glitch Effects, Futuristic Synth Leads, Dramatic Pre-Chorus Tension, Ningning And Winter Soaring High Notes, Emotional Vocal Climax, Layered Harmonies, Polished Sm-Style Production, Intense Dance Break, Catchy Repetitive Post-Chorus, Premium Studio Mastering, High-Impact Electronic Drop, Dark Sci-Fi Atmosphere, Next-Level Performance Vibe, 128-132 Bpm / Cyberpunk Atmosphere, Wide Stereo Imaging, Crisp Aggressive Mix, Balanced Low-End, Clean Vocal-Forward Production, Explosive Chorus Transitions, Viral Tiktok Hook Energy, Cinematic Vocal Layering, Powerful Crowd Chant Sections, Refined Distortion,",
    "K-Pop Futuristic Minimal Trap,100 Bpm,C Minor,Cold Luxury Boss Aura,Untouchable Dominant Energy With Hidden Vulnerability. Premium Ultra-Clean Studio Production,Deep Sustained 808 Sub Bass With Controlled Low-End,Punchy Sparse Kick,Dry Tight Snare/Clap,Crisp Restrained Hi-Hats,Large Negative Space,Dark Minimal Pluck,Low Atmospheric Pad,Subtle Reverse Hits And Rare Glitch Accents. Beat Stays Restrained And Breathable,Never Overcrowded,Leaving Maximum Space For Vocals. Female K-Pop Vocals Only,80% Slow-Mid Tempo Rhythmic Rap,Low Register,Slightly Husky And Cool Tone,Effortless Controlled Delivery,Confident Detached Attitude,Occasional Near-Whisper Phrases,Sharp Diction,Seductive But Not Exaggerated. 20% Short Melodic Catchy Hook With Layered Female Harmonies. No Constant Singing,No High Belting,No Bright Pop,No Latin Influence,No Rock Guitar,No Aggressive Edm,No Noisy Distortion,No Excessive Fx,No Robotic Vocals. Structure:Dark Intro,Rap Verse,Catchy Hook,Rap Verse,Hook,Whisper Bridge,",
    "90S R B Slow Jam Smooth R B Contemporary R B Electric Piano Fender Rhodes Deep Sub Bass Lush Pads Slow Rhythmic Groove 90 Bp Smooth Male Vocals Falsetto R&B, Soul, New Jack Swing Style Vocal Harmonies Stacked Vocals Call And Response",
]
NAME_BLOCK = re.compile(r"giselle|karina|ningning|winter|sm-style|whole different animal|tiktok", re.I)

# 효과 대조 짝 — 지금 1건(encore 210058 계기) · ⚠6곳 동시 변경 = 교락(sunomusic_encore_20261111_190050 «바꾼 곳»)
EFFECT_PAIR = {
    "case": "플라멩코 커버 v1 84fcb262·3223fbba ↔ v2 f7a1a05a·cd6fb7c7 (같은 원곡 31eaa64d·가사·style_weight 0.9)",
    "phrases": {"live mix": "v1 에 있음 → v2 studio mix", "studio mix": "v2 에 있음", "stadium ambience": "v1 에만", "crowd chants": "v1 에만", "jaleos": "v1 에만"},
    "confound": "v2 는 6곳 함께 바뀜(Fast→Slow Rumba·100 BPM · Live→Studio Mix · Stadium Ambience 뺌 · Female→Male · Crowd Chants And Jaleos 뺌) ⇒ «라이브↔스튜디오» 들림 차를 낱말 하나에 못 돌림 · 판정 = LEO·encore 청취(내 측정 0)",
}

# 한 칸 짝 시험 PH2 — encore 134146 · ⚠내가 읽은 곳 = 그 본문(hitmaking 133842 REPORT 는 reklcli · 직접 열람 0)
# 설계 = 발라드 B0 문장의 restrained vibrato 자리 하나만 바꿈 · 팔마다 2클립 · v6 · 가사 71605
PH2 = {
    "source": "encore 134146 ← hitmaking 20261112_133842 · reklcli:~/hitmaking/output/external/suno_phrase_ph2_20261112/REPORT.md",
    "noise": "같은 SP라도 날·요청이 다르면 ≈3반음까지 흔들림(같은 요청 두 클립은 σ≈0.7반음 · hitmaking 183544 as1 발라드 18짝 · 내가 읽은 곳 = encore 183647 본문) ⇒ 다른 날 렌더끼리 비교한 n<6 수치는 이 단서와 함께만",
    "verdict": "짝1(S1s↔N1)·짝2(S2↔N2) 둘 다 못 가름 → «Suno 말이라 더 먹힘» 근거 없음(반증도 아님)",
    "phrases": {
        "powerful belting": "최고음 p95: PH2 2/2 기준 밖(71.09·73.69 vs 기준 66.09~69.09) · PH1 2/2(67.99·67.82)는 넓어진 기준 안 ⇒ 경향(⛔4/4 아님) · 사전 전 채널 0(Suno 꼴 아님)",
        "powerful full-voice belts": "최고음 p95 1/2 밖(67.09·70.53) — 남의 말보다 낫다는 증거 없음 · Suno 꼴(V+ 1·HS 1·HU 8 · 축자 대조 115430)",
        "full-throated high notes": "최고음 0/2 · 세기(vox_lvl p95−p50) 12클립 중 최대 → 곁 칸 [경향] · 먹힘 근거 아님",
        "vocal with heavy vibrato": "긴 음 떨림 폭 1/2 밖(90.7¢ = 12클립 최대) · Suno 말(V+ 41 · Variety 고쳐쓰기 층)",
        "wide wobbling pitch on held notes": "긴 음 떨림 폭 0/2(둘 다 기준 밑)",
    },
}

# ACE ✦ 문장 틀 — sunolanguage acelang_v1.md(70출력 · 휴리스틱 칸 판정) · 판 단위 따름은 our_sp_on_ace_v0.md
ACE_FRAME = {
    "source": "agent-comm:projects/sunolanguage/exchange/ace_wizard_sp_20261113/acelang_v1.md · repo:sunolanguage data/acelang/frame_v1.json",
    "frame": ["장르 + «at NNN BPM» (첫 문장 70/70 · 씨앗 BPM 62/62 그대로 · 조는 씨앗에 있을 때만 · 지어 넣음 0/70)",
              "리듬·저역 / 리드·화성 / 보컬 — 순서 자유(정해진 순서 안 거스름 43/70)",
              "[믹스 문장 — 선택 · 39/70 · «The mix/production …» 머리 33/70]",
              "구조 활 intro → verses → pre-chorus → chorus → break → final chorus → outro (끝 문장 54/70 · 몫 중앙 25%)"],
    "size": "중앙 652자 (568~732) · 5문장 47/70",
    "variability": "같은 씨앗 출력끼리 낱말 자카드 중앙 0.25 = 표본기 ⇒ ace_n 은 여러 번 나온 말만 믿음",
    "follows_by_field": "BPM 대체로 따름(±3 안 21/32 · 빠른 신스팝 +4~+8) · 4/4 못 가름 · 조·드럼·리드·보컬·구조 미측정(드럼 = ACE MIDI 박 격자라 못 잼)",
}

STOP = set("a an the and or of with into to in on for by from as at that this is are its it over under while but than then so who which where when your their his her our has have be".split())
TOK = re.compile(r"[a-z0-9][a-z0-9&'+\-]*")
SEG = re.compile(r"[,;.:/\n|]+|\s+-\s+")


def norm_tok(w):
    w = w.replace("’", "'")
    return re.sub(r"'s$", "", w).strip("'-")


def segments(text):
    text = (text or "").replace("\\n", " ").replace("’", "'").replace("‘", "'").lower().replace("cajón", "cajon").replace("r&b", "rnb").replace("r & b", "rnb")
    for s in SEG.split(text):
        toks = [norm_tok(t) for t in TOK.findall(s)]
        toks = [t for t in toks if t]
        if toks:
            yield toks


def grams(text, nmax=4):
    out = set()
    for toks in segments(text):
        for n in range(1, nmax + 1):
            for i in range(len(toks) - n + 1):
                g = toks[i:i + n]
                if g[0] in STOP or g[-1] in STOP:
                    continue
                if any(t.isdigit() for t in g) and not re.fullmatch(r"\d{2,3} bpm", " ".join(g)):
                    continue  # «bpm 4»·«light 4» 같은 조각 = 4/4 쪼갬 · 숫자는 «NNN bpm» 꼴만
                out.add(" ".join(g))
    return out


CATS = [  # (칸, 낱말 정규식) — 위에서부터 먼저 걸리는 것 · 낱말 경계 기준
    ("금지형", r"^(no|without|never|avoid|not)\b"),
    ("추임새·관객", r"\b(crowd|chants?|jaleos?|audience|applause|cheers?|cheering|shouts?|ad-?libs?|hype|gang vocals?|palmas?)\b"),
    ("공간(라이브↔스튜디오)", r"\b(live[- ](mix|room|recording|performance|audience|concert|feel|show)|stadium|arena|ambience|ambient room|room|hall|reverb|reverb-soaked|studio|venue|club|concert|spacious|space|echo|cavernous|distant|negative space|cathedral|outdoor)\b"),
    ("믹스·마스터", r"\b(mix|mixed|mixing|master|mastering|mastered|limiting|limiter|compression|compressed|saturation|saturated|eq|loud|loudness|stereo|wide-stereo|imaging|polished|production|produced|lo-?fi|tape|analog|analogue|vinyl|crackle|hiss|sidechain|sidechained|mic|miked|close-mic|close-miked|mic'd|dry|wet|low-end|headroom|panned|separation|fidelity|hi-fi|clean mix|clean production)\b"),
    ("곡 흐름", r"\b(breakdown|drop|drops|build|build-up|buildup|builds|solo|bridge|intro|outro|verse|verses|chorus|choruses|refrain|hook|hooks|pre-chorus|post-chorus|final|climax|crescendo|fade|fades|half-time|key change|modulation|interlude|transition|transitions|swell|swells|rises|dance break|beat switch|switches|ending|section|sections|structure)\b"),
    ("전달", r"\b(delivery|spoken|spoken-word|whisper|whispered|whispers|near-whisper|belt|belts|belted|belting|melisma|melismas|melismatic|rap|rapped|rapping|flow|sung|singing|croon|crooned|crooning|call and response|call-and-response|phrasing|diction|scat|humming|hums|ad-lib|vibrato|runs)\b"),
    ("보컬 음색", r"\b(voice|voices|vocal|vocals|vocalist|soprano|alto|tenor|baritone|bass voice|falsetto|raspy|gritty|breathy|airy|husky|smoky|chest|head voice|nasal|choir|harmonies|harmony|stacked|male|female|duet|singer|tone)\b"),
    ("악기·연주", r"\b(guitar|guitars|piano|bass|bassline|drums?|synths?|synthesizer|strings|cajon|stomps?|claps?|handclaps|rhodes|organ|pads?|brass|horns?|sax|saxophone|trumpet|violin|cello|kick|snare|hi-hats?|hats|808s?|percussion|shaker|tambourine|flute|ukulele|banjo|harp|arpeggiated|arpeggios|fingerpicked|strummed|plucked|pluck|picked|struck|sub|leads?|keys|keyboard|electric piano|accordion|marimba|bells|glockenspiel|clarinet|mandolin|steel|acoustic|electric|orchestral|orchestra|beat|beats|groove box|sampler|samples?)\b"),
    ("결/리듬", r"\b(groove|rhythm|rhythmic|syncopated|syncopation|swing|swung|shuffle|bpm|tempo|four-on-the-floor|triplets?|polyrhythm|polyrhythmic|pulse|driving|laid-back|uptempo|up-tempo|downtempo|mid-tempo|midtempo|fast|slow|bounce|bouncy|halftime|rumba|clave|off-beat|offbeat|steady)\b"),
    ("장르", r"\b(pop|rock|hip-hop|hip hop|trap|jazz|rnb|soul|funk|funky|house|techno|edm|flamenco|k-pop|j-pop|hyperpop|ballad|folk|country|metal|punk|indie|ambient|dubstep|drill|reggae|reggaeton|dancehall|bossa|nova|latin|afrobeats?|disco|gospel|blues|emo|grunge|shoegaze|synthwave|synth-pop|city pop|electropop|electronic|electronica|dance|trance|drum and bass|dnb|garage|lofi|cinematic|orchestral|classical|opera|musical|anime|phonk|new jack swing|slow jam|grime|boom bap|neo-soul|alternative|post-punk|dream-pop|dream pop)\b"),
    ("무드", r"\b(melancholic|melancholy|dreamy|dark|uplifting|nostalgic|euphoric|playful|fierce|hopeful|sad|romantic|ethereal|haunting|moody|emotional|energetic|chill|intimate|warm|cold|bright|aggressive|confident|tender|bittersweet|joyful|somber|wistful|tense|dramatic|epic|powerful|explosive|lush|hazy|gritty|restrained|unhurried|introspective|vibrant|soulful|seductive|luxury|vibe|vibes|atmosphere|atmospheric|mood|energy)\b"),
]
CATS = [(c, re.compile(p)) for c, p in CATS]


def hy(g):
    return g.replace("-", " ")


def category(g):
    for c, rx in CATS:
        if rx.search(g):
            return c
    return "그 밖"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def main():
    refs = json.loads(REFS.read_text())["songs"]
    var = json.loads(VAR.read_text())["songs"]
    df = {k: collections.Counter() for k in ("V+", "V-", "Vkeep", "HS", "HU", "HD", "LS", "AG", "OD", "LEO")}
    ex = collections.defaultdict(dict)  # gram → 채널 → 예 id
    ch_n = collections.Counter()

    def add(ch, gs, eid):
        ch_n[ch] += 1
        for g in gs:
            df[ch][g] += 1
            ex[g].setdefault(ch, eid)

    # V± — 곡 단위(gid): 더함 = 어느 클립이든 Suno tags 에 있고 보낸 SP 에 없음 · 뺌 = 보낸 SP 에 있고 모든 클립 tags 에 없음
    for s in var:
        if not s.get("sp_sent"):
            continue
        sent = grams(s["sp_sent"])
        clips = [c for c in s["clips"] if c.get("sp_suno")]
        if not clips:
            continue
        per = [(c["clip"], grams(c["sp_suno"])) for c in clips]
        allu = set().union(*(u for _, u in per))
        # v2.2: 하이픈=공백 같은 꼴로 대조(v2.1 은 «electric guitar»→«electric-guitar» 고쳐쓰기를 뺌·더함으로 셈 — 189 중 79)
        sentN = {hy(g) for g in sent}; alluN = {hy(g) for g in allu}
        added = {}
        for cid, u in per:
            for g in u:
                if hy(g) not in sentN:
                    added.setdefault(g, cid)
        ch_n["V+"] += 1; ch_n["V-"] += 1; ch_n["Vkeep"] += 1
        for g, cid in added.items():
            df["V+"][g] += 1; ex[g].setdefault("V+", cid)
        for g in sent:
            if hy(g) in alluN:
                df["Vkeep"][g] += 1
            else:
                df["V-"][g] += 1; ex[g].setdefault("V-", f"gid {s['gid']}")
    # 홈
    for s in refs:
        st = s.get("style") or ""
        # upload 의 스타일 문장은 Suno 분석문인지 올린 사람 글인지 못 가름(«• Song Title» 꼴 섞임 · 11-12 표집) ⇒ HU
        suno_written = bool(s.get("gpt_description_prompt")) or s.get("task") == "agentic_thinking"
        if st.strip():
            add("HS" if suno_written else "HU", grams(st), s["id"])
        if s.get("display_tags"):
            add("HD", grams(s["display_tags"].replace(",", ",")), s["id"])
    db = sqlite3.connect(REPO / "sunolang.db")
    for tid, p in db.execute("select id, suno_prompt from tracks where suno_prompt is not null and trim(suno_prompt) != ''"):
        add("LS", grams(p), f"tracks:{tid}")
    sys.path.insert(0, str(REPO / "scripts"))
    from json_to_db import get_conn
    cur = get_conn().cursor()
    cur.execute("select global_id, clip_uuid, sp_suno from suno_clip_style where gen_method='agentic_remix' and sp_suno is not null")
    ag = collections.defaultdict(lambda: [None, set()])
    for gid, cu, sp in cur.fetchall():  # global_id 가 32/32 비어 있음 → 단위 = 서로 다른 tags 문장(24)
        k = gid or sp.strip()
        ag[k][0] = ag[k][0] or cu; ag[k][1] |= grams(sp)
    for gid, (cu, gs) in ag.items():
        add("AG", gs, cu)
    cur.execute("select global_id, min(clip_uuid::text), string_agg(display_tags, ', ') from suno_clip_style where display_tags is not null and display_tags <> '' group by global_id")
    for gid, cu, dt in cur.fetchall():
        add("OD", grams(dt), cu)
    for i, t in enumerate(LEO, 1):
        segs = [x for x in re.split(r"[,;.]", t) if not NAME_BLOCK.search(x)]
        add("LEO", grams(", ".join(segs)), f"LEO{i}")

    # ACE ✦ 출력 — 출력 단위(씨앗 여러 번 누름) · Suno 채널과 합산 0 · 하이픈=공백 꼴로 셈
    ace_n, ace_seed = collections.Counter(), collections.defaultdict(set)
    ace_docs = 0
    for f in ACE:
        for l in f.read_text().splitlines():
            d = json.loads(l); ace_docs += 1
            sd = d.get("seed_id") or d.get("seed")
            for g in grams(d["out"]):
                ace_n[hy(g)] += 1; ace_seed[hy(g)].add(sd)
    ch_n["ACE"] = ace_docs

    # 후보: Suno 확정·근거 채널에서 곡 ≥3 · 저자 모름 홈은 ≥5 · LEO 문장 구는 전부(재료 지정)
    keep = set()
    for ch, th in (("V+", 5), ("HS", 3), ("LS", 3), ("HD", 3), ("HU", 8), ("AG", 2), ("OD", 5)):
        keep |= {g for g, n in df[ch].items() if n >= th}
    # «그 밖» 칸 홑낱말(reframed·beneath 류 서술 연결어)은 Suno 가 20곡↑ 더한 것만
    keep = {g for g in keep if g in df["LEO"] or " " in g or category(g) != "그 밖" or df["V+"][g] >= 20}
    # «NNN BPM in <조>» = Suno 고정 꼴 하나 — 조 이름마다 행을 만들지 않음(곡 수는 meta.templates)
    KEYFRAG = re.compile(r"^(\d{2,3} )?bpm in( the key)?( [a-g](b|#|-flat|-sharp)?)?( (major|minor))?$|^in [a-g]( (major|minor))?$")
    keep = {g for g in keep if not KEYFRAG.match(g)}
    keep |= set(df["LEO"])
    keep |= set(PH2["phrases"])  # 시험한 구는 곡 수 0 이어도 행으로 둠(먹힘 칸 자리)
    # ACE 가 5출력↑ 쓴 2낱말↑ 구 = 행으로(Suno 0 이어도 · ace_only 표시) — 같은 꼴(하이픈) 행이 이미 있으면 그 행에 붙음
    have = {hy(g) for g in keep}
    edge = re.compile(r"\bbpm\b|^(between|driven|by)\b|\b(before|between|set|by|a)$")
    ace_only = {g for g in ace_n if " " in g and ace_n[g] >= 5 and g not in have and not re.search(r"\d", g) and not edge.search(g)}
    # ACE 행끼리 포섭: 더 긴 ACE 행이 출력 수의 80%↑ 를 덮으면 짧은 쪽 뺌(«pitched down» ⊂ «pitched down memphis rap vocal»)
    ace_only = {g for g in ace_only if not any(h != g and f" {g} " in f" {h} " and ace_n[h] >= 0.8 * ace_n[g] for h in ace_only)}
    keep |= ace_only
    keep = {g for g in keep if not NAME_BLOCK.search(g)}
    keep -= {"no", "not", "never", "without", "avoid"}  # 금지형 홑낱말 = 뜻 없음
    # 포섭: 더 긴 구 안에서만(같은 채널 곡 수의 80% 이상) 나오는 짧은 구는 뺌 — 근거 채널 합으로 판정
    tot = lambda g: sum(df[c][g] for c in ("V+", "HS", "HU", "LS", "HD", "AG", "OD"))
    by_len = sorted(keep, key=lambda g: -len(g.split()))
    drop = set()
    longer = collections.defaultdict(list)
    for g in by_len:
        w = g.split()
        for n in range(1, len(w)):
            for i in range(len(w) - n + 1):
                longer[" ".join(w[i:i + n])].append(g)
    for g in keep:
        if g in df["LEO"]:
            continue
        t = tot(g)
        if t and any(tot(h) >= 0.8 * t for h in longer.get(g, []) if h in keep):
            drop.add(g)
    keep -= drop

    # 지금 판 대조
    nz = lambda s: re.sub(r"[\s\-]+", " ", s.lower().replace("r&b", "rnb")).strip()
    v12 = {nz(t): (n, k) for t, n, k in db.execute("select term, n_songs, kind from suno_emitted_terms")}
    v35 = {nz(t) for t, in db.execute("select suno_term from expr_concepts")}
    oldwords = {w for t in list(v12) + list(v35) for w in t.split()}
    rows = []
    for g in keep:
        k = nz(g)
        ep = EFFECT_PAIR["phrases"].get(g)
        rows.append({
            "phrase": g, "category": category(g), "n_words": len(g.split()),
            "V+": df["V+"][g], "V-": df["V-"][g], "Vkeep": df["Vkeep"][g], "HS": df["HS"][g], "HU": df["HU"][g],
            "HD": df["HD"][g], "LS": df["LS"][g], "AG": df["AG"][g], "OD": df["OD"][g], "LEO": df["LEO"][g],
            "in_v1_2": k in v12, "v1_2_songs": v12.get(k, (0, ""))[0], "in_v3_5": k in v35,
            "new_kind": "기존" if (k in v12 or k in v35) else ("구 꼴만 새것" if all(w in oldwords for w in k.split()) else "새 낱말 포함"),
            "effect_pair": f"{ep} · 교락" if ep else None,
            "ace_n": ace_n[hy(g)], "ace_seeds": len(ace_seed[hy(g)]),
            # 홑낱말(vocal·rhythm)은 Suno 가 꼴만 바꿔도 V- 가 커서 표시 안 함
            "ace_vs_suno": None if " " not in g else ("ACE 씀·Suno 뺌" if ace_n[hy(g)] >= 5 and df["V-"][g] >= 15 and df["V-"][g] >= 2 * max(df["V+"][g], 1)
                            else "둘 다 씀" if ace_n[hy(g)] >= 5 and (df["V+"][g] >= 5 or df["HS"][g] >= 3)
                            else "ACE 만" if ace_n[hy(g)] >= 5 and not any(df[c][g] for c in ("V+", "Vkeep", "HS", "HU", "HD", "LS", "AG", "OD")) else None),
            "ace_follows": None,  # 들림 측정 = encore 렌더(지금 BPM 만 칸 아닌 판 단위 · meta.ace_frame)
            "test_result": f"PH2 n=2 · {PH2['phrases'][g]}" if g in PH2["phrases"] else None,
            "listen_layer": df["LS"][g],  # tracks 녹음 인식 79곡 중 곡 수
            "render_example": ex[g].get("V+") or ex[g].get("AG") or ex[g].get("HS") or ex[g].get("HU") or ex[g].get("OD") or ex[g].get("LEO"),
        })
    rows.sort(key=lambda r: (r["category"], -(r["V+"] + r["HS"] + r["LS"]), r["phrase"]))
    home_any, vplus = collections.Counter(), collections.Counter()  # 하이픈·띄어쓰기 같은 꼴로 모아 셈
    for g, n in (df["HS"] + df["HU"] + df["HD"]).items():
        home_any[nz(g)] += n
    for g, n in df["V+"].items():
        vplus[nz(g)] += n
    stale = sorted(((t, n) for t, (n, kind) in v12.items() if n >= 10 and home_any[t] == 0 and vplus[t] == 0), key=lambda x: -x[1])
    tpl = re.compile(r"\b\d{2,3} bpm in [a-g]", re.I)
    templates = {"NNN BPM in <조> — Variety 곡(Suno 씀)": sum(1 for x in var if any(tpl.search(c.get("sp_suno") or "") for c in x["clips"])),
                 "같은 꼴 — 보낸 SP": sum(1 for x in var if tpl.search(x.get("sp_sent") or "")),
                 "같은 꼴 — 홈 곡": sum(1 for x in refs if tpl.search(x.get("style") or ""))}
    meta = {"version": VERSION, "builder": "scripts/build_suno_phrase_dict_v2.py",
            "inputs": {"refs.json": sha(REFS), "variety_rewrites.json": sha(VAR), "tracks.suno_prompt": "sunolang.db"},
            "channel_docs": dict(ch_n), "effect_pair": EFFECT_PAIR, "ph2": PH2, "ace_frame": ACE_FRAME, "templates": templates,
            "compared_with": {"suno_emitted v1.2": "2026-10-16 · 5,904 낱말·구(우리 클립 Suno tags · V6 census)",
                              "expr_concepts v3.5": "2026-09-14 · 453 개념"},
            "stale_v1_2_absent_in_new": {"n": len(stale), "top": stale[:40],
                                         "뜻": "v1.2 에서 10곡↑ 이었는데 홈 1,345곡·Variety 더함 둘 다 0 — 폐기 아님 · 우리 입력 되울림이었을 수 있음"}}
    out = REPO / "data/suno_phrase_dict_v2"; out.mkdir(exist_ok=True)
    (out / "dict.json").write_text(json.dumps({"meta": meta, "rows": rows}, ensure_ascii=False, indent=1))
    db.execute("drop table if exists suno_phrase_dict")
    cols = list(rows[0].keys())
    db.execute("create table suno_phrase_dict (" + ", ".join(f'"{c}"' for c in cols) + ", dict_version text)")
    db.executemany(f"insert into suno_phrase_dict values ({','.join('?' * (len(cols) + 1))})",
                   [tuple(r[c] for c in cols) + (VERSION,) for r in rows])
    db.commit()
    c = collections.Counter(r["category"] for r in rows)
    print(json.dumps({"rows": len(rows), "dropped_subsumed": len(drop), "channel_docs": dict(ch_n), "by_cat": c,
                      "new_vs_both": sum(1 for r in rows if not r["in_v1_2"] and not r["in_v3_5"]),
                      "effect_pair_rows": sum(1 for r in rows if r["effect_pair"]), "test_rows": sum(1 for r in rows if r["test_result"]), "listen_layer_rows": sum(1 for r in rows if r["LS"]),
                      "stale": len(stale)}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
