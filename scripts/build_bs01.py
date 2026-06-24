#!/usr/bin/env python3
# BS01 — 신부 테마 첼로4중주 정식배치 10곡 빌드+적재+핸드오프
import os, json, datetime, psycopg2

SONGS = [
 {"pos":1,"title":"청혼","title_en":"The Proposal","key":"F major","bpm":72,"time_sig":"4/4",
  "sub":"Neoclassical chamber — tender proposal",
  "sp":"Neoclassical chamber instrumental for four cellos only — no other instruments. F major, 72 BPM, 4/4. Tender and hopeful, a quiet proposal. Cello 1 (highest) poses a rising melodic question in warm legato with gentle vibrato, the phrase lifting at its end like a held breath; Cello 2 echoes the motif a third below, hesitant then warmer; Cello 3 sustains soft inner harmony with slow arco swells; Cello 4 (lowest) answers from beneath with deep, reassuring pizzicato on the downbeats. The piece begins hushed and uncertain, the question repeating and growing braver, until all four cellos converge in a warm, affirming resolution — a yes blooming in four-part harmony. A gentle ritardando settles on a glowing major chord. Intimate, sincere, cinematic. Natural concert-hall reverb."},
 {"pos":2,"title":"첫 드레스","title_en":"The First Dress","key":"A major","bpm":88,"time_sig":"3/4",
  "sub":"Neoclassical chamber — light waltz",
  "sp":"Neoclassical chamber instrumental for four cellos only — no other instruments. A major, 88 BPM, a light 3/4 waltz. Delicate and shimmering, the glow of a first wedding dress. Cello 1 (highest) dances a graceful, lilting melody in airy spiccato and bright pizzicato; Cello 2 trades playful pizzicato sparks, like fabric catching light; Cello 3 brushes soft sustained harmony beneath; Cello 4 (lowest) keeps a buoyant pizzicato waltz pulse on beat one. The texture is feather-light and translucent, the cellos passing the melody hand to hand in quick counterpoint, with occasional arco swells lifting into brief radiant phrases. A twirling accelerando leads to a bright, smiling cadence. Tender, joyful, weightless. Natural concert-hall reverb."},
 {"pos":3,"title":"어머니의 손","title_en":"Mother's Hands","key":"D minor","bpm":60,"time_sig":"4/4",
  "sub":"Neoclassical chamber — bittersweet, rubato",
  "sp":"Neoclassical chamber instrumental for four cellos only — no other instruments. D minor, 60 BPM, 4/4, with rubato. Nostalgic and bittersweet — a mother's hands preparing her daughter. Cello 1 (highest) sings a tender, aching melody in long legato with deep expressive vibrato, phrasing freely with the breath, not the beat; Cello 2 weaves a sighing countermelody a sixth below; Cello 3 holds warm sustained harmony, swelling and receding like memory; Cello 4 (lowest) anchors with slow, sorrowful arco pedal tones. The piece moves quietly and intimately, the melody folding back on itself, gathering warmth until a single major chord opens like forgiveness near the end. A soft decrescendo into stillness. Warm, tearful, loving. Natural concert-hall reverb."},
 {"pos":4,"title":"결혼식 전야","title_en":"Eve of the Wedding","key":"B minor","bpm":66,"time_sig":"6/8",
  "sub":"Neoclassical chamber — restless 6/8",
  "sp":"Neoclassical chamber instrumental for four cellos only — no other instruments. B minor, 66 BPM, a flowing 6/8. Restless anticipation — the sleepless night before. Cello 1 (highest) traces an anxious, searching melody that rises and falls, never quite settling; Cello 2 shadows it in close counterpoint, a step behind; Cello 3 shimmers with soft tremolo, an undercurrent of nerves; Cello 4 (lowest) paces with a quiet, repeating pizzicato ostinato like footsteps in the dark. Tension gathers in layered tremolo and rising lines, then dissolves: the tremolo calms, the melody softens, and the four cellos breathe out together into a hushed, hopeful B major glow at dawn. Tender, suspenseful, resolving. Natural concert-hall reverb."},
 {"pos":5,"title":"신부 입장","title_en":"The Bride Enters","key":"D major","bpm":76,"time_sig":"3/4",
  "sub":"Neoclassical chamber — processional centerpiece",
  "sp":"Neoclassical chamber instrumental for four cellos only — no other instruments. D major, 76 BPM, a stately 3/4. Radiant and ceremonial — the bride's entrance in summer light. Cello 1 (highest) carries a soaring, noble processional melody in singing legato with warm vibrato; Cello 2 weaves a tender countermelody a third below; Cello 3 fills the inner harmony with sustained arco swells; Cello 4 (lowest) walks a deep, measured pizzicato that turns to long pedal tones. The piece opens intimate and hushed — solo Cello 1 over soft pizzicato — and builds through layered counterpoint to a full-bodied, radiant climax where all four cellos bloom in rich four-part harmony with double stops, like a bride stepping into the light. A warm decrescendo settles on a glowing final chord. Romantic, majestic, cinematic. Natural concert-hall reverb."},
 {"pos":6,"title":"서약","title_en":"The Vow","key":"G major","bpm":58,"time_sig":"4/4",
  "sub":"Neoclassical chamber — muted, sacred",
  "sp":"Neoclassical chamber instrumental for four cellos only — no other instruments. G major, 58 BPM, 4/4. Solemn and intimate — the exchange of vows. The four cellos play con sordino, muted and hushed, with long sustained legato lines. Cello 1 (highest) speaks a simple, reverent melody, almost spoken in its restraint; Cello 2 answers in gentle imitation, the two voices promising back and forth; Cello 3 holds a warm sustained pedal of inner harmony; Cello 4 (lowest) grounds the chord with deep, still bowed notes. The texture is sacred and unhurried, the harmony deepening note by note, until the mutes lift for one swelling, radiant phrase — a sealed promise — before returning to hushed stillness on a serene final chord. Tender, sacred, profound. Natural concert-hall reverb."},
 {"pos":7,"title":"첫 춤","title_en":"First Dance","key":"E-flat major","bpm":100,"time_sig":"3/4",
  "sub":"Neoclassical chamber — romantic waltz",
  "sp":"Neoclassical chamber instrumental for four cellos only — no other instruments. E-flat major, 100 BPM, a graceful 3/4 waltz. Joyful and flowing — the newlyweds' first dance. Cello 1 (highest) sings a sweeping, romantic waltz melody in warm legato with expressive rubato at the phrase ends; Cello 2 adds a turning countermelody and rich double stops; Cello 3 sustains a lilting harmonic cushion; Cello 4 (lowest) keeps a warm, dancing pizzicato on beat one with arco swells into each phrase. The cellos sweep and turn together, the melody passing between voices in elegant counterpoint, rising to a soaring, whirling climax before easing into a tender close. Romantic, elegant, radiant. Natural concert-hall reverb."},
 {"pos":8,"title":"아버지께","title_en":"To My Father","key":"A minor to C major","bpm":64,"time_sig":"4/4",
  "sub":"Neoclassical chamber — farewell, modulating",
  "sp":"Neoclassical chamber instrumental for four cellos only — no other instruments. A minor moving to C major, 64 BPM, 4/4, with rubato. A bittersweet farewell — a daughter and her father. Cello 1 (highest) sings a deeply emotional melody in long legato with aching vibrato; Cello 2 answers as a second voice, warm and low, like a father's reply; Cello 3 holds sustained harmony that swells with feeling; Cello 4 (lowest) anchors with slow, tender pedal tones. The piece begins in sorrowful A minor, the two melodic cellos in intimate dialogue, grief and gratitude entwined, then modulates warmly into C major as the harmony brightens — letting go with love. A gentle ritardando rests on a warm, grateful chord. Tearful, tender, redemptive. Natural concert-hall reverb."},
 {"pos":9,"title":"한여름의 빛","title_en":"Midsummer Light","key":"E major","bpm":84,"time_sig":"4/4",
  "sub":"Neoclassical chamber — radiant celebration",
  "sp":"Neoclassical chamber instrumental for four cellos only — no other instruments. E major, 84 BPM, 4/4. Radiant and warm — the golden glow of a midsummer celebration. Cello 1 (highest) sings a bright, generous melody in full singing legato with warm vibrato; Cello 2 weaves a sunlit countermelody and shimmering double stops; Cello 3 fills lush sustained harmony with arco swells; Cello 4 (lowest) drives a warm, rolling pizzicato that lifts the whole texture. The four cellos glow together in rich, open four-part harmony, the melody soaring over a warm, dancing foundation, building to a luminous, full-hearted climax like summer light over a celebration. A warm, beaming cadence. Joyful, radiant, expansive. Natural concert-hall reverb."},
 {"pos":10,"title":"새로운 길","title_en":"The New Road","key":"C major","bpm":80,"time_sig":"4/4",
  "sub":"Neoclassical chamber — hopeful departure",
  "sp":"Neoclassical chamber instrumental for four cellos only — no other instruments. C major, 80 BPM, 4/4. Hopeful and forward-moving — setting out on a new life together. Cello 1 (highest) sings a warm, optimistic melody that keeps reaching forward in flowing legato; Cello 2 adds an encouraging countermelody a third below; Cello 3 sustains bright inner harmony with gentle arco swells; Cello 4 (lowest) walks a steady, striding pizzicato like footsteps on an open road. The piece moves with gentle momentum, the melody opening outward and gaining warmth, the four cellos gathering into a full, glowing four-part harmony that resolves with quiet confidence — a door opening to the future. A warm, settled final chord. Hopeful, tender, uplifting. Natural concert-hall reverb."},
]

