"""실생성 연동 — 요청 한 건을 상태기계 위로 한 칸씩 민다(운영자 CLI).

  사연 접수(received)
   → lyrics-order  : 가사 발주서 작성(담당=LM 라인 · sunolanguage 는 가사를 쓰지 않는다)   → lyrics_pending
   → lyrics-in     : 가사 수령(버전 +1)                                                    → lyrics_ready
   → gen-order     : sunomusic 생성 발주서 작성(SP=sp_builder · 같은 가사·보컬 버전 재발주 차단) → generation_queued
   → gen-ack       : sunomusic 접수 확인                                                  → generating
   → audio-in      : 오디오 파일 수령(take 추가·sha256 자산 목록)                           → audio_ready
   → publish       : take 선택 확인 후 카드 완성                                           → ready

발주서는 `var/outbox/` 에 JSON 으로 떨어진다. agent-comm 발신은 사람이 확인하고
`scripts/send_msg.py <to> <키워드> <발주서>` 로 따로 한다(고객 사연이 공유 저장소에 실리므로 자동 발신하지 않는다).

사용:
  .venv/bin/python mvp/songcard/pipeline.py list
  .venv/bin/python mvp/songcard/pipeline.py show <rid>
  .venv/bin/python mvp/songcard/pipeline.py lyrics-order <rid> [--to leomusic2]
  .venv/bin/python mvp/songcard/pipeline.py lyrics-in <rid> --file lyrics.txt --by leomusic2 [--title 제목]
  .venv/bin/python mvp/songcard/pipeline.py gen-order <rid>
  .venv/bin/python mvp/songcard/pipeline.py gen-ack <rid>
  .venv/bin/python mvp/songcard/pipeline.py audio-in <rid> --file take.mp3 [--uuid U] [--gid G] [--select]
  .venv/bin/python mvp/songcard/pipeline.py publish <rid>
  .venv/bin/python mvp/songcard/pipeline.py fail <rid> --note "사유"
  .venv/bin/python mvp/songcard/pipeline.py redo-close <rid> <redo_id>
"""
import argparse
import json
import sys
from pathlib import Path

import store

OUTBOX = store.VAR / "outbox"


def _need(req, *allowed):
    if req["status"] not in allowed:
        sys.exit(f"⛔ {req['request_id']} 상태 {req['status']} — 이 단계는 {allowed} 에서만")


