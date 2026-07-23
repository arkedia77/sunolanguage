#!/usr/bin/env python3
# JMOM03 — 타마키코지 base + 슬픔어휘 변주 + 장르블렌드 4곡, 같은 가사(JMOM01/02 동일)
# LEO 직지시(07-23): 타마키코지 기본으로 유사 슬픔 단어 섞고 장르 섞어 4곡을 같은 가사로 생성.
#   base=玉置浩二 풍 감정 발라드(테너·와이드 비브라토·넓은 다이내믹) 유지, 트랙별로 장르 블렌드 + sorrow 어휘 변주.
import os, json, psycopg2

THEME = "어머니에 대한 미움과 그리움 (어릴적 버림) — 玉置浩二 base × 슬픔어휘·장르 블렌드 4변주"
BATCH = "JMOM03"
GID0 = 30172  # 다음 가용: 30173~30176
ALBUM = "타마키코지 base 슬픔·장르 블렌드 4변주 (JMOM 동일가사)"

# 가사 = JMOM01/02 동일 (같은 가사로 생성)
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

SONGS = [
 {"pos":1,"title":"그 골목 끝에서 (오케스트라 애가)","title_en":"At the End of That Alley (Orchestral Elegy)",
  "genre":"cinematic orchestral J-ballad","genre_group":"Ballad/Orchestral","bpm":64,"key":"B-flat minor","time_sig":"6/8",
  "blend":"玉置浩二 base × 시네마틱 오케스트라","sorrow_words":"mournful, sorrowful, grief-stricken, desolate, elegiac, tearful",
  "sp":"A grand, mournful cinematic ballad blending a Showa-era Japanese vocal ballad with sweeping film-score orchestration. Slow and tearful, around 64 BPM in a B-flat minor tonality, a 6/8 swell. A powerful male tenor, breathy and trembling in the verses, rises into a heartbroken, grief-stricken belted climax with rich wide vibrato and aching falsetto. Around it, a full orchestra weeps: sorrowful legato strings, a mournful solo cello, distant French horn, timpani swells and a lone grand piano. Choir-like pads sigh underneath. Immense dynamic range, from a fragile near-silence to an overwhelming, tearful crescendo. Sorrowful, desolate and elegiac, like a farewell that never ends. Timeless orchestral J-ballad grandeur, weeping strings, cinematic and devastating."},
 {"pos":2,"title":"그 골목 끝에서 (가스펠 소울)","title_en":"At the End of That Alley (Gospel Soul)",
  "genre":"gospel-soul blues ballad","genre_group":"R&B/Soul","bpm":66,"key":"B-flat major","time_sig":"6/8",
  "blend":"玉置浩二 base × 가스펠 소울/블루스","sorrow_words":"aching, heart-wrenching, anguished, pleading, cathartic",
  "sp":"An aching, soul-baring ballad blending a dramatic Japanese vocal ballad with gospel soul and slow blues. Around 66 BPM in B-flat, a slow 6/8 with a heavy, anguished feel. A powerful male tenor pleads and moans, intimate and breathy in the verses then erupting into a raw, heart-wrenching, tearful belted chorus with wide vibrato, gospel runs and cracking falsetto. Warm Hammond organ swells, mournful blues electric guitar with bent, weeping notes, gospel grand piano, deep upright bass and brushed drums build underneath. A soft, sorrowful gospel choir answers in the climaxes. Immense dynamics, from a whispered grief to a cathartic, anguished wail. Heartbroken, pleading, soulful and devastating. Timeless soul-gospel ballad, blues-drenched, tearful."},
 {"pos":3,"title":"그 골목 끝에서 (한 恨)","title_en":"At the End of That Alley (Han Lament)",
  "genre":"enka / Korean traditional 'han' ballad","genre_group":"Ballad/Traditional","bpm":62,"key":"B-flat minor","time_sig":"6/8",
  "blend":"玉置浩二 base × 엔카/한국 전통 한(恨)","sorrow_words":"plaintive, forlorn, desolate, yearning, inconsolable, haunting",
  "sp":"A plaintive, sorrow-steeped ballad blending a dramatic Japanese vocal ballad with the aching 'han' of Korean and enka traditional balladry. Slow and forlorn, around 62 BPM in a B-flat minor tonality, a rubato 6/8. A powerful male tenor, deeply mournful, trembles with wide traditional vibrato and long yearning bends, hushed and desolate in the verses then soaring into an anguished, tearful cry. Weeping strings and a lone piano carry the harmony, with a distant, plaintive traditional wind and soft sustained pads, sparse and spacious. Deep aching restraint that breaks into overwhelming grief. Forlorn, desolate, yearning and inconsolable, the sorrow of loss and longing. Timeless lament, traditional han balladry, tearful and haunting."},
 {"pos":4,"title":"그 골목 끝에서 (공허)","title_en":"At the End of That Alley (Hollow)",
  "genre":"atmospheric alt-R&B / cinematic pop ballad","genre_group":"Alt-R&B/Cinematic","bpm":68,"key":"B-flat minor","time_sig":"6/8",
  "blend":"玉置浩二 base × 앰비언트 얼트R&B/시네마틱 팝","sorrow_words":"desolate, melancholic, wistful, hollow, numb, aching",
  "sp":"A desolate, melancholic modern ballad blending a dramatic Japanese vocal ballad with atmospheric alt-R&B and cinematic pop. Slow and hollow, around 68 BPM in a B-flat minor tonality, a spacious 6/8. A powerful male tenor, numb and breathy in the verses, swells into a wistful, heartbroken, tearful chorus with wide vibrato and fragile falsetto. Around it: airy reverb-drenched electric piano, a deep sub bass, sparse soft cinematic drums, glassy pads and distant weeping strings that bloom in the climax, with faint vinyl-like texture. Vast empty space and immense dynamics, from a lonely hush to a soaring, sorrowful crescendo. Desolate, melancholic, wistful and aching, modern grief in a wide cinematic haze. Atmospheric ballad, heartbroken and beautiful."},
]

