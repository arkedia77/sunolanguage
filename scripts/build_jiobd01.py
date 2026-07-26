#!/usr/bin/env python3
# JIOBD01 — 정지오 29세 생일 앨범: 첼로 관통선(상수) × 10장르 클래식 크로스오버.
# LEO 직접 지시(07-27, 텔레 5692): '지오 내일(07-28) 배치, 콰이어/아카펠라 다 좋아'. kee 확정발주(P0).
# 설계 정본: agent-comm projects/sunomusic/AWARE100_DESIGN.md §2.
#   첼로=상수(지오=첼리스트), 장르=변수(넓은 취향). 정서=축하 밝음 + 성숙한 깊이.
#   생일 날짜 미확인 → 가사·제목에 날짜 숫자 미기재(나이 29/스물아홉만). 콰이어/아카펠라 3곡 배분(1·5·10).
#   10 병렬 전문 서브에이전트 저작 → 게이트 검증.
import os, json, re, psycopg2

THEME = "정지오 29세 생일 — 첼로 관통선(상수) × 10장르 클래식 크로스오버. 축하의 밝음 + 세상의 아름다움·곤란함을 아는 성숙한 깊이"
ALBUM = "스물아홉, 지오 (Twenty-Nine, Jio)"
BATCH = "JIOBD01"
GID0 = 30188  # 다음 가용: 30189~30198 (DB 실측 max sunolang gid<31000 = 30188, 30189+ 공백 확인)

HERE = os.path.dirname(os.path.abspath(__file__))
SONGS = json.load(open(os.path.join(HERE, '..', 'data', 'jiobd', 'JIOBD01_songs.json')))

# --- 게이트 ---
DATE_RX = re.compile(r'\b(19|20)\d{2}\b|\b\d{1,2}\s*월\s*\d{1,2}\s*일|\b\d{1,2}/\d{1,2}\b')
fails = []
for s in SONGS:
    if len(s["sp"]) > 1000: fails.append((s["pos"], "SP>1000", len(s["sp"])))
    if not s.get("lyrics") or "[" not in s["lyrics"]: fails.append((s["pos"], "no [Section]", 0))
    if "cello" not in s["sp"].lower(): fails.append((s["pos"], "no cello in SP", 0))
    dm = DATE_RX.search(s["title"]) or DATE_RX.search(s["lyrics"])
    if dm: fails.append((s["pos"], f"DATE NUMBER '{dm.group()}'", 0))

for s in SONGS:
    flag = "  OVER!" if len(s["sp"]) > 1000 else ""
    print(f"  {BATCH}-{s['pos']:<2} {s['genre_group']:<18} {s['title']:<22} {s['key']:<16} {s['bpm']}BPM  SP={len(s['sp'])}  LYR={len(s['lyrics'])}{flag}")
assert len({s['pos'] for s in SONGS}) == 10, "pos not 1..10 unique"
assert not fails, f"GATE FAIL: {fails}"
print(f"GATE: ALL {len(SONGS)} PASS (SP<=1000 · [Section] tags · cello in SP · no date numbers)")

if os.environ.get("DRYRUN"):
    print("DRYRUN — DB insert 생략"); raise SystemExit(0)

conf = {}
for ln in open(os.path.expanduser('~/.config/leofamily_music/db_sunolanguage.conf')):
    ln = ln.strip()
    if '=' in ln and not ln.startswith('#'):
        k, v = ln.split('=', 1); conf[k.strip()] = v.strip()
c = psycopg2.connect(host=conf['DB_HOST'], port=conf.get('DB_PORT', 5432), dbname=conf['DB_NAME'], user=conf['DB_USER'], password=conf.get('DB_PASSWORD', ''))
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
       ALBUM, f"facet: {s['facet']} | POV: {s['pov']}", 'ko', len(s["sp"])))
    gids.append(cur.fetchone()[0])
c.commit()
print("INSERTED gids:", gids)
cur.execute(f"SELECT global_id,title,genre,bpm,key_signature,status FROM songs WHERE batch='{BATCH}' ORDER BY global_id;")
print("VERIFY:"); [print("  ", r) for r in cur.fetchall()]
c.close()

os.makedirs(os.path.join(HERE, '..', 'data', 'jiobd'), exist_ok=True)
batch = {"batch": BATCH, "album": ALBUM, "line": "sunolanguage", "theme": THEME, "created": "2026-07-27",
  "gid_range": f"{GID0+1}~{GID0+len(SONGS)}",
  "origin": "LEO 직접 지시 07-27(텔레 5692·kimsecretary 라우팅): '지오 내일(07-28) 배치, 콰이어라 들어가는 곡 아카펠라 다 좋아'. kee 확정발주(P0, 불가침 슬롯).",
  "concept": "첼로 관통선(상수, 지오=첼리스트) × 10장르 클래식 크로스오버(필름스코어/재즈/탱고/포크/가스펠/켈틱/보사노바/플라멩코/일렉트로니카/록발라드). 축하+성숙한 깊이. 콰이어/아카펠라 배분=1·5·10. 생일 날짜 미확인→가사·제목 날짜숫자 없음(나이만).",
  "songs": [{"gid": GID0+s["pos"], "id": f"{BATCH}-{s['pos']}", "title": s["title"], "title_en": s["title_en"],
    "genre": s["genre"], "genre_group": s["genre_group"], "facet": s["facet"], "pov": s["pov"],
    "bpm": s["bpm"], "key": s["key"], "time_sig": s["time_sig"], "is_instrumental": False,
    "style_prompt": s["sp"], "sp_length": len(s["sp"]), "lyrics": s["lyrics"]} for s in SONGS]}
json.dump(batch, open(os.path.join(HERE, '..', 'data', 'jiobd', 'JIOBD01_batch.json'), 'w'), ensure_ascii=False, indent=2)
print("batch JSON -> data/jiobd/JIOBD01_batch.json")
