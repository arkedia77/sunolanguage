"""샘플 카드 3종 심기 — source=sample.

⛔ 샘플 음원은 **이 사연들로 만든 곡이 아니다.** 내부 제작곡(AWARE05, gid 30201·30202·30206)의
로컬 보관 mp3를 카드 동작(재생·헌사·가사·공유)을 보이려고 빌려 쓴다. 받는 사람·사연은 가상.
카드 화면에 sample_note 로 그대로 표시한다. 실존 인물용 곡(JIOBD01·VD 등)은 쓰지 않는다.

다시 실행해도 같은 client_key 라 중복으로 안 생긴다.
"""
import json
import re
from pathlib import Path

import sp_builder
import store

ROOT = Path(__file__).resolve().parents[2]
SONGS = json.loads((ROOT / "data/aware/AWARE05_songs.json").read_text(encoding="utf-8"))
RESULT = json.loads((ROOT / "data/aware/AWARE05_result.json").read_text(encoding="utf-8"))

SAMPLES = [
    {"idx": 7, "form": {"occasion": "anniversary", "recipient": "지민", "sender": "현우", "genre": "ballad", "vocal": "male",
                        "story": "(가상 사연) 처음 만난 겨울부터 열 번째 겨울까지.", "memory": "", "message": "열 번의 겨울 동안 곁에 있어줘서 고마워."}},
    {"idx": 2, "form": {"occasion": "thanks", "recipient": "김 선생님", "sender": "3학년 2반", "genre": "acoustic", "vocal": "female",
                        "story": "(가상 사연) 졸업을 앞두고 담임 선생님께.", "memory": "", "message": "선생님 덕분에 버틴 일 년이었어요."}},
    {"idx": 3, "form": {"occasion": "cheer", "recipient": "민서", "sender": "언니", "genre": "gospel", "vocal": "female",
                        "story": "(가상 사연) 첫 출근을 앞둔 동생에게.", "memory": "", "message": "넌 이미 충분해. 내일 잘 다녀와!"}},
]


def display_lyrics(raw: str) -> str:
    """가사 본문만 보이게 — 연출 브라켓 줄([piano grows…])은 빼고 구간명만 남긴다."""
    out = []
    for line in raw.splitlines():
        s = line.strip()
        m = re.fullmatch(r"\[(.+)\]", s)
        if m:
            name = m.group(1)
            if re.fullmatch(r"(Intro|Outro|Verse.*|Pre-Chorus|Chorus.*|Bridge.*|Final Chorus|Hook.*)", name, re.I):
                out.append(f"— {name} —")
            continue
        out.append(s)
    return re.sub(r"\n{3,}", "\n\n", "\n".join(out)).strip()


def main():
    for s in SAMPLES:
        song, res = SONGS[s["idx"]], RESULT["songs"][s["idx"]]
        assert song["title"] == res["title"], (song["title"], res["title"])
        gid = res["id"]
        audio = ROOT / f"data/aware/audio/{gid}_t1.mp3"
        sp = sp_builder.build_sp(s["form"]["occasion"], s["form"]["genre"], s["form"]["vocal"])
        req, created = store.create_request(s["form"], f"sample-{gid}", sp, source="sample")
        rid = req["request_id"]
        if created:
            note = f"샘플 음원 · 내부 제작곡 AWARE05 #{gid} 「{song['title']}」({song['genre']}) — 이 사연으로 만든 곡이 아닙니다"

            def f(r):
                r["title"] = song["title"]
                r["legacy_gid"] = str(gid)
                r["sample_note"] = note
                r["visibility"] = "link"
                r["lyrics_versions"].append({"v": 1, "text": display_lyrics(song["lyrics"]), "by": "AWARE05(sample)", "at": store._now()})
            store.update(rid, f)
            aid = store.add_asset(rid, audio)
            store.add_take(rid, res["suno_uuid1"], aid, select=True)
            for st in ["lyrics_ready", "generation_queued", "generating", "audio_ready", "ready"]:
                store.set_status(rid, st, "sample")
        r = store.get(rid)
        if not r.get("delivered") or "vocal" not in r["delivered"]:   # 납품본 묶음(take·가사판·보컬판) — 09-25 수리 이전 샘플도 여기서 채운다
            def fix(x):
                t = next(t for t in x["takes"] if t["selected"])
                t.setdefault("lyrics_v", x["lyrics_versions"][-1]["v"])
                t.setdefault("vocal_v", x["vocal_version"]["v"])
                store.deliver(x, t)
            r = store.update(rid, fix)
        print(f"{'NEW ' if created else 'KEEP'} {rid} /c/{r['share_token']}  gid={gid} {r['title']}")


if __name__ == "__main__":
    main()
