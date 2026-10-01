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

★2026-10-01 저장경계 (LEO 직접 결정 · 정본 =
  `repo:agent-comm projects/solself/attachments/A280_PRIVACY_REVIEW_20260930/LEO_STORAGE_DECISION_20261001.md`)

  **Git(agent-comm) = 프로젝트 정보만.** 설계·코드·일정·담당·상태 + «내용 없는» 업무 참조·완료 영수증.
  **서비스 데이터 = 별도 저장소.** 사연 원문뿐 아니라 **요약·가사 본문·음원·사용자 입력/동의 데이터**까지.
  ⇒ 10-01 오전까지의 「최소 비식별 요약은 Git 에 실어도 된다」 대안은 **이 결정으로 대체됐다**.

  그래서 `lyrics-order` 는 파일을 **두 개** 쓴다:
    `<rid>_lyrics_order.json`  = 내용본(요약·호칭·구조지시…). ⛔**Git 금지** — 별도 경로로만 전달.
    `<rid>_lyrics_ref.json`    = Git 통용 **참조본**. 업무ID·담당·상태·판본 해시뿐, 내용 0.
  내용본에는 여전히 **원문이 아니라 요약**만 들어간다(`--summary` 필수·fail-closed 4종 유지).
  ⚠전달 경로는 admin 제안 대기(kee 청구, 10-02 12:00) — 정해지기 전에는 **내용본을 보내지 않는다**.

사용:
  .venv/bin/python mvp/songcard/pipeline.py list
  .venv/bin/python mvp/songcard/pipeline.py show <rid>
  .venv/bin/python mvp/songcard/pipeline.py lyrics-order <rid> --summary "비식별 요약" [--to leomusic3]
  .venv/bin/python mvp/songcard/pipeline.py lyrics-in <rid> --file lyrics.txt --by leomusic3 [--title 제목]
        [--declaration match|none_verified] [--lyrics-sha12 <납품자 신고 해시 — 내가 재측정해 대조>]
  .venv/bin/python mvp/songcard/pipeline.py gen-order <rid>
  .venv/bin/python mvp/songcard/pipeline.py gen-ack <rid>
  .venv/bin/python mvp/songcard/pipeline.py audio-in <rid> --file take.mp3 [--uuid U] [--gid G] [--select]
  .venv/bin/python mvp/songcard/pipeline.py publish <rid>
  .venv/bin/python mvp/songcard/pipeline.py fail <rid> --note "사유"
  .venv/bin/python mvp/songcard/pipeline.py redo-close <rid> <redo_id>
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import store

OUTBOX = store.VAR / "outbox"


def _need(req, *allowed):
    if req["status"] not in allowed:
        sys.exit(f"⛔ {req['request_id']} 상태 {req['status']} — 이 단계는 {allowed} 에서만")


def _write(name, obj):
    store.secure_dir(OUTBOX)
    p = OUTBOX / name
    if p.exists():
        sys.exit(f"⛔ 이미 발주서가 있습니다(중복 발주 차단): {p}")
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")
    store.secure_file(p)      # 0640 — 발주서엔 요약·호칭이 들어간다
    print("WROTE", p)
    return p


def _assert_git_safe(ref: dict, order: dict):
    """참조본이 정말 «내용 0» 인지 기계가 본다. ★사람이 「내용 없음」이라고 적는 것과
    실제로 없는 것은 다르다 — 한 칸이라도 내용본에서 새어 들어오면 여기서 멈춘다."""
    blob = json.dumps(ref, ensure_ascii=False)
    leak = [k for k in ("요약(비식별)", "structure_hint", "호칭", "sp_draft", "받는_분", "보내는_분")
            if (v := order.get(k)) and str(v) in blob]
    if leak:
        sys.exit(f"⛔ 참조본에 내용이 섞였습니다: {leak} — Git 통에는 내용을 싣지 않습니다(LEO 10-01 저장경계)")
    print(f"  ↳ Git 통용 참조본 = 내용 0 확인(검사 칸 6) · 내용본은 var/outbox 로컬만")


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
    store.harden()          # umask 027 — 고객 데이터를 쓰는 프로세스다
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
    ap.add_argument("--declaration", help="납품자 신고 상태: match | none_verified (leomusic3 10-01 필수 칸)")
    ap.add_argument("--lyrics-sha12", help="납품자가 적어 준 가사 해시 — ★내가 다시 재서 대조한다")
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
        # ★Git 통용 «참조본» — 내용 0. 이 파일만 agent-comm 으로 나간다.
        blob = json.dumps(order, ensure_ascii=False, sort_keys=True).encode()
        ref = {
            "request_id": rid, "kind": "lyrics_order_ref", "to": a.to,
            "업무ID": rid,
            "담당": a.to, "상태": "lyrics_pending",
            "발주본_sha256": hashlib.sha256(blob).hexdigest()[:16],
            "★이_통의_성격": ("내용 없는 업무 참조·영수증입니다(LEO 10-01 저장경계). "
                         "가사 발주 «내용»(요약·호칭·구조 지시·SP)은 별도 서비스 경로로 전달됩니다."),
            "내용본_위치": "접수 서버 로컬 var/outbox/ — ⛔Git·agent-comm 에 올리지 않음",
            "전달_경로": "admin 제안 대기(kee 청구 10-02 12:00) — 정해지면 그 경로로 전달",
        }
        _write(f"{rid}_lyrics_ref.json", ref)
        _assert_git_safe(ref, order)
        store.set_status(rid, "lyrics_pending", f"to={a.to}")

    elif a.cmd == "lyrics-in":
        _need(req, "lyrics_pending", "lyrics_ready")
        text = Path(a.file).read_text(encoding="utf-8").strip()
        if not a.by:
            sys.exit("⛔ --by(가사 저자 슬롯)가 필요합니다")
        # ★납품에 붙는 신고 칸을 «버리지 않고 받는다»(leomusic3 10-01 `135710` §5⑴ — solself 반증으로
        #   그쪽 납품에 `declaration_status`·`lyrics_sha12` 가 필수가 됐다). 내 수령부가 흘리면 결속이 끊긴다.
        #   ⛔해시는 상대가 적어 준 값을 «믿지 않고» 내가 받은 본문에서 다시 잰다. 둘이 다르면 중단한다
        #   (전송 중 바뀌었거나 다른 파일을 가리킨 것 — 어느 쪽이든 그대로 진행하면 안 된다).
        sha12 = hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]
        if a.lyrics_sha12 and a.lyrics_sha12 != sha12:
            sys.exit(f"⛔ 가사 해시 불일치 — 신고 {a.lyrics_sha12} / 내가 받은 본문 {sha12}\n"
                     f"   같은 파일인지 확인하고 다시 주십시오(끝 공백은 제거 후 계산합니다).")
        if a.declaration and a.declaration not in ("match", "none_verified"):
            sys.exit("⛔ --declaration 은 match | none_verified 둘 중 하나입니다")

        def f(r):
            r["lyrics_versions"].append({
                "v": len(r["lyrics_versions"]) + 1, "text": text, "by": a.by, "at": store._now(),
                "lyrics_sha12": sha12,                      # 내가 실측한 값
                "declaration_status": a.declaration or None,  # 상대 신고(없으면 None — 「없음」이지 「통과」가 아니다)
            })
            if a.title:
                r["title"] = a.title
        store.update(rid, f)
        store.set_status(rid, "lyrics_ready", f"by={a.by}")
        print(f"  ↳ lyrics_sha12={sha12} (내가 재측정) · declaration_status="
              f"{a.declaration or '미신고 — ⛔「통과」가 아니라 「없음」'}")

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
