#!/usr/bin/env python3
# JMOM01 — 존 메이어(네오소울 블루스) 톤 보컬 발라드 1곡, dual-run(Suno + Google Lyria)
# LEO 직지시(07-23): 존메이어 느낌 진행·연주 SP → Suno 생성 + leomusic3 경유 Lyria 재생성(dual-run).
#   가사 주제 = 어머니에 대한 미움과 그리움 (어릴적 어머니에게 버림받은 것에 대한 양가감정).
import os, json, psycopg2

THEME = "어머니에 대한 미움과 그리움 (어릴적 버림받음) — 존메이어 네오소울 블루스 발라드"
BATCH = "JMOM01"
GID0 = 30170  # 다음 가용: 30171
ALBUM = "존메이어 톤 dual-run"

SP = "Soulful neo-soul blues ballad, modern singer-songwriter guitar, warm, intimate and aching. Slow 12/8 groove at 68 BPM in B-flat major, relaxed swung-triplet pocket. A warm, clean Fender Stratocaster leads with light tube overdrive and spring reverb, played fingerstyle with hybrid picking: string bends, wide slow-hand vibrato, sliding double-stops and blues licks answering the voice between lines. Lush neo-soul voicings carry the progression, extended major-9 and dominant-13 shapes through ii-V-I motion with borrowed minor-iv color and chromatic passing chords. A tender, breathy male vocal, smoky and emotional, close-mic'd and conversational in the verses, rising into a raw, pleading chorus with soulful runs and soft falsetto. A tight in-the-pocket trio backs it: soft behind-the-beat drums, round warm bass on the kick, subtle Rhodes comping. It builds from sparse, whispered verses into a soaring guitar-and-voice climax. Late-night, confessional, heartbroken, organic and human."

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
TITLE_EN = "At the End of That Alley"
GENRE = "neo-soul blues ballad (John Mayer style)"
GGROUP = "R&B/Soul"
SUB = "존메이어 톤 네오소울 블루스 발라드, 남성 소울 보컬"
BPM = 68
KEY = "B-flat major"

assert len(SP) <= 1000, f"SP over 1000: {len(SP)}"
print(f"{BATCH}-1  {TITLE}  {KEY} {BPM}BPM  SP={len(SP)}  LYR={len(LYRICS)}  PASS")

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
   ALBUM, "dual-run(Suno+Lyria) 존메이어 톤·모정 양가감정", 'ko', len(SP)))
print("INSERTED gid:", cur.fetchone()[0])
c.commit()
cur.execute("SELECT global_id,title,genre,bpm,key_signature,status,(lyrics IS NOT NULL) FROM songs WHERE batch=%s;", (BATCH,))
print("VERIFY:", cur.fetchone())
c.close()

os.makedirs('data/dualrun', exist_ok=True)
batch={"batch":BATCH,"line":"sunolanguage","theme":THEME,"created":"2026-07-23",
 "gid":gid,"title":TITLE,"title_en":TITLE_EN,"genre":GENRE,"genre_group":GGROUP,
 "bpm":BPM,"key":KEY,"is_instrumental":False,
 "origin":"LEO 직지시 07-23: 존메이어 느낌 SP→Suno 생성 + leomusic3 경유 Lyria dual-run 재생성. 가사=어머니 미움·그리움(어릴적 버림).",
 "dual_run":{"suno":"sunomusic 생성", "lyria":"leomusic3 경유 Google Lyria 동일가사 명시투입 재생성"},
 "style_prompt":SP,"sp_length":len(SP),"lyrics":LYRICS}
json.dump(batch, open('data/dualrun/JMOM01_batch.json','w'), ensure_ascii=False, indent=2)
print("batch JSON -> data/dualrun/JMOM01_batch.json")