# --- validate SP length ---
bad=[s for s in SONGS if len(s["sp"])>1000]
for s in SONGS:
    print(f"  BS01-{s['pos']:<2} {s['title']:<8} {s['key']:<20} {s['bpm']}BPM {s['time_sig']:<4} SP={len(s['sp'])}{'  OVER!' if len(s['sp'])>1000 else ''}")
assert not bad, f"SP over 1000: {[s['pos'] for s in bad]}"
print("SP gate: ALL PASS (<=1000)")

# --- DB insert gid 30121-30130 ---
conf={}
for ln in open(os.path.expanduser('~/.config/leofamily_music/db_sunolanguage.conf')):
    ln=ln.strip()
    if '=' in ln and not ln.startswith('#'):
        k,v=ln.split('=',1); conf[k.strip()]=v.strip()
c=psycopg2.connect(host=conf['DB_HOST'],port=conf.get('DB_PORT',5432),dbname=conf['DB_NAME'],user=conf['DB_USER'],password=conf.get('DB_PASSWORD',''))
cur=c.cursor()
cur.execute("SELECT COUNT(*) FROM songs WHERE global_id BETWEEN 30121 AND 30130;")
assert cur.fetchone()[0]==0, "gid range not free!"
gids=[]
for s in SONGS:
    gid=30120+s["pos"]
    cur.execute("""INSERT INTO songs
      (global_id, source_project, batch, creator, status, title, lyrics,
       style_prompt, genre, genre_group, subgenre, bpm, key_signature, theme)
      VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING global_id""",
      (gid,'sunolanguage','BS01','sunolanguage','pending_suno', s["title"], None,
       s["sp"], 'Neoclassical chamber (four cellos)', 'Contemporary', s["sub"],
       s["bpm"], s["key"], '신부 (A Bride Suite)'))
    gids.append(cur.fetchone()[0])
