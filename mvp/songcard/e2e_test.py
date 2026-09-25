"""종단 점검 — 서버가 떠 있는 상태에서 실행.

  .venv/bin/python mvp/songcard/e2e_test.py [--base http://127.0.0.1:8787] [--audio 파일.mp3]

사연 접수 → (중복 접수 차단) → 비공개 확인 → 파이프라인 단계(가사 발주·수령·생성 발주·접수·오디오·게시)
→ 카드 재생(Range) → 공유 전환 → 재요청 중복 차단 → 샘플 파이프라인 차단 까지 한 번에 본다.
⚠ 오디오는 --audio 로 준 파일을 붙인다(기본=샘플 mp3). 실생성 오디오가 아니면 결과 source 는 live 여도
   «실생성 연동 검증»이 아니라 «경로 검증»이다 — 출력에 그렇게 찍는다.
"""
import argparse
import json
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
PY = sys.executable
ok = fail = 0


def call(base, method, path, body=None, headers=None):
    req = urllib.request.Request(base + path, method=method, headers={"Content-Type": "application/json", **(headers or {})},
                                 data=json.dumps(body).encode() if body is not None else None)
    try:
        with urllib.request.urlopen(req) as r:
            data = r.read()
            return r.status, data, dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.read(), dict(e.headers)


def check(name, cond, extra=""):
    global ok, fail
    if cond:
        ok += 1
    else:
        fail += 1
    print(("✅" if cond else "❌"), name, extra)


def pipe(*args):
    r = subprocess.run([PY, str(HERE / "pipeline.py"), *args], capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr).strip()


def _store_get(rid):
    sys.path.insert(0, str(HERE))
    import store
    return store.get(rid)


