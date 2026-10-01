"""실생성 연동 — 요청 한 건을 상태기계 위로 한 칸씩 민다(운영자 CLI).

  사연 접수(received)
   → lyrics-order  : 가사 발주서 작성(담당=LM 라인 · sunolanguage 는 가사를 쓰지 않는다)   → lyrics_pending
   → lyrics-in     : 가사 수령(버전 +1)                                                    → lyrics_ready
   → gen-order     : sunomusic 생성 발주서 작성(SP=sp_builder · 같은 가사·보컬 버전 재발주 차단) → generation_queued
   → gen-ack       : sunomusic 접수 확인                                                  → generating
   → audio-in      : 오디오 파일 수령(take 추가·sha256 자산 목록)                           → audio_ready
   → publish       : take 선택 확인 후 카드 완성                                           → ready

발주서는 `var/outbox/` 에 JSON 으로 떨어진다. agent-comm 발신은 사람이 확인하고
`scripts/send_msg.py <to> <키워드> <발주서>` 로 따로 한다.

★2026-10-01 (kee `102626` — solself 반증 반영): **사연 원문은 git·agent-comm 에 싣지 않는다.**
  가사 발주서에 나가는 것 = «운영자가 쓴 최소 비식별 요약» + 업무ID뿐이다. 원문은 접수 서버 로컬(`var/`)에만 남는다.
  ⇒ `lyrics-order` 는 `--summary` 없이는 **거절한다**(fail-closed). 요약에 원문을 그대로 붙여 넣는 것도 막는다.

사용:
  .venv/bin/python mvp/songcard/pipeline.py list
  .venv/bin/python mvp/songcard/pipeline.py show <rid>
  .venv/bin/python mvp/songcard/pipeline.py lyrics-order <rid> --summary "비식별 요약" [--to leomusic3]
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


def _guard_summary(summary: str, form: dict, lyrics_ok: bool):
    """요약 칸의 fail-closed 검문. ★「요약을 쓰라」는 규칙은 지켜지는지 «기계가» 본다 —
    규칙만 적어 두면 바쁜 날 원문을 통째로 붙여 넣게 된다(그게 09-26 에 실제로 한 일이다)."""
    if not summary:
        sys.exit("⛔ --summary(또는 --summary-file)가 필요합니다 — 사연 원문은 발주서로 나가지 않습니다(kee 10-01).\n"
                 "   예: --summary '어머니께 드리는 감사. 30년 장사·새벽 준비·늦게 전하는 고마움. 이름·상호·지명 없음.'")
    if len(summary) > 400:
        sys.exit(f"⛔ 요약이 {len(summary)}자입니다 — 400자 이내의 «최소» 요약이어야 합니다")
    story = (form.get("story") or "") + "\n" + (form.get("memory") or "")
    norm = lambda x: "".join(x.split())
    ns, nq = norm(summary), norm(story)
    for i in range(0, max(0, len(nq) - 20) + 1):     # 원문 20자 연속이 그대로 들어가면 「요약」이 아니다
        if nq[i:i + 20] and nq[i:i + 20] in ns:
            sys.exit("⛔ 요약에 사연 원문이 20자 이상 그대로 들어 있습니다 — 다시 써 주십시오(발췌는 요약이 아닙니다).\n"
                     f"   걸린 대목: …{nq[i:i + 20]}…")
    if not lyrics_ok:
        for k, label in (("recipient", "받는 분 이름"), ("sender", "보내는 분 이름")):
            v = (form.get(k) or "").strip()
            if v and v in summary:
                sys.exit(f"⛔ 「가사에 이름 넣기」 동의가 없는데 요약에 {label}({v})이 들어 있습니다 — 호칭으로 바꿔 주십시오")


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
    ap.add_argument("--summary", help="가사용 최소 «비식별» 요약(필수) — 사연 원문은 발주서로 나가지 않는다")
    ap.add_argument("--summary-file", help="같은 요약을 파일로")
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
        import templates
        t = templates.TEMPLATES[f["occasion"]]
        summary = (a.summary or (Path(a.summary_file).read_text(encoding="utf-8") if a.summary_file else "")).strip()
        lyrics_ok = store.consent(f, "consent_lyrics")
        _guard_summary(summary, f, lyrics_ok)
        order = {
            "request_id": rid, "kind": "lyrics_order", "to": a.to,
            "note": "가사 담당 슬롯이 쓴다(sunolanguage 는 가사를 쓰지 않음). 브라켓은 코퍼스 서술형만.",
            "★개인정보": ("사연 원문은 싣지 않습니다(kee 10-01 102626). 아래 요약은 운영자가 쓴 최소 비식별본이며, "
                       "원문은 접수 서버 로컬에만 있습니다. 원문이 꼭 필요하면 kee 를 통해 요청해 주십시오."),
            "업무ID": rid,
            "occasion": f["occasion"], "template_label": t["label"],
            "structure_hint": t["structure_hint"],   # ★구조 지시일 뿐 — 문면은 받는 쪽이 쓴다
            "호칭": f.get("relation", ""),
            "전용_칸_항목": f.get("extra_label", ""),   # ⛔값은 안 싣는다(이름·날짜가 들어있을 수 있다)
            "요약(비식별)": summary,
            "genre": f["genre"], "vocal": f["vocal"], "sp_draft": req["sp"]["sp"],
            "가사에_실명_사용": lyrics_ok,
            "이름_지침": ("요청자가 «가사에 이름 넣기»에 동의했습니다. 아래 이름만 쓰십시오."
                       if lyrics_ok else "⛔가사에 실명을 쓰지 마십시오 — 호칭만 쓰십시오(동의 없음·기본값)."),
        }
        if lyrics_ok:
            order["받는_분"] = f.get("recipient", "")
            order["보내는_분"] = f.get("sender", "")
        _write(f"{rid}_lyrics_order.json", order)
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
        # 아직 어느 발주서에도 안 실린 «닫힌 재요청»을 싣는다 — 고객이 뭘 바꿔 달라 했는지가 발주서에 남게
        changes = [x for x in req["redos"] if x["status"] == "closed" and not x.get("ordered_in")]
        key = f"{rid}_gen_L{lv}_V{vv}"
        _write(f"{key}.json", {   # 파일명이 곧 중복 방지 키
            "request_id": rid, "kind": "suno_generation_order", "to": "sunomusic",
            "order_key": f"{rid}:L{lv}:V{vv}",
            "title": req.get("title") or f"{req['form']['recipient']}에게",
            "genre": req["vocal_version"]["genre"], "vocal": req["vocal_version"]["vocal"],
            "style_prompt": req["sp"]["sp"], "sp_chars": req["sp"]["sp_chars"],
            "lyrics": req["lyrics_versions"][-1]["text"],
            "change_requests": [{k: x.get(k) for k in ("redo_id", "what", "to", "note")} for x in changes],
            "takes": 2,
            "return": "오디오 파일(mp3/wav) 원본 + suno_uuid — ⛔cdn1 직링크는 09-25 실측 403이라 링크만으로는 회수 불가",
        })

        def mark(r):
            for x in r["redos"]:
                if x["status"] == "closed" and not x.get("ordered_in"):
                    x["ordered_in"] = key
        store.update(rid, mark)
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
        lv, vv = req["lyrics_versions"][-1]["v"], req["vocal_version"]["v"]
        cur = [t for t in req["takes"] if t.get("lyrics_v") == lv and t.get("vocal_v") == vv]
        if not cur:
            sys.exit(f"⛔ 현재 판(가사 L{lv}·보컬 V{vv})으로 만든 take 가 없습니다 — 옛 판 오디오로는 게시하지 않습니다")
        take = next((t for t in cur if t["selected"]), cur[0])

        def pub(r):
            for t in r["takes"]:
                t["selected"] = t["asset_id"] == take["asset_id"]
            store.deliver(r, take)
        store.update(rid, pub)
        store.set_status(rid, "ready", f"L{lv}·V{vv}")

    elif a.cmd == "fail":
        store.set_status(rid, "failed", a.note or "")

    elif a.cmd == "redo-close":
        x = next((x for x in req["redos"] if x["redo_id"] == a.extra), None)
        if not x:
            sys.exit(f"⛔ 재요청 {a.extra} 없음")
        if x["status"] == "closed":   # 두 번 닫아도 판이 또 오르지 않게
            print(f"= {a.extra} 는 이미 닫혀 있습니다(변경 없음)")
            return
        what = x["what"]
        if what in ("vocal", "genre"):
            import sp_builder
            if not x.get("to"):
                sys.exit(f"⛔ {a.extra} 에 바꿀 값(to)이 없습니다")
            vv = dict(req["vocal_version"])
            vv[what] = x["to"]
            vv["v"] += 1
            sp = sp_builder.build_sp(req["form"]["occasion"], vv["genre"], vv["vocal"])

            def f(r):
                r["vocal_version"] = vv
                r["sp"] = sp
        else:
            def f(r):
                pass

        def close(r):
            f(r)
            y = next(y for y in r["redos"] if y["redo_id"] == a.extra)
            y["status"] = "closed"
            y["closed_at"] = store._now()
        store.update(rid, close)
        req = store.get(rid)
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
