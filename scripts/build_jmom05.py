#!/usr/bin/env python3
# JMOM05 — JMOM03-2 '가스펠 소울'(gid30174) 변주: 남녀 듀엣 + 남자 E키. 같은 가사.
# LEO 정정(07-23): '가스펠버전으로, 공허 말고' → 대상=가스펠 소울(JMOM03-2), 공허(JMOM04) 아님.
#   변경=(1)남녀 듀엣(가스펠 call-and-response) (2)key E major. 가사 단어 JMOM 동일.
# 부수: JMOM04(공허 듀엣, gid30177) 취소 처리(status=canceled) — 잘못된 대상, 생성 전 회수.
import os, json, psycopg2

THEME = "어머니에 대한 미움과 그리움 (어릴적 버림) — 가스펠 소울 남녀 듀엣·E키 변주"
BATCH = "JMOM05"
GID0 = 30177  # 다음 가용: 30178
ALBUM = "가스펠 소울 남녀듀엣 E키 (JMOM03-2 변주)"
CANCEL_GID = 30177  # JMOM04 공허 듀엣 — 잘못된 대상, 취소

SP = "An aching, soul-baring gospel ballad as a male-female duet, blending a dramatic Japanese-style vocal ballad with gospel soul and slow blues. Around 66 BPM in E major, a slow 6/8 with a heavy, anguished, spiritual feel. A powerful, emotive male tenor leads in the E register, pleading and breathy in the verses then erupting into a raw, heart-wrenching, tearful belted chorus with wide vibrato, gospel runs and cracking falsetto; a soulful female voice answers him in call-and-response and soars above in the choruses, the two trading lines and harmonizing in grief. Warm Hammond organ swells, mournful blues electric guitar with bent weeping notes, gospel grand piano, deep upright bass and brushed drums build underneath. A soft sorrowful gospel choir lifts the climaxes. Immense dynamics, from a whispered grief to a cathartic, anguished duet wail. Heartbroken, pleading, soulful and devastating. Timeless gospel-soul duet ballad, blues-drenched and tearful."

# 가사 = JMOM 동일 단어 + 남녀 듀엣 역할태그
LYRICS = """[Male Verse 1]
그 골목 끝에서 손을 놓던 날
네 등은 점점 작아졌어
울지도 못하고 서 있던 아이
아직 거기 그대로 있어

[Female Pre-Chorus]
미워하려 하면 네 얼굴이 흐려지고
잊으려 하면 자꾸 네 목소리가 들려

[Duet Chorus]
엄마, 난 널 미워해 그리고 보고 싶어
이 두 마음이 매일 나를 찢어놔
버린 손인데 왜 아직 따뜻한 것만 같아
원망하다 결국 또 너를 불러
엄마…

[Female Verse 2]
남들 다 부르는 그 말 엄마가
내겐 왜 이렇게 무거운지
거울 속 네 눈을 닮은 나를
지우고 싶어 또 밤을 새워

[Male Pre-Chorus]
미워하려 하면 네 손이 떠오르고
잊으려 하면 자꾸 그 골목이 보여

[Duet Chorus]
엄마, 난 널 미워해 그리고 보고 싶어
이 두 마음이 매일 나를 찢어놔
버린 손인데 왜 아직 따뜻한 것만 같아
원망하다 결국 또 너를 불러
엄마…

[Duet Bridge]
딱 한 번만 물어보고 싶어
왜 나를 두고 갔는지
미움도 그리움도
다 네가 남기고 간 거잖아

[Duet Outro]
엄마, 난 널 미워해 그리고 보고 싶어
돌아오지 않을 걸 알면서도
오늘도 그 골목 끝을 바라봐
원망보다 그리움이 조금 더 커
엄마…"""

TITLE = "그 골목 끝에서 (가스펠 소울 · 남녀 듀엣)"
TITLE_EN = "At the End of That Alley (Gospel Soul · M/F Duet)"
GENRE = "gospel-soul blues duet ballad"
GGROUP = "R&B/Soul"
SUB = "玉置浩二 base × 가스펠 소울/블루스, 남녀 듀엣(call-and-response), 남자 E키(E major)"
BPM = 66
KEY = "E major"

assert len(SP) <= 1000, f"SP over 1000: {len(SP)}"
print(f"{BATCH}-1  {TITLE}  {KEY} {BPM}BPM 6/8  듀엣  SP={len(SP)}  LYR={len(LYRICS)}  PASS")

if os.environ.get("DRYRUN"):
    print("DRYRUN — DB insert 생략"); raise SystemExit(0)

conf={}
for ln in open(os.path.expanduser('~/.config/leofamily_music/db_sunolanguage.conf')):
    ln=ln.strip()
    if '=' in ln and not ln.startswith('#'):
        k,v=ln.split('=',1); conf[k.strip()]=v.strip()
c=psycopg2.connect(host=conf['DB_HOST'],port=conf.get('DB_PORT',5432),dbname=conf['DB_NAME'],user=conf['DB_USER'],password=conf.get('DB_PASSWORD',''))
cur=c.cursor()
# --- JMOM04 공허 듀엣 취소 (잘못된 대상) ---
cur.execute("UPDATE songs SET status='canceled' WHERE global_id=%s AND status='pending_suno' RETURNING global_id;", (CANCEL_GID,))
canc=cur.fetchone()
print("CANCELED (JMOM04 공허 듀엣):", canc[0] if canc else "이미 생성됨/없음 — 확인필요")
# --- JMOM05 삽입 ---
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
   ALBUM, "JMOM03-2 '가스펠 소울' 변주: 남녀 듀엣(가스펠 call-and-response)+남자 E키(E major). 가사 JMOM 동일, 역할태그 추가. LEO 정정('가스펠버전으로, 공허 말고').", 'ko', len(SP)))
print("INSERTED gid:", cur.fetchone()[0])
c.commit()
cur.execute("SELECT global_id,title,genre,bpm,key_signature,status FROM songs WHERE global_id IN (%s,%s) ORDER BY global_id;", (CANCEL_GID, gid))
print("VERIFY:"); [print("  ",r) for r in cur.fetchall()]
c.close()

os.makedirs('data/dualrun', exist_ok=True)
batch={"batch":BATCH,"line":"sunolanguage","theme":THEME,"created":"2026-07-23",
 "gid":gid,"title":TITLE,"title_en":TITLE_EN,"genre":GENRE,"genre_group":GGROUP,
 "bpm":BPM,"key":KEY,"time_sig":"6/8","is_instrumental":False,"vocal":"male-female duet, gospel call-and-response (남자 E키/E major)",
 "origin":"LEO 정정 07-23: '가스펠버전으로, 공허 말고' — 가스펠 소울(JMOM03-2)을 남녀 듀엣·남자 E키로. JMOM04(공허 듀엣) 취소.",
 "based_on":"JMOM03-2 '가스펠 소울' gid30174 (gospel-soul blues ballad, B-flat major). 변경=남녀 듀엣 역할태그+key E major.",
 "canceled":"JMOM04 gid30177 (공허 듀엣) — 잘못된 대상, 생성 전 취소.",
 "style_prompt":SP,"sp_length":len(SP),"lyrics":LYRICS}
json.dump(batch, open('data/dualrun/JMOM05_batch.json','w'), ensure_ascii=False, indent=2)
print("batch JSON -> data/dualrun/JMOM05_batch.json")