def _write(name, obj):
    OUTBOX.mkdir(parents=True, exist_ok=True)
    p = OUTBOX / name
    if p.exists():
        sys.exit(f"⛔ 이미 발주서가 있습니다(중복 발주 차단): {p}")
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")
    print("WROTE", p)
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd")
    ap.add_argument("rid", nargs="?")
    ap.add_argument("extra", nargs="?")
    ap.add_argument("--file")
    ap.add_argument("--by")
    ap.add_argument("--to", default="(kee 지정 대기)")
    ap.add_argument("--title")
    ap.add_argument("--uuid")
    ap.add_argument("--gid")
    ap.add_argument("--select", action="store_true")
    ap.add_argument("--note")
    a = ap.parse_args()

    if a.cmd == "list":
        db = store._load()
        for r in db["requests"].values():
            print(f"{r['request_id']:24} {r['source']:6} {r['status']:18} {r['form']['occasion']:12} → {r['form']['recipient']}")
        return
    req = store.get(a.rid) if a.rid else None
    if not req:
        sys.exit("⛔ 요청 id 가 없습니다")
    if req["source"] == "sample" and a.cmd != "show":
        sys.exit("⛔ 샘플 카드는 실생성 파이프라인에 올리지 않습니다")
    rid = req["request_id"]

    if a.cmd == "show":
        r = dict(req)
        r.pop("owner_token")
        print(json.dumps(r, ensure_ascii=False, indent=1))

    elif a.cmd == "lyrics-order":
        _need(req, "received")
        f = req["form"]
        _write(f"{rid}_lyrics_order.json", {
            "request_id": rid, "kind": "lyrics_order", "to": a.to,
            "note": "가사 담당 슬롯이 쓴다(sunolanguage 는 가사를 쓰지 않음). 브라켓은 코퍼스 서술형만.",
            "occasion": f["occasion"], "recipient": f["recipient"], "sender": f["sender"],
            "story": f["story"], "memory": f["memory"], "message": f["message"],
            "genre": f["genre"], "vocal": f["vocal"], "sp_draft": req["sp"]["sp"],
        })
        store.set_status(rid, "lyrics_pending", f"to={a.to}")

    elif a.cmd == "lyrics-in":
        _need(req, "lyrics_pending", "lyrics_ready")
        text = Path(a.file).read_text(encoding="utf-8").strip()
        if not a.by:
            sys.exit("⛔ --by(가사 저자 슬롯)가 필요합니다")

        def f(r):
            r["lyrics_versions"].append({"v": len(r["lyrics_versions"]) + 1, "text": text, "by": a.by, "at": store._now()})
            if a.title:
                r["title"] = a.title
        store.update(rid, f)
        store.set_status(rid, "lyrics_ready", f"by={a.by}")

    elif a.cmd == "gen-order":
        _need(req, "lyrics_ready")
        lv = req["lyrics_versions"][-1]["v"]
        vv = req["vocal_version"]["v"]
        _write(f"{rid}_gen_L{lv}_V{vv}.json", {   # 파일명이 곧 중복 방지 키
            "request_id": rid, "kind": "suno_generation_order", "to": "sunomusic",
            "order_key": f"{rid}:L{lv}:V{vv}",
            "title": req.get("title") or f"{req['form']['recipient']}에게",
            "style_prompt": req["sp"]["sp"], "sp_chars": req["sp"]["sp_chars"],
            "lyrics": req["lyrics_versions"][-1]["text"],
            "takes": 2,
            "return": "오디오 파일(mp3/wav) 원본 + suno_uuid — ⛔cdn1 직링크는 09-25 실측 403이라 링크만으로는 회수 불가",
        })
        store.set_status(rid, "generation_queued")

    elif a.cmd == "gen-ack":
        _need(req, "generation_queued")
        store.set_status(rid, "generating")

    elif a.cmd == "audio-in":
        _need(req, "generating", "audio_ready")
        aid = store.add_asset(rid, Path(a.file))
        store.add_take(rid, a.uuid, aid, select=a.select)
        if a.gid:
            store.update(rid, lambda r: r.__setitem__("legacy_gid", a.gid))
        store.set_status(rid, "audio_ready", f"asset={aid}")

    elif a.cmd == "publish":
        _need(req, "audio_ready")
        req = store.get(rid)
        if not req["lyrics_versions"] or not req["takes"]:
            sys.exit("⛔ 가사·take 가 있어야 카드가 됩니다")
        if not any(t["selected"] for t in req["takes"]):
            def sel(r):
                r["takes"][0]["selected"] = True
            store.update(rid, sel)
        store.set_status(rid, "ready")

    elif a.cmd == "fail":
        store.set_status(rid, "failed", a.note or "")

    elif a.cmd == "redo-close":
        def f(r):
            x = next(x for x in r["redos"] if x["redo_id"] == a.extra)
            x["status"] = "closed"
            if x["what"] in ("vocal", "genre"):
                r["vocal_version"]["v"] += 1
        store.update(rid, f)
        req = store.get(rid)
        x = next(x for x in req["redos"] if x["redo_id"] == a.extra)
        what = x["what"]
        if what == "lyrics":
            _write(f"{rid}_lyrics_redo_{a.extra}.json", {
                "request_id": rid, "kind": "lyrics_redo_order", "to": a.to,
                "customer_note": x["note"], "previous": req["lyrics_versions"][-1] if req["lyrics_versions"] else None,
            })
        store.set_status(rid, "lyrics_pending" if what == "lyrics" else "lyrics_ready", f"redo {a.extra}")
    else:
        sys.exit(__doc__)
    print(rid, "→", store.get(rid)["status"])


if __name__ == "__main__":
    main()
