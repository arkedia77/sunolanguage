#!/usr/bin/env python3
"""metatag_reopen_harvest_v1.py — 재개방분 수확·등급·코퍼스 대조.

입력: data/metatag_external/reopen_raw/*.txt (재개방으로 연 원문)
     data/metatag_external/yt/verify_v1/*.vtt (B-4로 회수한 자막)
산출: data/metatag_external/reopen_harvest_v1.json

★등급 규칙(값 보기 전에 고정)
  A_demo    출처가 **자기 생성물을 틀어** 보였음이 원문으로 확인됨
  B_recited 표기·주장은 있으나 시연 없음(전언)
  ★수치·성공률은 출처의 **자기신고**다 — N·방법 미기재면 시연이 있어도 **수치는 B**.

★대조 규칙
  코퍼스 조회는 **출력층만**(suno_sp_full·sp_entity·bracket_entity·stems_*). 입력층(leomusic_sp_full)은
  우리가 쓴 말이라 「Suno가 쓴다」의 근거가 못 된다.
  ★출력층 0은 **「Suno가 안 받는다」가 아니라 「우리 코퍼스가 본 적 없다」**. GAP은 후보이지 반증이 아니다.
"""
import json, re, sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data/metatag_external/reopen_raw"
VTT = ROOT / "data/metatag_external/yt/verify_v1"
IDX = ROOT / "data/reanalysis_v2/lexical_index.sqlite"
OUT = ROOT / "data/metatag_external/reopen_harvest_v1.json"
OUT_LAYERS = ("bracket_entity", "sp_entity", "suno_sp_full", "stems_bracket", "stems_sp")


def load_rows():
    c = sqlite3.connect(IDX)
    return [r for r in c.execute("SELECT source,song_id,sentence,entity,modifiers FROM entries")]


ROWS = load_rows()


def probe(term):
    p = re.compile(r"(?<![a-z])" + re.escape(term) + r"(?![a-z])", re.I)
    o = [r for r in ROWS if r[0] in OUT_LAYERS and p.search(" ".join(x for x in (r[2], r[3], r[4]) if x))]
    i = [r for r in ROWS if r[0] not in OUT_LAYERS and p.search(" ".join(x for x in (r[2], r[3], r[4]) if x))]
    return {"출력층": len(o), "곡수": len(set(r[1] for r in o)),
            "브라켓": len([r for r in o if "bracket" in r[0]]), "입력층": len(i)}


def visible(p: Path):
    b = p.read_text(encoding="utf-8", errors="replace")
    t = re.sub(r"<script.*?</script>|<style.*?</style>", " ", b, flags=re.S | re.I)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", t)).strip()


def vtt_text(p: Path):
    out = []
    for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
        l = line.strip()
        if not l or "-->" in l or l.startswith(("WEBVTT", "Kind:", "Language:", "NOTE")) or re.fullmatch(r"\d+", l):
            continue
        l = re.sub(r"<[^>]+>", "", l)
        if not out or out[-1] != l:
            out.append(l)
    return "\n".join(out)


# ── ⑴ miraheze 표기 대조 ────────────────────────────────────────────────
mira_f = RAW / "https_helldev_miraheze_org_wiki_Suno.txt"
mira = {"출처": "helldev.miraheze.org — RU 위키 「Suno 보컬·구조 태그」",
        "재개방_경위": "WebFetch 403 → curl(브라우저 UA)로 200. 가시 본문 11,568자.",
        "등급": "B_recited — 표기·설명은 있으나 자기 생성물 시연 없음"}
if mira_f.exists():
    t = visible(mira_f)
    uniq = sorted({m.group(1).strip() for m in re.finditer(r"\[([^\[\]\n]{1,60})\]", t)
                   if not re.search(r"[а-яА-Я]", m.group(1)) and "|" not in m.group(1)})
    have, gap = [], []
    for u in uniq:
        s = probe(u)
        (have if s["출력층"] else gap).append({"표기": u, **s})
    mira.update({
        "고유_영문표기": len(uniq),
        "★양성대조": f"{len(have)}/{len(uniq)}가 우리 출력층에 실재 — 출처가 실물 어휘를 담고 있다는 증거(잡음 아님)",
        "코퍼스에_있음": sorted(have, key=lambda x: -x["출력층"]),
        "★후보(출력층 0)": [g["표기"] for g in gap],
        "★후보_중_형식_신규": {
            "key:value 브라켓": ["Vocal Style: soulful", "Vocal Emotion: energetic",
                              "Vocal Effect: reverb", "Harmony: Yes", "Vocalist: Female"],
            "왜_따로_적나": ("어휘가 아니라 **형식**이다. 우리 출력층에 이 형식이 0인데, "
                        "`Vocalist: Female`은 우리 duet_bracket_grammar_v1이 다른 방법으로 "
                        "「명찰형은 죽는다」(`[Male Vocal]` exact 0곡)고 낸 것과 **같은 자리**를 가리킨다. "
                        "★독립 2경로가 같은 방향이나 **생성 없이는 여전히 미검증**이다."),
        },
        "★한계": "출력층 0은 「Suno가 안 받는다」가 아니라 「우리가 본 적 없다」. 후보이지 반증이 아니다.",
    })

