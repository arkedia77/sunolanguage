#!/usr/bin/env python3
# PSLEEP01 — 펫 딥슬립(수면 유도) 인스트루멘탈 배치 10곡 빌드+적재+핸드오프
# LEO 직지시(kee 경유 07-18): 강아지·고양이 딥슬립 음악 1배치. 자율(무옵션) 진행.
# 자율 설계: 강아지4·고양이3·범용3 / 저BPM·무타악기·무트랜지언트·롱폼 루프친화 /
#           주파수 배려(강아지 따뜻한 중저역, 고양이 골골펄스+부드러운 고역) / Instrumental=ON.
import os, json, datetime, psycopg2

SONGS = [
 # --- DOG (4) ---
 {"pos":1,"target":"dog","title":"강아지의 저녁","title_en":"A Dog's Quiet Evening","key":"C major","bpm":52,"time_sig":"4/4",
  "genre":"Ambient sleep (solo felt piano)","sub":"Dog deep-sleep — warm solo felt piano",
  "sp":"Ambient instrumental for deep sleep, designed for dogs. Solo felt piano in a warm low-mid register, 52 BPM, no percussion and no drums. Slow, simple, repeating melodic phrases with long pauses between them, each note soft-hammered and rounded, sustained with generous pedal. A gentle warm analog synth pad breathes underneath, evolving slowly with no sudden changes. Everything is legato and continuous, with no sharp attacks or transients, a narrow and steady dynamic range that never startles. The mood is safe, warm and drowsy, like a quiet house at night. Long-form and loopable, the ending settling softly so it can repeat seamlessly. Natural, soft room reverb. Minimal high frequencies."},
 {"pos":2,"target":"dog","title":"따뜻한 바닥","title_en":"Warm Floor","key":"A minor","bpm":48,"time_sig":"4/4",
  "genre":"Ambient sleep (cello drone + piano)","sub":"Dog deep-sleep — low cello drone, sparse piano",
  "sp":"Ambient instrumental for canine deep sleep. A warm low cello drone sustains beneath sparse, slow felt-piano notes, 48 BPM, no percussion. The cello holds long bowed pedal tones in a comforting low register while the piano places single gentle notes far apart, unhurried. A soft pad and faint warm sub-bass fill the space with a steady, enveloping warmth. No transients, no sudden dynamics, no bright or harsh high frequencies — only rounded, mid-low tones that soothe a dog's hearing. Continuous and glacial, the harmony shifting almost imperceptibly. Deeply calming, grounding, secure. Long-form and loop-friendly with a seamless soft close. Natural warm reverb."},
 {"pos":3,"target":"dog","title":"안전한 집","title_en":"Safe Home","key":"F major","bpm":50,"time_sig":"4/4",
  "genre":"Ambient sleep (harp + low strings)","sub":"Dog deep-sleep — soft harp over warm low strings",
  "sp":"Ambient instrumental for dogs to fall asleep. Soft harp arpeggios, slow and widely spaced, over a bed of warm sustained low strings, 50 BPM, no percussion. The harp is gentle and muted, notes rounded with no pluck attack, drifting downward like slow breathing. Low strings swell and recede in long legato waves underneath. Warm, safe, and enveloping, staying in a comforting mid-low range with minimal high-frequency content. No abrupt changes, no sharp transients, a soft and narrow dynamic range. Continuous long-form texture that loops without a seam. The feeling of a safe, warm den. Natural concert-hall reverb, soft and distant."},
 {"pos":4,"target":"dog","title":"숨소리처럼","title_en":"Like Breathing","key":"D major","bpm":54,"time_sig":"4/4",
  "genre":"Ambient sleep (breathing pad)","sub":"Dog deep-sleep — breath-paced warm pad swells",
  "sp":"Ambient instrumental for pet deep sleep, tuned for dogs. A warm analog synth pad rises and falls in slow, breath-like swells, 54 BPM, no percussion and no melody in the foreground. Beneath it, a soft low drone and gentle warm sub-bass hold steady. Occasional single, distant piano notes appear and fade. The whole piece breathes in and out at the pace of a resting animal, utterly continuous with no transients or sudden dynamics. Timbres are warm, rounded and mid-low, avoiding bright or piercing highs. Hypnotic, safe and drowsy. Long-form and seamlessly loopable. Soft natural reverb."},
 # --- CAT (3) ---
 {"pos":5,"target":"cat","title":"고양이 자장가","title_en":"Cat's Lullaby","key":"G major","bpm":55,"time_sig":"4/4",
  "genre":"Ambient sleep (purr pulse + harp)","sub":"Cat deep-sleep — purr pulse, sliding harp tones",
  "sp":"Ambient instrumental for cats to sleep, a gentle feline lullaby. A soft, low purring pulse — a warm, felt vibration around a slow steady rhythm — anchors the piece at 55 BPM, no drums or percussion. Above it, delicate harp and soft glassy bell-like tones slide gently between notes with smooth glissando, in the tender range cats respond to, but soft and never sharp. A warm pad sustains underneath. The purr-like pulse is comforting and maternal, the sliding tones like a mother cat's call. Continuous, soothing, with no transients or sudden changes. Long-form and loopable, closing softly. Natural gentle reverb."},
 {"pos":6,"target":"cat","title":"골골송","title_en":"The Purr Song","key":"E minor","bpm":50,"time_sig":"4/4",
  "genre":"Ambient sleep (purr-frequency drone)","sub":"Cat deep-sleep — sustained purr drone, glissando pads",
  "sp":"Ambient instrumental designed for feline deep sleep. A sustained purr-frequency drone pulses low and warm, a soft rhythmic vibration like a contented cat, no percussion, around 50 BPM. Gentle sliding tones and soft high sustained pads drift above in smooth glissando, staying delicate and rounded with no harsh or piercing frequencies. The texture is minimal and continuous, evolving so slowly it feels still. Warm, safe and hypnotic, built on the comforting rhythm of purring. No transients, narrow dynamic range. Long-form, seamlessly looping. Soft, intimate reverb."},
 {"pos":7,"target":"cat","title":"창가의 오후잠","title_en":"Windowsill Nap","key":"A major","bpm":52,"time_sig":"4/4",
  "genre":"Ambient sleep (glassy pads)","sub":"Cat deep-sleep — airy glassy pads, faint purr hum",
  "sp":"Ambient instrumental for a cat's afternoon nap. Soft, glassy sustained pads shimmer gently in a calm, airy register, 52 BPM, no percussion. A faint warm purr-pulse hums low underneath. Delicate bell and harp tones appear softly and slide between pitches, tender and smooth, never sharp or startling. Warm sunlight through a window rendered in sound — peaceful, still, drowsy. The harmony drifts almost imperceptibly with no sudden dynamics or transients. Continuous and loopable long-form. Gentle, soft reverb, intimate and close."},
 # --- UNIVERSAL (3) ---
 {"pos":8,"target":"universal","title":"델타","title_en":"Delta Drift","key":"C major","bpm":45,"time_sig":"4/4",
  "genre":"Ambient sleep (deep drone + pink noise)","sub":"Universal deep-sleep — warm drone, soft pink-noise wash",
  "sp":"Ambient instrumental for deep sleep, for pets and their humans together. A deep, warm ambient drone with soft sub-bass, extremely slow and evolving, around 45 BPM with no percussion. Layered warm pads shift glacially over a bed of gentle pink-noise wash, like distant soft rain. No melody, no transients, no sudden changes — only a vast, calming warmth that slows the breath. Stays in warm low-mid frequencies, soothing to both canine and feline hearing, avoiding harsh highs. Hypnotic, enveloping, timeless. Long-form and seamlessly loopable. Deep natural reverb."},
 {"pos":9,"target":"universal","title":"긴 밤","title_en":"The Long Night","key":"D minor","bpm":42,"time_sig":"4/4",
  "genre":"Ambient sleep (glacial evolving pad)","sub":"Universal deep-sleep — glacial night-long pad",
  "sp":"Ambient instrumental for long-form pet sleep. A glacial, evolving pad drifts through soft warm harmonies, 42 BPM, no percussion and no defined melody. Faint sustained low strings and a gentle drone hold beneath, swelling and receding over very long spans. The music barely moves, endlessly continuous, with no transients or dynamic spikes to disturb rest. Warm, dark and soft, all sharp high frequencies rolled off. Designed to play through the whole night, calming and steady. Perfectly loopable long-form. Soft, deep, distant reverb."},
 {"pos":10,"target":"universal","title":"함께 잠들다","title_en":"Sleeping Together","key":"E-flat major","bpm":50,"time_sig":"4/4",
  "genre":"Ambient sleep (felt piano + drone)","sub":"Universal deep-sleep — sparse felt piano over warm drone",
  "sp":"Ambient instrumental for pets and people to sleep side by side. Slow, warm felt-piano notes drift over a soft sustained pad and a gentle low drone, 50 BPM, no percussion. The piano is sparse and tender, phrases far apart, each note rounded and warm. Everything blends into a continuous, breathing calm with no transients or sudden changes and a soft, narrow dynamic range. Warm mid-low timbres soothe both animal and human hearing, with minimal bright high frequencies. Safe, intimate and drowsy, like resting together in the dark. Long-form and loopable. Natural, soft reverb."},
]