c.commit()
print("INSERTED songs gid:", gids)
cur.execute("SELECT global_id,title,bpm,key_signature,status,(lyrics IS NULL) instr FROM songs WHERE batch='BS01' ORDER BY global_id;")
print("VERIFY:"); [print("  ",r) for r in cur.fetchall()]
c.close()

# --- batch JSON + sunomusic handoff ---
os.makedirs('data/bride_suite', exist_ok=True)
batch={"batch":"BS01","series":"Bride Suite","line":"sunolanguage","theme":"신부 (A Bride Suite)",
 "ensemble":"Cello quartet (four cellos), neoclassical chamber instrumental",
 "created":"2026-06-23","gid_range":"30121~30130","origin":"seed = 한여름의 신부(1회성, 아카이브). Leo 지시: 신부 테마 정식배치 10곡.",
 "gt_note":"'cello quartet' literal=GT 0건(dead-zone) → 'four cellos'+음역별 역할분화 서술. cello/legato/vibrato/pizzicato/arco/tremolo/double stops/counterpoint/con sordino/rubato/pedal tones 전부 GT-attested.",
 "songs":[{"gid":30120+s["pos"],"id":f"BS01-{s['pos']}","title":s["title"],"title_en":s["title_en"],
   "genre":"Neoclassical chamber (four cellos)","genre_group":"Contemporary","subgenre":s["sub"],
   "is_instrumental":True,"bpm":s["bpm"],"key":s["key"],"time_sig":s["time_sig"],
   "style_prompt":s["sp"],"sp_length":len(s["sp"]),"lyrics":None} for s in SONGS]}
json.dump(batch, open('data/bride_suite/BS01_batch.json','w'), ensure_ascii=False, indent=2)
print("batch JSON -> data/bride_suite/BS01_batch.json")

ts=datetime.datetime.now()
msg={"created_at":ts.strftime('%Y-%m-%dT%H:%M:%S')+'+09:00',"from":"sunolanguage","to":"sunomusic",
 "type":"generation_request","priority":"P1",
 "task":"BS01 신부 테마 첼로4중주 정식배치 10곡 생성 요청 (LEO 지시)",
 "batch":"BS01","method":"DB-direct: songs gid 30121~30130 INSERT 완료(creator=sunolanguage, status=pending_suno, lyrics=NULL 무가사). DB에서 SP pull → 생성.",
 "generation_spec":"★Custom 모드 + Instrumental=ON(전곡 무가사 연주곡). 곡당 1회=2클립(uuid1/uuid2). style_prompt=tags란 그대로. 가사란 비움. 전 10곡 가동.",
 "writeback":"songs gid 기준 suno_uuid1/2+suno_url UPDATE, status=generated. 결과 회신: projects/sunolanguage/messages/ BS01_생성결과.json.",
 "songs":[{"gid":30120+s["pos"],"title":s["title"],"genre":"Neoclassical chamber (four cellos)","is_instrumental":True,"bpm":s["bpm"],"key":s["key"]} for s in SONGS]}
fn='/Users/purple/projects/agent-comm/projects/sunomusic/messages/sunomusic_sunolanguage_'+ts.strftime('%Y%m%d_%H%M%S')+'_BS01_신부첼로4중주_생성요청.json'
json.dump(msg, open(fn,'w'), ensure_ascii=False, indent=2)
print("handoff ->", fn.split('/')[-1])
print("TS:", ts.strftime('%Y%m%d_%H%M%S'))
