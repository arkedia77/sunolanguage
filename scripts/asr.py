import sys, json, time
from faster_whisper import WhisperModel
path = sys.argv[1]; size = sys.argv[2] if len(sys.argv) > 2 else "small"
t0 = time.time()
m = WhisperModel(size, device="cpu", compute_type="int8")
segs, info = m.transcribe(path, language="ko", word_timestamps=True, beam_size=5,
                          condition_on_previous_text=False)
out = []
for s in segs:
    out.append({"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip(),
                "words": [{"w": w.word, "s": round(w.start, 2), "e": round(w.end, 2)} for w in (s.words or [])]})
json.dump({"file": path, "model": size, "segments": out}, open(sys.argv[3], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"{path} · {size} · {len(out)}세그 · {time.time()-t0:.0f}s")
for s in out:
    print(f"  [{s['start']:6.2f}] {s['text']}")
