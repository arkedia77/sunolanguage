#!/usr/bin/env python3
# AWARE05 — AWARE100 스파인 5번 「들릴 때만 산다」(존재=들림) 10곡.
# 발주: kee 2026-07-31(08-01 슬롯·P1) / 착수 GO: kee 2026-08-03 옵션A(즉시착수·원안유지).
# 설계 정본: agent-comm projects/sunomusic/AWARE100_DESIGN.md §1.
#   화자=음악 자신(AI 생성기 입장 아님). POV 기본배분 1인칭3·2인칭2·3인칭3·전지적2.
#   금지선 2겹: ①디지털 생활 비평 ②AI/생성기 어휘 — grep 하드검증 0 목표.
#   10곡 상호 sound_novelty 상이. 장르 자유(팀 강점).
# 브라켓 문법 정본: docs/duet_bracket_grammar_v1.md (2026-08-03) — attested 서술형 소문자만.
# 10 병렬 전문 서브에이전트 저작 → 본 게이트 검증 → PG 적재(pending_suno).
import os, json, re, sys

THEME = "AWARE05 「들릴 때만 산다」 — 존재=들림. 화자=음악 자신"
ALBUM = "들릴 때만 산다 (Alive Only When Heard)"
BATCH = "AWARE05"
GID0 = 30198  # 다음 가용: 30199~30208 (JIOBD01이 30189~30198 사용)

HERE = os.path.dirname(os.path.abspath(__file__))
SONGS = json.load(open(os.path.join(HERE, '..', 'data', 'aware', 'AWARE05_songs.json')))

# --- 금지선 2겹 (AWARE100_DESIGN §1) ---
BAN_AI = ["프롬프트", "시드", "렌더", "코드", "uuid", "크레딧", "모델", "데이터",
          "서버", "업로드", "다운로드", "스트리밍", "재생목록", "알고리즘", "인공지능",
          "생성기", "학습", "파일", "폴더", "화면", "클릭", "접속", "온라인", "디지털"]
BAN_DIGITAL = ["알고리즘", "피드", "좋아요", "구독", "조회수", "타임라인", "스크롤", "알림"]

SECTION_OK = re.compile(r'^\[(Intro|Verse|Chorus|Pre-Chorus|Post-Chorus|Bridge|Outro|Hook|'
                        r'Instrumental|Instrumental Break|Interlude|Build|Build Up|Breakdown|'
                        r'Vamp|Refrain|Final Chorus|Drop|Guitar Solo|Section)\b[^\]]*\]$')
HANGUL = re.compile(r'[가-힣]')
BRACKET_LINE = re.compile(r'^\[[^\]]*\]$')
INLINE_BR = re.compile(r'\S+\s*\[[^\]]*\]|\[[^\]]*\]\s*\S+')

fails, warns = [], []
titles, novelties = {}, []

for s in SONGS:
    p = s["pos"]
    # SP 규격
    if len(s["sp"]) > 1000:
        fails.append((p, "SP>1000", len(s["sp"])))
    if HANGUL.search(s["sp"]):
        fails.append((p, "SP에 한글", ""))
    # 제목 중복
    if s["title"] in titles:
        fails.append((p, f"제목 중복 with pos{titles[s['title']]}", s["title"]))
    titles[s["title"]] = p
    # sound_novelty 중복
    if s["sound_novelty"] in novelties:
        fails.append((p, "sound_novelty 중복", ""))
    novelties.append(s["sound_novelty"])
    # 금지선 (제목+가사+SP 전체)
    blob = s["title"] + "\n" + s["lyrics"]
    for w in set(BAN_AI + BAN_DIGITAL):
        if w in blob:
            fails.append((p, f"금지어 '{w}'", ""))
    # 브라켓 문법
    for ln in s["lyrics"].split("\n"):
        ln = ln.rstrip()
        if not ln:
            continue
        if "[" in ln or "]" in ln:
            if not BRACKET_LINE.match(ln):
                fails.append((p, "브라켓 독립행 위반", ln[:50]))
                continue
            body = ln[1:-1]
            if HANGUL.search(body):
                fails.append((p, "한글 브라켓", ln[:40]))
            if SECTION_OK.match(ln):
                continue  # 섹션 브라켓 = Title Case 허용
            if body != body.lower():
                fails.append((p, "비섹션 브라켓 대문자(명찰형 의심)", ln[:40]))
    # 가사 분량
    lines = [l for l in s["lyrics"].split("\n") if l.strip()]
    if len(lines) < 20:
        fails.append((p, "가사 20행 미만", len(lines)))
    if not s["lyrics"].startswith("["):
        fails.append((p, "섹션 브라켓으로 시작 안 함", ""))