def _fresh_ready(B, audio):
    """새 live 요청 하나를 L1·V1 납품(ready)까지 올린다."""
    import secrets
    body = {"occasion": "thanks", "recipient": "회귀", "sender": "e2e", "story": "회귀 점검용 가상 사연입니다. 실제 인물 아님.",
            "memory": "", "message": "", "genre": "acoustic", "vocal": "female", "client_key": "e2e-" + secrets.token_hex(6)}
    r = json.loads(call(B, "POST", "/api/requests", body)[1])
    rid = r["request_id"]
    lyr = HERE / "var" / f"{rid}_lyrics.txt"
    lyr.write_text("(점검용 가사 L1)", encoding="utf-8")
    for st in [("lyrics-order", rid), ("lyrics-in", rid, "--file", str(lyr), "--by", "e2e-placeholder"),
               ("gen-order", rid), ("gen-ack", rid), ("audio-in", rid, "--file", audio, "--select"), ("publish", rid)]:
        rc, out = pipe(*st)
        assert rc == 0, out
    return rid, r["owner_token"], r["share_token"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://127.0.0.1:8787")
    ap.add_argument("--audio", default=str(HERE.parents[1] / "data/aware/audio/30201_t1.mp3"))
    ap.add_argument("--key", default=None)
    a = ap.parse_args()
    B = a.base
    import secrets
    key = a.key or "e2e-" + secrets.token_hex(6)

    body = {"occasion": "birthday", "recipient": "테스트", "sender": "e2e", "story": "종단 점검용 가상 사연입니다. 실제 인물 아님.",
            "memory": "", "message": "생일 축하해", "genre": "acoustic", "vocal": "female", "client_key": key}
    s1, d1, _ = call(B, "POST", "/api/requests", body)
    s2, d2, _ = call(B, "POST", "/api/requests", body)
    r1, r2 = json.loads(d1), json.loads(d2)
    check("사연 접수 201", s1 == 201, r1.get("request_id"))
    check("같은 client_key 재전송 → 새로 안 만듦", s2 == 200 and r2["request_id"] == r1["request_id"] and r2["created"] is False)
    rid, t, share = r1["request_id"], r1["owner_token"], r1["share_token"]

    s, _, _ = call(B, "GET", f"/api/cards/{share}")
    check("비공개 카드 — 토큰 없으면 404", s == 404)
    s, d, _ = call(B, "GET", f"/api/requests/{rid}?t={t}")
    check("오너 상태 조회", s == 200 and json.loads(d)["status"] == "received")
    s, d, _ = call(B, "POST", "/api/requests", {**body, "story": "짧음", "client_key": key + "x"})
    check("검증 — 짧은 사연 거절", s == 400, json.loads(d)["error"])

    lyr = HERE / "var" / f"{rid}_lyrics.txt"
    lyr.parent.mkdir(exist_ok=True)
    lyr.write_text("(종단 점검용 자리표시 가사 — 실제 가사 아님)\n생일 축하해\n", encoding="utf-8")
    steps = [
        ("lyrics-order", rid),
        ("lyrics-in", rid, "--file", str(lyr), "--by", "e2e-placeholder", "--title", "점검용 노래"),
        ("gen-order", rid),
        ("gen-ack", rid),
        ("audio-in", rid, "--file", a.audio, "--uuid", "e2e-no-uuid", "--select"),
        ("publish", rid),
    ]
    for st in steps:
        rc, out = pipe(*st)
        check(f"pipeline {st[0]}", rc == 0, out.splitlines()[-1] if out else "")
    rc, out = pipe("gen-ack", rid)
    check("상태기계 — 순서 어긴 단계 거절", rc != 0, out.splitlines()[-1])

    s, d, _ = call(B, "GET", f"/api/cards/{share}?t={t}")
    card = json.loads(d)
    check("카드 완성 ready·오디오·가사", s == 200 and card["status"] == "ready" and card["audio"] and card["lyrics"])
    s, d, h = call(B, "GET", card["audio"] + f"?t={t}", headers={"Range": "bytes=0-1023"})
    check("오디오 Range 206", s == 206 and len(d) == 1024, h.get("Content-Range"))
    s, _, _ = call(B, "GET", card["audio"])
    check("비공개 오디오 — 토큰 없으면 404", s == 404)

    s, _, _ = call(B, "POST", f"/api/requests/{rid}/share", {"t": t, "visibility": "link"})
    s2, d2, _ = call(B, "GET", f"/api/cards/{share}")
    check("공유 전환 후 링크만으로 열림", s == 200 and s2 == 200)
    check("공유 카드에 사연·SP·토큰 비노출", all(k not in json.loads(d2) for k in ("story", "sp", "owner_token")))

    s1, d1, _ = call(B, "POST", f"/api/requests/{rid}/redo", {"t": t, "what": "lyrics", "note": "2절에 이름", "redo_key": "rk1"})
    s2, d2, _ = call(B, "POST", f"/api/requests/{rid}/redo", {"t": t, "what": "vocal", "to": "male", "note": "다른 키", "redo_key": "rk2"})
    check("재요청 접수", s1 == 201)
    check("열린 재요청 있으면 두 번째는 새로 안 만듦", s2 == 200 and json.loads(d2)["created"] is False)

    samples = json.loads(call(B, "GET", "/api/samples")[1])
    check("샘플 카드 3종", len(samples) >= 3 and all(x["source"] == "sample" and x["sample_note"] for x in samples))
    rc, out = pipe("gen-order", samples[0]["request_id"])
    check("샘플은 실생성 파이프라인 차단", rc != 0, out.splitlines()[-1])

    # ── 회귀: solself 09-25 독립 재현 3건 ─────────────────────────────
    # (1) 보컬 재요청 값이 판·SP·발주서에 실린다 / 두 번 닫아도 판이 또 오르지 않는다
    rid2, t2, share2 = _fresh_ready(B, a.audio)
    s, d, _ = call(B, "POST", f"/api/requests/{rid2}/redo", {"t": t2, "what": "vocal", "note": "남자 목소리로", "redo_key": "k-v"})
    check("보컬 재요청 — 바꿀 값 없으면 거절", s == 400, json.loads(d)["error"])
    s, d, _ = call(B, "POST", f"/api/requests/{rid2}/redo", {"t": t2, "what": "vocal", "to": "male", "note": "남자 목소리로", "redo_key": "k-v"})
    rid_redo = json.loads(d)["redo"]["redo_id"]
    pipe("redo-close", rid2, rid_redo)
    rc, out = pipe("redo-close", rid2, rid_redo)
    pipe("gen-order", rid2)
    st = _store_get(rid2)
    order = json.loads((HERE / "var/outbox" / f"{rid2}_gen_L1_V2.json").read_text(encoding="utf-8"))
    check("(1) 보컬 판 값이 male 로 바뀜·V2", st["vocal_version"] == {"v": 2, "vocal": "male", "genre": "acoustic"}, st["vocal_version"])
    check("(1) 발주서 SP=male vocals·female 없음", "male vocals" in order["style_prompt"] and "female" not in order["style_prompt"], order["style_prompt"])
    check("(1) 발주서에 고객 변경요청 문면", any(c["note"] == "남자 목소리로" and c["to"] == "male" for c in order["change_requests"]))
    check("(1) 같은 재요청 두 번 닫아도 판 그대로", rc == 0 and "이미 닫혀" in out and st["vocal_version"]["v"] == 2)

    # (2) 새 가사 수령 중에도 카드는 «납품본»(옛 오디오+옛 가사) — 새 가사와 옛 오디오를 섞지 않는다
    rid3, t3, share3 = _fresh_ready(B, a.audio)
    old_card = json.loads(call(B, "GET", f"/api/cards/{share3}?t={t3}")[1])
    s, d, _ = call(B, "POST", f"/api/requests/{rid3}/redo", {"t": t3, "what": "lyrics", "note": "2절에 이름", "redo_key": "k-l"})
    pipe("redo-close", rid3, json.loads(d)["redo"]["redo_id"])
    newl = HERE / "var" / f"{rid3}_lyrics2.txt"
    newl.write_text("(점검용 새 가사 L2)", encoding="utf-8")
    pipe("lyrics-in", rid3, "--file", str(newl), "--by", "e2e-placeholder")
    mid = json.loads(call(B, "GET", f"/api/cards/{share3}?t={t3}")[1])
    check("(2) 제작 중 카드 = 옛 오디오 + 옛 가사(묶음 유지)", mid["audio"] == old_card["audio"] and mid["lyrics"] == old_card["lyrics"] and mid["updating"] is True)
    pipe("gen-order", rid3); pipe("gen-ack", rid3)
    pipe("audio-in", rid3, "--file", a.audio)      # 같은 파일 → 같은 자산이라 L2 take 가 생기지 않는다
    rc, out = pipe("publish", rid3)
    check("(2) 현재 판 take 없으면 게시 거절", rc != 0 and "take 가 없습니다" in out, out.splitlines()[-1])
    alt = HERE / "var" / f"{rid3}_alt.mp3"
    alt.write_bytes(Path(a.audio).read_bytes()[: 400_000])
    pipe("audio-in", rid3, "--file", str(alt), "--select"); pipe("publish", rid3)
    new_card = json.loads(call(B, "GET", f"/api/cards/{share3}?t={t3}")[1])
    check("(2) 게시 후 카드 = 새 오디오 + 새 가사", new_card["audio"] != old_card["audio"] and new_card["lyrics"] == "(점검용 새 가사 L2)" and not new_card["updating"])

    # (3) 서버와 다른 프로세스가 동시에 고쳐도 둘 다 남는다(잠금 안에서 0.3초씩 붙잡는 두 프로세스)
    worker = (
        "import sys,time;sys.path.insert(0,sys.argv[1]);import store\n"
        "def f(r):\n time.sleep(0.3);r.setdefault('_race',[]).append(sys.argv[3])\n"
        "store.update(sys.argv[2],f)\n"
    )
    ps = [subprocess.Popen([PY, "-c", worker, str(HERE), rid2, tag]) for tag in ("A", "B")]
    rcs = [p.wait(timeout=20) for p in ps]
    race = _store_get(rid2).get("_race", [])
    check("(3) 두 프로세스 갱신 모두 보존", rcs == [0, 0] and sorted(race) == ["A", "B"], race)
    for x in (rid2, rid3):
        pipe("fail", x, "--note", "e2e 점검용 — 실제 제작 아님")

    # 점검용 요청이 «실제 제작» 완성 카드로 남지 않게 닫는다
    pipe("fail", rid, "--note", "e2e 점검용 — 실제 제작 아님")
    print(f"\n{ok} 통과 / {fail} 실패 · request_id={rid} (점검 후 failed 로 닫음)")
    print("⚠ 오디오=기존 파일 부착 → «경로 검증»이지 «실생성 연동 검증» 아님")
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