THEME = "펫 딥슬립 (Pet Deep Sleep)"
BATCH = "PSLEEP01"
GID0 = 30150  # 다음 가용: 30151~30160

# --- validate SP length ---
over=[s for s in SONGS if len(s["sp"])>1000]
for s in SONGS:
    print(f"  {BATCH}-{s['pos']:<2} {s['target']:<9} {s['title']:<12} {s['key']:<14} {s['bpm']}BPM  SP={len(s['sp'])}{'  OVER!' if len(s['sp'])>1000 else ''}")
assert not over, f"SP over 1000: {[s['pos'] for s in over]}"
print(f"SP gate: ALL {len(SONGS)} PASS (<=1000)")

if os.environ.get("DRYRUN"):
    print("DRYRUN — DB insert 생략")
    raise SystemExit(0)

# --- DB insert gid 30151-30160 ---
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
       style_prompt, genre, genre_group, subgenre, bpm, key_signature, theme)
      VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING global_id""",
      (gid,'sunolanguage',BATCH,'sunolanguage','pending_suno', s["title"], None,
       s["sp"], s["genre"], 'Ambient', s["sub"], s["bpm"], s["key"], THEME))
    gids.append(cur.fetchone()[0])
c.commit()
print("INSERTED songs gid:", gids)
cur.execute(f"SELECT global_id,title,bpm,key_signature,status,(lyrics IS NULL) instr FROM songs WHERE batch='{BATCH}' ORDER BY global_id;")
print("VERIFY:"); [print("  ",r) for r in cur.fetchall()]
c.close()

# --- batch JSON ---
os.makedirs('data/pet_sleep', exist_ok=True)
batch={"batch":BATCH,"series":"Pet Deep Sleep","line":"sunolanguage","theme":THEME,
 "created":"2026-07-18","gid_range":f"{GID0+1}~{GID0+len(SONGS)}",
 "origin":"LEO 직지시(kee 경유 07-18): 강아지·고양이 딥슬립 음악 1배치. 자율(무옵션) 진행. leomusic3 병행발주 정체분 병행.",
 "design_note":"강아지4·고양이3·범용3. 저BPM(42~55)·무타악기·무트랜지언트·롱폼 루프친화. 주파수 배려: 강아지=따뜻한 중저역/고역 억제, 고양이=골골(purr)펄스+부드러운 sliding 고역, 범용=델타 드론+핑크노이즈. Instrumental=ON 무가사.",
 "songs":[{"gid":GID0+s["pos"],"id":f"{BATCH}-{s['pos']}","target":s["target"],"title":s["title"],"title_en":s["title_en"],
   "genre":s["genre"],"genre_group":"Ambient","subgenre":s["sub"],
   "is_instrumental":True,"bpm":s["bpm"],"key":s["key"],"time_sig":s["time_sig"],
   "style_prompt":s["sp"],"sp_length":len(s["sp"]),"lyrics":None} for s in SONGS]}
json.dump(batch, open('data/pet_sleep/PSLEEP01_batch.json','w'), ensure_ascii=False, indent=2)
print("batch JSON -> data/pet_sleep/PSLEEP01_batch.json")