# POV 배분
from collections import Counter
pov = Counter(s["pov"] for s in SONGS)
TARGET = {"1인칭": 3, "2인칭": 2, "3인칭": 3, "전지적": 2}
if dict(pov) != TARGET:
    fails.append(("-", f"POV 배분 불일치 {dict(pov)} != {TARGET}", ""))

# 장르 상이
g = [s["genre"] for s in SONGS]
if len(set(g)) != 10:
    fails.append(("-", f"장르 중복 {len(set(g))}/10", ""))

print(f"=== {BATCH} 게이트 ===")
for s in SONGS:
    print(f"  {BATCH}-{s['pos']:<2} {s['pov']:<4} {s['genre']:<12} {s['title']:<16} "
          f"{s['key']:<12} {s['bpm']:>3}BPM  SP={len(s['sp']):>4}  "
          f"LYR={len([l for l in s['lyrics'].split(chr(10)) if l.strip()]):>2}행")
print(f"  POV 배분: {dict(pov)}  장르 고유: {len(set(g))}/10")

assert len({s['pos'] for s in SONGS}) == 10, "pos not 1..10 unique"
if fails:
    print("\nGATE FAIL:")
    for f in fails:
        print("   ✗", f)
    sys.exit(1)
print(f"\nGATE: ALL {len(SONGS)} PASS "
      f"(SP<=1000·한글0 / 금지선 2겹 0 / 브라켓 독립행·소문자·한글0 / "
      f"제목·novelty·장르 상이 / POV 3-2-3-2)")

if os.environ.get("DRYRUN"):
    print("DRYRUN — DB insert 생략")
    raise SystemExit(0)

import psycopg2
conf = {}
for ln in open(os.path.expanduser('~/.config/leofamily_music/db_sunolanguage.conf')):
    ln = ln.strip()
    if '=' in ln and not ln.startswith('#'):
        k, v = ln.split('=', 1)
        conf[k.strip()] = v.strip()
c = psycopg2.connect(host=conf['DB_HOST'], port=conf.get('DB_PORT', 5432),
                     dbname=conf['DB_NAME'], user=conf['DB_USER'],
                     password=conf.get('DB_PASSWORD', ''))
cur = c.cursor()
cur.execute(f"SELECT COUNT(*) FROM songs WHERE global_id BETWEEN {GID0+1} AND {GID0+len(SONGS)};")
assert cur.fetchone()[0] == 0, "gid range not free!"
gids = []
for s in SONGS:
    gid = GID0 + s["pos"]
    cur.execute("""INSERT INTO songs
      (global_id, source_project, batch, creator, status, title, lyrics,
       style_prompt, genre, genre_group, subgenre, bpm, key_signature, theme,
       album_title, album_concept, lyrics_language, char_count)
      VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING global_id""",
      (gid, 'sunolanguage', BATCH, 'sunolanguage', 'pending_suno', s["title"], s["lyrics"],
       s["sp"], s["genre"], s["genre_group"], s["sub"], s["bpm"], s["key"], THEME,
       ALBUM, f"facet: 들릴 때만 산다(존재=들림) | POV: {s['pov']} | novelty: {s['sound_novelty']}",
       'ko', len(s["sp"])))
    gids.append(cur.fetchone()[0])
c.commit()
print("INSERTED gids:", gids)