# ── ⑵ B-4 자막에서 나온 「지시축」 주장 ─────────────────────────────────
claims = {
    "출처": "youtube Uy2jV0fqTPk — 「【Suno AI v4】曲にセリフを入れる[Spoken Word]と[Spoken Verse]」 (SunoAI Lab Notes)",
    "재개방_경위": "08-13 429로 자막 미회수 → 9일 시차 후 yt-dlp 재시도로 회수(수동자막 8개 언어).",
    "★등급": {
        "시연_존재": "A_demo — 자막 원문에 「먼저 [Spoken Word]를 시도해 보고 … 들어보겠습니다」"
                  "「이제 [Spoken Word]와 [Spoken Verse] 둘 다 들어보셨습니다」. 장르 3종(chillwave·bossa nova·death metal) A/B 시연.",
        "수치": "B_recited — 성공률 80%/50%는 출처의 **자기신고**이고 N·측정법 미기재.",
        "★08-13_대비": "그때는 설명란 철자만 봤고 등급을 A_demo로 달았다. 이제 **자막 원문으로 시연이 확인**된다 — 등급이 근거를 얻었다(강등 아님).",
    },
    "★왜_이것이_소득인가": (
        "우리 코퍼스는 **Suno가 뱉은 것**만 담아서 「입력했는데 무시당했다」를 **원리상 못 만든다**"
        "(v0 ⑥에 그렇게 적어 뒀다). 이 출처는 그 축을 가지고 있다 — 성공률·실패양식·위치효과·스타일 상호작용. "
        "★우리가 관측축만 쌓고 지시축을 안 쌓았다는 08-12 진단의 **첫 실질 보충**이다."),
    "주장": [
        {"주장": "[Spoken Word] = 음악을 무시하고 말한다 / [Spoken Verse] = 음악에 맞춰 말한다(음질 변경·효과 추가·간격 삽입)",
         "등급": "A_demo(시연 있음) · 해석은 출처 것"},
        {"주장": "성공률 [Spoken Word] 약 80% / [Spoken Verse] 약 50% — 태그를 써도 그 구간이 대사가 된다는 보장이 없다",
         "등급": "B_recited(자기신고·N 미기재)", "★우리축": "★우리가 원리상 못 만드는 축(무시당함)"},
        {"주장": "인트로(곡 시작부)에 배치하면 성공률이 급락한다 — Replace Section으로 앞 30초만 재생성하는 편이 낫다",
         "등급": "B_recited", "★우리축": "위치 효과. 우리 브라켓 대장에 위치 축 없음"},
        {"주장": "스타일에 \"spoken word\"를 넣으면 브라켓 성공률을 보완하나 **전곡이 대사화되는 부작용**이 크다",
         "등급": "B_recited",
         "★우리축": "★우리 2×3+1 사전등록의 **「스타일 서술 유무 × 브라켓 형태」 교차와 같은 축**. 외부가 방향을 먼저 말하고 있다."},
        {"주장": "\"Audiobook\" 스타일과 결합하면 전곡을 대사로 바꿀 수 있다", "등급": "B_recited",
         "★대조": "우리 출력층 `audiobook` 0회·`narrator` 0회"},
        {"주장": "장르 의존이 크다 — chillwave는 보컬 효과가 강하게 걸리고, bossa nova는 [Spoken Word]가 단절되며, death metal은 데스보이스를 못 만든다",
         "등급": "A_demo(3장르 시연)"},
        {"주장": "실패의 대부분은 **대사가 노래처럼 되는 것**이다", "등급": "B_recited",
         "★우리축": "★우리 VD 실측 「브라켓 텍스트 가창 누출」과 같은 축 — 설계가 쉬운 자리"},
    ],
    "★자막의_증명력_한계": "자막은 화자의 **말**이지 음원의 **태그 반응**이 아니다. 「틀어 보였다」까지가 최대치이고 "
                     "「그 태그가 작동했다」는 우리가 안 들었다. ⇒ 수치·인과 주장은 B를 넘지 못한다.",
}

# ── ⑶ 나머지 열린 출처 처분 ────────────────────────────────────────────
others = [
    {"출처": "help.suno.com/en/articles/11362369 (공식)", "열림": True,
     "★수확": 0, "판정": "온토픽 아님 — 「Voices(내 목소리 사용)」 기능 문서다. 메타태그 재고 0.",
     "부수": "공식 1차 출처로 Voices 기능 존재·스템 분리 자동 적용은 확인됨(메타태그와 무관)."},
    {"출처": "sunoarchitect.com (Kordra 상용 지식베이스)", "열림": True,
     "★수확": "형식 1 + 어휘군 1", "등급": "B_recited — 조언만·시연 없음",
     "내용": "[Spoken Word] 항목 + 「Vocal characteristic」 계열 표제어(Airy·Alto·Anointed·Anthemic·Auto-Tuned·Baritone…). "
             "★상용 제품의 태그 라이브러리라 **저자 1인 파생**일 수 있어 derivative 의심을 달아 둔다."},
    {"출처": "sunometatagcreator.com", "열림": True, "★수확": 0,
     "판정": "홈페이지만 열렸다. 2,596개 태그는 여전히 JS 도구 뒤 — **못 봄 유지**."},
]

out = {
    "무엇": "2단계 ⑺ 재개방 + 블로커 B-4 해소분의 수확·등급·코퍼스 대조",
    "재현": ".venv/bin/python scripts/metatag_reopen_harvest_v1.py",
    "선행": ["scripts/metatag_reopen_v1.py", "scripts/metatag_b4_captions_v1.py"],
    "★대조_축": "코퍼스 조회는 출력층만. 출력층 0 = 「우리가 본 적 없다」이지 「Suno가 안 받는다」가 아니다.",
    "miraheze_표기": mira,
    "지시축_주장": claims,
    "나머지_열린_출처": others,
}
OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"-> {OUT}")
print(f"miraheze 고유 {mira.get('고유_영문표기')} / 코퍼스 실재 {len(mira.get('코퍼스에_있음', []))} / 후보 {len(mira.get('★후보(출력층 0)', []))}")
print(f"지시축 주장 {len(claims['주장'])}건")