over=[s for s in SONGS if len(s["sp"])>1000]
for s in SONGS:
    print(f"  {BATCH}-{s['pos']} {s['genre_group']:<20} {s['key']:<13} {s['bpm']}BPM  SP={len(s['sp'])}  LYR={len(LYRICS)}{'  OVER!' if len(s['sp'])>1000 else ''}")
assert not over, f"SP over: {[s['pos'] for s in over]}"
assert len({s['pos'] for s in SONGS})==4
print(f"SP gate: ALL {len(SONGS)} PASS (<=1000), 가사 동일 {len(LYRICS)}자")

if os.environ.get("DRYRUN"):
    print("DRYRUN — DB insert 생략"); raise SystemExit(0)

conf={}
for ln in open(os.path.expanduser('~/.config/leofamily_music/db_sunolanguage.conf')):
    ln=ln.strip()
    if '=' in ln and not ln.startswith('#'):
        k,v=ln.split('=',1); conf[k.strip()]=v.strip()
c=psycopg2.connect(host=conf['DB_HOST'],port=conf.get('DB_PORT',5432),dbname=conf['DB_NAME'],user=conf['DB_USER'],password=conf.get('DB_PASSWORD',''))
cur=c.cursor()
cur.execute(f"SELECT COUNT(*) FROM songs WHERE global_id BETWEEN {GID0+1} AND {GID0+len(SONGS)};")
assert cur.fetchone()[0]==0, "gid range not free!"
gids=[]
for s in SONGS:
    gid=GID0+s["pos"]
    cur.execute("""INSERT INTO songs
      (global_id, source_project, batch, creator, status, title, lyrics,
       style_prompt, genre, genre_group, subgenre, bpm, key_signature, theme,
       album_title, album_concept, lyrics_language, char_count)
      VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING global_id""",
      (gid,'sunolanguage',BATCH,'sunolanguage','pending_suno', s["title"], LYRICS,
       s["sp"], s["genre"], s["genre_group"], s["blend"], s["bpm"], s["key"], THEME,
       ALBUM, f"玉置浩二 base × {s['blend']} / sorrow: {s['sorrow_words']}", 'ko', len(s["sp"])))
    gids.append(cur.fetchone()[0])
c.commit()
print("INSERTED gids:", gids)
cur.execute(f"SELECT global_id,title,genre,bpm,key_signature,status FROM songs WHERE batch='{BATCH}' ORDER BY global_id;")
print("VERIFY:"); [print("  ",r) for r in cur.fetchall()]
c.close()

os.makedirs('data/dualrun', exist_ok=True)
batch={"batch":BATCH,"line":"sunolanguage","theme":THEME,"created":"2026-07-23",
 "gid_range":f"{GID0+1}~{GID0+len(SONGS)}","album":ALBUM,
 "origin":"LEO 직지시 07-23: 타마키코지 기본으로 유사 슬픔 단어 섞고 장르 섞어 4곡을 같은 가사로. base=玉置浩二 감정 발라드 유지, 트랙별 장르블렌드+sorrow 어휘 변주.",
 "same_lyrics_as":"JMOM01/02 (gid30171/30172) 동일가사",
 "design_note":"통제변수=가사·玉置浩二 감정보컬 base. 조작변수=장르 블렌드 + sorrow 어휘 세트. 4변주=오케스트라애가/가스펠소울/한(恨)엔카/앰비언트얼트R&B.",
 "songs":[{"gid":GID0+s["pos"],"id":f"{BATCH}-{s['pos']}","title":s["title"],"title_en":s["title_en"],
   "genre":s["genre"],"genre_group":s["genre_group"],"blend":s["blend"],"sorrow_words":s["sorrow_words"],
   "bpm":s["bpm"],"key":s["key"],"time_sig":s["time_sig"],"is_instrumental":False,
   "style_prompt":s["sp"],"sp_length":len(s["sp"])} for s in SONGS],
 "lyrics":LYRICS}
json.dump(batch, open('data/dualrun/JMOM03_batch.json','w'), ensure_ascii=False, indent=2)
print("batch JSON -> data/dualrun/JMOM03_batch.json")
