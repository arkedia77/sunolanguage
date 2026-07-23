#!/usr/bin/env python3
# JMOM02 — JMOM01 '그 골목 끝에서' 재편성(玉置浩二/Tamaki Koji·안전지대 분위기), dual-run(Suno+Lyria)
# LEO 직지시(07-23): 타마키코지(玉置浩二) 분위기로 방금 곡을 다시. 나머지(가사·주제·제목)는 그대로.
#   변경=SP(편성/보컬/장르 분위기)만. 가사 JMOM01과 동일.
import os, json, psycopg2

THEME = "어머니에 대한 미움과 그리움 (어릴적 버림받음) — 玉置浩二(안전지대) 풍 대편성 J-발라드"
BATCH = "JMOM02"
GID0 = 30171  # 다음 가용: 30172
ALBUM = "타마키코지 톤 dual-run (JMOM01 재편성)"

SP = "A grand, deeply emotional Japanese ballad in a classic Showa-era J-ballad and city-pop ballad style, cinematic and heartbreaking. Slow, spacious tempo around 66 BPM in B-flat major, a 6/8 feel with a stately, swelling sway. Lush orchestral arrangement: sweeping legato string section, warm grand piano leading the harmony, soft sustained synth pads, gentle rounded electric bass, brushed drums that build with the song, and a distant, tender electric guitar with warm chorus. A powerful, soul-stirring male tenor leads, intimate, breathy and almost whispered in the verses, then blooming into soaring, passionate belted climaxes with rich, wide vibrato and delicate falsetto touches. Immense dynamic range, from a near-a-cappella hush to a grand, tearful crescendo backed by full strings. Sincere, sorrowful, nostalgic and overwhelming, the arrangement breathing and rising with the emotion. Timeless Japanese ballad grandeur, orchestral swells, heartfelt and dramatic."

# 가사 = JMOM01 동일 (나머지는 그대로)
LYRICS = """[Verse 1]
그 골목 끝에서 손을 놓던 날
네 등은 점점 작아졌어
울지도 못하고 서 있던 아이
아직 거기 그대로 있어

[Pre-Chorus]
미워하려 하면 네 얼굴이 흐려지고
잊으려 하면 자꾸 네 목소리가 들려

[Chorus]
엄마, 난 널 미워해 그리고 보고 싶어
이 두 마음이 매일 나를 찢어놔
버린 손인데 왜 아직 따뜻한 것만 같아
원망하다 결국 또 너를 불러
엄마…

[Verse 2]
남들 다 부르는 그 말 엄마가
내겐 왜 이렇게 무거운지
거울 속 네 눈을 닮은 나를
지우고 싶어 또 밤을 새워

[Pre-Chorus]
미워하려 하면 네 손이 떠오르고
잊으려 하면 자꾸 그 골목이 보여

[Chorus]
엄마, 난 널 미워해 그리고 보고 싶어
이 두 마음이 매일 나를 찢어놔
버린 손인데 왜 아직 따뜻한 것만 같아
원망하다 결국 또 너를 불러
엄마…

[Bridge]
딱 한 번만 물어보고 싶어
왜 나를 두고 갔는지
미움도 그리움도
다 네가 남기고 간 거잖아

[Outro]
엄마, 난 널 미워해 그리고 보고 싶어
돌아오지 않을 걸 알면서도
오늘도 그 골목 끝을 바라봐
원망보다 그리움이 조금 더 커
엄마…"""

TITLE = "그 골목 끝에서"
TITLE_EN = "At the End of That Alley (Tamaki Koji ver.)"
GENRE = "dramatic Japanese ballad (Showa J-ballad / city-pop ballad, Tamaki Koji style)"
GGROUP = "Ballad/J-Pop"
SUB = "玉置浩二(안전지대) 풍 대편성 J-발라드, 웅장한 스트링·감정 열창 남성 테너"
BPM = 66
KEY = "B-flat major"

assert len(SP) <= 1000, f"SP over 1000: {len(SP)}"
print(f"{BATCH}-1  {TITLE}  {KEY} {BPM}BPM 6/8  SP={len(SP)}  LYR={len(LYRICS)}  PASS")

if os.environ.get("DRYRUN"):
    print("DRYRUN — DB insert 생략"); raise SystemExit(0)

conf={}
for ln in open(os.path.expanduser('~/.config/leofamily_music/db_sunolanguage.conf')):
    ln=ln.strip()
    if '=' in ln and not ln.startswith('#'):
        k,v=ln.split('=',1); conf[k.strip()]=v.strip()
c=psycopg2.connect(host=conf['DB_HOST'],port=conf.get('DB_PORT',5432),dbname=conf['DB_NAME'],user=conf['DB_USER'],password=conf.get('DB_PASSWORD',''))
cur=c.cursor()
gid=GID0+1
cur.execute("SELECT COUNT(*) FROM songs WHERE global_id=%s;", (gid,))
assert cur.fetchone()[0]==0, "gid not free!"
cur.execute("""INSERT INTO songs
  (global_id, source_project, batch, creator, status, title, lyrics,
   style_prompt, genre, genre_group, subgenre, bpm, key_signature, theme,
   album_title, album_concept, lyrics_language, char_count)
  VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING global_id""",
  (gid,'sunolanguage',BATCH,'sunolanguage','pending_suno', TITLE, LYRICS,
   SP, GENRE, GGROUP, SUB, BPM, KEY, THEME,
   ALBUM, "JMOM01 동일가사 재편성=玉置浩二/안전지대 풍 대편성 J-발라드. dual-run(Suno+Lyria).", 'ko', len(SP)))
print("INSERTED gid:", cur.fetchone()[0])
c.commit()
cur.execute("SELECT global_id,title,genre,bpm,key_signature,status,(lyrics IS NOT NULL) FROM songs WHERE batch=%s;", (BATCH,))
print("VERIFY:", cur.fetchone())
c.close()

os.makedirs('data/dualrun', exist_ok=True)
batch={"batch":BATCH,"line":"sunolanguage","theme":THEME,"created":"2026-07-23",
 "gid":gid,"title":TITLE,"title_en":TITLE_EN,"genre":GENRE,"genre_group":GGROUP,
 "bpm":BPM,"key":KEY,"time_sig":"6/8","is_instrumental":False,
 "origin":"LEO 직지시 07-23: 타마키코지(玉置浩二) 분위기로 JMOM01 곡을 다시. 나머지(가사·주제·제목) 그대로 — SP 편성/보컬만 변경.",
 "artist_ref":"玉置浩二 (Kōji Tamaki), 안전지대(Anzen Chitai) 프론트맨 — 압도적 감정 열창·풍부한 비브라토·넓은 다이내믹·웅장한 오케스트라 발라드. SP엔 실명 미기재(스타일만 서술).",
 "based_on":"JMOM01 gid30171 (동일가사)",
 "dual_run":{"suno":"sunomusic 생성","lyria":"leomusic3 경유 Google Lyria 동일가사 명시투입 재생성"},
 "style_prompt":SP,"sp_length":len(SP),"lyrics":LYRICS}
json.dump(batch, open('data/dualrun/JMOM02_batch.json','w'), ensure_ascii=False, indent=2)
print("batch JSON -> data/dualrun/JMOM02_batch.json")
