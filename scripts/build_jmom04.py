#!/usr/bin/env python3
# JMOM04 — JMOM03-4 '공허'(gid30176) 변주: 남녀 듀엣 + 남자 E키. 같은 가사.
# LEO 직지시(07-23): 마지막곡(공허)을 남녀 듀엣, 남자 E키로 바꿔서. 원본 보존·새 gid.
#   base=공허(玉置浩二 base × 앰비언트 얼트R&B/시네마틱 팝, desolate/melancholic/hollow).
#   변경=(1)남녀 듀엣 보컬역할 태그 (2)key E minor. 가사 단어는 JMOM 동일.
import os, json, psycopg2

THEME = "어머니에 대한 미움과 그리움 (어릴적 버림) — 공허(앰비언트 얼트R&B) 남녀 듀엣·E키 변주"
BATCH = "JMOM04"
GID0 = 30176  # 다음 가용: 30177
ALBUM = "공허 남녀듀엣 E키 (JMOM03-4 변주)"

SP = "A desolate, melancholic modern ballad as a male-female duet, blending a dramatic Japanese-style vocal ballad with atmospheric alt-R&B and cinematic pop. Slow and hollow, around 68 BPM in E minor, a spacious 6/8. Two voices intertwine: a powerful, emotive male tenor leads in the E register, numb and breathy in the verses then swelling into a wistful, heartbroken, tearful climax with wide vibrato and fragile falsetto; a tender female vocal answers and harmonizes above him, soft and aching, the two trading lines and blooming together in the choruses. Around them: airy reverb-drenched electric piano, a deep sub bass, sparse soft cinematic drums, glassy pads and distant weeping strings that bloom in the climax, with faint vinyl-like texture. Vast empty space and immense dynamics, from a lonely hush to a soaring, sorrowful duet crescendo. Desolate, melancholic, wistful and aching, shared grief in a wide cinematic haze. Atmospheric duet ballad, heartbroken and beautiful."

# 가사 = JMOM 동일 단어. 남녀 듀엣 보컬역할 태그만 추가(단어 불변).
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

TITLE = "그 골목 끝에서 (공허 · 남녀 듀엣)"
TITLE_EN = "At the End of That Alley (Hollow · M/F Duet)"
GENRE = "atmospheric alt-R&B / cinematic pop duet ballad"
GGROUP = "Alt-R&B/Cinematic"
SUB = "玉置浩二 base × 앰비언트 얼트R&B, 남녀 듀엣, 남자 E키(E minor)"
BPM = 68
KEY = "E minor"

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
   ALBUM, "JMOM03-4 '공허' 변주: 남녀 듀엣+남자 E키(E minor). 가사 단어 JMOM 동일, 보컬역할 태그만 추가.", 'ko', len(SP)))
print("INSERTED gid:", cur.fetchone()[0])
c.commit()
cur.execute("SELECT global_id,title,genre,bpm,key_signature,status,(lyrics IS NOT NULL) FROM songs WHERE batch=%s;", (BATCH,))
print("VERIFY:", cur.fetchone())
c.close()

os.makedirs('data/dualrun', exist_ok=True)
batch={"batch":BATCH,"line":"sunolanguage","theme":THEME,"created":"2026-07-23",
 "gid":gid,"title":TITLE,"title_en":TITLE_EN,"genre":GENRE,"genre_group":GGROUP,
 "bpm":BPM,"key":KEY,"time_sig":"6/8","is_instrumental":False,"vocal":"male-female duet (남자 E키/E minor)",
 "origin":"LEO 직지시 07-23: 마지막곡(JMOM03-4 공허)을 남녀 듀엣, 남자 E키로 바꿔서. 원본 gid30176 보존, 새 gid30177.",
 "based_on":"JMOM03-4 '공허' gid30176 (atmospheric alt-R&B). 변경=남녀 듀엣 역할태그+key E minor(원 B-flat minor).",
 "style_prompt":SP,"sp_length":len(SP),"lyrics":LYRICS}
json.dump(batch, open('data/dualrun/JMOM04_batch.json','w'), ensure_ascii=False, indent=2)
print("batch JSON -> data/dualrun/JMOM04_batch.json")
